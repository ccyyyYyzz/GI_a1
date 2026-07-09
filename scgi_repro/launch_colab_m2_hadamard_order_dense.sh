#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR}"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="${COLAB:-/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab}"
REPO="${REPO:-https://github.com/ccyyyYyzz/GI_a1.git}"
REF="${REF:-scgi-colab-20260709}"
COLAB_GPU="${COLAB_GPU:-L4}"
CU_PER_HOUR="${CU_PER_HOUR:-0}"
PERSIST_ROOT="${PERSIST_ROOT:-}"
SYNC_SECONDS="${SYNC_SECONDS:-300}"
RUN_TAG="${RUN_TAG:-m2_hadamard_order_dense_r1}"
SHARDS="${SHARDS:-5}"
SHARD_LIST="${SHARD_LIST:-0 1 2 3 4}"
OBJECTS="${OBJECTS:-10}"
SEEDS="${SEEDS:-5}"
PROFILE="${PROFILE:-smoke}"
RHO_VALUES="${RHO_VALUES:-0.001,0.003,0.01,0.03,0.1,0.3,1.0,3.0,10.0}"
SIGMA_VALUES="${SIGMA_VALUES:-0.05,0.10,0.15,0.30,0.50}"
REFERENCE_PERIODS="${REFERENCE_PERIODS:-2,8,32}"
HADAMARD_ORDERS="${HADAMARD_ORDERS:-natural sequency cake random}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-21600}"
MAX_ZIP_MB="${MAX_ZIP_MB:-80}"
LAUNCH_DELAY_SECONDS="${LAUNCH_DELAY_SECONDS:-8}"

mkdir -p "$LOG_DIR"

launch_shard() {
  local account_home="$1"
  local account_label="$2"
  local shard_index="$3"
  local shard_spec="${shard_index}/${SHARDS}"
  local run_id="${account_label}_${RUN_TAG}_shard${shard_index}of${SHARDS}"
  local output_dir="results/${RUN_TAG}_shard${shard_index}of${SHARDS}"
  local log_file="$LOG_DIR/${run_id}.log"
  local pid_file="$LOG_DIR/${run_id}.wslpid"
  local command_text="python run_phase_m2.py --profile ${PROFILE} --objects ${OBJECTS} --seeds ${SEEDS} --rho-values '${RHO_VALUES}' --sigma-values '${SIGMA_VALUES}' --reference-periods '${REFERENCE_PERIODS}' --hadamard-orders '${HADAMARD_ORDERS}' --shard ${shard_spec} --resume --no-findings --output-dir ${output_dir}"

  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --session "$run_id" --gpu "$COLAB_GPU" --timeout "$TIMEOUT_SECONDS" \
    "$RUNNER" \
    --repo "$REPO" \
    --ref "$REF" \
    --workdir scgi_repro \
    --run-id "$run_id" \
    --accelerator "$COLAB_GPU" \
    --cu-per-hour "$CU_PER_HOUR" \
    --persist-root "$PERSIST_ROOT" \
    --sync-seconds "$SYNC_SECONDS" \
    --install-requirements \
    --command "$command_text" \
    --artifact-root "$output_dir" \
    --emit-zip \
    --max-zip-mb "$MAX_ZIP_MB" \
    > "$log_file" 2>&1 &
  echo "$!" > "$pid_file"
  echo "$run_id $! $log_file"
}

for shard_index in $SHARD_LIST; do
  case "$shard_index" in
    0|1)
      launch_shard "/var/tmp/codex-colab-accounts/pro1" "pro1" "$shard_index"
      ;;
    2|3|4)
      launch_shard "/var/tmp/codex-colab-accounts/pro2" "pro2" "$shard_index"
      ;;
    *)
      echo "Unsupported shard index: $shard_index" >&2
      exit 2
      ;;
  esac
  sleep "$LAUNCH_DELAY_SECONDS"
done
