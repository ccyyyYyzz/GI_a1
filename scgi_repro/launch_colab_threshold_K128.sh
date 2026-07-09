#!/usr/bin/env bash
# Extended tall-design threshold scan: K=128, 30 seeds, two Colab shards.
# REF is taken from the current HEAD (must be pushed).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR}"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="${COLAB:-/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab}"
REPO="${REPO:-https://github.com/ccyyyYyzz/GI_a1.git}"
REF="$(git -C "$ROOT" rev-parse HEAD)"
COLAB_GPU="${COLAB_GPU:-L4}"
TIMEOUT="${TIMEOUT:-14400}"
mkdir -p "$LOG_DIR"
echo "using REF=$REF"

launch_job() {
  local account_home="$1"; local run_id="$2"; local shard_spec="$3"
  local tag="${shard_spec/\//of}"
  local out_dir="results/tall_design_threshold_K128_${tag}"
  local log_file="$LOG_DIR/${run_id}.log"; local pid_file="$LOG_DIR/${run_id}.wslpid"
  : > "$log_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --session "$run_id" --gpu "$COLAB_GPU" --timeout "$TIMEOUT" \
    "$RUNNER" --repo "$REPO" --ref "$REF" --workdir scgi_repro --run-id "$run_id" --accelerator "$COLAB_GPU" \
    --install-requirements \
    --command "python run_tall_design_threshold.py --output-dir ${out_dir} --K 128 --seeds 30 --shard ${shard_spec}" \
    --artifact-root "$out_dir" --emit-zip --max-zip-mb 24 \
    > "$log_file" 2>&1 &
  echo "$!" > "$pid_file"
  echo "$run_id pid=$(cat "$pid_file") log=$log_file"
}

launch_job /var/tmp/codex-colab-accounts/pro1 "pro1_threshold_K128_seeds30_shard0of2_r1${RUN_ID_SUFFIX:-}" "0/2"
launch_job /var/tmp/codex-colab-accounts/pro2 "pro2_threshold_K128_seeds30_shard1of2_r1${RUN_ID_SUFFIX:-}" "1/2"
