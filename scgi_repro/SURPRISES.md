# Surprises

Unexpected or hypothesis-challenging results should be logged here instead of
being silently discarded.

## 2026-07-08 Smoke Run

The first `smoke` run used only 2 SCGI epochs and the paper lambda range with
`N=1024`. Dynamic DGI did not visibly fail, because `0.9995^1024` is still a
moderate decay relative to the APL paper's `N=16384`, and the SCGI network
underfit. The smoke profile was adjusted to use 8 epochs and a stronger
lambda range (`0.996-0.999`) so the small test exercises the intended failure
mode. The full/debug profiles retain the paper lambda range.

## 2026-07-09 Stage 0 Gain-Control Check

The Stage 0 smoke failure is not an irreversible dynamic-channel failure.
Oracle correction with the simulator's known exponential factors restores the
sample-0 DGI CNR from dynamic `0.489` to `3.062`, matching static DGI. A blind
analytic fit of `log(bucket[n]) = c + n log(lambda)` estimates
`lambda=0.998824` versus the true `0.998828` and restores CNR to `3.059`.

The SCGI U-Net still removes the large monotone slope but does not preserve the
small per-pattern bucket fluctuations that DGI uses for contrast. In the smoke
run, SCGI bucket MSE versus static is much lower than raw dynamic MSE
(`0.0157` versus `0.147`), but still orders of magnitude above analytic
correction (`2.87e-6`) and oracle correction (`~1e-15`). This explains why the
SCGI output can look slope-corrected while its DGI CNR remains worse than
dynamic DGI.

Follow-up: this was mitigated by switching the smoke SCGI model from direct
bucket synthesis to `gain_unet`, where the network predicts a positive gain map
and returns normalized `R/gain`. That preserves the high-frequency bucket
fluctuations needed by DGI. The latest smoke run improves CNR from dynamic
`0.489` to SCGI `1.954`, and the residual URED version reaches `3.389`.

## 2026-07-09 DCT Pairwise Sensitivity

Using orthonormal DCT rows as physical modulation patterns made the DCT paired
experiment unfairly low contrast. This was changed to full-contrast cosine rows
with row-energy inverse reconstruction. After the fix, DCT round-trip error is
still below `1e-12`, and DCT pairwise follows the expected degradation with
`rho`, but it remains slightly below Hadamard/SRHT in the current protocol-scale
4x3 grid. Treat this as a prompt for denser flip-boundary tests, not as a final
conclusion.
