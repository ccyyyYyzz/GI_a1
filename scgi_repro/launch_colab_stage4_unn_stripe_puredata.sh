#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR}"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="${COLAB:-/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab}"
REPO="${REPO:-https://github.com/ccyyyYyzz/GI_a1.git}"
REF="${REF:-scgi-colab-20260709}"
RUN_TAG="${RUN_TAG:-stage4_unn_stripe_puredata_colab_r1}"
SHARDS="${SHARDS:-2}"
SHARD_LIST="${SHARD_LIST:-0 1}"
PROFILE="${PROFILE:-full}"
CHECKPOINT="${CHECKPOINT:-results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt}"
MODEL_KIND="${MODEL_KIND:-exponential_residual_unet}"
OBJECT_NAMES="${OBJECT_NAMES:-stripe_target}"
STEPS_VALUES="${STEPS_VALUES:-25 50 100 200}"
LR_VALUES="${LR_VALUES:-0.0005 0.001 0.002}"
BETA_VALUES="${BETA_VALUES:-0}"
XI_VALUES="${XI_VALUES:-0 0.01}"
X_STEP_VALUES="${X_STEP_VALUES:-0.1}"
CHANNELS_VALUES="${CHANNELS_VALUES:-24 32}"
BLOCKS_VALUES="${BLOCKS_VALUES:-3}"
RESIDUAL_SCALE_VALUES="${RESIDUAL_SCALE_VALUES:-0.05 0.1}"
DENOISER_VALUES="${DENOISER_VALUES:-none}"
FIXED_INIT_SEED="${FIXED_INIT_SEED:-20240709}"
COLAB_GPU="${COLAB_GPU:-L4}"
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
  local command_text="python run_stage4_ured_sweep.py --profile ${PROFILE} --checkpoint ${CHECKPOINT} --model-kind ${MODEL_KIND} --object-names ${OBJECT_NAMES} --config-shard ${shard_spec} --steps-values '${STEPS_VALUES}' --lr-values '${LR_VALUES}' --beta-values '${BETA_VALUES}' --xi-values '${XI_VALUES}' --x-step-values '${X_STEP_VALUES}' --channels-values '${CHANNELS_VALUES}' --blocks-values '${BLOCKS_VALUES}' --residual-scale-values '${RESIDUAL_SCALE_VALUES}' --denoiser-values '${DENOISER_VALUES}' --fixed-init-seed ${FIXED_INIT_SEED} --output-dir ${output_dir} --save-traces"

  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --session "$run_id" --gpu "$COLAB_GPU" --timeout "$TIMEOUT_SECONDS" \
    "$RUNNER" \
    --repo "$REPO" \
    --ref "$REF" \
    --workdir scgi_repro \
    --run-id "$run_id" \
    --accelerator "$COLAB_GPU" \
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
    0)
      launch_shard "/var/tmp/codex-colab-accounts/pro1" "pro1" "$shard_index"
      ;;
    1)
      launch_shard "/var/tmp/codex-colab-accounts/pro2" "pro2" "$shard_index"
      ;;
    *)
      echo "Unsupported shard index: $shard_index" >&2
      exit 2
      ;;
  esac
  sleep "$LAUNCH_DELAY_SECONDS"
done
