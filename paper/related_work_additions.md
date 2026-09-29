# Related-work additions (P0-5)

Every entry below was checked on 2026-09-29 against a primary record: the
arXiv API (`export.arxiv.org`) for preprints, and Crossref (`api.crossref.org`)
for published versions. The source used is listed per entry. Positioning notes
rely only on each paper's abstract; nothing here was checked against a full
text unless stated.

## ⚠ Read first: findings that change the brief

1. **APT and the TOSEM "Reference-Based" paper are the same work.** arXiv
   2410.13542 (tool: APT) and TOSEM DOI 10.1145/3765758 (tool: RefTest) have
   the identical six-author list, the same Given/When/Then design, and the same
   evaluation (12 open-source projects, 1,515 methods). The TOSEM article is
   the archival version of the preprint, with the tool renamed. **Cite it once,
   as the TOSEM article.** Citing both as separate works would double-count one
   study.
2. **RefTest's abstract undercuts our retrieval novelty claim.** It describes
   existing LLM approaches as ones that "focus solely on the context within the
   code itself, such as referenced variables". In other words, it treats
   referenced-symbol context as established practice. Its own retrieval is also
   *in-project*: it retrieves existing tests of related methods. So "we retrieve
   from the project's own codebase" does not distinguish us from RefTest. Our
   defensible difference is narrower (see its entry below). The contribution
   bullets in §I should be checked against this before submission.
3. **ACH author order.** The brief says "Foster et al." That is the arXiv
   preprint's (alphabetical) order. The published FSE Companion '25 version
   lists **Mark Harman first** (Crossref and Semantic Scholar agree). Cite the
   published version as "Harman et al."
4. **SMART's title is not what reference [12] says.** The published title is
   *"Boosting LLMs for Mutation Generation"* (PACMSE, FSE 2026; arXiv
   2603.24560, first posted 2026-03-25). Its abstract describes RAG over "a
   vectorized dataset of real-world bugs". It does not say "bug-fix pairs",
   which is the wording [12] uses. No 2025 version was found. [12] should be
   replaced by the verified entry, not patched.
5. **LLMorpheus is now a journal paper.** It appeared in IEEE TSE 51(6), 2025.
   Cite that version instead of the arXiv preprint, and fix "B. Tip" → "F. Tip".
6. **"Closed-book" claims about cited systems.** §I says of the MuTAP- and
   Meta-style methods that "generation is closed-book". Adding ACH and RefTest
   puts more systems under that sentence. Their abstracts neither confirm nor
   rule out repository retrieval, so the sentence must not be extended to them
   without reading the full texts. RefTest is explicitly *not* closed-book.

---

## 1. Shin et al. — Retrieval-Augmented Test Generation: How Far Are We?

