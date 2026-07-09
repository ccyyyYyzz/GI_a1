#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
LOG_DIR="$ROOT/results/colab_runs"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="3113233d8bc238804f1b648b6ae021bb26b34867"
RUN_ID="${1:-pro1_gamma_debug_e60}"
ACCOUNT_HOME="${2:-/var/tmp/codex-colab-accounts/pro1}"

mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR/${RUN_ID}.log" "$LOG_DIR/${RUN_ID}.wslpid"

nohup env HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 run --gpu L4 --timeout 10800 \
  "$RUNNER" \
  --repo "$REPO" \
  --ref "$REF" \
  --workdir scgi_repro \
  --run-id "$RUN_ID" \
  --install-requirements \
  --command "python run_gamma_sweep.py --profile debug --epochs 60 --output results/stage_0/gamma_sweep_debug_e60_colab.csv" \
  --artifact-root results/stage_0 \
  --emit-zip \
  --max-zip-mb 20 \
  > "$LOG_DIR/${RUN_ID}.log" 2>&1 &

echo "$!" > "$LOG_DIR/${RUN_ID}.wslpid"
echo "$RUN_ID $!"
