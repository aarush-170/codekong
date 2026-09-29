"""Headline RAG-vs-closed-book comparison at EQUAL attempt budgets (P0-1).

The RAG arm was run at three retrieval depths, the closed-book arm once, so
pooling RAG over k gives it three attempts per mutant against one. The
headline therefore fixes RAG at a single depth (HEADLINE_K = 5): every arm
then gets exactly one attempt per surviving mutant, and every arm is scored
on the SAME mutant set (checked, not assumed).

The k sweep is kept, but only as its own artifact for RQ3.

Every cell is printed as kills/attempts (rate) so its denominator is
explicit. Outputs (under results_dir):

  headline_k5.csv / headline_k5.md   per subject, per class, and combined
  ksweep_rag.csv  / ksweep_rag.md    RAG at each k, per subject (RQ3)

Arms are data-driven: any closed-book-style condition in the raw CSVs
(NO_RAG, and FULL_CONTEXT once it exists) is included as-is; RAG is filtered
to HEADLINE_K.

    python -m module4_eval.headline_analysis
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.config import resolve
from module4_eval.compare_conditions import HARDNESS_ORDER, load_all_results

HEADLINE_K = 5
ARM_ORDER = ["NO_RAG", "FULL_CONTEXT", "RAG"]
ALL = "ALL"


def _fmt(num: int, den: int) -> str:
    if den == 0:
        return "—"
    return f"{num}/{den} ({100 * num / den:.1f}%)"


def headline_frame(df: pd.DataFrame, k: int = HEADLINE_K) -> pd.DataFrame:
    """Rows of the equal-budget comparison: one attempt per mutant per arm."""
    rag = df[(df["condition"] == "RAG") & (df["k"] == k)]
    other = df[df["condition"] != "RAG"]
    sel = pd.concat([other, rag], ignore_index=True)

    # Equal budgets are only real if every arm saw the same mutants once.
    for subject, g in sel.groupby("subject"):
        dup = g.duplicated(subset=["mutant_id", "condition"])
        if dup.any():
            raise ValueError(f"{subject}: >1 attempt per mutant in an arm: "
                             f"{g[dup][['mutant_id', 'condition']].values.tolist()}")
        sets = {c: frozenset(x["mutant_id"]) for c, x in g.groupby("condition")}
        if len(set(sets.values())) != 1:
            raise ValueError(f"{subject}: arms cover different mutant sets: "
                             f"{ {c: len(s) for c, s in sets.items()} }")
    return sel


def _arms(df: pd.DataFrame) -> list[str]:
    present = set(df["condition"])
    return [a for a in ARM_ORDER if a in present] + sorted(present - set(ARM_ORDER))


def _tally(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    return (df.groupby(keys)
              .agg(attempts=("mutant_id", "count"),
                   kills=("killed", "sum"),
                   valid_tests=("valid_test", "sum"))
              .reset_index())


def headline_table(sel: pd.DataFrame) -> pd.DataFrame:
    """Long table: subject x mutation_class x condition with counts.

    mutation_class == ALL is the subject total; subject == ALL pools subjects.
    """
    parts = [
        _tally(sel, ["subject", "mutation_class", "condition"]),
        _tally(sel, ["subject", "condition"]).assign(mutation_class=ALL),
        _tally(sel, ["mutation_class", "condition"]).assign(subject=ALL),
        _tally(sel, ["condition"]).assign(subject=ALL, mutation_class=ALL),
    ]
    t = pd.concat(parts, ignore_index=True)
    for col in ("attempts", "kills", "valid_tests"):
        t[col] = t[col].astype(int)
    t["kill_rate"] = t["kills"] / t["attempts"]
    t["valid_test_rate"] = t["valid_tests"] / t["attempts"]
    subj_order = sorted(set(sel["subject"])) + [ALL]
    cls_order = [c for c in HARDNESS_ORDER if c in set(sel["mutation_class"])] + [ALL]
    arm_order = _arms(sel)
    t["_s"] = t["subject"].map(subj_order.index)
    t["_c"] = t["mutation_class"].map(cls_order.index)
    t["_a"] = t["condition"].map(arm_order.index)
    return (t.sort_values(["_s", "_c", "_a"])
             .drop(columns=["_s", "_c", "_a"])
             [["subject", "mutation_class", "condition", "attempts", "kills",
               "kill_rate", "valid_tests", "valid_test_rate"]]
             .reset_index(drop=True))


def headline_markdown(t: pd.DataFrame, k: int = HEADLINE_K) -> str:
    arms = [a for a in ARM_ORDER if a in set(t["condition"])] + \
           sorted(set(t["condition"]) - set(ARM_ORDER))
    label = {a: (f"{a} (k={k})" if a == "RAG" else a) for a in arms}
    out = [f"# Headline comparison at equal attempt budgets (RAG k={k})", "",
           "One generation attempt per surviving mutant per arm; all arms "
           "scored on the same mutants. Each cell is **kills / attempts "
           "(kill rate)**; here attempts = number of surviving mutants.", ""]

    def block(title, rows, key, metric):
        num = "kills" if metric == "kill" else "valid_tests"
        hdr = [key, "mutants (= attempts per arm)"] + \
              [f"{label[a]}: {'kills' if metric == 'kill' else 'valid tests'} / attempts"
               for a in arms]
        out.extend([f"## {title}", "", "| " + " | ".join(hdr) + " |",
                    "|" + "---|" * len(hdr)])
        for name, g in rows:
            g = g.set_index("condition")
            n = int(g["attempts"].iloc[0])
            cells = [_fmt(int(g.loc[a, num]), int(g.loc[a, "attempts"]))
                     if a in g.index else "—" for a in arms]
            out.append("| " + " | ".join([str(name), str(n)] + cells) + " |")
        out.append("")

    subj = t[t["mutation_class"] == ALL]
    block("Kill rate by subject", subj.groupby("subject", sort=False),
          "subject", "kill")
    block("Valid-test rate by subject", subj.groupby("subject", sort=False),
          "subject", "valid")
    for s in [x for x in t["subject"].unique()]:
        cls = t[(t["subject"] == s) & (t["mutation_class"] != ALL)]
        block(f"Kill rate by mutation class — {s}",
              cls.groupby("mutation_class", sort=False), "mutation_class", "kill")
    return "\n".join(out)


def ksweep_table(df: pd.DataFrame) -> pd.DataFrame:
    """RQ3: RAG at every depth, per subject (and per class), with counts."""
    rag = df[df["condition"] == "RAG"].copy()
    rag["k"] = rag["k"].astype(int)
    t = pd.concat([
        _tally(rag, ["subject", "k"]).assign(mutation_class=ALL),
        _tally(rag, ["subject", "mutation_class", "k"]),
    ], ignore_index=True)
    t["kill_rate"] = t["kills"] / t["attempts"]
    t["valid_test_rate"] = t["valid_tests"] / t["attempts"]
    return (t.sort_values(["subject", "mutation_class", "k"])
             [["subject", "mutation_class", "k", "attempts", "kills",
               "kill_rate", "valid_tests", "valid_test_rate"]]
             .reset_index(drop=True))


def ksweep_markdown(t: pd.DataFrame) -> str:
    ks = sorted(t["k"].unique())
    out = ["# RQ3: RAG retrieval-depth sweep", "",
           "RAG arm only; each depth is a separate run of one attempt per "
           "mutant. Not a headline comparison — do not pool across k against "
           "a single-attempt arm. Cells are **count / attempts (rate)**.", ""]
    for metric, num in (("Valid-test rate", "valid_tests"), ("Kill rate", "kills")):
        hdr = ["subject", "class"] + [f"k={k}: {num.replace('_', ' ')} / attempts"
                                      for k in ks]
        out.extend([f"## {metric} by k", "", "| " + " | ".join(hdr) + " |",
                    "|" + "---|" * len(hdr)])
        for (s, c), g in t.groupby(["subject", "mutation_class"], sort=False):
            g = g.set_index("k")
            cells = [_fmt(int(g.loc[k, num]), int(g.loc[k, "attempts"]))
                     if k in g.index else "—" for k in ks]
            out.append("| " + " | ".join([s, c] + cells) + " |")
        out.append("")
    return "\n".join(out)


def main(cfg: dict) -> dict[str, Path]:
    df = load_all_results(cfg)
    outdir = resolve(cfg, cfg["output"]["results_dir"])
    head = headline_table(headline_frame(df))
    sweep = ksweep_table(df)
    paths = {"headline_csv": outdir / f"headline_k{HEADLINE_K}.csv",
             "headline_md": outdir / f"headline_k{HEADLINE_K}.md",
             "ksweep_csv": outdir / "ksweep_rag.csv",
             "ksweep_md": outdir / "ksweep_rag.md"}
    head.to_csv(paths["headline_csv"], index=False)
    paths["headline_md"].write_text(headline_markdown(head), encoding="utf-8")
    sweep.to_csv(paths["ksweep_csv"], index=False)
    paths["ksweep_md"].write_text(ksweep_markdown(sweep), encoding="utf-8")
    print(headline_markdown(head))
    for p in paths.values():
        print(f"[headline] wrote {p}")
    return paths


if __name__ == "__main__":
    from core.config import load_config
    main(load_config())
