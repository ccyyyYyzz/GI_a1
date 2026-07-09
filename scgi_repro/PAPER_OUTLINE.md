# Paper Outline

## Working Title

Measurement-Basis Identifiability In Time-Varying Multiplicative Single-Pixel
Channels

## Contribution Claims

1. We establish an identifiability view of blind gain correction in single-pixel
   imaging through time-varying multiplicative channels.
2. We derive complementary error-propagation laws for ordered orthogonal bases,
   randomized orthogonal bases, and i.i.d. random bases under estimator-matched
   caveats.
3. We map the regime where pairwise normalization is sufficient, where blind
   statistical correction is identifiable, and where reconstructions are at the
   noise floor.
4. We propose randomized orthogonal bases as a constructive design rule:
   randomized coefficient statistics provide a gain anchor while exact inversion
   preserves the oracle/static ceiling.

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
8. SRHT ablation: above-floor quality and delta versus ordered Hadamard.

## Draft Figure Captions

**Figure 1. Identifiability model for multiplicative single-pixel channels.**
The measured bucket sequence is modeled as `R_n=a_n<I_n,T>`, where the unknown
time-varying gain `a_n` is separable only when the ideal coefficient sequence has
a stable statistical anchor. Random speckles and SRHT-like randomized bases make
the coefficient sequence close to stationary, whereas ordered orthogonal bases
mix object-dependent low-order coefficients with gain drift.

**Figure 2. Oracle correction separates information loss from gain-estimation
failure.** M1 oracle runs divide each bucket by the true gain sequence before
reconstruction. Deterministic bases recover their static advantage under oracle
or pairwise-common-gain conditions, showing that their blind degradation is
mainly an identifiability/calibration problem rather than irreversible
information loss.

**Figure 3. Blind AGC has a window bias-variance tradeoff.** Local-mean AGC
reduces random bucket fluctuation as the window grows but increasingly smooths
over channel drift. The candidate law in `THEORY.md` predicts a competition
between `CV_B^2/W` variance and a drift-bias term proportional to
`sigma_a^2(rho W)^nu`. The targeted validation in
`results/theory_m4_agc_targeted_r1` improves AGC best-window fit R2 to 0.71-0.82
but still has 42-56% boundary-selected cells. The boundary-aware fit in
`results/theory_m4_agc_boundary_aware_r1` treats those hits as upper-bounded
intervals and reaches 0.80 interval satisfaction for random bases, 0.64 for
SRHT, and 0.40 for Hadamard, so Figure 3 should present the law as an
explanatory diagnostic rather than a final theorem.

**Figure 4. Residual gain errors propagate coherently through orthogonal
inversion but average through random measurements.** M4 residual-error sweeps
over 16, 32, and 64 pixel grids give `sigma_delta` exponents 2.001-2.003 with
minimum R2 0.99992. Fixed-size random-frame sweeps give random uniform/binary
frame exponents near -0.72 and -0.71, supporting the predicted averaging of
uncorrelated gain errors.

**Figure 5. Flip-boundary curves over drift rate and gain amplitude.** The
Hadamard-order dense boundary audit extends the sampled range to `rho=10`,
includes natural/sequency/cake/random Hadamard row orders, and records observed,
left-censored, not-reached, and sub-floor cells. After the `rel_mse<0.5`
above-floor gate, four log-rho boundary fits are observed in
`results/m2_boundary_audit_hadamard_order_dense_r1`; the M4 r2 censored tables
retain unresolved cells so the figure can show both fitted curves and
interval-qualified regions.

**Figure 6. Reference-frame calibration improves quality at a physical-frame
cost.** `reference_k2` is the best above-floor all-non-oracle method in 31/45
prompt-range rho/sigma cells, but it spends 3073 total physical frames for a
2048-frame measurement budget. Under strict equal-frame accounting,
`srht_paired+pairwise` is the winner in 29/45 above-floor cells; the remaining
strict cells are shown as sub-floor/noise-floor rather than method wins.

**Figure 7. Prompt-range phase diagram of basis/correction winners.** Dense M2
scans over nine drift rates (`rho=0.001..10`) and five gain amplitudes show that
`srht_paired+pairwise` dominates the above-floor strict equal-frame blind map,
while 16/45 strict cells are excluded from winner claims as sub-floor. Frozen
SCGI direct transfer over the same prompt range remains a negative baseline:
`scgi_frozen` averages -0.206 dB versus `none`, -0.796 dB versus `scgi_proxy`,
and -1.167 dB versus paired-basis `pairwise`. A proxy-input 1D trained SCGI
variant improves the network baseline to +0.329 dB versus `none` and -0.262 dB
versus `scgi_proxy`, but still does not change the above-floor
`srht_paired+pairwise` winner map.

**Figure 8. Randomized orthogonal bases buy identifiability above the
reconstruction floor.** The M3 ablation reports AGC signal recovery
(`1-rel_mse`) and delta PSNR versus ordered Hadamard over
`rho=0.001,0.1,1,10`. At `rho=0.001`, full SRHT is +5.453 dB over ordered
Hadamard, while row permutation, diagonal signs, and sign-time interleaving each
recover essentially the same advantage. At `rho=0.1`, AGC reconstructions are
already transitional/sub-floor by the default gate (`rel_mse` about 0.57-0.67),
and at `rho>=1` all blind variants collapse to the reconstruction floor, so the
sub-dB moderate/fast-drift deltas are grey-band coincidences rather than
effects. The caption should state that the prompt's `>=3 dB` fast gate is
refuted, but the constructive identifiability result is established where gain is
estimable.

