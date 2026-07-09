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
ACCOUNT_HOME="${1:-/var/tmp/codex-colab-accounts/pro2}"

env HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 run --gpu "$COLAB_GPU" --timeout 14400 \
  "$RUNNER" \
  --repo "$REPO" \
  --ref "$REF" \
  --workdir scgi_repro \
  --run-id pro2_full_e100_skip_ured \
  --accelerator "$COLAB_GPU" \
  --cu-per-hour "$CU_PER_HOUR" \
  --persist-root "$PERSIST_ROOT" \
  --sync-seconds "$SYNC_SECONDS" \
  --install-requirements \
  --command "python run_stage0.py --profile full --epochs 100 --tag colab_full_e100_skip_ured --skip-ured" \
  --artifact-root "results/stage_0/colab_full_e100_skip_ured" \
  --emit-zip \
  --max-zip-mb 20
