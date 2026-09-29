# WSL session runbook: P0-3 (FULL_CONTEXT), P0-6 (retriever ablation), P0-4 (mutmut evidence)

**Who this is for:** whoever sits at the original WSL machine, the one whose
home directory holds `~/codekong` and which produced the committed ctxlib
results in July 2026. You do not need any other background. Follow the
steps in order and type the commands exactly as written. **Where a step says
STOP, stop.** Do not work around it; send what you have (Step 9) and wait.

**Why the rules are strict.** The new runs are only worth anything if they are
comparable with results produced in July: same machine, same model weights,
same mutants, same index, same config. A different model blob under the same
name `qwen2.5-coder:7b`, a rebuilt index, or a different mutant file would
make every new number incomparable, and nobody could tell afterwards.

**Golden rules**

1. **Never run anything that writes inside `~/codekong`.** It is the evidence
   of the July runs. Treat it as read-only. All new work happens in a fresh
   clone, `~/codekong-p0`.
2. Never run `--phase mutate` or `--phase index`, and never run
   `run_pipeline.py` without `--results-tag`.
3. Never delete a `_checkpoint_*.jsonl` file.
4. Never run from a path under `/mnt/`. Copying files *to* `/mnt/c/...` at the
   end is fine.

---

## 0. Prerequisites: must be true before the session starts

These are checked in Step 4; if any is false, the session stops there.

- [ ] A branch containing the P0-3/P0-6 code is pushed to
      `https://github.com/aarush-170/codekong`. Its name is written here:
      `BRANCH=__________` (the authors fill this in). That branch must provide
      these `run_pipeline.py` options, which **do not exist on `main`**:
  - `--results-tag TAG`: writes `raw_TAG.csv`, `summary_TAG.csv`,
    `records_TAG.json` and `_checkpoint_TAG.jsonl`, and **refuses to run if
    `raw_TAG.csv` already exists**. Without it, a run overwrites the committed
    `raw_ctxlib.csv`.
  - `--mutant-ids-from CSV`: restricts the run to exactly the `mutant_id`s
    in that CSV and exits with an error if any are missing from
    `surviving_mutants.json` (no `--limit` sampling).
  - `--conditions FULL_CONTEXT`: the P0-3 arm.
  - `--retriever-variant {full,no_constants,no_depfetch}`: the P0-6 arms,
    implemented as retrieval-time switches on the *existing* index (no
    re-indexing).
  - The results tag is written into each call-log `purpose`, so token cost
    can be attributed per arm.
- [ ] The machine is plugged in and set not to sleep for about 3 hours.
- [ ] You know your Windows username (for copying results out in Step 9).

## Time budget

| Step | What | Expected wall-clock |
|---|---|---|
| 0–1 | Session setup; evidence capture (call log first) | 15 min |
| 2 | Pre-flight checks, including the two HARD STOPs | 10 min |
| 3 | Create the working copy `~/codekong-p0` | 10 min |
| 4 | Code check and smoke tests | 5 min |
| 5 | Drift check: re-run NO_RAG and RAG k=5 | 25 min (July: 705 s + 645 s) |
| 6 | P0-3 FULL_CONTEXT | 15–40 min (larger prompts; no prior timing) |
| 7 | P0-6 ablation, two variants at k=5 | 25 min (≈ 645 s each) |
| 8 | P0-4 mutmut evidence (timeboxed) | ≤ 30 min |
| 9 | Package and ship | 10 min |
| | **Total** | **≈ 2.5–3 h** |

The July timings come from `module4_eval/results/raw_ctxlib.csv` (`wall_seconds`, summed per arm).

---

## Step 0: Session setup (2 min)

Open a WSL terminal. Run:

```bash
[ -e ~/p0-session ] && echo "STOP: ~/p0-session already exists from an earlier session. Do not overwrite it; ask the authors." || mkdir -p ~/p0-session/evidence ~/p0-session/logs
```

If it printed STOP, stop. Otherwise create the environment file that every
later step re-reads:

```bash
cat > ~/p0-session/env.sh <<'ENV'
export OLD="$HOME/codekong"
export NEW="$HOME/codekong-p0"
export S="$HOME/p0-session"
export EV="$S/evidence"
export LOGS="$S/logs"
export PYTHONDONTWRITEBYTECODE=1
set -o pipefail
ENV
source ~/p0-session/env.sh
{ date -u; hostname; whoami; uname -a; } | tee "$EV/00_identity.txt"
```

