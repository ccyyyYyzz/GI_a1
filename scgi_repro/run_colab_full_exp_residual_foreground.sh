#!/usr/bin/env bash
set -euo pipefail

ROOT="/mnt/e/GAN_FCC_WORK/scgi-repro"
RUNNER="$ROOT/colab/colab_github_job_runner.py"
COLAB="/var/tmp/codex-colab-tools/colab-cli-venv/bin/colab"
REPO="https://github.com/ccyyyYyzz/GI_a1.git"
REF="${REF:-scgi-colab-20260709}"
COLAB_GPU="${COLAB_GPU:-L4}"
CU_PER_HOUR="${CU_PER_HOUR:-0}"
ACCOUNT_HOME="${1:-/var/tmp/codex-colab-accounts/pro2}"
EPOCHS="${2:-2}"
TAG="colab_full_exp_residual_e${EPOCHS}_skip_ured"

env HOME="$ACCOUNT_HOME" "$COLAB" --auth oauth2 run --gpu "$COLAB_GPU" --timeout 14400 \
  "$RUNNER" \
  --repo "$REPO" \
  --ref "$REF" \
  --workdir scgi_repro \
  --run-id "$TAG" \
  --accelerator "$COLAB_GPU" \
  --cu-per-hour "$CU_PER_HOUR" \
  --install-requirements \
  --command "python run_stage0.py --profile full --epochs ${EPOCHS} --tag ${TAG} --model-kind exponential_residual_unet --skip-ured" \
  --artifact-root "results/stage_0/${TAG}" \
  --emit-zip \
  --max-zip-mb 20
