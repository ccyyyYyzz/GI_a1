# Paper review R5: pre-submission referee pass on MANUSCRIPT_DRAFT

> Provenance: GPT-5 Pro (Pro Extended), 2026-07-09, conversation "论文评审 R5 任务".
> The ChatGPT GitHub connector exposed no issue-write surface in this session, so the prepared
> issue body was captured from the chat verbatim and committed here instead (this file = the ledger).
> Nonce: PAPERREV-R5B-3e8a1f
> Source reviewed: scgi_repro/paper_draft/MANUSCRIPT_DRAFT.md @ scgi-ceiling-diagnostic-r1, commit c99487b7.
> Context read: issues #1 (R1), #2 (R2), #3 (R3), #4 (R4 framing). Section 9 numbers treated as verified; the review targets interpretation, sufficiency, venue risk.

## (1) Executive judgment

**MAJOR REVISION, but on an accept trajectory.** Not acceptance-ready at PRA/IEEE-TCI level as-is; a revised version would be taken seriously if the proof package is self-contained, theorem statements are tightened to their actual assumptions, and the simulation story expands beyond the present demonstration panel.

Three main reasons:
1. The core idea is strong and publishable: the calibration paradox is real, memorable, technically interesting; the three-way split (algebraic / statistical anchoring / finite-noise conditioning) is the paper.
2. The draft asks the reviewer to trust too much: central results defer to "Appendix / issue #x" but the manuscript has no appendices. GitHub issues are not archival proofs.
3. Simulations persuasive but not referee-proof: need adversarial object spectra, more permutations/seeds, coherent residual gains, alternate low-photon estimators, and existing SCGI/DGI baselines.

## (2) BLOCKERS

**B1. Not self-contained as a theorem paper.** Include actual appendices A–F (formal statement, assumptions, proof, and a "what this does not claim" paragraph per theorem).

**B2. Theorem statements hide quantifiers/conventions.** Add a boxed convention table in Sec. 2: S linear log-gain subspace containing constants; p=dim S so nonconstant dim = p−1; all identifiability modulo global scale; local-differential vs generic-exact vs uniform-exact are distinct; rho_bw controls p≈rho_bw·N vs rho_pair adjacent-pair mismatch.

**B3. Condition (★) and Theorem B not theorem-grade in the main text.** State the probability model: Y_n=ell_n+m_T+z_n with {z_n} stationary centered beta-mixing/sub-exponential (or finite long-run variance); ell in a discrete Hölder class; W→∞, W/N→0, drift bias O(L·W^alpha); recovers CENTERED ell only; positivity/soft-log assumptions explicit. This is the most likely mathematical attack point.

**B4. Log-domain vs physical bucket models not reconciled.** Add a "bucket conventions" subsection before Theorem B: signed coefficient model; physical nonnegative offset model; ± pairwise Hadamard model; raw signed arms = diagnostic simulations only (not a valid physical log estimator without offset/soft-log).

**B5. SRHT overclaimed relative to theorem + ablation.** Phrase conditionally: signs give identical marginals but need Walsh-flat T² for covariance/window whitening; permutation makes flatness likely when K_4, K_∞ large; row-order randomization alone gives exchangeability but maybe not two-sided excitation; in the tested panel either randomization sufficed — not a universal theorem.

**B6. rho_pair / rho_bw distinction stated but rhetorically violated.** Sec. 9's "exactly as the tall-design counting demands" is too strong for an OU adjacent-decorrelation sweep; replace with "consistent with the same information-loss intuition" or run a decoupled (rho_bw, rho_pair) experiment.

**B7. Phase diagram constants under-exposed.** Table beside Fig. 5: measured C0, D_H, K_eff range, v_blind, noise/flux conventions, CIs for the fitted boundary.

**B8. Section 9 needs uncertainty reporting.** Bootstrap CIs over objects/seeds/permutations for slopes, correlations, winner maps, p-values, dB gains; 10 objects × 5 seeds is a development note, not a top-tier claim.

**B9. Prior-work positioning too thin.** Expand Sec. 3: canonical single-pixel / computational GI / Hadamard GI / DGI / dynamic-scattering references + blind gain/phase calibration and self-calibration; then state exactly what is added (temporal stationarity anchor + finite-noise design map).

**B10. Most memorable language easiest to attack.** Keep the hook, qualify the technical claims nearby.

