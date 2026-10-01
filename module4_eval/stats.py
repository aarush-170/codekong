"""Paired significance testing for the equal-budget headline (P0-2).

Each surviving mutant is attacked once by every arm (RAG at HEADLINE_K), so
kill outcomes are paired binary observations on the same mutants.

PRIMARY result — per subject, McNemar's exact test: under H0 the discordant
pairs split 50/50, so the p-value is an exact two-sided binomial test on them
(scipy.stats.binomtest). Per comparison (arm B vs arm A):

  2x2 table     a = both kill      b = only A kills
                c = only B kills   d = neither kills
  p_exact       McNemar exact, two-sided; 1.0 by definition when b + c == 0
  p_holm        Holm-Bonferroni over the pairwise comparisons in that
                subject (identity when there is only one comparison)
  risk_diff     kill-rate(B) - kill-rate(A) = (c - b) / n
  ci95          Newcombe (1998) method 10: Wilson score intervals of each
                marginal (scipy) combined with a continuity-corrected phi

SECONDARY result — combined, stratified by subject (exact CMH for matched
pairs). Under H0 every discordant pair is a fair coin whatever its stratum,
so the exact stratified p-value is binomtest(sum c_s, sum (b_s + c_s)); the
Mantel-Haenszel risk difference (pair-count weights) is
sum (c_s - b_s) / sum n_s. Both are numerically equal to the pooled values —
stratification is used so the combined test is subject-aware by
construction, not because it changes the numbers. It is reported for
completeness only: the per-subject results are the finding.

Writes results_dir/stats_<subject>.json and stats_combined.json.

    python -m module4_eval.stats
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import binomtest

from core.config import resolve
from module4_eval.compare_conditions import load_all_results
from module4_eval.headline_analysis import HEADLINE_K, _arms, headline_frame

CONFIDENCE = 0.95
BASELINE = "NO_RAG"
COMBINED_NOTE = ("Secondary, reported for completeness. Stratified by subject; "
                 "the per-subject McNemar tests are the finding. This is not "
                 "evidence that the effect holds across subjects.")
ZERO_DISC_NOTE = ("no discordant pairs: the arms agree on every mutant, so "
                  "McNemar's test has no information (p = 1 by definition)")


def _wilson(kills: int, n: int) -> tuple[float, float]:
    ci = binomtest(kills, n).proportion_ci(confidence_level=CONFIDENCE,
                                           method="wilson")
    return ci.low, ci.high


def newcombe_paired_ci(a: int, b: int, c: int, d: int,
                       cc_phi: bool = True) -> tuple[float, float]:
    """95% CI for p_B - p_A from a paired 2x2 (Newcombe 1998).

    p_B = (a + c) / n and p_A = (a + b) / n. cc_phi=True is method 10
    (continuity-corrected phi, Newcombe's recommendation); cc_phi=False is
    method 8. In Newcombe's notation e=a, f=c, g=b, h=d.
    """
    n = a + b + c + d
    p_b, p_a = (a + c) / n, (a + b) / n
    l_b, u_b = _wilson(a + c, n)
    l_a, u_a = _wilson(a + b, n)
    den = (a + b) * (c + d) * (a + c) * (b + d)
    num = a * d - b * c
    if cc_phi and num > 0:
        num = max(num - n / 2, 0.0)
    phi = num / math.sqrt(den) if den else 0.0
    theta = p_b - p_a
    delta = math.sqrt(max(0.0, (p_b - l_b) ** 2
                          - 2 * phi * (p_b - l_b) * (u_a - p_a)
                          + (u_a - p_a) ** 2))
    eps = math.sqrt(max(0.0, (u_b - p_b) ** 2
                        - 2 * phi * (u_b - p_b) * (p_a - l_a)
                        + (p_a - l_a) ** 2))
    return max(-1.0, theta - delta), min(1.0, theta + eps)


def holm(pvalues: list[float]) -> list[float]:
    """Holm-Bonferroni step-down adjusted p-values, in input order."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    adj, running = [0.0] * m, 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adj[i] = running
    return adj


def _exact_p(c: int, disc: int) -> float:
    return float(binomtest(c, disc, 0.5, alternative="two-sided").pvalue) \
        if disc else 1.0


def _paired_counts(a_kills: pd.Series, b_kills: pd.Series) -> tuple[int, ...]:
    if set(a_kills.index) != set(b_kills.index):
        raise ValueError("arms are not paired on the same mutants")
    b_kills = b_kills.reindex(a_kills.index)
    return (int((a_kills & b_kills).sum()), int((a_kills & ~b_kills).sum()),
            int((~a_kills & b_kills).sum()), int((~a_kills & ~b_kills).sum()))


def mcnemar_exact(a_kills: pd.Series, b_kills: pd.Series) -> dict:
    """Compare arm B against arm A on kill outcomes indexed by mutant_id."""
    a, b, c, d = _paired_counts(a_kills, b_kills)
    n = a + b + c + d
    lo, hi = newcombe_paired_ci(a, b, c, d)
    return {"n_pairs": n,
            "table": {"both_kill": a, "only_A_kills": b,
                      "only_B_kills": c, "neither_kills": d},
            "discordant_b": b, "discordant_c": c,
            "kills_A": a + b, "kills_B": a + c,
            "kill_rate_A": (a + b) / n, "kill_rate_B": (a + c) / n,
            "p_exact": _exact_p(c, b + c),
            "risk_difference": (c - b) / n,
            "ci95_risk_difference": [lo, hi],
            "ci_method": "Newcombe 1998 method 10 (Wilson score, "
                         "continuity-corrected phi)",
            "note": None if b + c else ZERO_DISC_NOTE}


def stratified_mcnemar(strata: dict[str, tuple[pd.Series, pd.Series]]) -> dict:
    """Exact CMH for matched pairs, stratified by subject (B vs A)."""
    per, n_tot, b_tot, c_tot = {}, 0, 0, 0
    for name, (a_k, b_k) in strata.items():
        a, b, c, d = _paired_counts(a_k, b_k)
        per[name] = {"n_pairs": a + b + c + d, "discordant_b": b,
                     "discordant_c": c}
        n_tot, b_tot, c_tot = n_tot + a + b + c + d, b_tot + b, c_tot + c
    return {"n_pairs": n_tot, "n_strata": len(per), "strata": per,
            "discordant_b": b_tot, "discordant_c": c_tot,
            "p_exact": _exact_p(c_tot, b_tot + c_tot),
            "risk_difference_mh": (c_tot - b_tot) / n_tot,
            "method": "exact stratified McNemar (CMH for matched pairs), "
                      "strata = subjects; MH risk difference, pair-count "
                      "weights",
            "note": None if b_tot + c_tot else ZERO_DISC_NOTE}


def _comparisons(arms: list[str]) -> list[tuple[str, str]]:
    base = [(BASELINE, x) for x in arms if x != BASELINE] if BASELINE in arms else []
    rest = [p for p in itertools.combinations(arms, 2) if BASELINE not in p]
    return base + rest


def _kills(g: pd.DataFrame) -> dict[str, pd.Series]:
    return {c: x.set_index("mutant_id")["killed"].astype(bool)
            for c, x in g.groupby("condition")}


def _with_holm(comps: list[dict]) -> list[dict]:
    for comp, p in zip(comps, holm([c["p_exact"] for c in comps])):
        comp["p_holm"] = p
    return comps


def subject_stats(g: pd.DataFrame, label: str, k: int = HEADLINE_K) -> dict:
    kills = _kills(g)
    comps = [{"A": a, "B": b, **mcnemar_exact(kills[a], kills[b])}
             for a, b in _comparisons(_arms(g))]
    return {"subject": label, "role": "primary", "rag_k": k,
            "test": "McNemar exact (two-sided)",
            "multiple_comparisons": f"Holm-Bonferroni over {len(comps)} "
                                    "comparison(s) in this subject",
            "comparisons": _with_holm(comps)}


def combined_stats(sel: pd.DataFrame, k: int = HEADLINE_K) -> dict:
    by_subj = {s: _kills(g) for s, g in sel.groupby("subject")}
    comps = []
    for a, b in _comparisons(_arms(sel)):
        strata = {s: (kl[a], kl[b]) for s, kl in by_subj.items()
                  if a in kl and b in kl}
        comps.append({"A": a, "B": b, **stratified_mcnemar(strata)})
    return {"subject": "combined", "role": "secondary", "rag_k": k,
            "note": COMBINED_NOTE,
            "multiple_comparisons": f"Holm-Bonferroni over {len(comps)} "
                                    "comparison(s)",
            "comparisons": _with_holm(comps)}


def _line(s: dict) -> str:
    head = f"{s['subject']} [{s['role']}]"
    if s["role"] == "secondary":
        head += f"\n  NOTE: {s['note']}"
    rows = []
    for c in s["comparisons"]:
        n = c["n_pairs"]
        if "risk_difference" in c:
            lo, hi = c["ci95_risk_difference"]
            eff = (f"kills {c['kills_B']}/{n} vs {c['kills_A']}/{n}  "
                   f"RD={c['risk_difference']:+.3f} [{lo:+.3f}, {hi:+.3f}]")
        else:
            eff = f"MH RD={c['risk_difference_mh']:+.3f} over {c['n_strata']} strata"
        rows.append(
            f"  {c['B']} vs {c['A']}: n={n}  b(only {c['A']})={c['discordant_b']} "
            f"c(only {c['B']})={c['discordant_c']}  p_exact={c['p_exact']:.3g} "
            f"p_holm={c['p_holm']:.3g}  {eff}"
            + (f"\n    note: {c['note']}" if c["note"] else ""))
    return head + "\n" + "\n".join(rows)


def main(cfg: dict, tags: list[str] | None = None) -> dict[str, Path]:
    sel = headline_frame(load_all_results(cfg, tags=tags))
    outdir = resolve(cfg, cfg["output"]["results_dir"])
    results = [subject_stats(g, s) for s, g in sel.groupby("subject")]
    results.append(combined_stats(sel))
    paths = {}
    for s in results:
        p = outdir / f"stats_{s['subject']}.json"
        p.write_text(json.dumps(s, indent=2), encoding="utf-8")
        paths[s["subject"]] = p
        print(_line(s))
    for p in paths.values():
        print(f"[stats] wrote {p}")
    return paths


if __name__ == "__main__":
    import argparse
    from core.config import load_config
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", nargs="*", default=None,
                    help="explicit raw_<tag>.csv files to analyse (default: "
                         "all untagged raw_*.csv)")
    main(load_config(), ap.parse_args().tags)
