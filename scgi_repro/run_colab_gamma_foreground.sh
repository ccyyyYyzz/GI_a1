#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="${REF:-scgi-colab-20260709}"
COLAB_GPU="${COLAB_GPU:-L4}"
CU_PER_HOUR="${CU_PER_HOUR:-0}"
PERSIST_ROOT="${PERSIST_ROOT:-}"
SYNC_SECONDS="${SYNC_SECONDS:-300}"
ACCOUNT_HOME="${1:-/var/tmp/codex-colab-accounts/pro1}"

COMMAND='python run_gamma_sweep.py --profile debug --epochs 60 --output results/stage_0/gamma_sweep_debug_e60_colab.csv && echo GAMMA_CSV_BEGIN && cat results/stage_0/gamma_sweep_debug_e60_colab.csv && echo GAMMA_CSV_END'

env HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 run --gpu "$COLAB_GPU" --timeout 10800 \
  "$RUNNER" \
  --repo "$REPO" \
  --ref "$REF" \
  --workdir scgi_repro \
  --run-id pro1_gamma_debug_e60_foreground \
  --accelerator "$COLAB_GPU" \
  --cu-per-hour "$CU_PER_HOUR" \
  --persist-root "$PERSIST_ROOT" \
  --sync-seconds "$SYNC_SECONDS" \
  --install-requirements \
  --command "$COMMAND"
