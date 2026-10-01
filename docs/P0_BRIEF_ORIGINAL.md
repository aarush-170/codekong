# CodeKong — Paper Repair Task Brief

**Paste this whole file to Claude Code in the `codekong` repo, or save it as `TASKS.md` and say: "Read TASKS.md and start with Phase 0."**

---

You are working on **CodeKong**, a research pipeline that tests whether codebase-grounded RAG helps an LLM write tests that kill surviving mutants. There is a completed paper draft targeting **AST 2027 (deadline 30 October 2026)**. Your job is to fix five defects that would cause reviewer rejection, in priority order.

Read `PROJECT_EXPLAINED.md`, `HANDOFF.md`, and `AGENTS.md` first. They describe the architecture and the invariants.

---

## HARD INVARIANTS — never violate these

1. **The kill criterion is two-sided and non-negotiable.** A generated test counts as a kill only if it PASSES on the original code AND FAILS on the mutated code. Never weaken, shortcut, or approximate this.
2. **Only `module3_llm/ollama_client.py` talks to a model.** Do not add model calls anywhere else.
3. **Exactly one retry** in the agentic loop. This is a research invariant, not a tuning knob.
4. **Test generation runs at temperature 0.0**; semantic mutant generation at 0.7. Do not change these.
5. **Never invent, estimate, extrapolate, or "reasonably infer" a number.** Every figure that lands in the paper must trace to a row in `module4_eval/results/`. If a number is unavailable, say so and stop — do not fill the gap.
6. **Never overwrite `module1_mutation/surviving_mutants.json`** with single-file-generator output.
7. Mutation phases require WSL2/Linux/macOS and must not run from `/mnt/c/...`. Respect `core/guards.py`; do not disable it.

---

## PHASE 0 — Audit before you change anything (do this first, report back, then stop)

Do not start fixing until you have reported this. I need to know the true state, not the state the docs claim.

1. `git log --oneline -30` and `git status`. What has changed recently, and is the worktree clean?
2. Inventory `module4_eval/results/`. For each subject, report: which files exist, how many mutants, which conditions, which `k` values, and the date.
3. Does `module4_eval/figures/` contain real figures or only `.gitkeep`?
4. Run `python tests/smoke_all.py`. Report pass/fail per check.
5. Does any record anywhere have `mutation_class == "syntactic"`? Search `records_*.json` and `raw_*.csv`. Answer yes or no with evidence.
6. What version of mutmut is installed, and what exactly breaks when it runs? Reproduce the failure and paste the actual error.
7. Read `paper/` — what format is the current draft in, and does it match the numbers in `module4_eval/results/`?

**Output a short table: what exists, what is missing, what is stale. Then wait for my go-ahead.**

---

## P0-1 — Equal attempt budgets (do this first; it is pure re-analysis, no new runs)

**Problem:** closed-book was run once per mutant (24 attempts on ctxlib). RAG was run at k ∈ {3,5,8} (72 attempts). The headline table compares 12.5% vs 77.8% across non-comparable denominators. A reviewer will say RAG got three shots and closed-book got one.

**Do:**
- Write `module4_eval/headline_analysis.py` that computes the primary RAG-vs-closed-book comparison **at fixed k=5 only**, giving 24 attempts vs 24 attempts per subject.
- Emit a new table (CSV + markdown) with per-subject and per-mutation-class breakdowns at k=5.
- Keep the k-sweep, but confine it to the RQ3 analysis where it belongs.
- Fix the `n` column inconsistency: currently the class table shows mutant counts (13/7/4) while the percentages use attempt counts (39/21/12). Make every table state its denominator explicitly in the header.

**Acceptance:** a single command regenerates the headline table; every cell's numerator and denominator are printed alongside the percentage; the k=5 table and the k-sweep table are separate artifacts.

---

## P0-2 — Statistical testing

**Problem:** the paper reports descriptive statistics only. With paired binary outcomes on the same mutants under two conditions, a standard test applies directly.

**Do:**
- Add `module4_eval/stats.py` implementing **McNemar's exact test** on the paired per-mutant kill outcomes (closed-book vs RAG at k=5), per subject and combined.
- Report the 2×2 discordant table (b and c cells), the exact p-value, the risk difference, and a confidence interval on the difference in proportions.
- Use `scipy.stats` for the exact binomial; do not hand-roll it.
- Handle the zero-discordant-pair case gracefully (it will occur on `sorts` and `schedule`).
- Write results to `module4_eval/results/stats_<subject>.json`.

**Acceptance:** running it prints, for ctxlib, the discordant counts and an exact p-value; `sorts` and `schedule` produce a defined, non-crashing result.

---

## P0-3 — FULL-CONTEXT control arm

**Problem:** ctxlib is five files. The whole repo fits in context. A reviewer will ask why retrieve at all instead of pasting the repo. We currently cannot answer.

