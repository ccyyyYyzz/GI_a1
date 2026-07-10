# Blocking findings

Severity meanings: **High** = a stated theorem or claimed validation is false or unsupported as written; **Medium** = scope, proof, or evidence mismatch likely to trigger a substantive reviewer objection; **Low** = provenance or presentation risk.

## High 1 — Corollary 2 ordinary-local iff is false

- **Location:** paper_draft/latex/appendix_body.tex:65–107, especially the statement near line 74 and the proof near line 91.
- **Issue:** The statement uses ordinary local identifiability language and gives an “if and only if (at the first-order level).” The kernel condition is an iff criterion for differential identifiability and a sufficient condition for ordinary local identifiability, but failure of the differential condition does not by itself imply a nearby exact alias.
- **Impact:** The necessity direction of the stated ordinary-local criterion is false. A three-dimensional explicit counterexample is in 02_COUNTEREXAMPLES_AND_PROOF_NOTES.md.
- **Minimum fix:** State the iff only for differential identifiability. State separately that kernel = gauge implies ordinary local identifiability by the immersion/constant-rank argument. The exact ordinary-local criterion is that zero be an isolated zero of the gauge-fixed nonlinear support map. With the appendix's stated Taylor bound, the proved radius is min{1, gamma / C_H}, not unconditionally gamma / C_H.

## High 2 — Theorem B triangular-array consistency lacks uniform control

- **Location:** paper_draft/latex/appendix_body.tex:374, 461–471; corresponding main-text Theorem B near paper_draft/latex/body.tex:140–146.
- **Issue:** The appendix explicitly permits a triangular array, while (B2a) asks only for a finite summable-autocovariance constant in each row. The displayed upper bound is then marked as converging to zero without requiring sigma_abs,N squared divided by W_N to vanish.
- **Impact:** All rowwise assumptions can hold while the estimator variance diverges. The theorem is false as an array-level consistency result.
- **Minimum fix:** Under (B2a), require the actual variance of the claimed pointwise window to vanish; use a supremum over n for a uniform-in-n conclusion. Sigma_abs,N squared / W_N tending to zero is a convenient sufficient condition. If the constants are intended to be fixed uniformly, state uniform moment, mixing, and covariance-sum envelopes. A triangular long-run-variance limit additionally needs uniform covariance-tail tightness. Give the corresponding uniform q-block/tail assumptions for (B2b).

## High 3 — Theorem C/D omit finite-window and experiment scope

- **Location:** paper_draft/latex/body.tex:169–178; paper_draft/latex/appendix_body.tex:541–563, 632–679, 811–815, 933–935.
- **Issue:** The optimized displays suppress conditions needed by the finite-window bounds: 1 <= W <= N (and coherence-time limits), nonvanishing window sensitivity, class-diameter/no-smoothing saturation, beta/window-order restrictions, and the distinction between blind high-count and oracle-known-carrier Poisson experiments. Theorem D uses a Gaussian submodel without fully defining whether minimax risk also takes a supremum over noise laws.
- **Impact:** The displayed rates can exceed a trivial finite-sample risk bound, and a Gaussian lower bound does not establish a lower bound for every fixed non-Gaussian mixing experiment.
- **Minimum fix:** Keep D.8 as the master finite-window statement and express the optimized bound as an infimum over feasible W. Present the power rate only in the interior regime. State Theorem D either for a fixed iid Gaussian experiment or define a product minimax risk with an explicit supremum over an admitted, normalized noise-law class. Split the blind and oracle Poisson results.

## High 4 — Prop. 3 raw validation is not a same-estimator validation

- **Location:** paper_draft/latex/appendix_body.tex:1388–1397 and 1533; src/mechanisms.py:487–489; run_prop3_raw_metric_export.py:149.
- **Issue:** Equation (F.7) assumes stable true S1 normalization. The implementation substitutes median(pair_sum) for S1, and the raw export reuses that implementation.
- **Impact:** Estimating S1 creates a global multiplicative/gauge term and cross terms absent from (F.7). The current raw empirical curve cannot be described as a direct validation of the exact theorem. On the recomputed raw panel, the implemented estimator's pooled slope is -2.00656, not the -2.11 reported at line 1533; the theorem-faithful true-S1 arm gives -2.12044 against prediction -2.11371.
- **Minimum fix:** Add an oracle-true-S1 QA arm and use it for the theorem check, or extend the theorem and prediction to include the implemented S1 estimator. Keep the practical median-normalized arm as a separate implementation result.

## High 5 — “exact” pair-ratio Gaussian read-noise MSE is false

- **Location:** paper_draft/latex/appendix_body.tex:1433–1435.
- **Issue:** For the actual paired ratio with independent equal-variance Gaussian read noises, the noisy sum and difference are independent nondegenerate Gaussians. The sum denominator has positive density arbitrarily close to zero while the conditional numerator variance remains positive, so the unregularized ratio has an infinite second moment.
- **Impact:** R_pair,read = 2 sigma_read squared / S2 is not an exact finite-risk identity for the noisy ratio estimator.
- **Minimum fix:** Either define a fixed/noiseless DC normalization and keep an exact linear-noise result for that estimator, or specify clipping/offset/conditioning and derive its risk. Otherwise label the familiar expression a high-SNR delta-method approximation; the leading correction also depends on gain/normalization and K_eff.