**If you open a new terminal at any point, first run `source ~/p0-session/env.sh`.**

## Step 1: Evidence capture. The call log comes first, before anything can overwrite it (10 min)

1a. The call log. Copy it first, preserving timestamps, and hash it:

```bash
source ~/p0-session/env.sh
ls -la "$OLD/module3_llm/llm_calls.jsonl" 2>&1 | tee "$EV/01a_calllog_ls.txt"
cp -a "$OLD/module3_llm/llm_calls.jsonl" "$EV/llm_calls.jsonl" 2>&1 | tee -a "$EV/01a_calllog_ls.txt"
sha256sum "$EV/llm_calls.jsonl" "$OLD/module3_llm/llm_calls.jsonl" | tee "$EV/01a_calllog.sha256"
wc -l "$EV/llm_calls.jsonl" | tee -a "$EV/01a_calllog.sha256"
```

The two hashes must be identical. If the file does not exist, search for copies and record what you find:

```bash
find "$HOME" -name 'llm_calls*.jsonl' -not -path '*/venv/*' -exec ls -la {} \; 2>/dev/null | tee "$EV/01a_calllog_search.txt"
```

If a copy is found elsewhere, copy it the same way (`cp -a <path> "$EV/llm_calls.jsonl"`). If none exists, continue: Step 2d will STOP, but the rest of the evidence is still worth capturing.

1b. Everything else from the July runs (read-only copies):

```bash
source ~/p0-session/env.sh
tar czf "$EV/old_results.tgz" -C "$OLD" module4_eval/results 2>&1 | tee "$LOGS/01b_tar.log"
ls -la "$OLD/module4_eval/results/" | tee "$EV/01b_results_ls.txt"
ls -la "$OLD"/module4_eval/results/_checkpoint_*.jsonl 2>&1 | tee "$EV/01b_checkpoints_ls.txt"
cp -a "$OLD/module1_mutation/surviving_mutants.json" "$EV/" 2>&1 | tee -a "$LOGS/01b_tar.log"
find "$HOME" -name 'surviving_mutants*.json' -not -path "$EV/*" -exec ls -la --time-style=full-iso {} \; 2>/dev/null | tee "$EV/01b_mutant_files.txt"
tar czf "$EV/old_generated_tests.tgz" -C "$OLD" module3_llm/generated_tests 2>&1 | tee -a "$LOGS/01b_tar.log"
tar czf "$EV/old_subjects.tgz" -C "$OLD" subjects config.yaml 2>&1 | tee -a "$LOGS/01b_tar.log"
tar czf "$EV/old_chroma_db.tgz" -C "$OLD" module2_rag/chroma_db 2>&1 | tee -a "$LOGS/01b_tar.log"
cp -a "$OLD/module2_rag/rag_context.json" "$EV/" 2>/dev/null; true
find "$OLD" -maxdepth 2 \( -name '*.log' -o -name 'nohup.out' \) -exec ls -la {} \; | tee "$EV/01b_logs_ls.txt"
```

Any `_checkpoint_*.jsonl` files are important. They may hold the outcomes of
runs that were interrupted and never reported.

1c. A fingerprint of the old tree, used by the rollback check:

```bash
source ~/p0-session/env.sh
( cd "$OLD" && find . -type f -not -path './venv/*' -not -path '*/__pycache__/*' -print0 | sort -z | xargs -0 sha256sum ) > "$EV/old_manifest.sha256"
wc -l "$EV/old_manifest.sha256"
git -C "$OLD" rev-parse HEAD 2>&1 | tee "$EV/01c_old_git.txt"
git -C "$OLD" status --short 2>&1 | head -50 | tee -a "$EV/01c_old_git.txt"
"$OLD/venv/bin/pip" freeze | tee "$EV/01c_pip_freeze.txt" > /dev/null
```

("not a git repository" in `01c_old_git.txt` is fine; just record it.)

## Step 2: Pre-flight checks (10 min)

2a. Not under `/mnt`:

```bash
source ~/p0-session/env.sh
for p in "$OLD" "$S"; do r=$(realpath "$p"); echo "$r"; case "$r" in /mnt/*) echo "STOP: $r is under /mnt";; esac; done | tee "$EV/02a_paths.txt"
```

