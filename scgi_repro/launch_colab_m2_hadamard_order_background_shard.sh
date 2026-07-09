#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR}"
COLAB="${COLAB:-/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab}"
REPO="${REPO:-https://github.com/ccyyyYyzz/GI_a1.git}"
REF="${REF:-scgi-colab-20260709}"
COLAB_GPU="${COLAB_GPU:-L4}"
RUN_TAG="${RUN_TAG:-m2_hadamard_order_dense_r1}"
SHARD_INDEX="${SHARD_INDEX:?Set SHARD_INDEX, for example 1.}"
SHARDS="${SHARDS:-5}"
ACCOUNT_HOME="${ACCOUNT_HOME:?Set ACCOUNT_HOME to a Colab account home.}"
ACCOUNT_LABEL="${ACCOUNT_LABEL:-account}"
SESSION="${SESSION:-${ACCOUNT_LABEL}_${RUN_TAG}_bg_shard${SHARD_INDEX}of${SHARDS}}"
RUN_ID="${RUN_ID:-$SESSION}"
OBJECTS="${OBJECTS:-10}"
SEEDS="${SEEDS:-5}"
PROFILE="${PROFILE:-smoke}"
RHO_VALUES="${RHO_VALUES:-0.001,0.003,0.01,0.03,0.1,0.3,1.0,3.0,10.0}"
SIGMA_VALUES="${SIGMA_VALUES:-0.05,0.10,0.15,0.30,0.50}"
REFERENCE_PERIODS="${REFERENCE_PERIODS:-2,8,32}"
HADAMARD_ORDERS="${HADAMARD_ORDERS:-natural sequency cake random}"

LOG_DIR="$ROOT/results/colab_runs"
CONFIG_DIR="$LOG_DIR/background_configs"
mkdir -p "$LOG_DIR" "$CONFIG_DIR"

OUTPUT_DIR="results/${RUN_TAG}_shard${SHARD_INDEX}of${SHARDS}"
COMMAND_TEXT="python run_phase_m2.py --profile ${PROFILE} --objects ${OBJECTS} --seeds ${SEEDS} --rho-values '${RHO_VALUES}' --sigma-values '${SIGMA_VALUES}' --reference-periods '${REFERENCE_PERIODS}' --hadamard-orders '${HADAMARD_ORDERS}' --shard ${SHARD_INDEX}/${SHARDS} --resume --no-findings --output-dir ${OUTPUT_DIR}"
CONFIG_FILE="$CONFIG_DIR/${RUN_ID}.json"
NEW_LOG="$LOG_DIR/${RUN_ID}.new.log"
LAUNCH_LOG="$LOG_DIR/${RUN_ID}.launch.log"

python3 - "$CONFIG_FILE" <<PY
import json
import sys
from pathlib import Path

payload = {
    "artifact_root": "$OUTPUT_DIR",
    "command": "$COMMAND_TEXT",
    "install_requirements": True,
    "ref": "$REF",
    "repo": "$REPO",
    "run_id": "$RUN_ID",
    "workdir": "scgi_repro",
}
Path(sys.argv[1]).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
PY

echo "BG_SESSION_NEW $SESSION"
HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 new --session "$SESSION" --gpu "$COLAB_GPU" 2>&1 | tee "$NEW_LOG"
echo "BG_UPLOAD_CONFIG $CONFIG_FILE"
HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 upload --session "$SESSION" "$CONFIG_FILE" /content/background_command_config.json
HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 upload --session "$SESSION" "$ROOT/colab/background_command_launcher.py" /content/background_command_launcher.py
echo "BG_EXEC_LAUNCHER $SESSION"
HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 exec --session "$SESSION" --file /content/background_command_launcher.py --timeout 120 2>&1 | tee "$LAUNCH_LOG"
echo "BG_SESSION_LAUNCHED $SESSION"
echo "status=/content/${RUN_ID}.status.json"
echo "log=/content/${RUN_ID}.log"
echo "archive=/content/${RUN_ID}_artifacts.zip"