**Do:**
- Add a third condition, `FULL_CONTEXT`, alongside `NO_RAG` and `RAG`. It supplies the entire subject repository source (excluding test files and the mutant itself) in place of retrieved chunks.
- Route it through the same prompt templates, same one-retry loop, same validator, same temperature. **Only the context source differs.**
- Log token counts for it exactly as for the other arms — cost is a headline result here.
- Add `--conditions FULL_CONTEXT` support to `run_pipeline.py`.
- Run on ctxlib and report the three-arm comparison.

**Acceptance:** `python run_pipeline.py --repo ctxlib --phase generate --conditions FULL_CONTEXT` completes; results appear in `raw_ctxlib.csv` with condition `FULL_CONTEXT`; the headline analysis handles three arms.

**Interpretation is mine, not yours.** Report the numbers whichever way they fall. If FULL_CONTEXT beats RAG, say so plainly — do not soften it, and do not tune the retriever afterwards to win.

---

## P0-4 — The four-classes problem

**Problem:** the paper's method section describes four mutant classes including syntactic (mutmut), but **no syntactic mutant appears in any result**. All runs used `--skip-mutmut`. This is the most serious issue in the paper — it claims something we did not measure.

**Do, in this order, and stop at the first one that works:**
1. Fix the mutmut 3.6 output parser in `module1_mutation/mutant_normalizer.py`. Report the exact format change.
2. If that fails within a reasonable effort, evaluate `cosmic-ray` as a drop-in replacement for the syntactic class.
3. If neither works, do **not** paper over it. Produce a short written statement of exactly which class is absent and why, suitable for pasting into the paper's Threats section, and flag every place in `paper/` that claims four classes so they can be corrected to three.

**Acceptance:** either syntactic mutants appear in `surviving_mutants.json` and flow through to results, or there is a written exclusion note plus a list of every claim in the paper that must change.

**Timebox this.** Do not let tooling block the other tasks — it is parallelisable with P0-1 and P0-2.

---

## P0-5 — Related work gaps

**Problem:** the draft omits the closest prior art, including one paper that reached the opposite conclusion.

**Do:** produce `paper/related_work_additions.md` with correct BibTeX and a 2–3 sentence positioning note for each of:

- **Shin et al., "Retrieval-Augmented Test Generation: How Far Are We?"** — arXiv 2409.12682, accepted ICSE 2026. Found RAG did *not* improve correctness (+6.5% line coverage only). **They retrieve from external sources (API docs, GitHub issues, Stack Overflow) for ML library APIs; we retrieve from the project's own codebase with explicit dependency resolution.** The positioning line is: what you retrieve matters more than whether you retrieve.
- **Zhang et al., APT — "LLM-based Unit Test Generation via Property Retrieval"** — arXiv 2410.13542.
- **"Reference-Based Retrieval-Augmented Unit Test Generation"** — TOSEM, DOI 10.1145/3765758.
- **Wang, Harman, Papadakis, Zhang et al., SMART** — FSE 2026. Retrieval for *mutant* generation over bug-fix pairs. Our contrast: they retrieve to make better mutants, we retrieve to make better tests.
- **Foster et al., "Mutation-Guided LLM-based Test Generation at Meta" (ACH)** — arXiv 2501.12862, FSE 2025 Industry. Note: the current reference [6] is the 2024 TestGen-LLM paper, which is a *different* system. Both should be cited.

Also fix: reference [11] LLMorpheus lists "B. Tip" — the author is **F. Tip** (arXiv 2404.09952, with J. Bell and M. Schäfer). Reference [12] "Wang et al., 2025" has no venue or identifier; it appears to be SMART.

**Verify every citation against the actual arXiv/DOI page before writing it.** Do not reproduce a citation from this brief without checking it.

---

## P1 — Only if P0 is fully closed

- **Real subjects.** Find 2–3 real PyPI packages with genuine cross-module constants/config, existing but incomplete test suites, and permissive licences. Pre-screen for baseline mutation score before committing — a mature suite with no survivors is useless to us. Propose candidates with evidence before running anything.
- **Capability arm.** Wire a second model behind the existing config-driven provider. Do not hardcode. Run all three arms symmetrically — same mutants, same prompts, same k. A partial arm is worthless.
- **Figures.** `module4_eval/figures/` is empty. Regenerate all figures from final data only, at the very end.

---

## Rules of engagement

- **Work one task at a time.** Report results and wait before moving on. Do not batch five fixes into one commit.
- **Branch per task.** Do not commit to `main`.
- **Run `python tests/smoke_all.py` before every commit.** It must stay green.
- **Never edit files in `module1_mutation/_scratch/`** — they are generated working copies.
- **If a result contradicts the paper's current claim, say so immediately and prominently.** Do not adjust the method until the numbers look better. Three of these tasks can legitimately overturn our headline finding; that is the point of running them.
- **If you are blocked or uncertain, stop and ask.** Do not guess at research design decisions.
- When you finish a task, state plainly: what you changed, what the numbers are now, what is still broken, and what you could not verify.
