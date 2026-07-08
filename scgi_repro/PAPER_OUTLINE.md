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

## Current Evidence Gaps

- The current SCGI reproduction is smoke/debug scale; full APL-scale training is
  not complete.
- The M2 dense reference scan is numerical-only and idealizes reference
  measurements as noiseless gain samples; a non-ideal detector/reference-noise
  section is still needed.
- Flip boundaries are discrete sampled diagnostics, not yet fitted theory curves
  with uncertainty.

## Venue Positioning

Primary: Physical Review A or IEEE Transactions on Computational Imaging.
Alternates: JOSA A, Optics Communications, Optics and Lasers in Engineering.

The manuscript should be framed as theory plus numerical evidence. Avoid
experimental-demonstration language unless raw experimental traces are later
obtained.
