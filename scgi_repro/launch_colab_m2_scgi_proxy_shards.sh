#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="${REF:-scgi-colab-20260709}"
COLAB_GPU="${COLAB_GPU:-L4}"
CU_PER_HOUR="${CU_PER_HOUR:-0}"
PERSIST_ROOT="${PERSIST_ROOT:-}"
SYNC_SECONDS="${SYNC_SECONDS:-300}"
BATCH="${BATCH:-m2_scgi_proxy_dense_$(date +%Y%m%d_%H%M%S)}"
SHARDS="${SHARDS:-5}"
OBJECTS="${OBJECTS:-10}"
SEEDS="${SEEDS:-5}"
PROFILE="${PROFILE:-debug}"
SHARD_LIST="${SHARD_LIST:-0 1 2 3 4}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-phase_m2_scgi_proxy}"
SCGI_CHECKPOINT="${SCGI_CHECKPOINT:-}"
SCGI_MODEL_KIND="${SCGI_MODEL_KIND:-}"

mkdir -p "$LOG_DIR"

launch_shard() {
  local account_home="$1"
  local account_label="$2"
  local shard_index="$3"
  local shard_spec="${shard_index}/${SHARDS}"
  local run_id="${account_label}_${BATCH}_shard${shard_index}of${SHARDS}"
  local output_dir="results/${OUTPUT_PREFIX}_${BATCH}_shard${shard_index}of${SHARDS}"
  local log_file="$LOG_DIR/${run_id}.log"
  local pid_file="$LOG_DIR/${run_id}.wslpid"
  local scgi_args=""
  if [[ -n "$SCGI_CHECKPOINT" ]]; then
    scgi_args="${scgi_args} --scgi-checkpoint ${SCGI_CHECKPOINT}"
  fi
  if [[ -n "$SCGI_MODEL_KIND" ]]; then
    scgi_args="${scgi_args} --scgi-model-kind ${SCGI_MODEL_KIND}"
  fi
  local command_text="python run_phase_m2.py --profile ${PROFILE} --objects ${OBJECTS} --seeds ${SEEDS} --shard ${shard_spec} --resume --no-findings${scgi_args} --output-dir ${output_dir}"

  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --gpu "$COLAB_GPU" --timeout 14400 \
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
    --max-zip-mb 50 \
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
  sleep 8
done
