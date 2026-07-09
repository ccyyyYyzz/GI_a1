#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="${REF:-scgi-colab-20260709}"
BATCH="${BATCH:-stage4_ured_sweep_$(date +%Y%m%d_%H%M%S)}"
SHARDS="${SHARDS:-5}"
SHARD_LIST="${SHARD_LIST:-0 1 2 3 4}"
PROFILE="${PROFILE:-full}"
CHECKPOINT="${CHECKPOINT:-results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt}"
MODEL_KIND="${MODEL_KIND:-exponential_residual_unet}"
OBJECT_NAMES="${OBJECT_NAMES:-stripe_target}"
STEPS_VALUES="${STEPS_VALUES:-300}"
LR_VALUES="${LR_VALUES:-0.001}"
BETA_VALUES="${BETA_VALUES:-0 0.05 0.10 0.25 0.50}"
XI_VALUES="${XI_VALUES:-0.25 0.50}"
X_STEP_VALUES="${X_STEP_VALUES:-0.25 0.50}"
CHANNELS_VALUES="${CHANNELS_VALUES:-24}"
BLOCKS_VALUES="${BLOCKS_VALUES:-3}"
RESIDUAL_SCALE_VALUES="${RESIDUAL_SCALE_VALUES:-0.1 0.3}"
DENOISER_VALUES="${DENOISER_VALUES:-avg_pool}"
DENOISE_KERNEL_VALUES="${DENOISE_KERNEL_VALUES:-3}"
NLM_H_VALUES="${NLM_H_VALUES:-0.08}"
FIXED_INIT_SEED="${FIXED_INIT_SEED:-20240709}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-21600}"
PRO1_HOME="${PRO1_HOME:-/var/tmp/codex-colab-accounts/pro1}"
PRO2_HOME="${PRO2_HOME:-/var/tmp/codex-colab-accounts/pro2}"
SHARD_0_HOME="${SHARD_0_HOME:-$PRO1_HOME}"
SHARD_1_HOME="${SHARD_1_HOME:-$PRO1_HOME}"
SHARD_2_HOME="${SHARD_2_HOME:-$PRO2_HOME}"
SHARD_3_HOME="${SHARD_3_HOME:-$PRO2_HOME}"
SHARD_4_HOME="${SHARD_4_HOME:-$PRO2_HOME}"
SHARD_0_LABEL="${SHARD_0_LABEL:-pro1}"
SHARD_1_LABEL="${SHARD_1_LABEL:-pro1}"
SHARD_2_LABEL="${SHARD_2_LABEL:-pro2}"
SHARD_3_LABEL="${SHARD_3_LABEL:-pro2}"
SHARD_4_LABEL="${SHARD_4_LABEL:-pro2}"

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
  local command_text="python run_stage4_ured_sweep.py --profile ${PROFILE} --checkpoint ${CHECKPOINT} --model-kind ${MODEL_KIND} --object-names ${OBJECT_NAMES} --config-shard ${shard_spec} --steps-values '${STEPS_VALUES}' --lr-values '${LR_VALUES}' --beta-values '${BETA_VALUES}' --xi-values '${XI_VALUES}' --x-step-values '${X_STEP_VALUES}' --channels-values '${CHANNELS_VALUES}' --blocks-values '${BLOCKS_VALUES}' --residual-scale-values '${RESIDUAL_SCALE_VALUES}' --denoiser-values '${DENOISER_VALUES}' --denoise-kernel-values '${DENOISE_KERNEL_VALUES}' --nlm-h-values '${NLM_H_VALUES}' --fixed-init-seed ${FIXED_INIT_SEED} --output-dir ${output_dir} --save-traces"

  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --gpu L4 --timeout "$TIMEOUT_SECONDS" \
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
    0)
      launch_shard "$SHARD_0_HOME" "$SHARD_0_LABEL" "$shard_index"
      ;;
    1)
      launch_shard "$SHARD_1_HOME" "$SHARD_1_LABEL" "$shard_index"
      ;;
    2)
      launch_shard "$SHARD_2_HOME" "$SHARD_2_LABEL" "$shard_index"
      ;;
    3)
      launch_shard "$SHARD_3_HOME" "$SHARD_3_LABEL" "$shard_index"
      ;;
    4)
      launch_shard "$SHARD_4_HOME" "$SHARD_4_LABEL" "$shard_index"
      ;;
    *)
      echo "Unsupported shard index: $shard_index" >&2
      exit 2
      ;;
  esac
  sleep 8
done
