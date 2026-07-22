#!/usr/bin/env bash
# Confirmatory run for PREREGISTRATION.md.
#
# Runs the 9-cell matrix at n=300 for the primary judge, then repeats for the
# weaker secondary judge. Results append to results.tsv as each cell completes,
# so a partial run is still usable. Cells are ordered by priority: the primary
# hypotheses first, so if the run is interrupted the most important cells exist.
#
# Usage: ./run_overnight.sh

set -uo pipefail
cd "$(dirname "$0")"

N=300
PY=./.venv/bin
OUT=results.tsv
LOG=overnight.log

if [ ! -f "$OUT" ]; then
  printf 'judge\tprotocol\taccess\tn\taccuracy\tstderr\ttimestamp\n' > "$OUT"
fi

run_cell () {
  local judge="$1" task="$2" protocol="$3" access="$4"
  echo "[$(date -u +%H:%M:%S)] START $judge $protocol/$access" | tee -a "$LOG"

  local raw
  raw=$("$PY/inspect" eval "oversight/task.py@${task}" \
          --model "$judge" -T n="$N" 2>&1) || true

  local acc se
  acc=$(echo "$raw" | grep -E '^accuracy' | awk '{print $2}' | head -1)
  se=$(echo "$raw"  | grep -E '^stderr'   | awk '{print $2}' | head -1)

  if [ -z "$acc" ]; then
    echo "[$(date -u +%H:%M:%S)] FAIL  $judge $protocol/$access" | tee -a "$LOG"
    echo "$raw" | tail -5 >> "$LOG"
    return
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$judge" "$protocol" "$access" "$N" "$acc" "$se" "$(date -u +%FT%TZ)" >> "$OUT"
  echo "[$(date -u +%H:%M:%S)] DONE  $judge $protocol/$access acc=$acc se=$se" | tee -a "$LOG"
}

# Validation gate: the obscured condition is void if a judge can read the cipher.
echo "=== validation gate ===" | tee -a "$LOG"
"$PY/python" -m oversight.validate 2>&1 | tail -6 | tee -a "$LOG"

for JUDGE in ollama/qwen2.5:7b ollama/qwen2.5:3b; do
  echo "=== judge $JUDGE ===" | tee -a "$LOG"

  # Priority order: primary hypotheses (H1, H2, H3, H4) before the control (H5).
  run_cell "$JUDGE" debate_none        debate      none
  run_cell "$JUDGE" direct_none        direct      none
  run_cell "$JUDGE" direct_obscured    direct      obscured
  run_cell "$JUDGE" debate_obscured    debate      obscured
  run_cell "$JUDGE" consultancy_none   consultancy none
  run_cell "$JUDGE" consultancy_obscured consultancy obscured
  run_cell "$JUDGE" direct_full        direct      full
  run_cell "$JUDGE" debate_full        debate      full
  run_cell "$JUDGE" consultancy_full   consultancy full
done

echo "[$(date -u +%H:%M:%S)] ALL DONE" | tee -a "$LOG"
column -t -s "$(printf '\t')" "$OUT"
