# Claims audit — `CodeKong_RAG_Mutation_Testing.docx`

Audited 2026-09-29 against commit `1e9a51e` (branch `p0-7-claims-audit`).
Every empirical claim, cited number, figure and reference in the draft is
listed with one verdict:

- **BACKED**: traced to a named file and row, recomputed where possible.
- **UNBACKED**: no recorded evidence exists, or the evidence contradicts it.
- **UNVERIFIABLE**: the evidence would live somewhere this repo does not contain
  (for example the WSL machine, an uncommitted subject, or a full text not read).

`BACKED*` means the number traces, but only under a convention the paper
contradicts elsewhere, usually RAG pooled over k ∈ {3,5,8}. Those rows are
already fixed by `EDITS_PENDING.md` E2–E6.

Paths are relative to the repo root. `R/` = `module4_eval/results/`.

---

## Summary: problems found (the first three were already known)

| # | Problem | Kind | Where |
|---|---|---|---|
| 1 | Four mutant classes claimed; the syntactic (mutmut) class was never run | UNBACKED claim | Abstract, §I, §III-A, Fig. 1 |
| 2 | §V-F retriever ablation reported as a result; no experiment recorded | UNBACKED result | Abstract, §I, §V-F, §VIII |
| 3 | Ref. [12] title and description match no real paper | fabricated reference | §II-C, [12] |
| **4** | **Ref. [6] (TestGen-LLM) is cited as mutation-guided test generation at scale. Its abstract describes coverage-improving test extension with build/pass/coverage filters and no mutation. The mutation-guided Meta system is ACH, which is not cited.** | **misattributed citation** | **§I, §II-B** |
| **5** | **Table I calls N "surviving-mutant counts". The pipeline evaluated a seeded random sample (`--limit`, `random.Random(42)`), and at least 16 distinct schedule survivors received generated tests against N = 6. The survivor totals are unknown, since `surviving_mutants.json` is not in the repo. The sampling is not disclosed.** | **UNBACKED / undisclosed sampling** | **Table I, §III-B, §IV-A, §VII-D** |
| **6** | **Unreported runs exist. `module3_llm/generated_tests/` (committed in `a4637ff` with the results) holds tests for 23 mutants that appear in no results file, including 5 sorting mutants with both arms completed on IDs outside `sorts_focused`. Their outcomes are not recorded anywhere. The paper also does not say that "sorts" is a curated 10-file subset, or how the subset was chosen.** | **undisclosed runs / selection** | **§IV-A, §V** |
| **7** | **The reproducibility statement claims the mutant sets are released. They are not in the repo. Nor are `records_schedule.json`, the `sorts_focused` subject, or a pinned schedule commit (`config.yaml` `pin_commit: ""`). The experiment's index also held stale chunks from an older ctxlib (see §C1).** | **UNBACKED claim** | **§VIII Reproducibility** |
| 8 | Refs [15]–[20] are never cited in the text, including [15], the Qwen2.5-Coder report for the model actually used | bibliography defect | References |
| 9 | "We also report retry rate and first-attempt kill rate": neither appears anywhere in the paper | UNBACKED claim | §IV-C |
| 10 | Fig. 2 plots the pooled numbers and has no generating script in the repo | UNVERIFIABLE provenance | Fig. 2 |

Items 4–7 are the new findings. Item 4 is a citation stating something the
cited paper does not say, which is the same kind of defect as [12]. Items 5
and 6 are disclosure problems that a reviewer with the artifact would find.

---

## A. Abstract