## Current Evidence And Gaps

- The current SCGI reproduction is strongest at smoke/debug scale. Full
  APL-scale Colab runs at 20 and 100 epochs complete but do not converge, so the
  SCGI reproduction should be presented as an executable diagnostic prototype
  until the full training setup is redesigned.
- Stage 4 now has an important diagnostic split: strict continuous URED remains
  below the APL gate, but target-free thresholded masks from target-aware
  best-trace images clear the URED CNR threshold on all four held-out objects.
  A thresholded-trace stop-rule audit now finds fixed target-free stopping rules
  that also clear all four objects, but this still changes the original
  continuous-output reporting protocol.
- The dense M2 reference scan supports `srht_paired + pairwise` as the
  above-floor strict equal-frame blind winner. The high-rho merge covers
  `rho=0.001..10`; after the reconstruction-floor gate, 29/45 strict cells are
  above-floor SRHT/pairwise wins and 16/45 are sub-floor. This is useful
  evidence for the randomized-orthogonal design rule, but it is still idealized.
- The dense `scgi_proxy` scan shows that a blind smooth-gain proxy improves over
  raw/AGC baselines without reference frames, but it does not displace SRHT
  pairwise as the equal-frame winner and should not be described as a trained
  SCGI-network result.
- Hadamard row-order support now covers natural, sequency, cake-cutting-proxy,
  and random orders. A monitored smoke run verifies the expanded phase-map
  plumbing, and `results/m2_hadamard_order_dense_r1_merged` now completes the
  full 9x5 prompt grid with all order variants. The dense strict equal-frame map
  remains mostly `srht_paired + pairwise` above-floor, with one
  `hadamard_random_paired + scgi_proxy` cell and 16/45 sub-floor cells.
- Frozen-network M2 smoke and prompt-range dense baselines now exist. Directly
  applying the returned SCGI checkpoint to M2 sequences underperforms
  proxy/pairwise baselines, so a credible network-level phase diagram would need
  basis-aware retraining, fine-tuning, or a different sequence representation.
- A supervised M2 fine-tuning path now exists. Direct-output and single
  `gain_unet` smokes are negative, while basis-specific `gain_unet` routing has
  local held-out signal (`srht_paired + scgi_frozen` is selected in 2/6
  pre-floor diagnostic cells at `rho=0.3`) but remains below `none`,
  `scgi_proxy`, and paired `pairwise` on average.
- Signed-safe outputs and true-gain prediction have also been tested. Raw-bucket
  `gain_predictor_unet` remains negative, but fixing checkpoint metadata loading
  and feeding a blind proxy-gain envelope into a 1D gain predictor yields a
  dense trained-network baseline: +0.329 dB versus `none`, +0.604 dB versus AGC,
  and -0.262 dB versus `scgi_proxy` on the full prompt grid.
- The M2 dense reference scan idealizes reference measurements as noiseless gain
  samples. Compact and full nonideal digital-twin scans now exist, and the full
  scan preserves the pairwise winner under detector/SLM perturbations. Published
  APL/OE figure-level channel anchors now exist, but raw detector/SLM calibration
  is still needed before claiming hardware-calibrated nonideal performance.
- M3 now has a monitored 10-object x 5-seed high-rho ablation. It confirms
  information preservation under oracle correction and shows a real
  randomization advantage at `rho=0.001` under AGC (+5.453 dB for full SRHT over
  ordered Hadamard), but it refutes the prompt's `>=3 dB` fast-drift gate.
  Because `rho=0.1` is already transitional/sub-floor by the default gate and
  `rho>=1` blind reconstructions are at floor, moderate/fast deltas should be
  presented as sub-floor coincidences, not effects. The least-squares random
  control in `results/m3_random_comparator_fast_ls_r1` narrows the estimator
  caveat: random binary remains at floor (`rel_mse` 0.963-0.987), and SRHT is
  only +0.059 to +0.322 dB above the best random basis in fast drift.
- Flip boundaries are now represented both as observed fits and censored
  intervals. `results/m2_boundary_audit_hadamard_order_dense_r1` gives four above-floor
  prompt-range log-rho boundary fits with `R2 >= 0.9`, while
  `results/theory_m4_paper_r2_highrho` keeps the censored cells for paper
  plotting.
- M4 high-rho r2 theory hooks now support quadratic residual-gain scaling with
  bootstrap confidence intervals, random/SRHT coefficient spreading up to 4096
  pixels, censored flip-boundary accounting, and AGC window diagnostics.
  `results/paper_figures_r1` now renders the current M2/M4 figure draft set
  with PNG previews, SVG sidecars, and raster/vector manifests. The new
  `results/paper_figures_r1/multipanels` directory adds draft 300-dpi
  multipanel PNG/PDF/SVG assemblies for Figures 3, 4, and 7, with an 11-row
  panel manifest linking each panel to source CSV evidence. The targeted and
  boundary-aware AGC sweeps are complete but remain diagnostic, so the
  publication version still needs venue-specific final artwork and a stronger
  AGC estimator or tighter censored-law validation.
- A competitive fine-tuned SCGI-network correction is now present in the dense
  prompt-range M2 phase diagram, but it is a secondary baseline rather than the
  dominant correction strategy.
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
