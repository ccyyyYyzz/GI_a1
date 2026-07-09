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

## 2026-07-09 Full-Scale SCGI Undertraining

Colab L4 successfully ran the requested full profile at 128x128 and N=16384 for
both 20 and 100 SCGI epochs. The 100-epoch run did not improve the full-profile
SCGI result: SCGI CNR stayed near `0.127`, validation SCGI KS pass rate was only
`0.176`, and the corrected slope remained strongly negative.

This changes the diagnosis from "need more runtime" to "need a redesigned
full-scale training/data-scaling setup." The analytic and oracle controls still
recover the static distribution, so the channel is not unrecoverable; the current
learned full-profile correction is the failing component.

## 2026-07-09 Dense M2 SRHT Dominance

The dense M2 reference protocol over 10 objects x 5 seeds produced a cleaner
winner structure than expected. Under strict 2048-frame blind comparison,
`srht_paired + pairwise` wins all 35 rho/sigma cells. Under any-budget
reference-calibrated comparison, `srht_paired + reference_k2` wins all 35 cells
but spends 3073 total physical frames.

This supports SRHT as the strongest compact construction in the current ideal
simulator, but it also means the original "random bases can blind-correct while
Hadamard cannot" story needs sharper wording: the best blind method in this
implementation is a randomized orthogonal paired basis, not an i.i.d. random
correlation basis.

## 2026-07-09 AGC Window Law Is Weakly Parametric

The paper-r1 M4 run added an empirical best-window AGC law over rho, sigma, and
window fractions. The output is useful as a diagnostic table, but the fitted
power law is weak for the bases where it matters most: random binary has
R2 about 0.55, random uniform about 0.44, and SRHT about 0.29.

This means the AGC bias-variance behavior is not captured well by a simple
`best_window ~ rho^a sigma_a^b` fit on the current grid. Treat AGC window
selection as a protocol parameter or derive a richer bias-variance model before
using it as a theoretical claim.

## 2026-07-09 Full URED Proxy Is Not Paper URED

The authoritative full Stage 3 threshold matrix now runs SCGI, SCGI-UNN, and
SCGI-URED on all four held-out targets with the returned exp-residual checkpoint.
The result is a useful negative control: SCGI has mean/min CNR `3.083/2.492`,
SCGI-UNN has `2.446/2.254`, and SCGI-URED has `5.084/2.270`. URED is above UNN
for every target, but it is far below the APL URED minimum of `10.43` and does
not rescue the stripe target.

One implementation trap also surfaced: sharding Stage 3 objects before drawing
dynamic factors makes every shard reuse the first lambda draw. `run_stage3_tests.py`
now draws the full object set first and only then filters the shard, so sharded
and non-sharded runs share the same per-object dynamic factors.