| Claim | Verdict | Evidence |
|---|---|---|
| "generates four escalating mutant classes (operator swaps, …)" | **UNBACKED** | No `syntactic` row in any `R/raw_*.csv` or `R/records_*.json`; all runs used `--skip-mutmut` (HANDOFF.md). |
| "indexes the codebase—including module-level constants" | BACKED | `module2_rag/rag_indexer.py` `module_constant_chunks`; `rates.py::const:*` chunks in `R/records_ctxlib.json` `context_chunks`. |
| "retrieves the definitions of the symbols a unit references" | BACKED | `module2_rag/retriever.py` `referenced_symbols` / `_fetch_definitions`; distance-0.0 definition chunks rank first in the records. |
| "strict two-sided kill criterion" | BACKED | `agentic/test_gen_agent.py`; validation stages `original` then `mutant` in the records. |
| "three subjects of differing information dependence" | BACKED | `R/raw_{ctxlib,sorts_focused,schedule}.csv`. |
| "raises the kill rate from 12.5% to 77.8%" | BACKED* | `R/raw_ctxlib.csv`: NO_RAG 3/24; RAG pooled 56/72. Equal-budget value is 19/24 = 79.2% (`R/headline_k5.csv`, ctxlib/ALL/RAG). E6. |
| "valid-test rate from 25% to 88%" | BACKED* (inconsistent) | NO_RAG 6/24. The 88% is k = 5 (21/24 = 87.5%, `R/headline_k5.csv`), **not** the pooled 62/72 = 86.1% that §V's convention says RAG figures use. Consistent at k = 5 after E2. |
| "at a seven-fold lower token cost per kill" | BACKED* | `R/cost_ctxlib.csv`: 47,576/3 = 15,859 vs 125,758/56 = 2,246 (×7.06). RAG pooled over k; no k = 5 figure possible from committed data. E7 BLOCKED. |
| "on self-contained algorithmic code it yields no benefit (a 22.2% tie)" | BACKED | `R/raw_sorts_focused.csv`: 2/9 both arms (and 6/27 pooled). |
| "a small local model floors on complex stateful code" | BACKED | `R/raw_schedule.csv`: 0 kills, 0 valid tests in all 24 rows. |
| "An ablation shows both … are necessary" | **UNBACKED** | No ablation data in `R/`. E8. |

## B. §I Introduction

| Claim | Verdict | Evidence |
|---|---|---|
| Mutation analysis is a validated proxy for real faults [4] | BACKED (literature) | [4] verified (Crossref 10.1145/2635868.2635929). |
| MuTAP "prompts an LLM with the surviving mutant and the original function and requests a killing test" [5] | UNVERIFIABLE | [5] exists (Crossref 10.1016/j.infsof.2024.107468); prompt design not checked against full text. |
| "Industrial systems apply the idea at scale [6]" | **UNBACKED (misattribution)** | [6] is TestGen-LLM (Crossref 10.1145/3663529.3663839). Its abstract: LLM improvement of existing tests, filtered on build/pass/coverage; no mutants. The mutant-killing Meta system is ACH (10.1145/3696630.3728544). |
| "A shared assumption unites them: generation is closed-book" | **UNBACKED** | False for RefTest (TOSEM 10.1145/3765758), which retrieves in-project tests. E11/E12. |
| "dependency-aware RAG lifts the kill rate from 12.5% to 77.8%" | BACKED* | As Abstract. E6. |
| "on self-contained sorting code it changes nothing" | BACKED | `R/raw_sorts_focused.csv`. |
| "a 7B model floors on a stateful OO library regardless of retrieval" | BACKED | `R/raw_schedule.csv`. |
| Contribution 1: "unifying four escalating mutant classes" | **UNBACKED** | Three classes measured. |
| Contribution 2: retriever; "We show both are necessary" | **UNBACKED** | No ablation (E8); novelty contested by RefTest (E12). |
| Contribution 4: "A released context-dependent benchmark and the complete pipeline" | BACKED (partly) | `subjects/ctxlib/` and pipeline in repo. See item 7 for what is not released. |
| Contribution 5: "an ablation isolating the retriever's two components" | **UNBACKED** | E8. |

## C. §II Background and related work

| Claim | Verdict | Evidence |
|---|---|---|
| Mutation-testing history [1]–[3], higher-order mutants [2], real-fault link [4] | BACKED (literature) | [1] 10.1109/C-M.1978.218136; [2] 10.1109/TSE.2010.62; [3] 10.1016/bs.adcom.2018.03.015; [4] as above. |
| EvoSuite "optimise[s] coverage … low-readability assertions" [8] | UNVERIFIABLE | [8] exists (10.1145/2025113.2025179); characterisation not checked. |
| TestPilot generates tests "from signatures and docstrings" [9] | UNVERIFIABLE | [9] exists (10.1109/TSE.2023.3334955). |
| "Meta's deployment [6] uses mutation to guide LLM test generation at scale" | **UNBACKED (misattribution)** | See §I row on [6]. |
| "These methods are closed-book with respect to the wider repository" | **UNBACKED** | E11. |
| µBERT [10] and LLMorpheus [11] generate realistic faults | BACKED (literature) | [10] 10.1109/ICSTW55395.2022.00039; [11] 10.1109/TSE.2025.3562025 (author initial wrong in draft, E9). |
| "retrieval-boosted mutant generation [12] fetches historical bug-fix pairs" | **UNBACKED (fabricated ref)** | E9/E10. |
| "repository-level code assistants show that repo context improves code completion [13]" | BACKED (literature) | [13] 10.18653/v1/2023.emnlp-main.151. |

