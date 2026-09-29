# RQ3: RAG retrieval-depth sweep

RAG arm only; each depth is a separate run of one attempt per mutant. Not a headline comparison — do not pool across k against a single-attempt arm. Cells are **count / attempts (rate)**.

## Valid-test rate by k

| subject | class | k=3: valid tests / attempts | k=5: valid tests / attempts | k=8: valid tests / attempts |
|---|---|---|---|---|
| ctxlib | ALL | 21/24 (87.5%) | 21/24 (87.5%) | 20/24 (83.3%) |
| ctxlib | higher_order | 3/4 (75.0%) | 4/4 (100.0%) | 4/4 (100.0%) |
| ctxlib | sdl | 13/13 (100.0%) | 13/13 (100.0%) | 12/13 (92.3%) |
| ctxlib | semantic | 5/7 (71.4%) | 4/7 (57.1%) | 4/7 (57.1%) |
| schedule | ALL | 0/6 (0.0%) | 0/6 (0.0%) | 0/6 (0.0%) |
| schedule | higher_order | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| schedule | sdl | 0/5 (0.0%) | 0/5 (0.0%) | 0/5 (0.0%) |
| sorts_focused | ALL | 6/9 (66.7%) | 6/9 (66.7%) | 5/9 (55.6%) |
| sorts_focused | sdl | 2/3 (66.7%) | 2/3 (66.7%) | 2/3 (66.7%) |
| sorts_focused | semantic | 4/6 (66.7%) | 4/6 (66.7%) | 3/6 (50.0%) |

## Kill rate by k

| subject | class | k=3: kills / attempts | k=5: kills / attempts | k=8: kills / attempts |
|---|---|---|---|---|
| ctxlib | ALL | 19/24 (79.2%) | 19/24 (79.2%) | 18/24 (75.0%) |
| ctxlib | higher_order | 3/4 (75.0%) | 4/4 (100.0%) | 4/4 (100.0%) |
| ctxlib | sdl | 11/13 (84.6%) | 11/13 (84.6%) | 10/13 (76.9%) |
| ctxlib | semantic | 5/7 (71.4%) | 4/7 (57.1%) | 4/7 (57.1%) |
| schedule | ALL | 0/6 (0.0%) | 0/6 (0.0%) | 0/6 (0.0%) |
| schedule | higher_order | 0/1 (0.0%) | 0/1 (0.0%) | 0/1 (0.0%) |
| schedule | sdl | 0/5 (0.0%) | 0/5 (0.0%) | 0/5 (0.0%) |
| sorts_focused | ALL | 2/9 (22.2%) | 2/9 (22.2%) | 2/9 (22.2%) |
| sorts_focused | sdl | 0/3 (0.0%) | 0/3 (0.0%) | 0/3 (0.0%) |
| sorts_focused | semantic | 2/6 (33.3%) | 2/6 (33.3%) | 2/6 (33.3%) |
