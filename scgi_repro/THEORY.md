# Theory Notes

## Core Model

The time-varying multiplicative channel is

```text
R_n = a_n B_n
```

where `B_n = <I_n, T>` is the ideal single-pixel measurement and `a_n` is a
time-varying gain.

## H1: Identifiability

Blind gain correction needs a statistical anchor. Under a time-varying
multiplicative channel `R_n = a_n B_n`, the reconstructable regime is set by
whether the unknown gain is identifiable from the observed bucket sequence.
Randomizing pattern structure supplies that anchor: i.i.d. random patterns do so
through central-limit-like stationary bucket statistics, while randomized
orthogonal patterns such as SRHT do so through sign and row-order randomization
while retaining an exact inverse under oracle/static calibration.

Ordered deterministic orthogonal bases can lose this anchor. Their coefficients
are object-dependent and ordered; low-frequency or low-sequency coefficients can
be much larger than others. The observed sequence `R_n` therefore mixes object
structure and gain drift, so a blind estimator can struggle to distinguish
"large coefficient" from "large gain". This is an identifiability/robustness
claim, not an absolute-quality claim: under the equal-frame correlation protocol, i.i.d.
random bases can be worst in absolute PSNR because they use DGI/correlation
reconstruction while orthogonal bases use exact inversion. The operative design
variable is sign/phase randomization that stabilizes coefficient statistics.

## H2: Error Propagation

For an orthogonal basis with ideal coefficients `c_k` and residual gain error
`delta_k`, inverse reconstruction contains terms proportional to

```text
sum_k delta_k c_k phi_k
```

so the MSE scales as `sum_k delta_k^2 c_k^2` when the basis is orthonormal.
There is no measurement averaging mechanism; errors in energetic coefficients
become structured artifacts.

For random correlation reconstruction, residual gain errors are mixed through
many independent speckles. The leading error contribution averages down with the
measurement count, giving an empirical law close to

```text
MSE_gain ∝ Var(delta) ||T||^2 / N
```

up to constants determined by pattern distribution and normalization.

## H3: Pairwise Normalization

Differential pairs `(1+P)/2` and `(1-P)/2` cancel a common gain when the channel is
effectively constant over the pair. If the per-frame drift rate
`rho = t_f / tau_c` is small, pairwise normalization approaches oracle correction.
When `rho` approaches `O(0.1-1)`, the two frames see different gains and the ratio
becomes biased. Additive noise is also amplified when the pair sum is small.

Implementation note: the compact `jitter` channel now makes adjacent-frame
mismatch scale with `rho`. Earlier versions imposed a fast-noise floor even at
small `rho`, which was not a valid H3 test.

Reference-frame calibration is a separate non-blind baseline. In the compact
simulator, `reference_kK` samples the multiplicative gain every `K` measurement
frames using a known fixed reference pattern and linearly interpolates the gain
for intervening object frames. Its expected error increases with drift speed and
with `K`, while its physical cost is an overhead of roughly `1/K` extra SLM
frames. M2 CSVs therefore track both measurement frames and total physical
frames.

### AGC Window Bias-Variance Sketch

For a blind local-mean AGC estimator, write the ideal bucket sequence as
`B_n = mu_B + eps_n`, with `E[eps_n]=0` and coefficient of variation
`CV_B = sigma_B / mu_B`. A centered window estimator has the approximate form

```text
ahat_n = mean_{j in W(n)} R_j / mu_B
       = mean_{j in W(n)} a_j (mu_B + eps_j) / mu_B.
```

The first-order stochastic term has variance roughly `a_n^2 CV_B^2 / W`.
The drift term is a local smoothing bias: for an OU-like gain, a useful
engineering approximation is

```text
E[(ahat_n/a_n - 1)^2] ~= C_v CV_B^2 / W + C_d sigma_a^2 (rho W)^nu,
```

where `nu` is between 1 and 2 depending on whether the window sees
non-differentiable OU increments or locally smooth drift. This gives the
candidate scaling

```text
W* ∝ (CV_B^2 / (sigma_a^2 rho^nu))^(1/(nu+1)).
```

The AGC-window sweeps should be interpreted as diagnostics of this tradeoff,
not as a confirmed law. The first paper-r2 grid had many best-window selections
on the sampled bounds and random/SRHT fits with only low-to-moderate R2. The
targeted follow-up in `results/theory_m4_agc_targeted_r1` widens and densifies
the window grid, but 42-56% of best-window cells still sit on a boundary and
the fitted R2 values remain 0.71-0.82. This supports the existence of a
bias-variance tension but not a publication-ready scaling law for the current
AGC estimator. The boundary-aware follow-up in
`results/theory_m4_agc_boundary_aware_r1` treats lower-grid selections as
upper-bounded optimum intervals rather than exact observations. It gives interval-satisfaction
fractions of 0.80 for random binary/uniform bases, 0.64 for SRHT, and 0.40 for
Hadamard using exact-point tolerance and bounded-point hinge inequalities, so
censoring helps interpret random-basis AGC but still argues for a diagnostic
rather than theorem-level claim.

