#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${ROOT:-$SCRIPT_DIR}"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="${COLAB:-/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab}"
REPO="${REPO:-https://github.com/ccyyyYyzz/GI_a1.git}"
REF="${REF:-scgi-ceiling-diagnostic-r1}"
COLAB_GPU="${COLAB_GPU:-L4}"

mkdir -p "$LOG_DIR"

launch_job() {
  local account_home="$1"
  local run_id="$2"
  local timeout_seconds="$3"
  local artifact_root="$4"
  local max_zip_mb="$5"
  local command_text="$6"
  local log_file="$LOG_DIR/${run_id}.log"
  local pid_file="$LOG_DIR/${run_id}.wslpid"

  rm -f "$log_file" "$pid_file"
  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --session "$run_id" --gpu "$COLAB_GPU" --timeout "$timeout_seconds" \
    "$RUNNER" \
    --repo "$REPO" \
    --ref "$REF" \
    --workdir scgi_repro \
    --run-id "$run_id" \
    --accelerator "$COLAB_GPU" \
    --install-requirements \
    --command "$command_text" \
    --artifact-root "$artifact_root" \
    --emit-zip \
    --max-zip-mb "$max_zip_mb" \
    > "$log_file" 2>&1 &
  echo "$!" > "$pid_file"
  echo "$run_id pid=$(cat "$pid_file") log=$log_file"
}

launch_job \
  "/var/tmp/codex-colab-accounts/pro1" \
  "pro1_stage0_debug_prompt_exact_colab_r1" \
  21600 \
  "results/stage_0/stage0_debug_prompt_exact_colab_r1" \
  160 \
  "python run_stage0.py --profile debug --epochs 10 --tag stage0_debug_prompt_exact_colab_r1 --checkpoint-every 1"

launch_job \
  "/var/tmp/codex-colab-accounts/pro2" \
  "pro2_stage1_full_diagnostics_colab_r1" \
  10800 \
  "results/stage_1_prompt_full_colab_r1" \
  80 \
  "python run_stage1_diagnostics.py --profile full --samples 10 --output-dir results/stage_1_prompt_full_colab_r1"
