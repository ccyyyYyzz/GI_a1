# Theory Notes

## Core Model

The time-varying multiplicative channel is

```text
R_n = a_n B_n
```

where `B_n = <I_n, T>` is the ideal single-pixel measurement and `a_n` is a
time-varying gain.

## H1: Identifiability

Blind gain correction needs a statistical anchor. For i.i.d. random patterns,
`B_n` is a sum of many weakly dependent pixel contributions. Under mild object
conditions the central-limit theorem makes the sequence approximately stationary
and near Gaussian. The unknown gain `a_n` then appears as a slow modulation of a
known-ish distribution.

For deterministic orthogonal bases, coefficients are object-dependent and
ordered. Low-frequency or low-sequency coefficients can be much larger than
others. The observed sequence `R_n` mixes object structure and gain drift, so a
blind estimator cannot distinguish "large coefficient" from "large gain".

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

- static/oracle: SRHT is close to Hadamard;
- fast blind drift: SRHT is close to random bases;
- residual artifacts are whitened compared with ordered Hadamard.

## Current Numerical Hooks

The compact M1 runner now emits two quantitative hooks for turning these notes
into a paper-ready theory section:

- `mechanism_m1_agc_window_sweep.csv` tests the gain-estimation variance versus
  AGC window length.
- `mechanism_m1_error_scaling_fit.csv` fits residual-gain error propagation.

These quick fits are diagnostics only. The required M4 version should rerun the
same measurements over a dedicated N sweep, attach uncertainty bars, and report
the flip-boundary law used by the M2 phase diagram.