If STOP appears, stop.

2b. Guards pass:

```bash
source ~/p0-session/env.sh
cd "$OLD" && "$OLD/venv/bin/python" -c "
from core.guards import assert_fork_capable_linux, assert_not_windows_mount
assert_fork_capable_linux(); assert_not_windows_mount('$OLD'); print('GUARDS OK')" 2>&1 | tee "$EV/02b_guards.txt"; cd ~
```

If it does not print `GUARDS OK`, stop.

2c. The model and the Ollama server:

```bash
source ~/p0-session/env.sh
{ echo '== version'; ollama --version
  echo '== list'; ollama list
  echo '== which server'; systemctl is-active ollama 2>&1; ps -eo pid,user,lstart,cmd | grep '[o]llama serve'
  echo '== api/tags'; curl -s http://localhost:11434/api/tags
  echo; echo '== api/show'; curl -s http://localhost:11434/api/show -d '{"model":"qwen2.5-coder:7b"}' | head -c 4000
  echo; echo '== manifests'; for d in "$HOME/.ollama" /usr/share/ollama/.ollama; do f="$d/models/manifests/registry.ollama.ai/library/qwen2.5-coder/7b"; [ -f "$f" ] && { stat "$f"; cat "$f"; echo; }; done
} 2>&1 | tee "$EV/02c_ollama.txt"
```

If `curl` returns nothing, Ollama is not running. Start it the way it normally
runs on this machine (the "which server" lines show whether that is systemd or
a manual `ollama serve`), then re-run 2c.

2d. **HARD STOP A: is this the same model that produced the July results?**
No model digest was recorded in July, so the test is this: the installed
`qwen2.5-coder:7b` must be unchanged since before the first July ctxlib call in
the call log.

```bash
source ~/p0-session/env.sh
"$OLD/venv/bin/python" - <<'PY' 2>&1 | tee "$EV/02d_model_check.txt"
import csv, json, os, urllib.request, datetime as dt
OLD, EV = os.environ["OLD"], os.environ["EV"]
ids = {r["mutant_id"] for r in csv.DictReader(open(f"{OLD}/module4_eval/results/raw_ctxlib.csv"))}
calls = []
if os.path.exists(f"{EV}/llm_calls.jsonl"):
    for line in open(f"{EV}/llm_calls.jsonl", encoding="utf-8"):
        try: r = json.loads(line)
        except Exception: continue
        p = r.get("purpose", "")
        if p.startswith("testgen:") and p.split(":")[-1] in ids:
            calls.append(r)
utc = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat()
print("ctxlib testgen calls in log:", len(calls))
by = {}
for r in calls:
    c = r["purpose"].split(":")[1]; by[c] = by.get(c, 0) + 1
print("calls by condition:", by, "(committed cost_ctxlib.csv sums: NO_RAG 47, RAG 92)")
print("model names used:", sorted({r.get("model") for r in calls}))
first = min((r["ts"] for r in calls), default=None)
print("first ctxlib call:", utc(first) if first else None)
print("last ctxlib call: ", utc(max(r["ts"] for r in calls)) if calls else None)
tags = json.load(urllib.request.urlopen("http://localhost:11434/api/tags"))
inst = [m for m in tags.get("models", []) if m["name"] == "qwen2.5-coder:7b"]
for m in inst:
    print("installed:", m["name"], m["digest"], "modified_at", m["modified_at"])
import re
def parse(s):  # Ollama reports nanoseconds; drop the fraction before parsing
    return dt.datetime.fromisoformat(re.sub(r"\.\d+", "", s).replace("Z", "+00:00"))
ok = bool(calls) and len(inst) == 1 and first is not None and \
     parse(inst[0]["modified_at"]) < dt.datetime.fromtimestamp(first, dt.timezone.utc)
print("MODEL CHECK:", "PASS" if ok else "FAIL")
if ok:
    open(f"{EV}/MODEL_DIGEST.txt", "w").write(inst[0]["digest"] + "\n")
PY
```

**If it prints `MODEL CHECK: FAIL`, STOP.** That covers: no call log, no ctxlib
calls in it, zero or several matching models, or a model modified after the
July runs began. Go straight to Step 9, then report.

