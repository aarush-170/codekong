"""CodeKong — single entry point.

    python run_pipeline.py --repo sorts                 # full pipeline
    python run_pipeline.py --repo sorts --phase mutate  # one phase
    python run_pipeline.py --repo schedule --k 3 5 8 --limit 20

Phases: mutate -> index -> generate (both conditions, retrieval inside the
RAG arm per k) -> evaluate. Runs one subject repo at a time, per the design.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from core import schema
from core.config import load_config, resolve
from core.guards import assert_fork_capable_linux, assert_not_windows_mount
from core.hardware import recommend_model


def select_mutants(mutants: list[dict], limit: int | None = None,
                   ids_csv: str | Path | None = None) -> list[dict]:
    """Pick the mutants to run. --limit is the seeded random sample;
    --mutant-ids-from runs exactly the mutant_ids in a CSV (file order kept)
    and fails loudly if any are absent from the mutant file."""
    if ids_csv is not None:
        import csv
        with open(ids_csv, newline="", encoding="utf-8") as fh:
            rd = csv.DictReader(fh)
            if "mutant_id" not in (rd.fieldnames or []):
                raise SystemExit(f"{ids_csv}: no mutant_id column")
            wanted = {row["mutant_id"] for row in rd if row["mutant_id"]}
        have = {m["mutant_id"] for m in mutants}
        missing = sorted(wanted - have)
        if missing:
            raise SystemExit(f"{len(missing)} of {len(wanted)} mutant_ids in "
                             f"{ids_csv} are missing from the mutant file: "
                             f"{missing}")
        return [m for m in mutants if m["mutant_id"] in wanted]
    if limit and limit < len(mutants):
        # Deterministic random sample, NOT mutants[:limit]: the head of the
        # list is alphabetical by file, so small probes used to land entirely
        # on one file's worst-case code (e.g. external_sort's I/O classes)
        # and measure the subject's pathology instead of the model.
        import random
        return random.Random(42).sample(mutants, limit)
    return mutants


def check_results_tag(results_dir: Path, tag: str) -> None:
    """Refuse to start if this tag's output exists: a finished arm must never
    be overwritten (the untagged files are the committed July evidence)."""
    raw = Path(results_dir) / f"raw_{tag}.csv"
    if raw.exists():
        raise SystemExit(f"{raw} already exists — refusing to overwrite a "
                         "finished run. Choose a new --results-tag.")


def phase_mutate(cfg, args, client):
    from agentic import mutation_agent
    assert_fork_capable_linux()
    out = mutation_agent.run(cfg, args.repo, client,
                             skip_mutmut=args.skip_mutmut,
                             skip_semantic=args.skip_semantic)
    print(f"[pipeline] surviving mutants at {out}")


def phase_index(cfg, args):
    from agentic import knowledge_agent
    knowledge_agent.run(cfg, args.repo)


def phase_generate(cfg, args, client):
    from agentic import retrieval_agent
    from agentic.test_gen_agent import generate_and_validate
    from module2_rag.retriever import Retriever
    from module4_eval.metrics_logger import log_metrics
    from module4_eval.validator import audit_results
    from module4_eval.checkpoint import Checkpoint

    results_dir = resolve(cfg, cfg["output"]["results_dir"])
    tag = args.results_tag
    check_results_tag(results_dir, tag)
    mutants = select_mutants(
        schema.load_mutants(resolve(cfg, cfg["output"]["surviving_mutants"])),
        limit=args.limit, ids_csv=args.mutant_ids_from)
    print(f"[pipeline] generating tests for {len(mutants)} mutants "
          f"(results tag: {tag}, retriever variant: {args.retriever_variant})")

    # Crash-safe checkpoint: each result is streamed to an append-only side-file
    # and a rerun of the SAME command resumes, skipping finished work. Vital for
    # the overnight run on a machine without Claude Code to babysit it.
    ck = Checkpoint(results_dir / f"_checkpoint_{tag}.jsonl")
    all_results = ck.load()
    if all_results:
        print(f"[pipeline] resuming from {ck.path.name}: "
              f"{len(all_results)} results already recorded")
    conditions = (["NO_RAG", "RAG"] if args.conditions == "both"
                  else [args.conditions])

    if "NO_RAG" in conditions:
        for m in mutants:
            if ck.is_done(m["mutant_id"], "NO_RAG", None):
                continue
            r = generate_and_validate(cfg, args.repo, m, None, "NO_RAG", client,
                                     run_tag=tag)
            print(f"[NO_RAG] {m['mutant_id']}: {r['status']}")
            ck.record(r)
            all_results.append(r)

    if "RAG" in conditions:
        ks = args.k or cfg["rag"]["k_values"]
        retriever = Retriever(cfg, args.repo, args.retriever_variant)
        for k in ks:
            # Persist the retrieval handoff for auditability (JSON file
            # protocol between Retrieval Agent and Test Generation Agent).
            retrieval_agent.run(cfg, args.repo, k=k, mutants=mutants,
                                variant=args.retriever_variant)
            for m in mutants:
                if ck.is_done(m["mutant_id"], "RAG", k):
                    continue
                chunks = retriever.retrieve(m, k)
                r = generate_and_validate(cfg, args.repo, m, chunks, "RAG",
                                          client, k=k, run_tag=tag,
                                          variant=args.retriever_variant)
                print(f"[RAG k={k}] {m['mutant_id']}: {r['status']}")
                ck.record(r)
                all_results.append(r)

    log_metrics(cfg, all_results, tag)
    audit_results(all_results)
    raw = results_dir / f"records_{tag}.json"
    raw.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    ck.clear()  # consolidated into records_<tag>.json — drop the side-file


def phase_evaluate(cfg, args):
    from module4_eval import compare_conditions
    compare_conditions.main(cfg)


def main():
    ap = argparse.ArgumentParser(description="CodeKong pipeline")
    ap.add_argument("--repo", required=True, help="subject key from config.yaml")
    ap.add_argument("--phase", default="all",
                    choices=["all", "mutate", "index", "generate", "evaluate"])
    ap.add_argument("--conditions", default="both",
                    choices=["both", "RAG", "NO_RAG"])
    ap.add_argument("--k", type=int, nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=None,
                    help="cap number of mutants (seeded random sample)")
    ap.add_argument("--mutant-ids-from", metavar="CSV", default=None,
                    help="run exactly the mutant_ids in this CSV (column "
                         "mutant_id); error if any are missing; excludes --limit")
    ap.add_argument("--results-tag", metavar="TAG", default=None,
                    help="REQUIRED for generate: outputs raw_/summary_/records_"
                         "<TAG>, checkpoint _checkpoint_<TAG>.jsonl; refuses "
                         "to start if raw_<TAG>.csv exists")
    ap.add_argument("--retriever-variant", default="full",
                    choices=["full", "no_constants", "no_depfetch"],
                    help="RAG ablation switch (retrieval-time, same index); "
                         "RAG-only")
    ap.add_argument("--skip-mutmut", action="store_true")
    ap.add_argument("--skip-semantic", action="store_true")
    args = ap.parse_args()
    if args.mutant_ids_from and args.limit:
        ap.error("--mutant-ids-from and --limit are mutually exclusive")
    if args.phase in ("all", "generate"):
        if not args.results_tag:
            ap.error("--results-tag is required when generating (it keeps "
                     "runs from overwriting the committed results)")
        import re
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", args.results_tag):
            ap.error("--results-tag may contain only letters, digits, _ . -")
    if args.retriever_variant != "full" and args.conditions != "RAG":
        ap.error("--retriever-variant other than 'full' needs --conditions RAG")

    cfg = load_config()
    assert_not_windows_mount(cfg["_project_root"])
    if args.repo not in cfg["subjects"]:
        sys.exit(f"unknown --repo {args.repo!r}; configured: "
                 f"{list(cfg['subjects'])}")
    pinned = Path(cfg["_project_root"]) / cfg["subjects"][args.repo]["path"]
    if not pinned.exists():
        sys.exit(f"subject repo missing at {pinned} — run ./setup.sh first")

    hw = recommend_model()
    print(f"[pipeline] hardware probe: {json.dumps(hw)}")
    if hw["recommended_model"] != cfg["llm"]["model"]:
        print(f"[pipeline] note: config model is {cfg['llm']['model']}, probe "
              f"suggests {hw['recommended_model']} — config wins.")

    client = None
    if args.phase in ("all", "mutate", "generate"):
        from module3_llm.ollama_client import OllamaClient
        client = OllamaClient(cfg)

    if args.phase in ("all", "mutate"):
        phase_mutate(cfg, args, client)
    if args.phase in ("all", "index"):
        phase_index(cfg, args)
    if args.phase in ("all", "generate"):
        phase_generate(cfg, args, client)
    if args.phase in ("all", "evaluate"):
        phase_evaluate(cfg, args)


if __name__ == "__main__":
    main()
