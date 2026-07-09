#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="${REF:-scgi-colab-20260709}"
BATCH="${BATCH:-stage3_threshold_full_$(date +%Y%m%d_%H%M%S)}"
SHARDS="${SHARDS:-4}"
SHARD_LIST="${SHARD_LIST:-0 1 2 3}"
URED_STEPS="${URED_STEPS:-500}"
PROFILE="${PROFILE:-full}"
CHECKPOINT="${CHECKPOINT:-results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt}"
MODEL_KIND="${MODEL_KIND:-exponential_residual_unet}"

mkdir -p "$LOG_DIR"

launch_shard() {
  local account_home="$1"
  local account_label="$2"
  local shard_index="$3"
  local shard_spec="${shard_index}/${SHARDS}"
  local run_id="${account_label}_${BATCH}_shard${shard_index}of${SHARDS}"
  local output_dir="results/${BATCH}_shard${shard_index}of${SHARDS}"
  local log_file="$LOG_DIR/${run_id}.log"
  local pid_file="$LOG_DIR/${run_id}.wslpid"
  local command_text="python run_stage3_tests.py --profile ${PROFILE} --checkpoint ${CHECKPOINT} --model-kind ${MODEL_KIND} --include-unn-ured --ured-steps ${URED_STEPS} --object-shard ${shard_spec} --output-dir ${output_dir}"

  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --gpu L4 --timeout 14400 \
    "$RUNNER" \
    --repo "$REPO" \
    --ref "$REF" \
    --workdir scgi_repro \
    --run-id "$run_id" \
    --install-requirements \
    --command "$command_text" \
    --artifact-root "$output_dir" \
    --emit-zip \
    --max-zip-mb 80 \
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
