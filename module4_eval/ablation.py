"""Retriever ablation table (P0-6) — kept OUT of the headline on purpose.

Arms are RAG at k=5 with retrieval-time switches on the same index:
  full          reference arm (the headline RAG k=5 rows)
  no_constants  constants chunks removed from retrieval
  no_depfetch   dependency-aware definition fetch skipped

Inputs are explicit --tags (raw_<tag>.csv): one reference file and one file
per ablation arm, all over the SAME mutants. Each ablation arm is compared
with the reference by McNemar's exact test (Holm across the ablation arms).

    python -m module4_eval.ablation --reference ctxlib \
        --arms ctxlib_ablation_no_constants ctxlib_ablation_no_depfetch
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from core.config import resolve
from module4_eval.compare_conditions import load_all_results
from module4_eval.headline_analysis import HEADLINE_K, _fmt
from module4_eval.stats import holm, mcnemar_exact


def _arm_rows(df: pd.DataFrame, k: int) -> pd.DataFrame:
    rag = df[(df["condition"] == "RAG") & (df["k"] == k)]
    if rag["mutant_id"].duplicated().any():
        raise ValueError("more than one RAG attempt per mutant in an arm")
    return rag.set_index("mutant_id")


def ablation_stats(reference: pd.DataFrame, arms: dict[str, pd.DataFrame],
                   k: int = HEADLINE_K) -> dict:
    ref = _arm_rows(reference, k)
    out = {"k": k, "n_mutants": len(ref), "reference": {
        "kills": int(ref["killed"].sum()), "valid_tests": int(ref["valid_test"].sum())},
        "arms": []}
    comps = []
    for name, df in arms.items():
        a = _arm_rows(df, k)
        if set(a.index) != set(ref.index):
            raise ValueError(f"{name}: arm covers different mutants than the "
                             "reference — not a paired comparison")
        r = mcnemar_exact(ref["killed"].astype(bool),
                          a["killed"].astype(bool))
        r.update(arm=name, kills=int(a["killed"].sum()),
                 valid_tests=int(a["valid_test"].sum()),
                 variant=sorted(set(a["retriever_variant"].dropna()))
                 if "retriever_variant" in a else [])
        comps.append(r)
    for r, p in zip(comps, holm([c["p_exact"] for c in comps])):
        r["p_holm"] = p
    out["arms"] = comps
    return out


def ablation_markdown(s: dict) -> str:
    n = s["n_mutants"]
    lines = ["# P0-6: retriever ablation (RAG k=%d, ctxlib)" % s["k"], "",
             "Not part of the headline table. Reference = full retriever. "
             "McNemar exact vs reference (A = reference, B = ablated arm); "
             "Holm across ablation arms. Cells are count / attempts (rate).", "",
             "| arm | kills / attempts | valid tests / attempts | "
             "only ref kills (b) | only arm kills (c) | p exact | p Holm |",
             "|---|---|---|---|---|---|---|",
             f"| full (reference) | {_fmt(s['reference']['kills'], n)} | "
             f"{_fmt(s['reference']['valid_tests'], n)} | — | — | — | — |"]
    for c in s["arms"]:
        lines.append(f"| {c['arm']} | {_fmt(c['kills'], n)} | "
                     f"{_fmt(c['valid_tests'], n)} | {c['discordant_b']} | "
                     f"{c['discordant_c']} | {c['p_exact']:.3g} | "
                     f"{c['p_holm']:.3g} |")
    return "\n".join(lines) + "\n"


def main(cfg: dict, reference: str, arm_tags: list[str]) -> dict[str, Path]:
    ref = load_all_results(cfg, tags=[reference])
    arms = {t: load_all_results(cfg, tags=[t]) for t in arm_tags}
    s = ablation_stats(ref, arms)
    outdir = resolve(cfg, cfg["output"]["results_dir"])
    paths = {"json": outdir / "ablation_ctxlib.json",
             "md": outdir / "ablation_ctxlib.md"}
    paths["json"].write_text(json.dumps(s, indent=2), encoding="utf-8")
    paths["md"].write_text(ablation_markdown(s), encoding="utf-8")
    print(ablation_markdown(s))
    return paths


if __name__ == "__main__":
    import argparse
    from core.config import load_config
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", required=True,
                    help="tag whose RAG k=5 rows are the full-retriever arm")
    ap.add_argument("--arms", nargs="+", required=True)
    a = ap.parse_args()
    main(load_config(), a.reference, a.arms)