If it passes, the digest in `MODEL_DIGEST.txt` becomes the reference digest
for every future run.

2e. **HARD STOP B: are the exact 24 ctxlib mutants available?** Mutant IDs are
content hashes (`core/schema.py`: `sha1(file|function|mutated_code)`), so this
check proves the mutant contents, not just their names.
`surviving_mutants.json` is overwritten by every `mutate` run, so it may now
hold a different subject.

```bash
source ~/p0-session/env.sh
"$OLD/venv/bin/python" - <<'PY' 2>&1 | tee "$EV/02e_mutant_check.txt"
import csv, glob, hashlib, json, os
OLD, EV, H = os.environ["OLD"], os.environ["EV"], os.environ["HOME"]
ids = {r["mutant_id"] for r in csv.DictReader(open(f"{OLD}/module4_eval/results/raw_ctxlib.csv"))}
cands = [f"{OLD}/module1_mutation/surviving_mutants.json"] + sorted(set(glob.glob(f"{H}/**/surviving_mutants*.json", recursive=True)) - {f"{OLD}/module1_mutation/surviving_mutants.json"})
best = None
for path in cands:
    if "/venv/" in path or path.startswith(EV): continue
    try: ms = json.load(open(path, encoding="utf-8"))
    except Exception as e: print("unreadable:", path, e); continue
    valid = {}
    for m in ms:
        h = hashlib.sha1(f"{m['file']}|{m['function']}|{m['mutated_code']}".encode()).hexdigest()[:10]
        if m.get("mutant_id") == f"{m['mutation_class']}_{m['function']}_{h}":
            valid[m["mutant_id"]] = m
    have = ids & set(valid)
    print(f"{path}: {len(ms)} mutants, {len(have)}/24 ctxlib ids present with valid hash")
    if len(have) == 24 and best is None: best = path
print("MUTANT CHECK:", "PASS " + best if best else "FAIL")
if best: open(f"{EV}/MUTANT_FILE.txt", "w").write(best + "\n")
PY
```

**If it prints `MUTANT CHECK: FAIL`, STOP.** Do not try to rebuild the
mutants, and do not run `--phase mutate`, which would generate *different*
mutants. The authors can reconstruct them from the prompts in the call log.
Go to Step 9.

## Step 3: Working copy (10 min)

```bash
source ~/p0-session/env.sh
[ -e "$NEW" ] && echo "STOP: $NEW already exists" || git clone https://github.com/aarush-170/codekong "$NEW" 2>&1 | tee "$LOGS/03_clone.log"
```

If it printed STOP, stop. Otherwise fill in `BRANCH` from the Prerequisites, then:

```bash
source ~/p0-session/env.sh
BRANCH=__________
cd "$NEW" && git checkout "$BRANCH" 2>&1 | tee -a "$LOGS/03_clone.log"
git rev-parse HEAD | tee "$EV/03_new_git_sha.txt"
cp -a "$(cat "$EV/MUTANT_FILE.txt")" "$NEW/module1_mutation/surviving_mutants.json"
mkdir -p "$NEW/module2_rag" && cp -a "$OLD/module2_rag/chroma_db" "$NEW/module2_rag/"
ls -la "$NEW/module1_mutation/surviving_mutants.json" "$NEW/module2_rag/chroma_db" | tee "$EV/03_copied.txt"
```

**Do not rebuild the index.** The July index contains chunks that a fresh
build would not reproduce (see `paper/CLAIMS_AUDIT.md` §C1). The copy keeps
retrieval identical.

3b. **HARD STOP C: the subject, results and config must match what ran in July.**

```bash
source ~/p0-session/env.sh
{ echo '== ctxlib source diff (OLD vs committed)'; diff -r -x __pycache__ -x .pytest_cache "$OLD/subjects/ctxlib" "$NEW/subjects/ctxlib" && echo "IDENTICAL"
  echo '== raw_ctxlib.csv diff'; diff "$OLD/module4_eval/results/raw_ctxlib.csv" "$NEW/module4_eval/results/raw_ctxlib.csv" && echo "IDENTICAL"
  echo '== config sections that affect generation'
  "$OLD/venv/bin/python" -c "
import yaml,json
a=yaml.safe_load(open('$OLD/config.yaml')); b=yaml.safe_load(open('$NEW/config.yaml'))
for k in ('llm','rag','mutation','agentic'):
    print(k, 'IDENTICAL' if a.get(k)==b.get(k) else 'DIFFERENT: '+json.dumps({'old':a.get(k),'new':b.get(k)}))
print('ctxlib subject', 'IDENTICAL' if a['subjects'].get('ctxlib')==b['subjects'].get('ctxlib') else 'DIFFERENT')"
} 2>&1 | tee "$EV/03b_consistency.txt"
```