## D. §III Pipeline (method claims)

| Claim | Verdict | Evidence |
|---|---|---|
| "Provider and model are configuration, not code" | BACKED | `config.yaml` `llm.provider/model`; `module3_llm/ollama_client.py` sole model client. |
| "every model call is logged with token counts" | BACKED (code) / UNVERIFIABLE (data) | `ollama_client.py` appends to `llm.call_log`; the log `module3_llm/llm_calls.jsonl` is gitignored and not in the repo. |
| "generation temperature is fixed for determinism" | BACKED (config) | `config.yaml` `temperature_testgen: 0.0`, `temperature_semantic: 0.7`. |
| (i) "Operator/constant swaps are produced mechanically by mutmut" | **UNBACKED** | Never run (item 1). |
| (ii) SDL "removes one statement while preserving parseability" | BACKED | `module1_mutation/sdl_generator.py`; sdl rows in all raw CSVs. |
| (iii) semantic mutants by LLM at temperature 0.7 | BACKED (config/code) | `config.yaml`; semantic rows present. |
| (iv) higher-order "combine two first-order mutants of the same function" | BACKED | `module1_mutation/hom_combiner.py` (same-function pairs, cap `max_hom_per_function: 3`). |
| "Every mutant is ast.parse-validated and normalised to one schema" | BACKED (code) | `core/schema.py`; smoke `test_schema_roundtrip`. |
| Survival filter: scratch copy, apply in place, purge byte-code caches, run suite | BACKED (code) | `module1_mutation/mutation_runner.py`, `core/testexec.py` (`MutantApplier`, `-B`). |
| "Survivors define the generation task and provide the denominator for all kill rates" | **UNBACKED** | Denominator is a `--limit` sample of survivors (`run_pipeline.py` `random.Random(42).sample`), not all survivors (item 5). |
| Embeddings: all-MiniLM-L6-v2, ChromaDB [14] | BACKED | `config.yaml` `rag.embedding_model`, `rag.chroma_path`. |
| "we index every module-level constant as its own chunk" | BACKED | `rag_indexer.module_constant_chunks`. |
| Algorithm 1 steps 1–6 | BACKED | `retriever.retrieve`: definitions seeded at distance 0.0, then similarity hits, dedup, drop own function, sort, first k. Note: fewer than k chunks can be returned (e.g. 4 at k = 5 for `sdl_bulk_discount_00aa7bbf25`). |
| "embedding similarity … tends to surface sibling functions rather than a constants table" | UNBACKED (as a general claim) | Consistent with one case in the records (member_price: similarity hits are `member_price` docstring, `checkout_total`), but no measurement. E8 item 4. |
| Prompting: NO_RAG gets diff, original function, existing test; RAG adds top-k chunks; "all other factors held identical" | BACKED | `module3_llm/llm_rewriter.build_prompt`: same template, only `context_section` differs. |
| "exactly one retry … structured validator feedback" | BACKED | `config.yaml` `agentic.max_retries: 1`; `test_gen_agent.py` loop `range(1 + max_retries)`. |
| kill(t) ⇔ pass(t,O) ∧ ¬pass(t,M); per-test timeout | BACKED | `test_gen_agent.py`; `config.yaml` `test_timeout_seconds: 10`. |

## E. §IV Experimental design