## High 6 — Main-text scalar v_blind conflicts with Appendix F

- **Location:** paper_draft/latex/body.tex:245–254; paper_draft/latex/appendix_body.tex:1498–1512; run_prop3_boundary.py:287–291; run_prop3_verdict_tables.py:132 and 172.
- **Issue:** The main text presents a scalar blind-residual term, while the appendix correctly says no scalar representation is asserted for a same-record blind estimator. The runners additionally feed the scale-aligned gain_rel_mse into the proxy, whereas (F.12) needs the raw residual q_delta = mean[(a / a_hat - 1) squared].
- **Impact:** Overlapping-window residuals are correlated, may have nonzero mean, and share the record noise. The full Theorem 1 covariance and residual–noise cross terms do not reduce to the scalar proxy without extra assumptions. In the existing panel q_delta / aligned gain error rises to median 1.21–1.26 at sigma = 0.5.
- **Minimum fix:** Restrict the scalar formula to exogenous, centered, frame-uncorrelated residuals. Export q_delta_raw, its mean, and covariance diagnostics. Label same-record scalar curves as conditional proxies, or compute the full covariance/cross-term expression.

## Medium findings

### M1 — beta greater than one is not globally covered by the simple window

- **Location:** paper_draft/latex/body.tex:143, 169–178; paper_draft/latex/appendix_body.tex:466, 493–497, 862–935.
- **Issue:** Standard Hölder notation for beta greater than one requires control/cancellation of lower-order polynomial components. The appendix itself notes that arbitrary carriers and edge windows need carrier-adapted moments or a proved local-polynomial estimator.
- **Minimum fix:** Restrict the general one-sided/arbitrary-carrier theorem to beta <= 1; isolate internal balanced-window or explicit local-polynomial extensions.

### M2 — alpha-to-zero/plain-log joint-limit wording

- **Location:** paper_draft/latex/body.tex near line 167.
- **Issue:** Sending alpha to zero at fixed finite Poisson intensity does not recover an integrable plain log because zero counts remain possible.
- **Minimum fix:** State a high-count limit with fixed alpha, or a joint limit controlling exp(-lambda) times the magnitude of log alpha.

### M3 — long-run variance remainder needs additive form

- **Location:** paper_draft/latex/appendix_body.tex:485 and 1010–1023.
- **Issue:** A multiplicative sigma_LR squared / W times (1+o(1)) form fails when sigma_LR squared = 0; the appendix later gives the differenced-noise counterexample itself.
- **Minimum fix:** Use sigma_LR squared / W + o(W^-1), reserving the multiplicative form for strictly positive long-run variance.

### M4 — finite-window Gaussian CRB simplification

- **Location:** paper_draft/latex/appendix_body.tex near line 579.
- **Issue:** For correlated finite-window Gaussian noise the exact common-shift information is 1-transpose Sigma-inverse 1, not generally W_eff / sigma_LR squared.
- **Minimum fix:** Give the exact matrix expression, then state the long-run-variance approximation under the required Toeplitz/spectral conditions.

### M5 — mixed metric in Fig. 9 bridge description

- **Location:** paper_draft/latex/body.tex near line 233; run_paper_fig4_bridge.py:105–132; results/paper_fig4_bridge_r2b/fig4_caption.md:3.
- **Issue:** The prose groups arms under scale-aligned relMSE, while the random-DGI runner uses a raw residual norm and the orthogonal arm uses a scale-aligned metric.
- **Minimum fix:** Separate metrics by arm in text/caption or recompute a common metric.

### M6 — permutation semantics still need disciplined wording

- **Location:** paper_draft/latex/body.tex:16, 120, 203, 211; paper_draft/latex/appendix_body.tex near line 1227.
- **Issue:** Pixel permutation/sign randomization, acquisition-order permutation, ensemble covariance, finite-population exchangeability, and a fixed realized draw are not interchangeable.
- **Minimum fix:** Preserve the P_col/D versus P_row distinction already present in parts of the manuscript and remove remaining claims that a fixed pixel-permuted draw is itself temporally exchangeable/stationary.

### M7 — truncated Gaussian prior step is only a sketch

- **Location:** paper_draft/latex/appendix_body.tex:549–561.
- **Issue:** Independent Gaussian priors truncated to an ellipsoid are no longer independent, and their prior Fisher information is not the displayed untruncated sum without an argument.
- **Minimum fix:** Cite and instantiate a standard Pinsker/Assouad construction, or explicitly bound the effect of truncation. Do not present the current two sentences as a complete van Trees proof.

### M8 — orthogonal inversion is not universally the “best conduit”

