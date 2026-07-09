# Findings

## Current Status

The repository now contains executable CUDA-verified smoke implementations for
both requested tasks:

- SCGI simulation, supervised correction, DGI reconstruction, and URED-style
  refinement.
- Basis/channel mechanism scans covering random, Hadamard, DCT, Fourier, and
  SRHT bases under multiplicative drift.

These findings are smoke-scale evidence, not final paper-scale claims.

## SCGI Reproduction

Experiment: Stage 0 smoke SCGI with synthetic objects, 32x32 pixels, 1024
patterns, 80 epochs.

Prediction: raw dynamic DGI should fail, SCGI should restore contrast, and
oracle/analytic correction should bound the attainable result.

Result: dynamic DGI CNR is 0.489, SCGI DGI CNR is 1.954, SCGI-URED CNR is 3.389,
and oracle CNR is 3.062. Corrected KS p-value is 0.064.

Supports/refutes: supports the core APL mechanism at smoke scale.

Notes: debug MNIST at 64x64 and 4096 patterns reaches SCGI-URED CNR 3.800
locally. A Colab L4 160-epoch debug run reaches SCGI CNR 2.147 and URED CNR
4.467 with validation SCGI KS pass rate 0.75. This is stronger than the local
80-epoch run but still below the strict prompt gates for raw SCGI CNR and
validation KS pass rate.

Colab full-profile probes: a 128x128, 16384-pattern, 20-epoch run completes on
L4 in 117 s, and a 100-epoch SCGI-only run completes in 456 s. The original
100-epoch gain U-Net had SCGI CNR 0.127. After widening the gain range, the same
full 100-epoch setup reaches SCGI CNR 1.171 and validation MSE 4.21e-4, a large
improvement but still below the analytic/static CNR 2.535 bound.

Gamma sweep: Colab debug 60-epoch sweep over gamma values `{0, 0.1, 1, 10}`
finds the best SCGI CNR at gamma=1.0 (2.242), but all four gamma settings fail
the strict KS gate.

Physics-informed model check: `exponential_residual_unet` adds an exponential
gain fit before a small residual U-Net. A smoke 2-epoch run reaches SCGI CNR
3.059, validation SCGI KS pass rate 1.0, and validation MSE 2.69e-6. A full
Colab 2-epoch run reaches SCGI CNR 2.535, validation SCGI KS pass rate 1.0, and
validation MSE 1.83e-8, matching the analytic exponential/static control.

## Stage 3 Held-Out Targets

Experiment: load the saved Stage 0 smoke checkpoint and test letter/stripe/ring
targets not used for training.

Prediction: dynamic DGI should fail; SCGI should improve over dynamic DGI; oracle
and analytic exponential correction should remain upper-bound controls.

Result: output written to `results/stage_3/smoke` and
`results/colab_imports/pro1_debug_e160_stage3/artifacts/stage_3_colab/debug`.
SCGI improves CNR over dynamic DGI for all four held-out objects. In the Colab
160-epoch checkpoint, CNRs are 8.54 for `letter_A`, 2.18 for `stripe_target`,
2.77 for `letter_L`, and 2.63 for `ring`.

Supports/refutes: supports directionality but not prompt-level Stage 3 thresholds.

Full-profile exp-residual Stage 3: using the Colab full checkpoint, SCGI matches
analytic/static CNR on all held-out targets (`letter_A` 3.3095, `letter_L`
3.5481, `ring` 2.9819, `stripe_target` 2.4919). The all-target CNR>=3 gate still
fails because the static upper bound is below 3 for `ring` and `stripe_target`;
the static PSNR>20 gate also fails because static DGI PSNR is only about 7.46-8.76
dB in this full held-out setup.

## Stage 1 Diagnostics

Experiment: standalone Stage 1 data-simulation diagnostics for three smoke
samples.

Prediction: static bucket measurements should be near Gaussian, dynamic
measurements should decay according to the lambda factors, and lambda draws
should fall inside the configured profile range.

Result: output written to `results/stage_1/smoke`. The three plotted samples
have static-bucket KS p-values of 1.0 and gain end values from 0.347 to 0.0288.

Supports/refutes: supports the Stage 1 simulator contract for smoke scale.

## M1 Oracle And AGC

Experiment: expanded compact M1 scan with random, Hadamard, DCT, Fourier, and
SRHT bases.

