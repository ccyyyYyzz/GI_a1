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
RUN_TAG="${RUN_TAG:-stage4_ured_continuous_binary_refine_colab_r1}"
SHARDS="${SHARDS:-5}"
SHARD_LIST="${SHARD_LIST:-0 1 2 3 4}"
PROFILE="${PROFILE:-full}"
CHECKPOINT="${CHECKPOINT:-results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt}"
MODEL_KIND="${MODEL_KIND:-exponential_residual_unet}"
OBJECT_NAMES="${OBJECT_NAMES:-stripe_target}"
STEPS_VALUES="${STEPS_VALUES:-31 32 33}"
LR_VALUES="${LR_VALUES:-0.00045 0.0005}"
BETA_VALUES="${BETA_VALUES:-0.55}"
XI_VALUES="${XI_VALUES:-0.5}"
X_STEP_VALUES="${X_STEP_VALUES:-0.13 0.14 0.15}"
CHANNELS_VALUES="${CHANNELS_VALUES:-24}"
BLOCKS_VALUES="${BLOCKS_VALUES:-3}"
RESIDUAL_SCALE_VALUES="${RESIDUAL_SCALE_VALUES:-0.06 0.08 0.10}"
DENOISER_VALUES="${DENOISER_VALUES:-nlm}"
DENOISE_KERNEL_VALUES="${DENOISE_KERNEL_VALUES:-3}"
NLM_H_VALUES="${NLM_H_VALUES:-0.060 0.062 0.064}"
NLM_PATCH_SIZE_VALUES="${NLM_PATCH_SIZE_VALUES:-5}"
NLM_PATCH_DISTANCE_VALUES="${NLM_PATCH_DISTANCE_VALUES:-6}"
BINARY_PRIOR_VALUES="${BINARY_PRIOR_VALUES:-0.005 0.010 0.015 0.020}"
FIXED_INIT_SEED="${FIXED_INIT_SEED:-20240709}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-21600}"
MAX_ZIP_MB="${MAX_ZIP_MB:-120}"
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
  local command_text="python run_stage4_ured_sweep.py --profile ${PROFILE} --checkpoint ${CHECKPOINT} --model-kind ${MODEL_KIND} --object-names ${OBJECT_NAMES} --config-shard ${shard_spec} --steps-values '${STEPS_VALUES}' --lr-values '${LR_VALUES}' --beta-values '${BETA_VALUES}' --xi-values '${XI_VALUES}' --x-step-values '${X_STEP_VALUES}' --channels-values '${CHANNELS_VALUES}' --blocks-values '${BLOCKS_VALUES}' --residual-scale-values '${RESIDUAL_SCALE_VALUES}' --denoiser-values '${DENOISER_VALUES}' --denoise-kernel-values '${DENOISE_KERNEL_VALUES}' --nlm-h-values '${NLM_H_VALUES}' --nlm-patch-size-values '${NLM_PATCH_SIZE_VALUES}' --nlm-patch-distance-values '${NLM_PATCH_DISTANCE_VALUES}' --binary-prior-values '${BINARY_PRIOR_VALUES}' --fixed-init-seed ${FIXED_INIT_SEED} --output-dir ${output_dir} --save-traces"

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