## H4: Energy Concentration

Deterministic transform bases concentrate natural and digit-like objects in a
small number of low-order coefficients. Miscalibrating these coefficients has
large global cost. Random bases spread object energy across measurements, making
single-frame calibration errors less catastrophic.

## SRHT Design Rule

The subsampled randomized Hadamard transform uses `H D`, with `D` a fixed random
diagonal sign matrix. For a fixed object `T`, the diagonal randomization mixes
spatial signs before the deterministic Hadamard transform. The resulting
coefficient sequence is closer to a stationary random sequence while retaining a
fast exact inverse in the oracle/static limit.

The working prediction is:

- static/oracle: SRHT is close to Hadamard because both are exactly invertible;
- slow or moderate blind drift: randomization supplies a gain-identifiability
  anchor while preserving orthogonal inversion;
- fast blind drift: every blind basis can collapse to the reconstruction floor,
  so tiny PSNR deltas are floor coincidences unless at least one compared method
  is above-floor.

## Current Numerical Hooks

The compact M1 runner emits two quantitative hooks for turning these notes into
a paper-ready theory section:

- `mechanism_m1_agc_window_sweep.csv` tests the gain-estimation variance versus
  AGC window length.
- `mechanism_m1_error_scaling_fit.csv` fits residual-gain error propagation.

The dedicated M4 runner `run_theory_m4.py` now adds fitted-law outputs under
`results/theory_m4_compact`, `results/theory_m4_paper_r1`, and the current
high-rho rerun `results/theory_m4_paper_r2_highrho`:

- `m4_error_scaling_fit.csv` sweeps image sizes up to 64x64 in the paper-r2 run.
  The fitted residual-error exponent for `sigma_delta` is 2.001-2.003 across
  bases with minimum R2 0.99992; bootstrap intervals tightly bracket the
  expected quadratic dependence.
- `m4_random_frame_scaling_fit.csv` fixes the object size at 32x32 and varies
  random measurement frames. Random uniform/binary bases give
  `delta_rel_mse ~ sigma_delta^1.995 * num_frames^-0.71` with R2 > 0.998. This
  supports the random-basis averaging mechanism, though the exponent is a compact
  empirical fit rather than an asymptotic theorem.
- `m4_energy_concentration_summary.csv` measures H4 directly. At 4096 pixels,
  the top 5% of coefficients contain about 0.88-0.92 of DCT/Fourier/Hadamard
  energy, but only about 0.28 for random/SRHT bases; SRHT's effective-rank
  fraction is about 0.482, close to random bases.
- `m4_flip_boundary_fit.csv` fits observed, non-censored flip-boundary points,
  while `m4_flip_boundary_censored_intervals.csv` and summaries retain
  left-censored and not-reached cells instead of discarding them. In the high-rho
  r2 run, five observed fits are available; three have R2 >= 0.9
  (`reference_k32`, `reference_k8`, and `scgi_proxy` against `srht_paired`).
  This is a censored-aware accounting layer, not yet a full survival-style
  boundary estimator.
- `results/m2_boundary_audit_highrho` extends the M2 rho grid to the prompt
  upper range `rho=10` and recomputes log-rho interpolated boundaries under the
  `rel_mse<0.5` above-floor gate. Four observed boundary fits now have
  `R2 >= 0.9`; strict equal-frame winner cells are above-floor in 29/45 sampled
  rho/sigma cells and the remaining 16/45 cells are labelled sub-floor/noise
  floor rather than headline method wins.
- `m4_agc_window_law_fit.csv` logs empirical best-window scaling. The paper-r2
  random/SRHT fits have low-to-moderate R2 (`0.29-0.55`).
- `results/theory_m4_agc_targeted_r1` reruns the AGC validation with a denser
  window grid and 86,400 raw rows. Fits improve to R2 `0.71-0.82`, but
  best-window selections remain boundary-heavy (`boundary_frac = 0.42-0.56`).
  The candidate bias-variance law should therefore remain an explanatory sketch,
  not a claimed quantitative theorem.
- `results/theory_m4_agc_boundary_aware_r1` fits a censored hinge model to the
  targeted best-window table. It writes four basis-level fits and 180 interval
  rows; interval satisfaction is strongest for random binary/uniform bases
  (`0.80`), moderate for SRHT (`0.64`), and weak for Hadamard (`0.40`).

Remaining theory work before publication: redesign or further validate the AGC
estimator beyond the current censored diagnostic, convert the high-rho boundary
diagnostics into final vector figures, and connect the published figure-level
channel anchors to a hardware-calibrated nonideal model if raw detector/SLM logs
become available.
