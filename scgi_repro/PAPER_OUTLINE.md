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
  equal-frame blind winner. The high-rho merge covers `rho=0.001..10` and keeps
  `srht_paired + pairwise` as the winner in 45/45 equal-frame cells. This is
  useful evidence for the SRHT design rule, but it is still idealized.
- The dense `scgi_proxy` scan shows that a blind smooth-gain proxy improves over
  raw/AGC baselines without reference frames, but it does not displace SRHT
  pairwise as the equal-frame winner and should not be described as a trained
  SCGI-network result.
- Frozen-network M2 smoke and dense baselines now exist. Directly applying the
  returned SCGI checkpoint to M2 sequences underperforms proxy/pairwise
  baselines, so a credible network-level phase diagram would need basis-aware
  retraining, fine-tuning, or a different sequence representation.
- The M2 dense reference scan idealizes reference measurements as noiseless gain
  samples. Compact and full nonideal digital-twin scans now exist, and the full
  scan preserves the pairwise winner under detector/SLM perturbations. Published
  APL/OE figure-level channel anchors now exist, but raw detector/SLM calibration
  is still needed before claiming hardware-calibrated nonideal performance.
- Flip boundaries are discrete sampled diagnostics, not yet fitted theory curves
  with full uncertainty, although `results/m2_boundary_audit_highrho` now gives
  five prompt-range log-rho boundary fits with `R2 >= 0.9`.
- M4 paper-r1 theory hooks now support quadratic residual-gain scaling with
  bootstrap confidence intervals, random/SRHT coefficient spreading up to 4096
  pixels, censored flip-boundary accounting, and AGC window diagnostics. The
  publication version still needs a cleaner analytical AGC law and paper-ready
  boundary figures/captions.
- A competitive fine-tuned SCGI-network correction is not yet part of the M2
  phase diagram; the implemented frozen dense baseline underperforms.
- Published-curve calibration is limited to figure-level priors: APL intensity
  traces fit `lambda_per_measurement = 0.999897-0.999921`, and OE Fig. 6
  fixed-reference PSNR crosses 30 dB near `beta = 1.90 x 10^-2 mm^-1`.
  Hardware-calibrated OU/channel parameters remain unavailable without raw logs.

## Venue Positioning

Primary: Physical Review A or IEEE Transactions on Computational Imaging.
Alternates: JOSA A, Optics Communications, Optics and Lasers in Engineering.

The manuscript should be framed as theory plus numerical evidence. Avoid
experimental-demonstration language unless raw experimental traces are later
obtained.