**If any line says `DIFFERENT`, or a `diff` prints differences instead of
`IDENTICAL`, STOP** and go to Step 9.

## Step 4: Code check (5 min)

```bash
source ~/p0-session/env.sh
cd "$NEW" && source "$OLD/venv/bin/activate"
python run_pipeline.py --help | tee "$EV/04_help.txt" | grep -E -c -- '--results-tag|--mutant-ids-from|--retriever-variant|FULL_CONTEXT'
python tests/smoke_all.py 2>&1 | tee "$LOGS/04_smoke.log" | tail -1
```

The `grep -c` line must print **4** or more, and the smoke line must read
`[smoke] N/N passed`. **Otherwise STOP**: the code prerequisite is not met.

## Steps 5–7: The runs

All runs happen in `$NEW` with the old venv active. **Run one at a time**, in
order. After each, run its "check" command before starting the next.

Run this prefix once in each terminal before any run command in Steps 5–7:

```bash
source ~/p0-session/env.sh; cd "$NEW"; source "$OLD/venv/bin/activate"
IDS=module4_eval/results/raw_ctxlib.csv
```

### Step 5: Drift check (25 min)

This re-runs the July arms on today's setup, so the new arms can be compared
against a same-day baseline. It also tests the paper's "deterministic at
temperature 0" claim.

```bash
python run_pipeline.py --repo ctxlib --phase generate --conditions NO_RAG --mutant-ids-from $IDS --results-tag ctxlib_rerun_norag 2>&1 | tee "$LOGS/05a_rerun_norag.log"
python run_pipeline.py --repo ctxlib --phase generate --conditions RAG --k 5 --retriever-variant full --mutant-ids-from $IDS --results-tag ctxlib_rerun_rag_k5 2>&1 | tee "$LOGS/05b_rerun_rag_k5.log"
```

Check:

```bash
python - <<'PY' 2>&1 | tee "$EV/05_drift.txt"
import pandas as pd
old = pd.read_csv("module4_eval/results/raw_ctxlib.csv")
for tag, cond, k in (("ctxlib_rerun_norag", "NO_RAG", None), ("ctxlib_rerun_rag_k5", "RAG", 5)):
    new = pd.read_csv(f"module4_eval/results/raw_{tag}.csv")
    o = old[(old.condition == cond) & ((old.k == k) if k else old.k.isna())].set_index("mutant_id").status
    n = new.set_index("mutant_id").status
    diff = [(m, o[m], n.get(m)) for m in o.index if n.get(m) != o[m]]
    print(f"{tag}: rows={len(new)} (expect 24), status mismatches vs July={len(diff)}")
    for d in diff: print("   ", *d)
PY
```

**Do not stop on mismatches.** Record them; the authors interpret them.
Stop only if a run did not produce 24 rows (see Recovery).

### Step 6: P0-3 FULL_CONTEXT (15–40 min)

```bash
python run_pipeline.py --repo ctxlib --phase generate --conditions FULL_CONTEXT --mutant-ids-from $IDS --results-tag ctxlib_fullcontext 2>&1 | tee "$LOGS/06_fullcontext.log"
```

Check:

```bash
python -c "import pandas as pd; d=pd.read_csv('module4_eval/results/raw_ctxlib_fullcontext.csv'); print(len(d), 'rows (expect 24)'); print(d.status.value_counts().to_dict())" 2>&1 | tee "$EV/06_fullcontext_check.txt"
```

Report the numbers whichever way they fall. Do not change anything and re-run
to get different ones.

### Step 7: P0-6 retriever ablation at k=5 (25 min)

