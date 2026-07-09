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
BATCH="${BATCH:-nonideal_m2_full_$(date +%Y%m%d_%H%M%S)}"
SHARDS="${SHARDS:-5}"
SHARD_LIST="${SHARD_LIST:-0 1 2 3 4}"
OBJECTS="${OBJECTS:-10}"
SEEDS="${SEEDS:-5}"
PROFILE="${PROFILE:-debug}"
RHO_VALUES="${RHO_VALUES:-0.001 0.003 0.01 0.03 0.1 0.3 1.0}"
SIGMA_VALUES="${SIGMA_VALUES:-0.05 0.10 0.15 0.30 0.50}"
BASES="${BASES:-random_uniform random_binary hadamard_paired dct_paired fourier_fourstep srht_paired}"
CORRECTIONS="${CORRECTIONS:-none oracle agc scgi_proxy reference_k2 reference_k8 reference_k32}"

mkdir -p "$LOG_DIR"

launch_shard() {
  local account_home="$1"
  local account_label="$2"
  local shard_index="$3"
  local shard_spec="${shard_index}/${SHARDS}"
  local run_id="${account_label}_${BATCH}_shard${shard_index}of${SHARDS}"
  local output_dir="results/nonideal_m2_${BATCH}_shard${shard_index}of${SHARDS}"
  local log_file="$LOG_DIR/${run_id}.log"
  local pid_file="$LOG_DIR/${run_id}.wslpid"
  local command_text="python run_nonideal_m2.py --profile ${PROFILE} --objects ${OBJECTS} --seeds ${SEEDS} --rho '${RHO_VALUES}' --sigma-a '${SIGMA_VALUES}' --bases '${BASES}' --corrections '${CORRECTIONS}' --shard ${shard_spec} --resume --output-dir ${output_dir}"

  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --gpu "$COLAB_GPU" --timeout 14400 \
    "$RUNNER" \
    --repo "$REPO" \
    --ref "$REF" \
    --workdir scgi_repro \
    --run-id "$run_id" \
    --accelerator "$COLAB_GPU" \
    --cu-per-hour "$CU_PER_HOUR" \
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
