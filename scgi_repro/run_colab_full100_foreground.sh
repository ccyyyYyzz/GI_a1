#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="${REF:-scgi-colab-20260709}"
ACCOUNT_HOME="${1:-/var/tmp/codex-colab-accounts/pro2}"

env HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 run --gpu L4 --timeout 14400 \
  "$RUNNER" \
  --repo "$REPO" \
  --ref "$REF" \
  --workdir scgi_repro \
  --run-id pro2_full_e100_skip_ured \
  --install-requirements \
  --command "python run_stage0.py --profile full --epochs 100 --tag colab_full_e100_skip_ured --skip-ured"
