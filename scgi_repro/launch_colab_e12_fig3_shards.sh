#!/usr/bin/env bash
# E12 uncertainty sweep: Fig3 gain-error at 20 seeds, split by rho across two Colab accounts.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR}"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="${COLAB:-/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab}"
REPO="${REPO:-https://github.com/ccyyyYyzz/GI_a1.git}"
REF="${REF:?pass the exact pushed commit SHA}"
COLAB_GPU="${COLAB_GPU:-L4}"
TIMEOUT="${TIMEOUT:-14400}"
mkdir -p "$LOG_DIR"
launch_job() {
  local account_home="$1"; local run_id="$2"; local rho="$3"; local tag="$4"
  local out_dir="results/paper_fig3_gain_error_e12_${tag}"
  local log_file="$LOG_DIR/${run_id}.log"; local pid_file="$LOG_DIR/${run_id}.wslpid"
  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --session "$run_id" --gpu "$COLAB_GPU" --timeout "$TIMEOUT" \
    "$RUNNER" --repo "$REPO" --ref "$REF" --workdir scgi_repro --run-id "$run_id" --accelerator "$COLAB_GPU" \
    --install-requirements \
    --command "python run_paper_fig3_gain_error.py --output-dir ${out_dir} --seeds 20 --rho ${rho}" \
    --artifact-root "$out_dir" --emit-zip --max-zip-mb 24 \
    > "$log_file" 2>&1 &
  echo "$!" > "$pid_file"
  echo "$run_id pid=$(cat "$pid_file") log=$log_file"
}
launch_job /var/tmp/codex-colab-accounts/pro1 "pro1_fig3_e12_seeds20_rho1e3_r1${RUN_ID_SUFFIX:-}" "0.001" "rho1e3"
launch_job /var/tmp/codex-colab-accounts/pro2 "pro2_fig3_e12_seeds20_rho1e2_r1${RUN_ID_SUFFIX:-}" "0.01" "rho1e2"
