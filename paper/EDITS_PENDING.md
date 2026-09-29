# Pending edits to `CodeKong_RAG_Mutation_Testing.docx`

One accumulating list. Every task branch appends here; nobody edits the
`.docx` from a branch. Each entry gives the **exact current wording** and the
**exact replacement**, so applying it is mechanical. Every number in a
replacement names the results file it comes from.

Status values: `READY` (apply as written) · `BLOCKED` (number not yet
available — do not fill in) · `DECISION` (needs a call from the authors).

---

## E1 · §VII-D Conclusion validity — `READY` · source: P0-2 (`p0-2-mcnemar`)

Numbers from `module4_eval/results/stats_{ctxlib,sorts_focused,schedule,combined}.json`.

**Current:**

> The study spans 39 survivors across three subjects (24 in the primary subject)—enough to expose a large effect and its boundary, but pilot-scale. We therefore report descriptive statistics and a worked mechanism rather than inferential tests, and identify replication on real, cross-module codebases as the necessary next step.

**Replace with:**

> The study spans 39 survivors across three subjects (24 in the primary subject) and is pilot-scale. Both conditions receive one attempt per mutant (RAG at k = 5), so kill outcomes are paired, and we test them per subject with McNemar's exact test; per-subject results are the primary analysis. On the context-dependent subject, RAG killed 16 mutants that closed-book generation did not, and closed-book killed none that RAG missed (exact p = 3.1 × 10⁻⁵; risk difference +0.667, 95% CI [+0.402, +0.806], Newcombe's paired score interval). On the self-contained and complex-OO subjects the two conditions agreed on every mutant, so the test carries no information; their intervals ([−0.247, +0.247] and [−0.390, +0.390]) are wide enough that these ties do not establish the absence of an effect. A subject-stratified combined test is reported for completeness only, since the finding is that the effect is subject-dependent. Replication on real, cross-module codebases remains the necessary next step.

Notes:
- Holm-adjusted p-values equal the raw ones today (one comparison per subject). When FULL_CONTEXT lands (P0-3) there are three comparisons per subject; re-run `python -m module4_eval.stats` and replace `3.1 × 10⁻⁵` with the `p_holm` value, stating "Holm-adjusted".
- If a combined figure is quoted anywhere, it must be the stratified one from `stats_combined.json` (p = 3.1 × 10⁻⁵, MH risk difference +0.410), must carry the "for completeness" framing, and must note that all 16 discordant pairs come from ctxlib.

---

## E2 · §V preamble — `READY` · source: P0-1 (`p0-1-equal-budgets`)

**Current:**

> All figures are computed from the raw per-mutant records; RAG values aggregate over k ∈ {3,5,8} unless a depth is named.

**Replace with:**

> All figures are computed from the raw per-mutant records. Headline comparisons fix RAG at k = 5, so each condition receives exactly one generation attempt per surviving mutant; the depth sweep k ∈ {3,5,8} is reported only for RQ3.

---

## E3 · §IV-C Metrics, kill-rate definition — `READY` · source: P0-1

**Current:**

> Kill rate is the fraction of generation attempts yielding a kill; because the RAG condition is run at three depths, its attempts are three times the number of mutants.

**Replace with:**

> Kill rate is the fraction of surviving mutants killed, with one generation attempt per mutant per condition (RAG at k = 5); every table states its numerator and denominator.

---

## E4 · Table II (kill rate by subject) — `READY` · source: P0-1

Numbers from `module4_eval/results/headline_k5.csv`. Change the `N` header to `Mutants (= attempts per arm)` and use `kills/attempts (rate)` cells.

| Row | Current (closed-book / RAG / Δ) | Replace with |
|---|---|---|
| Context-dependent (24) | 12.5% / 77.8% / +65.3 | 3/24 (12.5%) / 19/24 (79.2%) / +66.7 |
| Self-contained (9) | 22.2% / 22.2% / 0.0 | 2/9 (22.2%) / 2/9 (22.2%) / 0.0 |
| Complex OO (6) | 0.0% / 0.0% / 0.0 | 0/6 (0.0%) / 0/6 (0.0%) / 0.0 |
| Combined (39) | 12.8% / 53.0% / +40.2 | 5/39 (12.8%) / 21/39 (53.8%) / +41.0 |

