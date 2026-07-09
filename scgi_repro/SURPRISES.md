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
pre-floor diagnostic best-map structure than expected. Under strict 2048-frame
blind comparison, `srht_paired + pairwise` is selected in all 35 rho/sigma
cells. Under any-budget reference-calibrated comparison,
`srht_paired + reference_k2` is selected in all 35 cells but spends 3073 total
physical frames.

This supports SRHT as the strongest compact construction in the current ideal
simulator, but it also supersedes the earlier random-versus-Hadamard shorthand:
the best blind method in this implementation is a randomized orthogonal paired
basis, not an i.i.d. random correlation basis.

The later high-rho and Hadamard-row-order audits add an important qualifier:
after applying a `rel_mse<0.5` above-floor gate, the prompt-range strict map has
29/45 above-floor cells. In the latest row-order audit, 28 of those cells select
`srht_paired + pairwise`, one selects `hadamard_random_paired + scgi_proxy`, and
16/45 cells are sub-floor. This does not weaken the above-floor winner result;
it prevents the fast/high-amplitude noise-floor cells from being misreported as
method wins.

## 2026-07-09 M3 Fast Drift Is A Reconstruction Floor

The M3 SRHT ablation did not fail in the expected way. The prompt asked for a
`>=3 dB` fast-drift SRHT advantage, but at `rho>=1` every blind variant has
`rel_mse` near 0.9 and PSNR around 10.8-11.0 dB. Tiny deltas in that region are
therefore floor coincidences, not evidence about row order or sign design.

The constructive signal lives at slow drift instead. Under AGC at `rho=0.001`,
full SRHT is +5.453 dB over ordered Hadamard, while row permutation alone,
diagonal signs alone, and sign-time interleaving each recover essentially the
same advantage. At `rho=0.1`, the AGC rows are already transitional/sub-floor by
the default gate (`rel_mse` about 0.57-0.67), so their sub-dB deltas should not
be reported as a robust effect. The design message is "randomize the coefficient
sequence to make gain identifiable while preserving exact inversion," not "SRHT
beats Hadamard by 3 dB in fast drift."

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

Follow-up stripe sweeps narrowed the failure mode. A 40-config avg-pool RED
screen tops out at final CNR `2.916` and target-aware trace CNR `3.831`, while
switching the denoiser to non-local means raises the same stripe target to final
CNR `5.131` and target-aware diagnostic trace CNR `8.913`. This is a large
implementation sensitivity, but not a solved reproduction: the trace peak uses
ground truth for diagnosis, and even that remains below the APL URED minimum
`10.43`.

The sweep runner also inherited the earlier sharding trap: filtering to only
`stripe_target` before drawing dynamic factors gave stripe the first lambda draw.
That is now fixed. In the repaired all-object NLM audit, fixed 200-step NLM RED
reaches final CNRs `8.453/6.033/10.270/7.842` for A/stripe/L/ring. The
all-target minimum is still below 10.43. The gap is therefore not merely an
average-pool denoiser failure; stopping, regularization, and NLM fidelity remain
unresolved.

Target-free proxy traces make this sharper rather than solving it. In
`results/stage4_ured_proxy_audit_r1`, the best simple proxy rule
(`max_proxy_min`) lifts the selected all-object minimum to `6.210`, but still
has max regret `12.766` versus ground-truth trace peaks. Loss minimization is a
poor stop signal (`min=2.858`). The surprising part is that a visible proxy
correlation exists, especially for `proxy_min`, but it is not yet reliable
enough to claim a method.

## 2026-07-09 Soft-Otsu Success Is Not The NLM Basin

The modified soft-Otsu RED path clears the APL URED CNR gate on all four
continuous outputs, but a matched NLM-only control does not. The isolated
NLM-only trace audit leaves `stripe_target` below threshold with best historical
trace CNR `9.670`; rerunning the same 15-step, low-residual, five-seed basin
with `denoiser=nlm` reaches only `7.337/7.677` final/trace CNR on stripe.
Therefore the pass should be reported as a modified soft-Otsu regularizer, not
as closure of the original NLM-only URED reproduction.

## 2026-07-09 Published Curves Are Gentler Than The Prompt Prior

Figure-level APL digitization gives collected-trace
`lambda_per_measurement = 0.999897-0.999921`, which is much closer to unity than
the lower end of the prompt simulator range. The corrected traces are visually
stable by centerline standard deviation, but their band-width proxy is still
about 0.104. This suggests the paper-level CNR gap is not solved by simply
making the exponential decay stronger; ROI definition, denoiser architecture,
and reconstruction details matter.

## 2026-07-09 Static DGI PSNR Gate Is Not A Display Bug

The full Stage 3 static DGI audit added MNIST held-out targets and compared raw,
minmax, scale-aligned, and affine-aligned reconstructions. Even the best
affine-aligned static DGI PSNR is only `15.92` dB, below the prompt's 20 dB
sanity gate. Static CNR reaches `3.55`, so the random-DGI reconstruction is
usable for APL-style contrast analysis, but pixelwise PSNR is a poor acceptance
gate for these noisy random-basis DGI images.

A separate full paired-Hadamard exact inverse ceiling reaches `80.00` dB minimum
PSNR on the same targets. That means the objects and dimensionality are not the
blocker; the PSNR gap is specific to random-DGI correlation noise and should not
be counted as an APL random-DGI protocol pass.