| Claim | Verdict | Evidence |
|---|---|---|
| ctxlib: functions reference constants in a separate module; docstrings never state the values; values "non-standard and unguessable" | BACKED (by inspection) | `subjects/ctxlib/rates.py`, `billing.py`, `grading.py`, `shipping.py`. Docstrings name `rates.X` but give no values. |
| "sorts comprises classic sorting algorithms from TheAlgorithms/Python" | **UNBACKED as stated** | The subject is `sorts_focused`, a curated 10-file subset (HANDOFF.md). It is not in the repo (`subjects/*` gitignored), has `url: ""` in `config.yaml`, and its selection criteria are recorded nowhere. |
| schedule is dbader/schedule | BACKED | `config.yaml` `subjects.schedule.url`. No pinned commit (`pin_commit: ""`). |
| Table I, ctxlib: Files 5, Funcs 13 | BACKED | Recomputed with `rag_indexer.build_index` (embedding stubbed): 5 files, 13 functions. |
| Table I, ctxlib: Chunks 49 | **UNBACKED vs current code** | Current indexer yields **47** (13 function, 13 docstring, 12 constants, 9 test). The experiment's collection held ≥ 2 chunks the current code cannot produce (§C1 below), which likely explains 49. |
| Table I, sorts: Files 10, Funcs 12, Chunks 27; schedule: 2 / 16 / 189 | UNVERIFIABLE | Subjects not in repo; schedule commit not pinned. |
| Table I, Muts 24 / 9 / 6 "surviving-mutant counts" | **BACKED as evaluated counts; UNBACKED as survivor counts** | Row counts per arm in `R/raw_*.csv` are 24/9/6. Schedule had ≥ 16 distinct survivors with generated tests (item 5). |
| qwen2.5-coder:7b via Ollama, temperature 0; semantic at 0.7 | BACKED (config) / UNVERIFIABLE (weights) | `config.yaml`. The model digest was never recorded. |
| "The two conditions share model, prompts, mutants, and temperature; only retrieval differs" | BACKED | Same mutant IDs per arm (checked by `headline_frame`); prompt builder as §D. |
| §IV-C: kill rate counts attempts, "three times the number of mutants" for RAG | BACKED (describes the pooled convention) | Superseded by E3. |
| §IV-C "We also report retry rate and first-attempt kill rate" | **UNBACKED** | Not reported anywhere in the paper. The data exists in `R/summary_*.csv` `retry_rate`, `first_attempt_kill_rate`. |

## F. §V Results