## (3) Numbered minor fixes (section anchors)

1. Abstract: "safest ... against additive noise" → scope to fixed square orthogonal linear inversions under known gain / equal budget.
2. Abstract: "every square invertible design fails algebraically" needs "for unconstrained objects, nonzero carrier entries, admissible nonconstant log-gain perturbations, modulo global scale."
3. Abstract/Sec.1: SRHT claim conditional on Walsh-flatness / successful permutation / positivity margin.
4. Sec.1: define "static-correction ceiling" before use.
5. Sec.1: two Peng/Chen refs insufficient for the field survey — add canonical GI, single-pixel camera, Hadamard GI, DGI, dynamic-scattering refs.
6. Sec.2: notation table for K, N, S, p, rho_bw, rho_pair, K_eff, K_inf, K_4, C0, D_H, B_L.
7. Sec.2: state gauge convention once (center ell, or LS scale alignment).
8. Sec.2: clarify where T is assumed nonnegative vs signed.
9. Sec.4: Corollary 1's "closed under the induced action" phrase obscure — simplify.
10. Sec.4: "support zeros can be" → "KNOWN support zeros can be" + cite rank condition.
11. Sec.4: Thm A' explicitly = generic exact finite-sample identifiability, not conditioning/algorithmic recovery.
12. Sec.5: make (★) quantitative (sup_n |mean_W log B − c_T| or probability bound).
13. Sec.5: "random illumination satisfies (★) by construction" true for iid, NOT automatic for finite row permutations / single fixed SRHT order — add distinction.
14. Sec.5: Prop 1 — add "higher cumulants and log means can depend on object shape, but only time-independent terms affect the gain gauge."
15. Sec.5/Fig.3: "object enters only through K_eff" → soften to "to leading Gaussian/log-variance order and within the tested object panel."
16. Sec.6: alpha (soft-log offset) vs Hölder smoothness symbol collision — add notation warning.
17. Sec.6: "below the Fisher reference" must say "below the unbiased/local Fisher reference because bias is present"; show bias and variance separately in Fig. 7.
18. Sec.7: "subsampled" confusing when main SRHT reconstruction is full N=K — say full randomized Hadamard; reserve "subsampled" for N<K (then bias/prior issue).
19. Sec.7: design rule (sign+perm) vs Fig.6 (either alone suffices) — add theorem-guarantee vs empirical-disruption paragraph.
20. Sec.8: Thm 1 state whether relMSE is scale-aligned (affects relMSE/v<1 for DC-dominated objects).
21. Sec.8: define r(rho_pair) BEFORE the displayed equation.
22. Sec.8: C0 → C0(pipeline) throughout.
23. Sec.9 protocol: exact seeds, object list/source, mask generation, photon/noise convention, AGC window grid, alignment metric.
24. Sec.9: Brown–Forsythe p-values — discuss multiplicity correction.
25. Sec.9: "28 above-floor cells" needs full denominator + justification of relMSE<0.5 gate.
26. Sec.9: raw non-paired Hadamard arm labeled physically/log-domain problematic unless offset buckets used.
27. Sec.10: move the "each analogue needs its own operator analysis" caveat earlier.
28. References: full bibliographic entries + DOIs.

## (4) Missing experiments (referee would demand)