```bash
python run_pipeline.py --repo ctxlib --phase generate --conditions RAG --k 5 --retriever-variant no_constants --mutant-ids-from $IDS --results-tag ctxlib_ablation_no_constants 2>&1 | tee "$LOGS/07a_no_constants.log"
python run_pipeline.py --repo ctxlib --phase generate --conditions RAG --k 5 --retriever-variant no_depfetch --mutant-ids-from $IDS --results-tag ctxlib_ablation_no_depfetch 2>&1 | tee "$LOGS/07b_no_depfetch.log"
```

Check:

```bash
for t in ctxlib_ablation_no_constants ctxlib_ablation_no_depfetch; do python -c "import pandas as pd; d=pd.read_csv('module4_eval/results/raw_$t.csv'); print('$t', len(d), 'rows (expect 24)', d.status.value_counts().to_dict())"; done 2>&1 | tee "$EV/07_ablation_check.txt"
```

## Step 8: P0-4 mutmut evidence, timeboxed to 30 minutes

The goal is **evidence only**: capture exactly what mutmut prints, so the
parser can be fixed later. Do **not** run `run_pipeline.py --phase mutate`,
which would overwrite `surviving_mutants.json`. Work in a throwaway copy.

```bash
source ~/p0-session/env.sh; source "$OLD/venv/bin/activate"
M="$S/mutmut_ctxlib"; cp -a "$NEW/subjects/ctxlib" "$M"; cd "$M"
{ mutmut --version; pip show mutmut; } 2>&1 | tee "$EV/08_mutmut_version.txt"
printf '\n[tool.mutmut]\nsource_paths = ["."]\npytest_add_cli_args_test_selection = ["test_ctxlib.py"]\n' >> pyproject.toml
cat pyproject.toml | tee "$EV/08a_pyproject.txt"
timeout 1200 mutmut run > "$EV/08a_run_stdout.txt" 2> "$EV/08a_run_stderr.txt"; echo "exit $?" | tee -a "$EV/08a_run_stdout.txt"
mutmut results > "$EV/08a_results_stdout.txt" 2> "$EV/08a_results_stderr.txt"; echo "exit $?" | tee -a "$EV/08a_results_stdout.txt"
head -50 "$EV/08a_results_stdout.txt"
```

This first config is the pipeline's own (`source_paths = ["."]`). Now a
second, which excludes the test file from mutation:

```bash
M2="$S/mutmut_ctxlib_src_only"; cp -a "$NEW/subjects/ctxlib" "$M2"; cd "$M2"
printf '\n[tool.mutmut]\nsource_paths = ["billing.py", "grading.py", "shipping.py", "rates.py"]\npytest_add_cli_args_test_selection = ["test_ctxlib.py"]\n' >> pyproject.toml
timeout 1200 mutmut run > "$EV/08b_run_stdout.txt" 2> "$EV/08b_run_stderr.txt"; echo "exit $?" | tee -a "$EV/08b_run_stdout.txt"
mutmut results > "$EV/08b_results_stdout.txt" 2> "$EV/08b_results_stderr.txt"; echo "exit $?" | tee -a "$EV/08b_results_stdout.txt"
ls -la mutants 2>&1 | head -20 | tee "$EV/08b_mutants_dir.txt"
cd ~
```

If 30 minutes pass, stop Step 8 wherever it is. Whatever was captured is
enough.

## Step 9: Package and ship (10 min)

Always run this, including after any STOP.

```bash
source ~/p0-session/env.sh
[ -d "$NEW/module4_eval/results" ] && tar czf "$EV/new_results.tgz" -C "$NEW" module4_eval/results 2>/dev/null
[ -f "$NEW/module3_llm/llm_calls.jsonl" ] && cp -a "$NEW/module3_llm/llm_calls.jsonl" "$EV/new_llm_calls.jsonl"
[ -d "$NEW/module3_llm/generated_tests" ] && tar czf "$EV/new_generated_tests.tgz" -C "$NEW" module3_llm/generated_tests
( cd "$OLD" && find . -type f -not -path './venv/*' -not -path '*/__pycache__/*' -print0 | sort -z | xargs -0 sha256sum ) > "$S/old_manifest_after.sha256"
diff -q "$EV/old_manifest.sha256" "$S/old_manifest_after.sha256" && echo "OLD TREE UNCHANGED" | tee "$EV/09_old_unchanged.txt" || echo "WARNING: OLD TREE CHANGED" | tee "$EV/09_old_unchanged.txt"
tar czf "$HOME/p0-session.tgz" -C "$HOME" p0-session
sha256sum "$HOME/p0-session.tgz" | tee "$HOME/p0-session.tgz.sha256"
```

