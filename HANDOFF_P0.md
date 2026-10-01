# HANDOFF_P0 — paper-repair work in progress (authoritative, 2026-10-01)

**If you are a new session picking this up, read this file first, all of it.**
It supersedes `HANDOFF.md` and the "Current state" sections of `CLAUDE.md` /
`AGENTS.md`, which are stale. Nothing here depends on any earlier chat: every
decision, result and open question is written down below or in the files it
points to.

---

## 1. What is going on (60 seconds)

CodeKong is a research pipeline testing whether codebase-grounded RAG helps an
LLM write tests that kill surviving mutants (see `PROJECT_EXPLAINED.md`,
`AGENTS.md`). There is a paper draft, `paper/CodeKong_RAG_Mutation_Testing.docx`,
targeting **AST 2027, deadline 30 October 2026**.

The authors issued a repair brief (`docs/P0_BRIEF_ORIGINAL.md`) listing defects
that would get the paper rejected. Work has been proceeding task by task. Since
the brief, the authors made decisions that **override parts of it** — see §4.
Where this file and the brief disagree, this file wins.

## 2. Reading order

1. This file.
2. `docs/P0_BRIEF_ORIGINAL.md` — the original brief (task list, hard invariants, rules of engagement).
3. `paper/CLAIMS_AUDIT.md` — every claim in the paper marked BACKED / UNBACKED / UNVERIFIABLE. The most important document for understanding the paper's real state.
4. `paper/EDITS_PENDING.md` — the single accumulating list of edits to the `.docx` (E1–E18), with exact current and replacement wording and a status for each.
5. `RUNBOOK_WSL_SESSION.md` — the runbook for the experiment session on the WSL machine.
6. `paper/related_work_additions.md` — verified citations and positioning notes.
7. `AGENTS.md` / `CLAUDE.md` — architecture, invariants and hazards (still accurate apart from their "Current state" sections).

## 3. Non-negotiable rules (from the brief + author instructions since)

**Research invariants**
1. A kill = test PASSES on original AND FAILS on mutant. Never weaken.
2. Only `module3_llm/ollama_client.py` talks to a model.
3. Exactly ONE retry in the agentic loop.
4. Test generation at temperature 0.0; semantic-mutant generation at 0.7.
5. **Never invent, estimate or extrapolate a number.** Every figure in the paper must trace to a row in `module4_eval/results/`. If unavailable, say so and stop.
6. Never overwrite `module1_mutation/surviving_mutants.json` with single-file-generator output.
7. Mutation phases need WSL2/Linux/macOS, never from `/mnt/c/...`; do not disable `core/guards.py`.

**Working rules**
- One task at a time. Report results and **wait for the author's go-ahead** before moving on. Report numbers (with numerators/denominators) **before** committing them.
- **Branch per task.** Never commit to `main`.
- `python tests/smoke_all.py` must be green before every commit. It is now **14/14** (docs saying 9/9 are stale). Add smoke checks for anything new.
- Never edit `module1_mutation/_scratch/`.
- **Never edit the `.docx`.** All paper changes go into `paper/EDITS_PENDING.md` as one accumulating file, each entry with the exact current wording and the exact replacement, status `READY` / `PROPOSED` / `BLOCKED` / `DECISION` / `SUPERSEDED`. Verify every quoted "current" passage is verbatim in the paper (see §9 for how).
- If a result contradicts the paper, say so immediately and prominently. Do not tune methods afterwards to make numbers look better. **Interpretation is the authors', not yours.**
- If blocked or uncertain about a research-design decision, stop and ask.
- Verify every citation against arXiv / Crossref / DOI before writing it. Do not trust the brief's citation details (several were wrong — §6).
- Do not push, merge, or publish anything without explicit permission.
- The Anthropic/OpenAI SDKs are banned from this codebase by design.

## 4. Author decisions made after the brief (dated, binding)