Keep running: (a) tall-design threshold scan (Thm A'); (b) multi-permutation whitening power. Beyond:

- **E1. Conditioning near the tall threshold** [compute-heavy]: quotient-Jacobian smallest singular values / Fisher condition numbers vs N−(K+p), for Gaussian/nonneg-random/tall-SRHT/physical designs. Output: identifiability probability + conditioning quantiles phase plot.
- **E2. End-to-end blind recovery at threshold with real solvers** [compute-heavy]: NLS/alt-min/regularized MLE below/at/above K+p; oracle + random init; success, gain error, relMSE, convergence failures, basin sizes.
- **E3. Adversarial object spectra with matched K_eff** [compute-heavy]: same K_eff, different K_inf/K_4/Walsh spectrum (flat, sparse spikes, DC-dominated, checkerboard, stripe, Walsh-aligned T², random dense). Expose when the K_eff collapse breaks.
- **E4. Coherent residual-gain validation of Thm 1** [not compute-heavy]: same v, different covariance (iid, AR(1), sinusoidal, low-pass, blockwise); show scalar v·B_L fails and full matrix formula succeeds.
- **E5. Low-photon estimator bakeoff** [compute-heavy]: soft-log vs clipped log vs Anscombe vs full Poisson MLE; bias/variance/MSE separately across lambda-bar.
- **E6. Baselines vs existing SCGI / dynamic-scaling pipelines** [compute-heavy]: SCGI-style Gaussian-likelihood correction + ordinary DGI/reference normalization (+ optionally a small learned baseline), same budgets/objects/drift.
- **E7. Decouple rho_pair from rho_bw** [compute-heavy]: 2D grid with controlled Fourier bandwidth dimension p and separately controlled adjacent increment variance; map where tall-algebraic, pairwise differencing, stationarity anchoring each fail.
- **E8. End-to-end row/sign/permutation ablation beyond whitening** [compute-heavy]: many draws; distribution of gain error and relMSE; probability of a bad SRHT draw.
- **E9. DGI constant + photon-budget convention audit** [not compute-heavy]: measured C0 per pattern distribution/normalization; boundary prediction under equal-exposure/equal-count/fixed-flux.
- **E10. Hardware-realistic nuisance stress test** [compute-heavy]: calibration error, dead pixels, offset drift, gain jumps, clipping, quantization, mild motion; failure taxonomy per basis.
- **E11. Oracle / metered-gain baselines** [not compute-heavy]: oracle known-gain, noisy metered gain, no correction, blind — for every reconstruction figure.
- **E12. Figure-level uncertainty + reproducibility sweep** [compute-heavy, straightforward]: scale Sec. 9 to more seeds/objects/randomizations; bootstrap ALL headline numbers (0.96 vs 0.02, +5.45 dB, boundary R², K_eff correlations, Brown–Forsythe rates). Most direct use of expiring Colab credit.

## (5) Venue fit

- **IEEE-TCI — strongest fit.** Pitch: computational-imaging design theory for blind multiplicative calibration in single-pixel imaging, with identifiability thresholds, SRHT acquisition rules, and an exact finite-noise relMSE bridge. Expects: stronger baselines, reproducible sim details, uncertainty bars, measured constants.
- **PRA — viable only if theory made airtight** (archival proofs, sharply motivated physical model); risk: read as signal processing without hardware.
- **JOSA A — safest optics fallback, lower ceiling.**
- Recommendation: **IEEE-TCI first** after experimental + self-contained-proof revisions; PRA if the final becomes theorem-dominant; JOSA A fallback.

## (6) Three sentences most likely to be quoted against us (with rewrites)

1. "Ordered orthogonal scanning is the safest single-pixel acquisition against additive noise — and the most treacherous under blind multiplicative drift." → **Rewrite:** "For a fixed square linear inverse with known gain, an ordered orthogonal scan minimizes conditioning-driven amplification of additive noise; with unknown slow multiplicative gain and unconstrained objects, the same deterministic chronology can create an exact gain–object ambiguity."
2. "Randomized-Hadamard (SRHT) acquisition achieves both orthogonal conditioning and a stationary carrier." → **Rewrite:** "Randomized Hadamard/SRHT preserves orthogonal conditioning, and under Walsh-flatness or a successful random permutation of a sufficiently spread object it supplies the stationary or exchangeable carrier needed by the windowed gain estimator."
3. "At rho ≥ 1 all variants converge within ±0.09 dB at the noise floor: fast drift extinguishes blind separation for every basis alike, exactly as the tall-design counting of Theorem A′ demands when p approaches N." → **Rewrite:** "At the largest simulated adjacent-pair decorrelation rates, all blind variants empirically approach the noise floor; this is consistent with the information-loss intuition behind the p→N algebraic limit, but it is not a direct test of the low-pass dimension threshold unless gain bandwidth and adjacent-pair decorrelation are controlled separately."

## Bottom line

A real paper, not yet submission-ready. The best version is not "random beats Hadamard" but: **blind calibration is a property of acquisition chronology; ordered orthogonal scans can be perfectly invertible and still uncalibratable, while random/SRHT designs make the object carrier stationary enough to estimate relative gain and predict finite-noise image error.** Make the proofs self-contained, discipline the claims, add the adversarial/conditioning experiments → credible IEEE-TCI submission with a possible PRA angle.