Copy out to Windows (replace `WINUSER`):

```bash
mkdir -p /mnt/c/Users/WINUSER/Downloads/codekong-p0-session && cp "$HOME/p0-session.tgz" "$HOME/p0-session.tgz.sha256" /mnt/c/Users/WINUSER/Downloads/codekong-p0-session/ && ls -la /mnt/c/Users/WINUSER/Downloads/codekong-p0-session/
```

Send the authors `p0-session.tgz` and its `.sha256`, plus one line saying
which step you reached and whether any STOP fired. Do not commit or push
anything to `main`.

---

## What lands where

| Step | Output | Location |
|---|---|---|
| 1 | July call log, results, mutants, tests, subjects, index, tree fingerprint | `~/p0-session/evidence/` |
| 2 | Ollama version/list/tags/show/manifest; model and mutant checks; reference digest | `evidence/02*.txt`, `MODEL_DIGEST.txt`, `MUTANT_FILE.txt` |
| 3–4 | New clone SHA, consistency diffs, `--help`, smoke log | `evidence/03*`, `evidence/04_help.txt`, `logs/04_smoke.log` |
| 5–7 | `raw_/summary_/records_<tag>` per arm | `~/codekong-p0/module4_eval/results/`, shipped as `evidence/new_results.tgz` |
| 5–7 | Per-call tokens for every new arm | `~/codekong-p0/module3_llm/llm_calls.jsonl`, shipped as `evidence/new_llm_calls.jsonl` |
| 5–7 | Console output of each run | `~/p0-session/logs/0[5-7]*.log` |
| 8 | mutmut version, configs, raw `run`/`results` output | `evidence/08*.txt` |
| 9 | Everything, tarred and hashed | `~/p0-session.tgz` and the Windows copy |

## Recovery: if a run crashes midway

Runs checkpoint after every mutant, to
`~/codekong-p0/module4_eval/results/_checkpoint_<tag>.jsonl`.

1. **Do not delete the checkpoint file.** Check it exists and count lines:
   `wc -l ~/codekong-p0/module4_eval/results/_checkpoint_<tag>.jsonl`.
2. If Ollama died (`curl -s http://localhost:11434/api/tags` returns nothing),
   restart it the same way it was running in Step 2c. Use the systemd service
   if that is what 2c showed (`sudo systemctl restart ollama`); otherwise run
   `ollama serve` in a separate terminal. **Do not `ollama pull` anything.**
   That could replace the model. Re-run `curl -s http://localhost:11434/api/tags`
   and confirm the digest still matches `evidence/MODEL_DIGEST.txt`; if it does
   not, STOP.
3. Re-run **exactly the same command** (same `--results-tag`). It prints
   `resuming from _checkpoint_<tag>.jsonl: N results already recorded` and
   skips finished mutants. Append to the same log: use `tee -a` instead of
   `tee`.
4. If the same mutant crashes the run twice, STOP. Go to Step 9 and report the
   mutant ID and the last 50 lines of the log.
5. If WSL itself restarted, open a terminal, `source ~/p0-session/env.sh`, and
   continue from step 1 of this list. Nothing in this runbook uses `/tmp`, so
   nothing is lost.
6. If a run refuses to start because `raw_<tag>.csv` already exists, that arm
   already finished. Do not delete the file to re-run it. Move on to the next
   step.

## Rollback: when it is safe to abandon the session

You can stop at any point and walk away safely **once all of these are true**:

1. `~/p0-session/evidence/llm_calls.jsonl` exists and its hash in
   `01a_calllog.sha256` matches the original, or Step 1a recorded that no call
   log exists.
2. Step 9 printed `OLD TREE UNCHANGED`. This proves `~/codekong`, the July
   evidence, was not modified.
3. `p0-session.tgz` is copied to Windows and its `.sha256` matches.
4. Nothing was committed or pushed to `main`.

When all four hold, `~/codekong-p0` and `~/p0-session` can be deleted, or kept.
Nothing in the committed repository depends on them. If check 2 prints
`WARNING: OLD TREE CHANGED`, do not delete anything: report it, because the
July evidence may have been altered, and the diff between the two manifest
files shows what changed.
