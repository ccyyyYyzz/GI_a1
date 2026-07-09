#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="3113233d8bc238804f1b648b6ae021bb26b34867"

mkdir -p "$LOG_DIR"

launch_job() {
  local account_home="$1"
  local run_id="$2"
  local timeout_seconds="$3"
  local command_text="$4"
  local artifact_root="$5"

  local log_file="$LOG_DIR/${run_id}.log"
  local pid_file="$LOG_DIR/${run_id}.wslpid"
  rm -f "$log_file" "$pid_file"

  nohup env HOME="$account_home" "$COLAB" --auth oauth2 run --gpu L4 --timeout "$timeout_seconds" \
    "$RUNNER" \
    --repo "$REPO" \
    --ref "$REF" \
    --workdir scgi_repro \
    --run-id "$run_id" \
    --install-requirements \
    --command "$command_text" \
    --artifact-root "$artifact_root" \
    --emit-zip \
    --max-zip-mb 20 \
    > "$log_file" 2>&1 &
  echo "$!" > "$pid_file"
  echo "$run_id $!"
}

launch_job "/var/tmp/codex-colab-accounts/pro1" "pro1_debug_e160_stage3" 14400 \
  "python run_stage0.py --profile debug --epochs 160 --tag colab_debug_e160_ured && python run_stage3_tests.py --profile debug --checkpoint results/stage_0/colab_debug_e160_ured/model_checkpoint.pt --output-dir results/stage_3_colab" \
  "results"

launch_job "/var/tmp/codex-colab-accounts/pro2" "pro2_full_e20_probe" 10800 \
  "python run_stage0.py --profile full --epochs 20 --tag colab_full_e20_probe --skip-ured" \
  "results/stage_0/colab_full_e20_probe"

launch_job "/var/tmp/codex-colab-accounts/pro2" "pro2_gamma_debug_e60" 10800 \
  "python run_gamma_sweep.py --profile debug --epochs 60 --output results/stage_0/gamma_sweep_debug_e60_colab.csv" \
  "results/stage_0"
