# Headline comparison at equal attempt budgets (RAG k=5)

One generation attempt per surviving mutant per arm; all arms scored on the same mutants. Each cell is **kills / attempts (kill rate)**; here attempts = number of surviving mutants.

## Kill rate by subject

| subject | mutants (= attempts per arm) | NO_RAG: kills / attempts | RAG (k=5): kills / attempts |
|---|---|---|---|
| ctxlib | 24 | 3/24 (12.5%) | 19/24 (79.2%) |
| schedule | 6 | 0/6 (0.0%) | 0/6 (0.0%) |
| sorts_focused | 9 | 2/9 (22.2%) | 2/9 (22.2%) |
| ALL | 39 | 5/39 (12.8%) | 21/39 (53.8%) |

## Valid-test rate by subject

| subject | mutants (= attempts per arm) | NO_RAG: valid tests / attempts | RAG (k=5): valid tests / attempts |
|---|---|---|---|
| ctxlib | 24 | 6/24 (25.0%) | 21/24 (87.5%) |
| schedule | 6 | 0/6 (0.0%) | 0/6 (0.0%) |
| sorts_focused | 9 | 6/9 (66.7%) | 6/9 (66.7%) |
| ALL | 39 | 12/39 (30.8%) | 27/39 (69.2%) |

## Kill rate by mutation class — ctxlib

| mutation_class | mutants (= attempts per arm) | NO_RAG: kills / attempts | RAG (k=5): kills / attempts |
|---|---|---|---|
| sdl | 13 | 2/13 (15.4%) | 11/13 (84.6%) |
| semantic | 7 | 1/7 (14.3%) | 4/7 (57.1%) |
| higher_order | 4 | 0/4 (0.0%) | 4/4 (100.0%) |

## Kill rate by mutation class — schedule

| mutation_class | mutants (= attempts per arm) | NO_RAG: kills / attempts | RAG (k=5): kills / attempts |
|---|---|---|---|
| sdl | 5 | 0/5 (0.0%) | 0/5 (0.0%) |
| higher_order | 1 | 0/1 (0.0%) | 0/1 (0.0%) |

## Kill rate by mutation class — sorts_focused

| mutation_class | mutants (= attempts per arm) | NO_RAG: kills / attempts | RAG (k=5): kills / attempts |
|---|---|---|---|
| sdl | 3 | 0/3 (0.0%) | 0/3 (0.0%) |
| semantic | 6 | 2/6 (33.3%) | 2/6 (33.3%) |

## Kill rate by mutation class — ALL

| mutation_class | mutants (= attempts per arm) | NO_RAG: kills / attempts | RAG (k=5): kills / attempts |
|---|---|---|---|
| sdl | 21 | 2/21 (9.5%) | 11/21 (52.4%) |
| semantic | 13 | 3/13 (23.1%) | 6/13 (46.2%) |
| higher_order | 5 | 0/5 (0.0%) | 4/5 (80.0%) |