- **Location:** paper_draft/latex/body.tex:241.
- **Issue:** Equal per-frame residual variance does not imply B_L >= 1 for every exact linear reconstruction. With K = 1, A = (1,1) transpose, L = (1/2,1/2), and T = 1, one has LA = 1, zero reconstruction floor, but B_L = 1/2.
- **Minimum fix:** Make the comparison only between the named square-orthogonal and manuscript DGI pipelines under their specified designs/noise budgets, or prove an optimization result under explicit acquisition-energy and frame-budget constraints.

### M9 — Theorem B’s “only ambiguity remaining” overreaches its estimand

- **Location:** paper_draft/latex/appendix_body.tex:480–485.
- **Issue:** Consistency of centered gain identifies the relative-gain functional, not the full object in the bucket-only marginal experiment used by Theorem B. Under iid exchangeable pattern coordinates, T = (1,2) and T-prime = (2,1) induce the same marginal carrier/record law but are not scale-related. This is not an alias for the richer joint experiment in which the realized illumination pattern is observed together with each bucket.
- **Minimum fix:** Say that the constant gauge is the only ambiguity of the centered-gain estimand in the stated bucket-only experiment. Do not infer full (a,T) statistical identifiability from consistency of that functional; define a joint-pattern experiment separately if intended.

### M10 — signed orthogonal coefficients are not direct Poisson intensities

- **Location:** paper_draft/latex/appendix_body.tex:1367–1386.
- **Issue:** Proposition F.2(b) requires nonnegative physical intensity Phi_n = gamma_n a_n b_n. The orthogonal specialization permits signed b_n = (UT)_n, for which that direct Poisson model is undefined when b_n < 0.
- **Minimum fix:** Route the Poisson specialization through physical complementary masks or a positive offset and carry the corresponding allocation/covariance, or state that the signed-coefficient formula is a post-differencing Gaussian/linear reconstruction model rather than a direct Poisson experiment.

### M11 — generic known-zero sufficiency lacks its required witness

- **Location:** paper_draft/latex/body.tex:77; paper_draft/latex/appendix_body.tex:109.
- **Issue:** The main text says K0 >= p - 1 generic known support zeros restore local identifiability, but the appendix labels this sufficiency “expected.” Generic full rank needs at least one explicit witness; because H inverse appears, clear a power of det(H) before invoking an algebraic exceptional set. Moreover, K0 >= p - 1 is necessary only for differential identifiability/full-rank sufficiency, not for ordinary local identifiability through higher-order terms.
- **Minimum fix:** Supply and verify a witness for the claimed design/object class, or make the main text conditional on the displayed rank test and label K0 >= p - 1 as a differential dimension-count prediction. Do not call the count necessary for ordinary local identifiability.

### M12 — the boundary and below-wall regimes are conflated

- **Location:** paper_draft/latex/body.tex:99.
- **Issue:** At N = K + p - 1 generic local identifiability already holds and only global exact necessity is open, but the prose folds this boundary into the below-wall discussion. Below the local wall the algebraic model needs additional information; stationarity, support, and sparsity are examples, not an exhaustive necessary menu.
- **Minimum fix:** Treat N = K + p - 1 separately. Below the local wall, say that additional structure or statistical information is required and present the named mechanisms as examples.

### M13 — D.4 uses unstated cross-frame conditional independence

- **Location:** paper_draft/latex/appendix_body.tex:589–642 and 695.
- **Issue:** The exact diagonal variance V_n is derived using conditional independence of the Poisson counts across distinct frames, but this assumption is stated only in the proof.
- **Minimum fix:** Add cross-frame conditional independence to the theorem's count model before claiming the exact finite-window identity.

### M14 — D.4.1 mixes linear intensity and log-gain parameters

- **Location:** paper_draft/latex/appendix_body.tex:615–621 and 862.
- **Issue:** The theorem defines theta as log-gain through lambda = Lambda0 exp(theta) b + d and gives the correct logarithmic safe interval. The protocol remark instead writes a linear bracket and Pois(theta b).
- **Minimum fix:** Use the logarithmic interval already displayed at lines 615–621 and write Pois(Lambda0 exp(theta) b) at d = 0 throughout the instantiation.

### M15 — the B2b block length drops beta0

- **Location:** paper_draft/latex/appendix_body.tex:504–512 and 465–475.
- **Issue:** From beta(k) <= beta0 exp[-(k/b)^kappa], choosing q with log(4W/delta) does not control the coupling error uniformly for arbitrary beta0.
- **Minimum fix:** Put beta0 inside the logarithm, for example log(C beta0 W / delta), or normalize the assumption so beta0 is absorbed into a declared universal constant.

## Low findings

- results/prop3_raw_metric_r1/run_manifest.json records an older commit and git_dirty_excluding_output = true. A clean rerun is advisable if this directory is used as submission-authoritative evidence.
- paper_draft/latex/main.tex and supplement.tex still contain author/affiliation placeholders or review-state labels. This is a submission blocker but not a scientific one.
