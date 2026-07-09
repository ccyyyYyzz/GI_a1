# Paper Outline

## Working Title

Measurement-Basis Identifiability In Time-Varying Multiplicative Single-Pixel
Channels

## Contribution Claims

1. We establish an identifiability view of blind gain correction in single-pixel
   imaging through time-varying multiplicative channels.
2. We derive complementary error-propagation laws for deterministic orthogonal
   bases and i.i.d. random bases.
3. We map the regime where pairwise normalization is sufficient and where blind
   statistical correction is preferable.
4. We propose SRHT as a constructive design rule combining orthogonal inversion
   with randomized coefficient statistics.

## Main Figures

1. Model and identifiability diagram.
2. Oracle gain correction across random, Hadamard, and SRHT bases.
3. Blind gain estimation error versus window size and basis.
4. Error-propagation scaling laws.
5. Pairwise normalization failure curve versus drift rate and noise.
6. Reference-frame calibration tradeoff: correction quality versus extra SLM
   frame overhead (`reference_k2/k8/k32`).
7. Phase diagram over drift rate and gain amplitude, with separate
   any-budget, equal-total-frame, and reference-only best-method maps.
8. SRHT ablation: none / permutation / diagonal signs / both.

## Current Evidence And Gaps

- The current SCGI reproduction is strongest at smoke/debug scale. Full
  APL-scale Colab runs at 20 and 100 epochs complete but do not converge, so the
  SCGI reproduction should be presented as an executable diagnostic prototype
  until the full training setup is redesigned.
- The dense M2 reference scan supports `srht_paired + pairwise` as the strict
  equal-frame blind winner across the current 35-cell grid. This is useful
  evidence for the SRHT design rule, but it is still idealized.
- The dense `scgi_proxy` scan shows that a blind smooth-gain proxy improves over
  raw/AGC baselines without reference frames, but it does not displace SRHT
  pairwise as the equal-frame winner and should not be described as a trained
  SCGI-network result.
- The M2 dense reference scan idealizes reference measurements as noiseless gain
  samples; a non-ideal detector/reference-noise section is still needed.
- Flip boundaries are discrete sampled diagnostics, not yet fitted theory curves
  with uncertainty, although `run_theory_m4.py` now provides observed-only
  compact fits as a starting point.
- M4 compact theory hooks support quadratic residual-gain scaling and
  random/SRHT coefficient spreading, but the publication version still needs a
  larger N sweep, bootstrap confidence intervals, AGC window law, and censored
  flip-boundary treatment.
- A true pretrained/frozen SCGI-network correction is not yet part of the M2
  phase diagram.

## Venue Positioning

Primary: Physical Review A or IEEE Transactions on Computational Imaging.
Alternates: JOSA A, Optics Communications, Optics and Lasers in Engineering.

The manuscript should be framed as theory plus numerical evidence. Avoid
experimental-demonstration language unless raw experimental traces are later
obtained.
