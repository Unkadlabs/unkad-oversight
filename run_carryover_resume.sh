#!/usr/bin/env bash
# Resume the framing carry-over run, skipping cells already complete.
#
# Safe to run repeatedly. A cell counts as done only if its log holds a full
# n=300; anything partial is deleted and re-run, because a half cell analysed by
# accident is worse than no cell.
#
# This is a separate file from run_carryover.sh on purpose. Do NOT edit a script
# while bash is executing it: bash reads scripts incrementally by byte offset,
# and rewriting one underneath a live run makes the interpreter resume in the
# wrong place. We did that earlier today and it re-ran a finished cell.
#
# Usage: ./run_carryover_resume.sh

set -uo pipefail
cd "$(dirname "$0")"

N=300
JUDGE=ollama/qwen2.5:7b
PY=./.venv/bin
DIR=collapse/logs-carryover
LOG=carryover.log
export OPENAI_API_KEY=ollama

mkdir -p "$DIR"

# Drop partial logs so a resumed cell starts clean.
"$PY/python" - <<'PY'
from inspect_ai.log import read_eval_log
from pathlib import Path
for p in Path("collapse/logs-carryover").glob("*.eval"):
    try:
        n = len(read_eval_log(str(p)).samples or [])
    except Exception:
        n = -1
    if n != 300:
        print(f"removing partial log {p.name} (n={n})")
        p.unlink()
PY

complete () {
  "$PY/python" - "$1" <<'PY'
import sys, glob
from inspect_ai.log import read_eval_log
cell = sys.argv[1].replace("_", "-")
for p in glob.glob(f"collapse/logs-carryover/*{cell}*.eval"):
    try:
        if len(read_eval_log(p).samples or []) == 300:
            sys.exit(0)
    except Exception:
        pass
sys.exit(1)
PY
}

for CELL in consultancy_cipher_neutral consultancy_cipher_warned \
            debate_cipher_neutral debate_cipher_warned; do
  if complete "$CELL"; then
    echo "[$(date -u +%H:%M:%S)] SKIP  $CELL (already complete)" | tee -a "$LOG"
    continue
  fi
  echo "[$(date -u +%H:%M:%S)] START $CELL" | tee -a "$LOG"
  "$PY/inspect" eval "collapse/task.py@${CELL}" --model "$JUDGE" -T n="$N" \
      --log-dir "$DIR" > /dev/null 2>&1 || true
  echo "[$(date -u +%H:%M:%S)] DONE  $CELL" | tee -a "$LOG"
done

echo "[$(date -u +%H:%M:%S)] ALL DONE" | tee -a "$LOG"
"$PY/python" -c "
from inspect_ai.log import read_eval_log
import glob
for p in sorted(glob.glob('$DIR/*.eval')):
    log = read_eval_log(p); ss = log.samples or []
    yes = sum(1 for s in ss if getattr(next(iter((s.scores or {}).values()), None), 'answer', None) == 'YES')
    print(f'{log.eval.task.split(\"/\")[-1]:30s} n={len(ss):3d}  YES={yes/max(1,len(ss)):.3f}')
"
