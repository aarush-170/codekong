# Pending edits to `CodeKong_RAG_Mutation_Testing.docx`

One accumulating list. Every task branch appends here; nobody edits the
`.docx` from a branch. Each entry gives the **exact current wording** and the
**exact replacement**, so applying it is mechanical. Every number in a
replacement names the results file it comes from.

Status values: `READY` (apply as written) · `PROPOSED` (drafted, awaiting author approval) · `SUPERSEDED` (replaced by a later entry) · `BLOCKED` (number not yet
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

---

## E9 · References [6], [11], [12] and new entries — `READY` · source: P0-5 (`p0-5-related-work`)

Details and verification sources for every entry are in `paper/related_work_additions.md`.

**[6] Current:**

> [6] N. Alshahwan, J. Chheda, A. Finogenova, B. Gokkaya, et al., “Automated unit test improvement using large language models at Meta,” in Proc. ACM FSE (Industry), 2024.

**Replace with:**

> [6] N. Alshahwan, J. Chheda, A. Finogenova, B. Gokkaya, et al., “Automated unit test improvement using large language models at Meta,” in Companion Proc. ACM FSE, 2024, pp. 185–196, doi: 10.1145/3663529.3663839.

**[11] Current:**

> [11] B. Tip, J. Bell, and M. Schäfer, “LLMorpheus: Mutation testing using large language models,” arXiv:2404.09952, 2024.

**Replace with:**

> [11] F. Tip, J. Bell, and M. Schäfer, “LLMorpheus: Mutation testing using large language models,” IEEE Trans. Softw. Eng., vol. 51, no. 6, pp. 1645–1665, 2025, doi: 10.1109/TSE.2025.3562025.

**[12] Current:**

> [12] Y. Wang et al., “Retrieval-augmented mutant generation via historical bug-fix pairs,” 2025.

**Replace with:**

> [12] B. Wang, M. Deng, M. Chen, C. Yang, Y. Lin, M. Harman, M. Papadakis, and J. M. Zhang, “Boosting LLMs for mutation generation,” Proc. ACM Softw. Eng., vol. 3, no. FSE, pp. 3368–3391, 2026, doi: 10.1145/3808156.

**Append after [20]:**

> [21] J. Shin, N. Shiri Harzevili, R. Aleithan, H. Hemmati, and S. Wang, “Retrieval-augmented test generation: How far are we?,” in Proc. IEEE/ACM ICSE, 2026, pp. 767–779, doi: 10.1145/3744916.3773163.
>
> [22] Z. Zhang, X. Liu, Y. Lin, X. Gao, H. Sun, and Y. Yuan, “Reference-based retrieval-augmented unit test generation,” ACM Trans. Softw. Eng. Methodol., vol. 35, no. 6, pp. 1–34, 2026, doi: 10.1145/3765758.
>
> [23] M. Harman, J. Ritchey, I. Harper, S. Sengupta, K. Mao, A. Gulati, C. Foster, and H. Robert, “Mutation-guided LLM-based test generation at Meta,” in Companion Proc. ACM FSE, 2025, pp. 180–191, doi: 10.1145/3696630.3728544.

Cite APT/RefTest **once**, as [22]. The arXiv preprint 2410.13542 is the same study. Renumber in citation order during the final pass.

---

## E10 · §II-C, SMART sentence — `READY` · source: P0-5

**Current:**

> and retrieval-boosted mutant generation [12] fetches historical bug-fix pairs.

**Replace with:**

> and SMART [12] retrieves from a vectorised dataset of real-world bugs to generate more realistic mutants.

---

## E11 · §II-B, retrieval-for-test-generation paragraph — `SUPERSEDED` by E16 · source: P0-5

The current sentence "These methods are closed-book with respect to the wider repository." cannot be followed by RefTest [22], which retrieves in-project tests. Proposed: **insert after** “Our study isolates what retrieved codebase context adds on top of a MuTAP-style baseline.”

> Retrieval has recently been applied to test generation directly. Shin et al. [21] retrieve API documentation, GitHub issues and Stack Overflow posts for ML-library APIs and find that RAG does not improve test correctness, though it raises line coverage by 6.5% on average. Zhang et al. [22] retrieve existing tests of related in-project methods to guide the generation of new ones. Meta’s ACH [23] generates concern-specific mutants that current tests miss and then generates tests to kill them. We differ in target and in what is retrieved: we attack surviving mutants under a two-sided kill criterion, retrieve the definitions a unit reads, and isolate when that context changes the outcome.

Decision needed: whether "These methods are closed-book…" should be narrowed to name only the systems verified to be closed-book (MuTAP [5], TestPilot [9]).

---

## E12 · §I, "closed-book" and novelty claims — `SUPERSEDED` by E13–E15 · source: P0-5

**Current (§I):**

> Industrial systems apply the idea at scale [6]. A shared assumption unites them: generation is closed-book—the model sees only the unit under test, not the surrounding codebase.

Adding [22] and [23] makes "a shared assumption unites them" false for [22] and unverified for [23]. Also, §I contribution 2 claims the dependency-aware retriever as a contribution, but RefTest's abstract names "referenced variables" as context existing approaches already use. Suggested direction, not final wording: frame the contribution as the *controlled measurement* of when codebase context helps mutant killing, rather than the novelty of retrieving referenced definitions.

---

## Reframe (E13–E18): prior work is not closed-book; the retriever is not a contribution

Source: P0-5 follow-up (`p0-5b-intro-reframe`). Author decisions (2026-09-29):
(1) drop the retriever mechanism as a contribution, since RefTest [22] treats referenced-variable context as prior practice; (2) contribution 2 becomes the controlled, per-subject measurement; (3) §I's premise that existing methods are closed-book is false and must be rewritten, not softened.

**Every sentence in the draft that says prior work is closed-book**, found by searching the full text:

| Where | Sentence | Handled by |
|---|---|---|
| Abstract | "…but existing methods prompt them closed-book, giving them only the unit under test." | E13 |
| §I ¶2 | "A shared assumption unites them: generation is closed-book—the model sees only the unit under test, not the surrounding codebase." | E14 |
| §I ¶3 | "This assumption is at odds with how software is written." (refers back to the above) | E14 |
| §II-B | "These methods are closed-book with respect to the wider repository." | E16 |
| §II-C | "We bring dependency-aware repo retrieval to mutation-killing test generation…" (novelty claim) | E17 |

All other uses of "closed-book" in the draft name our own baseline condition and stay.

**ACH [23] is UNVERIFIED** with respect to repository retrieval. Its abstract neither says nor rules out that it retrieves codebase context. The wording below describes ACH only by what its abstract states (it generates concern-specific mutants, then tests that kill them), so it holds whichever way that question resolves.

Reference numbers [21]–[23] follow E9.

---

## E13 · Abstract, framing sentence — `PROPOSED`

**Current:**

> Large language models (LLMs) can generate tests to kill surviving mutants, but existing methods prompt them closed-book, giving them only the unit under test. Real functions, however, often depend on constants, lookup tables, and helpers defined elsewhere, so the fact needed to write a discriminating assertion may be absent from the unit.

**Replace with:**

> Large language models (LLMs) can generate tests to kill surviving mutants, and retrieval has begun to enter test generation, supplying external documentation or neighbouring tests. Real functions, however, often depend on constants, lookup tables, and helpers defined elsewhere, so the fact needed to write a discriminating assertion may be absent from the unit, and it is this kind of context whose value for mutant killing we isolate.

---

## E14 · §I, paragraphs 2–3 — `PROPOSED`

**Current (¶2, whole paragraph):**

> A growing body of work uses LLMs to strengthen suites by generating tests that kill surviving mutants. MuTAP [5] is emblematic: it prompts an LLM with the surviving mutant and the original function and requests a killing test. Industrial systems apply the idea at scale [6]. A shared assumption unites them: generation is closed-book—the model sees only the unit under test, not the surrounding codebase.

**Replace with:**

> A growing body of work uses LLMs to strengthen test suites. MuTAP [5] targets mutation directly, augmenting its prompts with surviving mutants so that the model writes tests that reveal them. At Meta, TestGen-LLM [6] extends existing test classes under build, pass and coverage filters, and ACH [23] generates mutants for a specific concern and then generates tests that kill them. Retrieval has also entered test generation, so far drawing on two kinds of knowledge: external API documentation, issues and Q&A posts [21], which did not improve test correctness, and existing tests of related methods in the same project [22]. What we isolate here is a third kind—the definitions a unit reads, such as the constants, tables and helpers its behaviour depends on—and its effect on killing surviving mutants.

This also fixes the misattribution of mutation-guided generation to [6] (`CLAIMS_AUDIT.md` item 4). The MuTAP wording follows its abstract ("augmenting prompts with surviving mutants").

**Current (¶3, first sentence only):**

> This assumption is at odds with how software is written.

**Replace with:**

> The question matters because of how software is written.

The rest of ¶3 stays. Its "Closed-book, it can only guess" describes a generator without that context, not the cited work.

---

## E15 · §I, contribution list — `PROPOSED` (fill-ins `BLOCKED` on P0-4 / P0-6)

**Current (five bullets):**

> A pipeline unifying four escalating mutant classes under one schema, providing a difficulty spectrum for per-class analysis.
>
> A dependency-aware retriever that (a) indexes module-level constants as first-class chunks and (b) explicitly fetches the definitions of the symbols a unit references. We show both are necessary for RAG to help.
>
> A controlled RAG-vs-closed-book study reported per subject, exposing the boundary condition rather than averaging it away.
>
> A released context-dependent benchmark and the complete pipeline for replication under the strict two-sided kill criterion.
>
> A quantitative and qualitative analysis, including a worked example and an ablation isolating the retriever’s two components.

**Replace with (four bullets):**

> 1. A controlled measurement of when codebase retrieval helps an LLM kill surviving mutants. Closed-book and retrieval-augmented generation share model, prompts, mutants, decoding temperature and attempt budget; a kill requires the test to pass on the original program and fail on the mutant; and results are reported and tested per subject rather than averaged, so the conditions under which the effect holds, and vanishes, are visible.
>
> 2. A pipeline that generates [MUTANT-CLASSES] under one schema and filters them to survivors of the existing suite, supporting per-class analysis.
>
> 3. A released context-dependent benchmark and the complete pipeline for replication under the two-sided kill criterion.
>
> 4. A qualitative analysis of how generated tests fail with and without retrieval, including a worked example[ABLATION-CLAUSE].

Fill-ins, by task outcome:
- `[MUTANT-CLASSES]` (**BLOCKED on P0-4**): if syntactic mutants are restored, "four escalating mutant classes (operator swaps, statement deletion, LLM-authored semantic faults, and higher-order combinations)". Otherwise, "three mutant classes (statement deletion, LLM-authored semantic faults, and higher-order combinations)".
- `[ABLATION-CLAUSE]` (**BLOCKED on P0-6**): if the ablation is run, ", and an ablation of the retriever’s two components". Otherwise, delete the placeholder and add nothing. Per the author decision, no softened version.
- Bullet 3 is only true once the mutant sets and per-mutant records for all subjects are actually in the released artifact (`CLAIMS_AUDIT.md` item 7).

The retriever stays in §III as method. It describes how context is chosen and is no longer claimed as novel.

---

## E16 · §II-B, whole paragraph — `PROPOSED`

**Current:**

> Search-based generators such as EvoSuite [8] optimise coverage without natural-language understanding and often yield low-readability assertions. LLM-based generators instead exploit code semantics: MuTAP [5] prompts with surviving mutants; TestPilot [9] and related systems generate unit tests from signatures and docstrings; Meta’s deployment [6] uses mutation to guide LLM test generation at scale. These methods are closed-book with respect to the wider repository. Our study isolates what retrieved codebase context adds on top of a MuTAP-style baseline.

**Replace with:**

> Search-based generators such as EvoSuite [8] optimise coverage without natural-language understanding and often yield low-readability assertions. LLM-based generators instead exploit code semantics: MuTAP [5] augments its prompts with surviving mutants; TestPilot [9] and related systems generate unit tests from signatures and docstrings; at Meta, TestGen-LLM [6] extends existing tests under build, pass and coverage filters, and ACH [23] generates tests that kill concern-specific mutants. Retrieval-augmented test generation is more recent. Shin et al. [21] retrieve API documentation, GitHub issues and Stack Overflow posts for ML-library APIs and find that RAG does not improve test correctness, though it raises line coverage by 6.5% on average. Zhang et al. [22] retrieve existing tests of related methods in the same project to guide each phase of a new test. Our closed-book baseline follows MuTAP; our retrieval condition supplies the definitions a unit reads, and the study isolates what that context adds to mutant killing.

---

## E17 · §II-C, final sentence — `PROPOSED`

**Current:**

> We bring dependency-aware repo retrieval to mutation-killing test generation and quantify when it pays off.

**Replace with:**

> We measure when retrieving a unit’s dependencies pays off for mutation-killing test generation.

---

## E18 · Fig. 1 caption and content — `PROPOSED` (box 1 `BLOCKED` on P0-4)

**Current caption:**

> Fig. 1.  The CodeKong pipeline. Shaded stages are contributions of this work.

**Replace with:**

> Fig. 1.  The CodeKong pipeline.

The figure itself must be regenerated (it is an embedded PNG with no source in the repo):
- Remove the shading, which marks "Mutant Generation" and "Dependency-aware Retrieval" as contributions.
- Box 1: replace "4 classes: operator swap, statement deletion, LLM-semantic, higher-order" with the P0-4 outcome (see E15 `[MUTANT-CLASSES]`).
- Box 4: "closed-book vs. RAG (k=3,5,8)" should read "closed-book vs. RAG (k=5; k=3,5,8 for RQ3)". Add FULL_CONTEXT here if P0-3 lands.