Verified: arXiv 2409.12682 (v2, comment "Accepted as Research Track Paper at
ICSE'26"); Crossref DOI 10.1145/3744916.3773163 (ICSE 2026, pp. 767–779).

```bibtex
@inproceedings{shin2026ragtestgen,
  author    = {Shin, Jiho and Shiri Harzevili, Nima and Aleithan, Reem and
               Hemmati, Hadi and Wang, Song},
  title     = {Retrieval-Augmented Test Generation: How Far Are We?},
  booktitle = {Proceedings of the IEEE/ACM 48th International Conference on
               Software Engineering (ICSE)},
  year      = {2026},
  pages     = {767--779},
  doi       = {10.1145/3744916.3773163},
  note      = {arXiv:2409.12682}
}
```

IEEE string: J. Shin, N. Shiri Harzevili, R. Aleithan, H. Hemmati, and S. Wang, "Retrieval-augmented test generation: How far are we?," in *Proc. IEEE/ACM ICSE*, 2026, pp. 767–779, doi: 10.1145/3744916.3773163.

**Positioning.** Shin et al. study RAG for unit-test generation of ML/DL
library APIs (TensorFlow, PyTorch, scikit-learn, JAX, XGBoost). They retrieve
from *external* knowledge sources: API documentation, GitHub issues and Stack
Overflow. They report that RAG does not improve test correctness, though it
raises line coverage by 6.5% on average. We retrieve instead from the codebase
under test, resolving the definitions of the symbols a unit references, and we
measure mutant kills rather than coverage. Taken together, the two results
suggest that *what* is retrieved matters more than *whether* one retrieves. We
note the differences in model scale (four frontier or large models vs. our 7B
local model) and in outcome measure, which rule out a direct comparison.

## 2. Zhang et al. — Reference-Based Retrieval-Augmented Unit Test Generation (RefTest; preprint: APT)

Verified: Crossref DOI 10.1145/3765758 (TOSEM 35(6), 1–34, 2026); arXiv
2410.13542 (same authors; title "LLM-based Unit Test Generation via Property
Retrieval"; tool APT).

```bibtex
@article{zhang2026reftest,
  author  = {Zhang, Zhe and Liu, Xingyu and Lin, Yuanzhang and Gao, Xiang and
             Sun, Hailong and Yuan, Yuan},
  title   = {Reference-Based Retrieval-Augmented Unit Test Generation},
  journal = {ACM Transactions on Software Engineering and Methodology},
  volume  = {35},
  number  = {6},
  pages   = {1--34},
  year    = {2026},
  doi     = {10.1145/3765758},
  note    = {Extended version of arXiv:2410.13542 (tool: APT)}
}
```

IEEE string: Z. Zhang, X. Liu, Y. Lin, X. Gao, H. Sun, and Y. Yuan, "Reference-based retrieval-augmented unit test generation," *ACM Trans. Softw. Eng. Methodol.*, vol. 35, no. 6, pp. 1–34, 2026, doi: 10.1145/3765758.

**Positioning.** RefTest also retrieves from inside the project. For a focal
method it retrieves related methods and *their existing tests*, and uses them
to guide the Given/When/Then phases of the new test. Its goal is general unit-test quality
(correctness, completeness, maintainability). Ours differs in three narrower
ways: the target is a specific surviving mutant under a two-sided kill
criterion; the retrieved context is the *definitions* (constants, tables,
helpers) a unit reads, not neighbouring tests; and the study isolates when such
context helps, including where it does not. Because RefTest's abstract treats
referenced-variable context as prior practice, we should not claim
dependency-aware context as new in itself. What we can claim is the controlled
measurement of its effect on mutant killing.

## 3. Wang et al. — SMART: Boosting LLMs for Mutation Generation

Verified: Crossref DOI 10.1145/3808156 (Proc. ACM Softw. Eng. 3(FSE),
3368–3391, 2026); arXiv 2603.24560 (comment "to be published in the
collection of FSE 2026").

```bibtex
@article{wang2026smart,
  author  = {Wang, Bo and Deng, Ming and Chen, Mingda and Yang, Chengran and
             Lin, Youfang and Harman, Mark and Papadakis, Mike and
             Zhang, Jie M.},
  title   = {Boosting {LLMs} for Mutation Generation},
  journal = {Proceedings of the ACM on Software Engineering},
  volume  = {3},
  number  = {FSE},
  pages   = {3368--3391},
  year    = {2026},
  doi     = {10.1145/3808156}
}
```

IEEE string: B. Wang, M. Deng, M. Chen, C. Yang, Y. Lin, M. Harman, M. Papadakis, and J. M. Zhang, "Boosting LLMs for mutation generation," *Proc. ACM Softw. Eng.*, vol. 3, no. FSE, pp. 3368–3391, 2026, doi: 10.1145/3808156.

**Positioning.** SMART (Semantic Mutation with Adaptive Retrieval and
Tuning) applies RAG over a vectorised dataset of real-world bugs, together with
focused code chunking and fine-tuning. Its aim is to generate mutants that are
more realistic and more coupled to real faults, evaluated on Defects4J and
ConDefects (Java). It uses retrieval on the *mutant-generation* side; we use
retrieval on the *test-generation* side to kill mutants that already exist.
The two are complementary: SMART makes better mutants, and we study what a
generator needs to know to kill them.

## 4. Harman et al. — Mutation-Guided LLM-based Test Generation at Meta (ACH)

Verified: Crossref DOI 10.1145/3696630.3728544 (FSE Companion '25, pp.
180–191; published author order Harman first); arXiv 2501.12862 (preprint,
alphabetical order, Foster first).

```bibtex
@inproceedings{harman2025ach,
  author    = {Harman, Mark and Ritchey, Jillian and Harper, Inna and
               Sengupta, Shubho and Mao, Ke and Gulati, Abhishek and
               Foster, Christopher and Robert, Herv{\'e}},
  title     = {Mutation-Guided {LLM}-based Test Generation at {Meta}},
  booktitle = {Companion Proceedings of the 33rd ACM International Conference
               on the Foundations of Software Engineering (FSE Companion)},
  year      = {2025},
  pages     = {180--191},
  doi       = {10.1145/3696630.3728544},
  note      = {arXiv:2501.12862}
}
```

IEEE string: M. Harman, J. Ritchey, I. Harper, S. Sengupta, K. Mao, A. Gulati, C. Foster, and H. Robert, "Mutation-guided LLM-based test generation at Meta," in *Companion Proc. ACM FSE*, 2025, pp. 180–191, doi: 10.1145/3696630.3728544.

**Positioning.** ACH is the closest industrial analogue to our objective. It
generates a few concern-specific mutants that current tests miss, then
generates tests to kill them, with an LLM-based equivalent-mutant detector. It
was applied to 10,795 Android Kotlin classes, and engineers accepted 73% of
its tests. ACH shows that mutant-targeted test generation works at scale. Our
study asks a narrower, controlled question it does not isolate: how much of a
generator's success comes from retrieved codebase context. ACH is a different
system from TestGen-LLM (reference [6]), and both should be cited.

## 5. Fix to reference [6] — TestGen-LLM (keep; add identifiers)

Verified: Crossref DOI 10.1145/3663529.3663839 (FSE Companion '24, pp.
185–196). The Crossref spelling "Finogenova" matches the draft. The arXiv
record (2402.09171) spells it "Finegenova", which is a preprint typo; do not
copy it.

```bibtex
@inproceedings{alshahwan2024testgenllm,
  author    = {Alshahwan, Nadia and Chheda, Jubin and Finogenova, Anastasia and
               Gokkaya, Beliz and Harman, Mark and Harper, Inna and
               Marginean, Alexandru and Sengupta, Shubho and Wang, Eddy},
  title     = {Automated Unit Test Improvement using Large Language Models at
               {Meta}},
  booktitle = {Companion Proceedings of the 32nd ACM International Conference
               on the Foundations of Software Engineering (FSE Companion)},
  year      = {2024},
  pages     = {185--196},
  doi       = {10.1145/3663529.3663839}
}
```

## 6. Fix to reference [11] — LLMorpheus (author and venue)

Verified: Crossref DOI 10.1109/TSE.2025.3562025 (IEEE TSE 51(6), 1645–1665,
June 2025); arXiv 2404.09952 (authors Frank Tip, Jonathan Bell, Max Schaefer).

```bibtex
@article{tip2025llmorpheus,
  author  = {Tip, Frank and Bell, Jonathan and Sch{\"a}fer, Max},
  title   = {{LLMorpheus}: Mutation Testing Using Large Language Models},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {51},
  number  = {6},
  pages   = {1645--1665},
  year    = {2025},
  doi     = {10.1109/TSE.2025.3562025}
}
```

## 7. Fix to reference [12] — replace with SMART (entry 3)

The current [12] ("Y. Wang et al., 'Retrieval-augmented mutant generation via
historical bug-fix pairs,' 2025.") matches no record found in arXiv or
Crossref. Its description fits SMART but its title, first-author initial
(Y. vs. B. Wang), year and characterisation ("bug-fix pairs") do not. Replace
it with entry 3, and update the §II-C sentence that cites it (see
`EDITS_PENDING.md` E10).