Prediction: oracle gain correction should restore deterministic bases; blind AGC
should depend strongly on whether the coefficient sequence supplies a stable
statistical anchor.

Result: oracle correction restores complete Hadamard/SRHT to near-exact
reconstruction. The protocol-statistics run writes 4200 oracle/AGC rows and
1750 AGC-window rows under `results/mechanism_m1_protocol_o10s5`.

Supports/refutes: supports H1 as a working hypothesis.

## M1 Pairwise Failure

Experiment: paired-basis jitter scan after fixing the jitter channel so
adjacent-frame mismatch is controlled by `rho`.

Prediction: pairwise normalization should approach oracle under slow drift and
degrade as `rho` and `sigma_a` increase.

Result: in the 10-object x 5-seed mechanism runs, SRHT pairwise is the best
blind method across the sampled M2 grid. Pairwise performance still degrades as
`rho` and `sigma_a` increase.

Supports/refutes: supports H3 in the compact setting.

## M1 Error Propagation

Experiment: residual gain error injection and log-log fit of relative MSE versus
residual gain amplitude.

Prediction: deterministic paired bases should show coherent error propagation;
random correlation reconstruction should show a different, more averaged error
profile.

Result: fit table written to
`results/mechanism_m1_protocol_o10s5/mechanism_m1_error_scaling_fit.csv`.
Hadamard and SRHT have slopes about 1.18 in this compact diagnostic.

Supports/refutes: partially supports H2, but the current protocol-statistics run
is still not a clean N-scaling law. It needs a dedicated N sweep before
publication use.

## M2 Phase Scan

Experiment: M2 scan with equal 2048 measurement-frame budgets plus explicit
reference-frame overhead accounting, using 10 objects x 5 seeds over the 7 x 5
rho/sigma grid.

Prediction: best blind method should depend on channel drift speed and amplitude.

Result: `results/phase_m2_reference_protocol_o10s5/phase_scan.csv` records
68,250 rows. The outputs separate `best_blind_methods.csv` from
`best_equal_frame_blind_methods.csv`, so extra-reference-frame methods are not
silently compared as if they used the same physical budget.

Follow-up dense Colab-sharded check:
`results/phase_m2_scgi_proxy_dense_r1_merged/phase_scan.csv` adds
`scgi_proxy`, a blind smooth-gain SCGI-style proxy. It contributes 10,500 dense
rows inside a 78,750-row merged scan, uses zero reference frames, and is kept
separate from claims about a trained SCGI network.

Supports/refutes: supports the current M2 compact conclusion that
`srht_paired + pairwise` is the best strict equal-frame blind method across all
35 sampled rho/sigma cells. `srht_paired + reference_k2` is the best
reference-calibrated method across all 35 cells but uses 3073 total physical
frames instead of 2048, so it should be reported as a separate semi-calibrated
baseline. Dense `scgi_proxy` improves over `none` in 88.6% and over AGC in
66.7% of matched basis/rho/sigma means, but it never beats pairwise on paired
bases and does not change the best 35-cell equal-frame map. Flip-boundary output
is now diagnostic rather than a fitted law: 104 rows are `not_reached`, 17
`left_censored`, and 14 `observed` in the reference protocol.

## Rendered Figures

Latest figure manifest: `E:/GAN_FCC_WORK/scgi-repro/results/figures/figure_manifest.csv`.

## M4 Theory Hooks

Experiment: dedicated compact M4 runner over image sizes 8/16/32, residual gain
amplitudes, fixed-32x32 random frame counts, and dense M2 flip-boundary outputs.

Prediction: residual gain reconstruction error should scale roughly
quadratically with residual gain amplitude; random bases should average residual
errors down as frame count increases; SRHT should spread coefficient energy
similarly to random bases.

Result: output written to `results/theory_m4_compact`. The residual-gain
`sigma_delta` exponent is 1.98-2.00 across bases with minimum R2 0.991. Fixed-P
random frame scaling gives `num_frames` exponents about -0.71/-0.72 for
random binary/uniform bases with R2 > 0.998. At 1024 pixels, DCT/Fourier/Hadamard
top-5% energy is 0.81-0.86, while random/SRHT is about 0.28.

Supports/refutes: supports H2/H4 as compact fitted-law evidence. It does not yet
complete the paper-grade theory requirement because flip-boundary fits are still
mostly censored or insufficiently sampled, and bootstrap uncertainty intervals
and nonideal calibration are still open.