**2026-09-29**
- **Environment split.** Analysis/writing (P0-1, P0-2, P0-5, audit) on the Windows box. **P0-3, P0-4, P0-6 run only on the ORIGINAL WSL machine** that produced the July results — same model blob, config, index. Do NOT install Ollama elsewhere for these. Before running: record `ollama list` digest, `ollama --version`, resolved config; if the model does not match, STOP. Confirm repo not under `/mnt/c`.
- **P0-6 (retriever ablation) created** and is **critical path, equal priority with P0-3**. §V-F of the paper reports an ablation that was never run. Preference: re-run it (variants: (a) constants-indexing disabled, (b) dependency-fetch disabled; same ctxlib mutants, same prompts). **If it cannot be run before the deadline, §V-F AND every dependent claim come out entirely — no softened wording, not reworded as a hypothesis.**
- **Statistics:** per-subject McNemar exact is PRIMARY. Combined test is SECONDARY, stratified by subject, labelled "for completeness; per-subject results are the finding". Holm-Bonferroni across pairwise comparisons per subject.
- **Citations:** the verified versions in `paper/related_work_additions.md` override the brief. APT (arXiv 2410.13542) and the TOSEM "Reference-Based" paper (RefTest) are the same study — cite once, as TOSEM.
- **E12 reframe accepted:** the dependency-aware retriever is **dropped as a contribution** (engineering, not novelty — RefTest treats referenced-variable context as prior practice). New contribution = the controlled, per-subject measurement of WHEN retrieval helps mutation-killing generation under the two-sided kill criterion.
- **E11 escalated:** §I's premise "existing methods are closed-book" is false. Rewrite every such sentence (do not soften). Frame: prior retrieval supplies external docs (Shin) or neighbouring tests (RefTest); we retrieve definitions and measure when that helps.
- **ACH (Harman et al., FSE'25 Companion):** whether it retrieves repo context is **UNVERIFIED**. Never assert it does; write claims so they do not depend on it.
- **Fabrication sweep** ordered (done → `paper/CLAIMS_AUDIT.md`).
- **WSL runbook** ordered (done → `RUNBOOK_WSL_SESSION.md`).

## 5. Task status

| Task | Status | Where |
|---|---|---|
| Phase 0 audit | Done, reported | (summarised in §6) |
| P0-1 equal budgets (headline at RAG k=5) | **Done**, committed `a72c3cf` | `module4_eval/headline_analysis.py`, `results/headline_k5.*`, `results/ksweep_rag.*` |
| P0-2 McNemar + Holm + stratified combined | **Done**, committed `7bbb25b` | `module4_eval/stats.py`, `results/stats_*.json` |
| P0-5 related work | **Done**, committed `1e9a51e` | `paper/related_work_additions.md`, EDITS E9–E10 |
| Claims audit (fabrication sweep) | **Done**, committed `cdce066` | `paper/CLAIMS_AUDIT.md` |
| E11/E12 intro reframe | **Drafted, awaiting author approval** (`PROPOSED`) `757fa03` | EDITS E13–E18 |
| WSL runbook | **Done** `c7223be`; **cannot be executed yet** (needs code, next row) | `RUNBOOK_WSL_SESSION.md` |
| **Code prerequisites for P0-3/P0-6** | **Done** on branch `p0-3-code-prereqs` (on top of `handoff-p0`); FULL_CONTEXT = whole non-test repo minus only the function under test (author decision 2026-10-01); smoke 15/15 | §7, `module2_rag/full_context.py`, `module4_eval/ablation.py` |
| P0-3 FULL_CONTEXT arm (run) | Pending — WSL session | runbook Step 6 |
| P0-6 retriever ablation (run) | Pending — WSL session | runbook Step 7 |
| P0-4 syntactic class / mutmut | Pending — evidence capture in WSL session, parser fix after | runbook Step 8 |
| RQ4 cost at k=5 | **BLOCKED** — needs July `llm_calls.jsonl` from WSL | EDITS E7, runbook Step 1a |
| P1 (real subjects, 2nd model, figures) | Only after all P0 closed | brief |

## 6. What we know (facts established so far — do not re-derive)

**Environment (Windows box `C:\Users\user\CodeKong`)**: Python 3.13 (anaconda), pandas, scipy 1.16. **No WSL, no Docker, no Ollama, no mutmut.** So nothing that calls a model or mutmut can run here. `module2_rag/chroma_db` and `surviving_mutants.json` are not present here (gitignored). The original WSL machine's paths appear in records as `/home/adarsh_rajesh/codekong/`.

**Results that exist** (`module4_eval/results/`, all from 2026-07-13, commit `a4637ff`): ctxlib (24 mutants: 13 sdl / 7 semantic / 4 higher_order), sorts_focused (9: 3 sdl / 6 semantic), schedule (6: 5 sdl / 1 higher_order; **no `records_schedule.json`**). Each: NO_RAG once, RAG at k=3,5,8. **No syntactic mutants anywhere.** `module4_eval/figures/` is empty.

**Headline at equal budget (RAG k=5)** — from `results/headline_k5.csv`, `results/stats_*.json`:

| Subject | Closed-book | RAG k=5 | McNemar exact (b / c) | Risk diff [95% CI, Newcombe m10] |
|---|---|---|---|---|
| ctxlib | 3/24 (12.5%) | 19/24 (79.2%) | p = 3.05e-5 (0 / 16) | +0.667 [+0.402, +0.806] |
| sorts_focused | 2/9 | 2/9 | p = 1, no discordant pairs | 0.000 [−0.247, +0.247] |
| schedule | 0/6 | 0/6 | p = 1, no discordant pairs | 0.000 [−0.390, +0.390] |
| combined (secondary, stratified) | 5/39 | 21/39 | p = 3.05e-5 (all 16 discordant from ctxlib) | MH RD +0.410 |

ctxlib by class at k=5: sdl 2/13 → 11/13; semantic 1/7 → 4/7; higher_order 0/4 → 4/4. Valid tests ctxlib 6/24 → 21/24. The paper's pooled numbers (77.8%, 53.0%) are being replaced by these (E2–E6). The stratified combined test is mathematically identical to the pooled exact McNemar for matched pairs — this was disclosed to the authors and is documented in `stats.py`.

**Paper defects found** (full list with evidence: `paper/CLAIMS_AUDIT.md` summary table):
1. Four mutant classes claimed; syntactic never measured (all runs `--skip-mutmut`).
2. §V-F ablation reported as a result; never run.
3. Ref [12] fabricated (real paper is SMART, "Boosting LLMs for Mutation Generation", PACMSE FSE 2026, B. Wang et al.).
4. Ref [6] (TestGen-LLM) misattributed as mutation-guided; that is ACH (not cited).
5. Table I "surviving-mutant counts" are actually a seeded `--limit` sample; schedule had ≥16 distinct survivors vs N=6; sampling undisclosed.
6. 23 mutants have committed generated tests but no result rows (incl. 5 sorts mutants with both arms complete, IDs outside `sorts_focused`); outcomes unrecorded; the curation of `sorts_focused` is undisclosed.
7. Reproducibility statement overclaims (mutant sets, `records_schedule.json`, `sorts_focused` subject, pinned schedule commit — none in repo).
8. Refs [15]–[20] never cited in the text.
Plus: stale ChromaDB index (current indexer → 47 ctxlib chunks, paper says 49; 9 RAG records used stale chunks); "k=8 dips" is one test; §V-F's showcase mutant `member_price` was never killed by RAG; Fig. 2 has no generating script; RQ4 cost pooled over k.

**Citation corrections** (verified; details in `paper/related_work_additions.md`): ACH published author order is **Harman first**, not Foster; LLMorpheus is now IEEE TSE 51(6) 2025, author **F. Tip**; Shin et al. ICSE 2026 pp. 767–779, DOI 10.1145/3744916.3773163.

**Code facts that matter for the next step**
- `run_pipeline.phase_generate` → `metrics_logger.log_metrics(cfg, results, tag=args.repo)` **overwrites** `raw_<repo>.csv`, `summary_<repo>.csv`, `records_<repo>.json`. Any new ctxlib run today would destroy the committed ctxlib results.
- Checkpoint file is `results/_checkpoint_<repo>.jsonl`; rerunning the same command resumes; cleared after a run completes.
- `--limit N` = `random.Random(42).sample(mutants, N)` over `surviving_mutants.json`.
- `surviving_mutants.json` is a single shared file overwritten by every `--phase mutate` — the ctxlib set may no longer exist on the WSL machine.
- Mutant IDs are content hashes: `core/schema.make_mutant_id` = `f"{class}_{function}_{sha1(file|function|mutated_code)[:10]}"` — lets you verify mutant identity.
- `module2_rag/rag_indexer.build_index` uses `upsert` and never deletes → stale chunks persist. **Never rebuild the WSL index** before P0-3/P0-6.
- Call-log `purpose` = `testgen:{condition}:{class}:{mutant_id}` — **no k, no variant**. `metrics_logger.cost_from_call_log` regex only matches `RAG|NO_RAG`.
- `compare_conditions.load_all_results` globs `raw_*.csv` and `drop_duplicates(subset=[mutant_id, condition, k, subject])` → any extra tagged `raw_ctxlib_*.csv` with the same subject/condition would be **silently merged/deduplicated** into the headline. Analysis must select files explicitly.
- Generated RAG test files are named without k (`<id>_RAG_a1.py`), so each k overwrites the previous one on disk.

## 7. DONE (2026-10-01, branch `p0-3-code-prereqs`): code prerequisites. Original spec kept below.

Not started; **ask the author for go-ahead first** (they were asked; no answer yet). Branch: create from `handoff-p0` (the tip). Everything must be smoke-testable offline with fakes (see existing `test_agentic_retry_loop` / `test_ollama_client_rest` patterns in `tests/smoke_all.py`).

Interface the runbook depends on (`RUNBOOK_WSL_SESSION.md` §0 — keep these names exactly):
1. `--results-tag TAG` → outputs `raw_TAG.csv`, `summary_TAG.csv`, `records_TAG.json`, checkpoint `_checkpoint_TAG.jsonl`. **Refuse to start if `raw_TAG.csv` exists.** Default (no tag) behaviour for back-compat is the author's call — safest is to make the tag required whenever `--phase generate` runs.
2. `--mutant-ids-from CSV` → run exactly the `mutant_id`s in that CSV; exit non-zero if any are missing from `surviving_mutants.json`; mutually exclusive with `--limit`.
3. `--conditions FULL_CONTEXT` → third arm. Per brief: entire subject repository source (excluding test files and the mutant itself) in place of retrieved chunks; same templates, same one-retry loop, same validator, same temperature; only the context source differs. Log tokens like other arms. **Open question for the author:** does "excluding the mutant itself" mean excluding the function under test (already in the prompt) or the whole file? Ask before implementing.
4. `--retriever-variant {full,no_constants,no_depfetch}` (RAG only). Recommended implementation (author has not objected): **retrieval-time switches on the existing index**, not a re-index — `no_constants` filters out `metadata.kind == "constants"` chunks from both the similarity results and the dependency fetch; `no_depfetch` skips `Retriever._fetch_definitions`. Keeps every other chunk (including stale ones) identical to July.
5. Put the results tag into the call-log `purpose` so per-arm token cost is attributable; extend `cost_from_call_log` accordingly.
6. Analysis: extend `headline_analysis.py` / `stats.py` to take explicit file lists (do not rely on the `raw_*.csv` glob once tagged files exist). Ablation arms must NOT enter the headline table; they get their own table. Synthetic three-arm path already tested (`test_three_arm_pipeline`).
7. Update `RUNBOOK_WSL_SESSION.md` §0 with the branch name, then the branch must be **pushed** for the WSL machine to fetch it — **ask permission before pushing**.

## 8. Open questions awaiting the authors

1. Go-ahead to implement §7, and permission to push when green.
2. Approve / amend E13–E18 (intro reframe) in `paper/EDITS_PENDING.md`.
3. E8 items 4 and 7 (§III-C mechanism sentences; §VI practitioner advice) are `DECISION`.
4. Keep or drop the runbook's same-day drift re-run (Step 5, ~25 min) — recommended keep.
5. `module4_eval/results/rq_answers.json` and `compare_conditions.py` still report pooled-over-k numbers. Point them at the k=5 headline, or just stop citing them?
6. How to disclose findings 5–6 (undisclosed sampling, unreported runs) — the authors' call; nothing drafted yet.
7. ~~FULL_CONTEXT definition ambiguity~~ — resolved 2026-10-01: exclude only the function under test.

## 9. Git state and how to resume

- Repo: `https://github.com/aarush-170/codekong`. **Nothing from this work has been pushed.** Local `main` = `origin/main` = `fe6d4ae`.
- Branches are **stacked linearly** (each built on the previous):
  `main` → `p0-1-equal-budgets` (a72c3cf) → `p0-2-mcnemar` (7bbb25b) → `p0-5-related-work` (1e9a51e) → `p0-7-claims-audit` (cdce066) → `p0-5b-intro-reframe` (757fa03) → `wsl-runbook` (c7223be) → `handoff-p0` (this file).
- **Resume with:** `git checkout handoff-p0` — it contains everything.
- If you are on a different machine, these branches exist only in this folder; copy the whole folder (including `.git`) or get permission to push.
- If you open this folder from a different Windows user account and git refuses with "detected dubious ownership", run once: `git config --global --add safe.directory C:/Users/user/CodeKong`.

Useful commands:
```bash
python tests/smoke_all.py                      # must end "14/14 passed"
python -m module4_eval.headline_analysis       # regenerates headline_k5.* and ksweep_rag.*
python -m module4_eval.stats                   # regenerates stats_*.json
```

Verifying quoted paper text (do this for every new EDITS_PENDING entry): `python tools/verify_paper_quotes.py` checks every `**…Current…**` quote block in `paper/EDITS_PENDING.md` is verbatim in the `.docx` (currently 15 blocks, 0 missing). `python tools/verify_paper_quotes.py --dump` prints the paper's full text — use it instead of opening the `.docx`. The draft uses curly apostrophes (’) and em dashes (—); match them exactly.

Web lookups that worked: arXiv API `https://export.arxiv.org/api/query?id_list=...` (use https, `curl -L`), Crossref `https://api.crossref.org/works/<doi>` and `?query.bibliographic=`, ACL Anthology `.bib` URLs. ACM DL pages return 403; DBLP was unreachable; Semantic Scholar rate-limits.

## 10. File map of everything added by this work

| File | Purpose |
|---|---|
| `HANDOFF_P0.md` | This file |
| `docs/P0_BRIEF_ORIGINAL.md` | The authors' original repair brief (overridden where §4 says) |
| `module4_eval/headline_analysis.py` | Equal-budget (k=5) headline + separate k-sweep tables, explicit denominators |
| `module4_eval/stats.py` | McNemar exact per subject (primary), Holm, Newcombe method-10 CI, stratified combined (secondary) |
| `module4_eval/results/headline_k5.{csv,md}`, `ksweep_rag.{csv,md}`, `stats_*.json` | Generated outputs (regenerate with the commands above) |
| `tests/smoke_all.py` | +3 checks: `test_headline_equal_budget`, `test_paired_stats` (incl. Newcombe 1998 Table III reference values), `test_three_arm_pipeline` |
| `requirements.txt` | + `scipy>=1.11` |
| `paper/EDITS_PENDING.md` | All pending `.docx` edits E1–E18 |
| `paper/related_work_additions.md` | Verified BibTeX/IEEE strings + positioning |
| `paper/CLAIMS_AUDIT.md` | Claim-by-claim audit of the draft |
| `RUNBOOK_WSL_SESSION.md` | WSL experiment session runbook |
| `tools/verify_paper_quotes.py` | Checks EDITS_PENDING quotes are verbatim in the .docx; `--dump` prints paper text |
