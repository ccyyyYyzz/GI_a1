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

Static DGI upper-bound audit:
`results/stage3_static_dgi_audit` adds four MNIST held-out targets and recomputes
random static DGI metrics with raw/minmax display and scale/affine post-hoc
alignment. The best affine-aligned random static DGI PSNR is 15.92 dB and the
mean is 14.01 dB, still below the 20 dB gate. The best random static CNR is
3.55. A separate full paired-Hadamard exact inverse sanity row reaches 80.00 dB
minimum PSNR, proving the targets are reconstructable and narrowing the failure
to random-DGI correlation noise rather than display scale, offset, or object
dimensionality.

Full-profile threshold matrix: `results/stage3_threshold_matrix_full_r2_authoritative`
adds 500-step SCGI-UNN and SCGI-URED for all four full held-out targets using the
returned exp-residual checkpoint. Mean/min CNRs are SCGI 3.083/2.492, SCGI-UNN
2.446/2.254, and SCGI-URED 5.084/2.270. URED is consistently above UNN, but the
compact URED proxy still fails APL minima: SCGI 3.39, UNN 7.93, and URED 10.43.

Stage 4 stripe-target sweeps:
`results/stage4_ured_sweep_r2_stripe_merged` shows a 40-config avg-pool
RED/UNN screen cannot rescue the binding stripe target: best final CNR is 2.916
and best target-aware trace CNR is 3.831. `results/stage4_ured_sweep_nlm_r1_stripe`
then replaces the fallback denoiser with non-local means and improves stripe to
final CNR 5.131 and best target-aware diagnostic trace CNR 8.913 in a
single-object screen. The runner was then fixed so object filtering no longer
changes each object's dynamic lambda draw, and
`results/stage4_ured_sweep_nlm_allobjects_r1` reruns the best NLM candidates on
all four objects. The better fixed 200-step NLM configuration has final CNRs
`8.453`, `6.033`, `10.270`, and `7.842`, with target-aware diagnostic trace
CNRs `13.210`, `8.185`, `19.904`, and `14.300`. This supports denoiser fidelity,
regularization, and stopping as candidate bottlenecks, but it still refutes a
paper-threshold reproduction claim for APL URED 10.43.
`results/stage4_ured_sweep_nlm_deeper_r1_stripe` tests 18 deeper 400-step stripe
configs around the best region and does not improve the target-aware peak
(`best_trace_cnr=8.520`). `results/stage4_ured_sweep_nlm_earlystop_r1_stripe`
then converts the observed early peak into a fixed-step sweep; the best
deployable stripe final CNR improves to `8.932` at 40 steps and `nlm_h=0.06`,
but remains below the APL URED minimum. `results/stage4_trace_audit_r1` records
the combined final-vs-trace audit across these sweeps.

Stage 4 target-free proxy audit:
`results/stage4_ured_proxy_audit_r1` adds per-step `proxy_*` traces for losses,
denoiser residual, TV/roughness, Otsu, entropy, and image range statistics. The
best simple target-free rule by all-object minimum is `max_proxy_min`, with
selected CNR mean/min `9.971/6.210`, but it still misses target-aware trace peaks
by mean/max regret `3.748/12.766`. Loss-based stopping is not viable here:
`min_loss` selects mean/min CNR `4.015/2.858`. No tested proxy is a validated
deployable stopping rule.

Published calibration: `results/published_calibration` encodes the APL Fig. 6
and Fig. 9 CNR targets plus OE PSNR/SSIM target values. Current APL comparison
has 16 rows and all are below the relevant published minima.

Published channel anchors: `results/published_channel_calibration` digitizes APL
Fig. 5/Fig. 7 intensity traces and compacts OE attenuation/distance curves into
machine-readable priors. APL collected traces fit
`lambda_per_measurement = 0.999897-0.999921`; corrected traces have mean
centerline standard deviation 0.0126 and mean visual band sigma proxy 0.104.
OE Fig. 6 fixed-reference PSNR crosses 30 dB near
`beta = 1.90 x 10^-2 mm^-1`, while no-reference PSNR stays below 30 dB.

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
reference-frame overhead accounting, using 10 objects x 5 seeds. The original
dense scan used a 7 x 5 rho/sigma grid; the high-rho extension expands this to
the prompt-range 9 x 5 grid with `rho = 0.001..10`.

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

High-rho prompt-range check:
`results/phase_m2_scgi_proxy_dense_r1_highrho_merged/phase_scan.csv` merges the
7-rho dense `scgi_proxy` scan with five monitored local high-rho shards for
`rho=3,10`. The merged table has 101,250 rows and covers all 45 prompt-range
rho/sigma cells. `results/m2_boundary_audit_highrho` adds log-rho interpolated
flip-boundary fits; five observed fits reach `R2 >= 0.9`, including
`scgi_proxy/srht_paired` vs Hadamard with `R2=0.9889`. It also writes
`m2_psnr_rho_curves_sigma_0p30.png` and `m2_boundary_fit_curves.png`.