| Claim | Verdict | Evidence |
|---|---|---|
| "All figures are computed from the raw per-mutant records" | UNVERIFIABLE for Fig. 2 | No script in the repo produces Fig. 2. `module4_eval/compare_conditions.make_figures` makes different plots with different titles. Values match pooled numbers (12, 78, 22, 22, 0, 0). |
| Table II all cells (24/12.5/77.8/+65.3; 9/22.2/22.2/0; 6/0/0/0; 39/12.8/53.0/+40.2) | BACKED* | `R/raw_*.csv` pooled over k: ctxlib 3/24 vs 56/72; sorts 2/9 vs 6/27; schedule 0/6 vs 0/18; combined 5/39 vs 62/117. k = 5 values in E4. |
| "reporting the tie and the floor is what makes the win credible" | (argument) | Holds only if the unreported runs (item 6) are disclosed. |
| Table III all cells (13/15.4/82.1; 7/14.3/61.9; 4/0/91.7) | BACKED* | `R/summary_ctxlib.csv` rows NO_RAG/RAG × class; RAG n = 39/21/12 attempts while the table's n shows 13/7/4 mutants. k = 5 values in E5. |
| "semantic mutants gain less than statement-deletion mutants" | BACKED | Holds pooled and at k = 5 (`R/headline_k5.csv`). |
| "… because semantic mutants sometimes require multi-value arithmetic the 7B model still botches even when handed the values" | **PARTLY BACKED** | Of the 3 RAG k = 5 semantic failures (`R/records_ctxlib.json`, final validation): `delivery_days` is an arithmetic slip (asserts express local = 2; true (1+1)//2 = 1). `member_price` asserts a 2% bronze discount although the retrieved `DISCOUNTS` gives 0.0, which is a misread, not arithmetic. `letter_grade` asserts 'B' where the band gives 'A', also a misread. |
| "Closed-book, only 25% of generated tests pass on the original program" | BACKED | `R/raw_ctxlib.csv` NO_RAG `valid_test`: 6/24. |
| "the model guesses the codebase's constants and guesses wrong" | BACKED (mostly) | Of 18 NO_RAG invalid tests (final validation in `R/records_ctxlib.json`), 15 fail on a wrong guess of a `rates.py` constant or threshold (e.g. `bulk_discount(10) == 0.1`, true 0.04; this includes guesses of `LATE_FEE_GRACE_DAYS` and `HONOR_GPA`). 2 invent a nonexistent key (`KeyError: 'zone1'`), and 1 references an unimported name (`NameError: PRIORITY_SURCHARGE`). |
| "With retrieval, 83–88% of tests are valid" (Table IV: 87.5 / 87.5 / 83.3) | BACKED | `R/ksweep_rag.csv` ctxlib/ALL: 21/24, 21/24, 20/24. |
| "Depth k = 3–5 is the sweet spot; k = 8 dips slightly, evidence that more context is not always better" | **UNBACKED inference** | The "dip" is one test (21 → 20 of 24). No test supports a depth effect. |
| Table V: 47,576 / 3 / 15,859; 125,758 / 56 / 2,246 | BACKED* | `R/cost_ctxlib.csv` (sum of prompt + eval tokens per condition); RAG pooled over k. E7. |
| Listing 1: closed-book asserts 0.1 → INVALID; RAG asserts 0.04 → KILLED | BACKED | `R/records_ctxlib.json` `sdl_bulk_discount_00aa7bbf25`: NO_RAG INVALID_TEST ("assert 0.04 == 0.1"); RAG KILLED at k = 3/5/8 with `rates.py::const:BULK_BREAKS` retrieved first. Test files `module3_llm/generated_tests/sdl_bulk_discount_00aa7bbf25_{NO_RAG,RAG}_a1.py`. Note the RAG test file is overwritten per k, so the file on disk is from the last k run. |
| "The same pattern recurs across ctxlib" | BACKED (mostly) | See the NO_RAG failure breakdown above. |
| §V-F: "With a naive … index and pure embedding similarity, the top results for the member_price mutant were the member_price docstring and … checkout_total; the DISCOUNTS constant … was absent" | **UNBACKED** | No naive-index run is recorded. |
| §V-F: "so the retrieved context was useless and RAG matched closed-book" | **UNBACKED** | No record. |
| §V-F: "After (a) … and (b) …, the DISCOUNTS chunk is retrieved first for that mutant" | BACKED, but misleading by omission | `R/records_ctxlib.json` `semantic_member_price_1c4835c3ed` RAG k = 3/5/8: `rates.py::const:DISCOUNTS` first. That mutant was **INVALID_TEST under RAG at every k** (asserts a 2% bronze discount against a retrieved 0.0). The example the paper uses to show retrieval working is a case where retrieval did not help. |
| "Removing either addition returns retrieval to the naive, ineffective behaviour—both are necessary" | **UNBACKED** | E8. |

## G. §VI–§VIII Discussion, threats, conclusion

| Claim | Verdict | Evidence |
|---|---|---|
| §VI: "on the stateful library, neither condition produced any valid test" | BACKED | `R/raw_schedule.csv` valid_test all False. |
| §VI practitioner advice to index constants and tables | UNBACKED (rests on the ablation) | E8 item 7. |
| §VII-A: equivalent mutants "do not bias the RAG-vs-closed-book delta" | **UNBACKED reasoning** | Equivalent mutants cannot be killed by either arm, so they *attenuate* the risk difference toward 0. They do not leave it unbiased. |
| §VII-B: "Temperature 0 makes generation deterministic and reproducible" | UNVERIFIABLE | No repeated run exists to check this. Ollama at temperature 0 is not guaranteed bit-identical across hardware or versions, and the model digest was not recorded. |
| §VII-B: byte-code caches purged | BACKED | `core/testexec.py`. |
| §VII-C: "we use a local 7B model", ctxlib synthetic | BACKED | `config.yaml`; `subjects/ctxlib`. |
| §VII-D: "39 survivors … report descriptive statistics … rather than inferential tests" | Superseded | E1; "survivors" is itself wrong (item 5). |
| §VIII: 12.5% → 77.8%; 25% → 88%; seven-fold; "an ablation shows …" | as Abstract | E6, E7, E8. |
| Reproducibility: "The pipeline, the ctxlib benchmark, the mutant sets, and the per-mutant records are released" | **UNBACKED (partly)** | Pipeline, ctxlib, `R/records_{ctxlib,sorts_focused}.json` present. **Missing:** `module1_mutation/surviving_mutants.json` (all subjects), `R/records_schedule.json`, the `sorts_focused` subject, and a pinned schedule commit. |
| Reproducibility: "every model call and token count is logged" | UNVERIFIABLE | Log not in repo (§D). |
| Reproducibility: "generation is deterministic at temperature 0" | UNVERIFIABLE | As §VII-B. |

### C1. Index provenance (supports Table I and reproducibility rows)

The experiment's ChromaDB collection contained chunks that the committed
indexer and committed ctxlib cannot produce:

- `test_ctxlib.py::test_member_price_bronze_no_discount::test`, retrieved in 7
  records. The committed test file has `test_member_price_bronze_identity`
  instead, so the test was renamed after indexing.
- `rates.py::module_constants:TAX_RATES,SHIPPING,…::constants`, retrieved in 5
  records. This is an older multi-constant chunk format.

`build_index` uses `upsert` and never deletes, so stale chunks persisted.
**9 RAG records** (1 at k = 5, 8 at k = 8) retrieved at least one stale chunk. A
fresh rebuild of the index would not reproduce their inputs. **Do not rebuild
the WSL index before P0-3/P0-6. Back it up.**

---

## H. References

Verified 2026-09-29 against Crossref, the arXiv API and the ACL Anthology.

| Ref | Verdict | Evidence / issue |
|---|---|---|
| [1] DeMillo, Lipton, Sayward 1978 | BACKED | 10.1109/C-M.1978.218136, Computer 11(4):34–41. |
| [2] Jia & Harman 2011 | BACKED | 10.1109/TSE.2010.62, TSE 37(5):649–678. |
| [3] Papadakis et al. 2019 | BACKED (title, venue, pages) | 10.1016/bs.adcom.2018.03.015, pp. 275–378. Crossref has no author list, so authors were not independently checked. |
| [4] Just et al. FSE 2014 | BACKED | 10.1145/2635868.2635929, pp. 654–665. |
| [5] Dakhel et al. IST 2024 (MuTAP) | BACKED | 10.1016/j.infsof.2024.107468, vol. 171. |
| [6] Alshahwan et al. 2024 (TestGen-LLM) | BACKED as a reference; **MISATTRIBUTED in text** | 10.1145/3663529.3663839, FSE Companion '24, pp. 185–196. Text credits it with mutation guidance (item 4). |
| [7] Lewis et al. NeurIPS 2020 | BACKED | arXiv 2005.11401 ("Accepted at NeurIPS 2020"). |
| [8] Fraser & Arcuri 2011 | BACKED | 10.1145/2025113.2025179, pp. 416–419. |
| [9] Schäfer et al. TSE 2024 | BACKED | 10.1109/TSE.2023.3334955, TSE 50(1):85–105. |
| [10] Degiovanni & Papadakis ICSTW 2022 | BACKED | 10.1109/ICSTW55395.2022.00039, pp. 160–169. |
| [11] LLMorpheus | **WRONG AUTHOR / OUTDATED** | "B. Tip" → F. Tip; now IEEE TSE 51(6) 2025. E9. |
| [12] "Y. Wang et al. 2025" | **FABRICATED** | E9/E10. |
| [13] Zhang et al. EMNLP 2023 (RepoCoder) | BACKED | 10.18653/v1/2023.emnlp-main.151. |
| [14] Reimers & Gurevych EMNLP 2019 | BACKED | ACL Anthology D19-1410, pp. 3982–3992 (Crossref shows 3980–3990; the Anthology is authoritative). |
| [15] Qwen2.5-Coder report | BACKED; **never cited** | arXiv 2409.12186. The model used should cite it (§IV-B). |
| [16] Chen et al. 2021 | BACKED; **never cited** | arXiv 2107.03374. |
| [17] Andrews et al. ICSE 2005 | BACKED; **never cited** | 10.1145/1062455.1062530. |
| [18] Ammann & Offutt 2nd ed. | BACKED; **never cited** | 10.1017/9781316771273 (2016). |
| [19] Kang et al. ICSE 2023 | BACKED; **never cited** | 10.1109/ICSE48619.2023.00194. |
| [20] Lemieux et al. ICSE 2023 (CodaMosa) | BACKED; **never cited** | 10.1109/ICSE48619.2023.00085. |

## I. Figures

| Figure | Verdict | Issue |
|---|---|---|
| Fig. 1 (pipeline) | **UNBACKED content** | Box 1 says "4 classes: operator swap, …". The caption says shaded stages are contributions, and "Dependency-aware Retrieval" is shaded (withdrawn by E12). Box 4 says "RAG (k=3,5,8)", which fits the sweep but not the equal-budget headline. |
| Fig. 2 (kill rate by subject) | BACKED* values; UNVERIFIABLE provenance | Plots pooled 12/78/22/22/0/0. No generating script in the repo. `module4_eval/figures/` is empty. Regenerate from `R/headline_k5.csv` with a committed script. |

---

## What this audit could not check

- Full texts of cited papers: only abstracts and metadata were read. Any
  characterisation of a cited paper's method beyond its abstract is marked
  UNVERIFIABLE.
- Anything on the WSL machine: the call log, `surviving_mutants.json`, the
  ChromaDB index, the model digest, and the outcomes of the 23 unreported runs.
  The WSL runbook's recovery steps capture these.