---

## E5 · Table III (ctxlib by class) — `READY` · source: P0-1

Numbers from `headline_k5.csv`. The `n` column already shows mutants; with k = 5 the percentages now use the same denominator.

| Class (n) | Current (closed-book / RAG / Δ) | Replace with |
|---|---|---|
| Statement deletion (13) | 15.4% / 82.1% / +66.7 | 2/13 (15.4%) / 11/13 (84.6%) / +69.2 |
| Semantic (7) | 14.3% / 61.9% / +47.6 | 1/7 (14.3%) / 4/7 (57.1%) / +42.9 |
| Higher-order (4) | 0.0% / 91.7% / +91.7 | 0/4 (0.0%) / 4/4 (100.0%) / +100.0 |

The §V-B text ("semantic mutants gain less than statement-deletion mutants") still holds at k = 5 (+42.9 < +69.2); no text change needed there.

---

## E6 · Abstract, §I and §VIII headline figure — `READY` · source: P0-1

The phrase `from 12.5% to 77.8%` appears four times. Three are handled here — the Abstract ("dependency-aware RAG raises the kill rate from 12.5% to 77.8%"), §I ("dependency-aware RAG lifts the kill rate from 12.5% to 77.8%"), and §VIII ("dependency-aware retrieval raised the kill rate from 12.5% to 77.8%"); the fourth, in §V-A, is below.

**In all three, replace** `from 12.5% to 77.8%` **with** `from 12.5% to 79.2% (3/24 to 19/24 mutants, one attempt each)`.

In §V-A, **replace** `On ctxlib the kill rate rises from 12.5% to 77.8%, a 65-point gap;` **with** `On ctxlib the kill rate rises from 3/24 (12.5%) to 19/24 (79.2%), a 66.7-point gap (McNemar exact p = 3.1 × 10⁻⁵);`

In §V-A, **replace** `The combined average (12.8% → 53.0%) is real but driven entirely by ctxlib;` **with** `The combined figure (5/39 → 21/39) is driven entirely by ctxlib, which supplies all 16 discordant pairs;`

The valid-test figures (25% → 88%) are unchanged at k = 5 (6/24 → 21/24 = 87.5%).

---

## E7 · Token cost per kill (RQ4) — `BLOCKED` · source: P0-1

Affected: Abstract ("at a seven-fold lower token cost per kill"), §V-D and Table V (2,246 vs 15,859 tokens/kill), §VIII ("at a seven-fold lower cost per kill").

These numbers pool RAG calls over k ∈ {3,5,8} (`cost_ctxlib.csv` has no k column) against single-attempt closed-book calls, so they are not an equal-budget comparison. A k = 5 figure needs the per-call log `module3_llm/llm_calls.jsonl`, which is gitignored and exists, if at all, only on the WSL machine. **Do not estimate.** Recover the log in the WSL session, or remove the cost claims.

---

## E8 · Retriever ablation (§V-F and dependants) — `BLOCKED` · source: P0-6

No recorded experiment backs these claims. If P0-6 is not run before the deadline, remove items 1, 2, 3, 5 and 6 entirely (no softened or hypothetical rewording). Items 4 and 7 are `DECISION`.

1. Abstract: "An ablation shows both indexing constants and retrieving referenced symbols are necessary."
2. §I contribution 2: "We show both are necessary for RAG to help."
3. §I contribution 5: "…including a worked example and an ablation isolating the retriever’s two components."
4. §III-C: "This matters because a naive function/docstring index cannot surface a value a test needs." and "…which, for a code query, tends to surface sibling functions rather than a constants table." (`DECISION`)
5. §V-F, the whole subsection.
6. §VIII: "and an ablation shows both indexing constants and retrieving referenced symbols are required."
7. §VI: the recommendation to index "not only functions but the constants and tables that encode a system’s domain rules" leans on the ablation. (`DECISION`)