Frozen-network smoke check:
`results/phase_m2_scgi_frozen_smoke/phase_scan.csv` adds `scgi_frozen`, which
loads the returned SCGI checkpoint and applies the frozen network to M2
measurement sequences with square-padding/cropping. The smoke run has 1785 rows,
including 210 `scgi_frozen` rows. Mean equal-frame blind PSNR is 12.75 dB for
`scgi_frozen`, below `none` at 16.87 dB, `scgi_proxy` at 17.94 dB, and
`pairwise` at 22.25 dB.

Dense frozen-network check:
`results/phase_m2_scgi_frozen_dense_r1_merged/phase_scan.csv` has 89,250 rows,
all five shard labels, and 10,500 `scgi_frozen` rows. The 35-cell strict
equal-frame best map is unchanged: `srht_paired + pairwise` wins in 35/35
rho/sigma cells. Mean equal-frame blind PSNR is 16.64 dB for `scgi_frozen`,
16.64 dB for `none`, 17.40 dB for `scgi_proxy`, and 21.43 dB for `pairwise`.
`scgi_frozen` beats `none` in 60.3% of matched comparisons but by only
+0.0047 dB on average, beats `scgi_proxy` in 18.8%, and beats pairwise on paired
bases in 6.5%.

Frozen high-rho prompt-range completion:
`results/phase_m2_scgi_frozen_dense_r1_highrho_merged/phase_scan.csv` adds five
local `rho=3,10` shards to the dense frozen baseline. The merged table has
114,750 rows, covers all 45 rho/sigma cells from `0.001..10`, and contains
13,500 `scgi_frozen` rows. `results/m2_boundary_audit_frozen_highrho` again
selects `srht_paired + pairwise` as the strict equal-frame non-oracle winner in
45/45 cells. Across matched rows, direct frozen transfer is still not
competitive: `scgi_frozen` averages -0.206 dB versus `none`, -0.796 dB versus
`scgi_proxy`, and -1.167 dB versus paired-basis `pairwise`.

Fine-tuned SCGI-network smoke:
`run_m2_scgi_train.py` trains a supervised M2-specific corrector on simulated
observed/ideal frame sequences, and `run_phase_m2.py` now supports checkpoint
metadata plus a basis-name checkpoint map. A direct-output U-Net smoke is
strongly negative: mean `scgi_frozen` PSNR is 11.08 dB, or -6.99 dB versus
raw `none`. A single `gain_unet` checkpoint is less destructive but still weak:
14.71 dB mean and -3.37 dB versus `none`. The basis-specific `gain_unet` smoke
shows local signal on a held-out rho/sigma/object grid, where
`srht_paired + scgi_frozen` wins 2/6 strict equal-frame cells at `rho=0.3`.
Overall, however, it remains below non-network baselines on matched rows:
-0.90 dB versus `none`, -1.69 dB versus `scgi_proxy`, and -2.48 dB versus
paired-basis `pairwise`.

Gain-prediction SCGI smoke:
`src/scgi_model.py` now includes signed-safe SCGI outputs and a
`gain_predictor_unet` that predicts positive multiplicative gains. The
checkpoint metadata path applies these models as `observed / gain_hat` rather
than clamped corrected measurements. This removes the most obvious output-range
mismatch, but it does not make the network competitive. On the same held-out
grid, row-max-normalized gain targets give mean `scgi_frozen` PSNR 12.04 dB
(-3.27 dB versus `none`), and raw gain targets give 12.05 dB (-3.26 dB versus
`none`, -3.85 dB versus `scgi_proxy`, and -6.19 dB versus paired `pairwise`).

Supports/refutes: supports the current M2 compact conclusion that
`srht_paired + pairwise` is the best strict equal-frame blind method across all
45 sampled prompt-range rho/sigma cells. `srht_paired + reference_k2` is the best
reference-calibrated method in 43/45 cells but uses 3073 total physical
frames instead of 2048, so it should be reported as a separate semi-calibrated
baseline. Dense `scgi_proxy` improves over `none` in 88.6% and over AGC in
66.7% of matched basis/rho/sigma means, but it never beats pairwise on paired
bases and does not change the best equal-frame map. The high-rho boundary audit
now provides R2-qualified flip-boundary fits, but the frozen-network results
and fine-tuned smoke results show that the current network paths are real but
weak baselines, not yet a competitive basis-aware SCGI phase diagram. The gain
predictor result specifically suggests that the next bottleneck is not only the
output clamp, but the input representation's inability to separate object
coefficient envelope from channel gain.

## Rendered Figures

Latest figure manifest: `E:/GAN_FCC_WORK/scgi-repro/results/figures/figure_manifest.csv`.

Latest paper-facing M2/M4 figure manifest:
`results/paper_figures_r1/paper_figure_manifest.csv`. This includes strict
equal-frame and all-non-oracle M2 winner maps over `rho=0.001..10`, the observed
M2 boundary-fit table, residual-gain scaling fit table, random-frame scaling
curve and fit table, top-5% coefficient-energy curve, and AGC window-law table.
Each manifest row now has a `vector_svg` sidecar, and
`paper_figure_manifest_vectors.csv` lists the 11 SVG assets directly.

## M4 Theory Hooks

Experiment: dedicated M4 runner over image sizes 16/32/64, residual gain
amplitudes, fixed-32x32 random frame counts, dense M2 flip-boundary outputs, AGC
window fractions, and bootstrap uncertainty intervals.

Prediction: residual gain reconstruction error should scale roughly
quadratically with residual gain amplitude; random bases should average residual
errors down as frame count increases; SRHT should spread coefficient energy
similarly to random bases.

Result: compact output is written to `results/theory_m4_compact`; paper-r1
output is written to `results/theory_m4_paper_r1`; high-rho paper-r2 output is
written to `results/theory_m4_paper_r2_highrho` using the prompt-range frozen
M2 phase table. The residual-gain
`sigma_delta` exponent is 2.001-2.003 across bases with minimum R2 0.99992.
Fixed-P random frame scaling gives `num_frames` exponents about -0.71/-0.72 for
random binary/uniform bases with R2 > 0.998 and bootstrap intervals excluding
zero. At 4096 pixels, DCT/Fourier/Hadamard top-5% energy is 0.88-0.92, while
random/SRHT is about 0.28. Censored flip-boundary tables now retain
left-censored and not-reached cells. The separate high-rho M2 boundary audit
extends rho coverage to 10 and yields five boundary fits with `R2 >= 0.9`.
AGC best-window fits are present but weak for random/SRHT bases (`R2=0.29-0.55`).
The targeted AGC rerun in `results/theory_m4_agc_targeted_r1` expands the window
grid to 86,400 raw rows and improves fit R2 to 0.71-0.82, but 42-56% of
best-window cells still select a grid boundary. The boundary-aware rerun in
`results/theory_m4_agc_boundary_aware_r1` treats those boundary hits as
upper-bounded intervals and reaches interval satisfaction 0.80 for random
binary/uniform, 0.64 for SRHT, and 0.40 for Hadamard. The AGC law is therefore
diagnostic rather than final. `results/paper_figures_r1` now renders the M2/M4
paper-facing figure draft set from these CSVs with PNG previews and SVG vector
sidecars. `THEORY.md` contains a candidate AGC bias-variance law and
`PAPER_OUTLINE.md` contains draft captions for the eight main figures.

Supports/refutes: strongly supports H2/H4 fitted-law evidence and moves M4
toward paper-grade closure. The targeted AGC sweep is now complete and shows the
simple window law is still too boundary-sensitive for a final quantitative
claim; the censored model is a useful interpretation layer but not a replacement
for a stronger AGC estimator. M4 remains short of full publication closure
because the current paper figures are individual SVG sidecars rather than final
venue-formatted multi-panel layouts, and the figure-level published-channel
priors still need to be tied to a hardware-calibrated nonideal model.

## Nonideal Digital Twin

Experiment: M2 ideal/nonideal comparison with SLM quantization, finite contrast,
detector noise, reference-sample noise, and frame timing jitter. The compact
smoke run covers random uniform, Hadamard-paired, and SRHT-paired bases. The
full run covers the dense 7-rho x 5-sigma grid, 10 objects, 5 seeds, and the
same basis/correction family as the dense M2 scan.

Prediction: if the SRHT/pairwise conclusion is not only an artifact of perfect
patterns and noiseless reference samples, the equal-frame winner should remain
stable under moderate SLM quantization, finite contrast, detector noise,
reference-sample noise, and frame timing jitter.

Result: compact output is written to `results/nonideal_m2_compact`; full output
is written to `results/nonideal_m2_full_r1_merged`. The full merged scan has
157,500 rows, split evenly between ideal and nonideal conditions, with all five
Colab shard labels present. The equal-frame winner is pairwise in all 35
rho/sigma cells for both ideal and nonideal conditions. The winning equal-frame
basis shifts from 16 Hadamard / 19 SRHT cells under ideal conditions to 23
Hadamard / 12 SRHT cells under nonideal conditions. Oracle mean PSNR falls from
65.36 dB to 28.35 dB, confirming that the nonideal perturbations are active.
Pairwise mean PSNR drops only 0.17 dB. Under nonideal matched comparisons,
`scgi_proxy` improves over `none` in 83.6% of cases and over AGC in 65.8%, but
beats pairwise on paired bases only 7.6% of the time.

Supports/refutes: supports the robustness direction at full scan scale and
satisfies the uncalibrated full nonideal main-scan requirement. It still does
not satisfy hardware-level calibration because the perturbation parameters are
normalized placeholders. Published APL/OE figure-level anchors now exist under
`results/published_channel_calibration`, but raw hardware measurements are not
available from the papers.
