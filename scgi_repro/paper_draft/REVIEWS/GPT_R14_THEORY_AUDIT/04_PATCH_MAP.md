# Minimum repair map

This is an implementation handoff, not an edit log. No listed source file was modified by R14.

## Repair order

| Order | Target | Required action | Acceptance check |
|---:|---|---|---|
| 1 | appendix_body.tex Corollary 2; matching archival Markdown/main references | Split differential iff from ordinary-local sufficiency; incorporate or defeat the explicit 3-by-3 counterexample. | Counterexample no longer contradicts any statement; proof uses the same identifiability notion as the statement. |
| 2 | appendix_body.tex Theorem B; body.tex Theorem B | Add triangular-array uniformity/rate conditions. | The iid N(0,N), W=sqrt(N) array violates a stated hypothesis. |
| 3 | body.tex Theorems C–D; appendix D.1–D.4 | Separate blind high-count, fixed-Gaussian minimax, and oracle-known-carrier Poisson experiments; restore finite-window and beta/sensitivity conditions. | Every optimized display names its feasible regime; D.8 remains valid globally; no Gaussian submodel is used to claim a bound for every fixed noise law. |
| 4 | Appendix F, mechanisms.py, Prop. 3 runner/results/prose | Decide the estimator: oracle true-S1 theorem arm versus practical median-normalized arm. | The equation, implementation, exported prediction, metric, and caption all describe the same estimator. |
| 5 | Appendix F read-noise term | Replace exact noisy-ratio MSE by a fixed-normalization identity, a regularized theorem, or a labeled high-SNR approximation. | The estimator has a finite, defined second moment under its stated noise law. |
| 6 | body.tex reconstruction bridge | Restrict scalar v_blind to exogenous centered frame-uncorrelated residuals; route same-record estimators through the full covariance/cross-term formula. | No scalar proxy is called an identity for the overlapping-window estimator. |
| 7 | figures/captions/results summaries | Reconcile raw versus scale-aligned metrics and low-photon error-budget units. | Every numerical claim can be regenerated from the named metric and estimator. |
| 8 | body.tex leverage interpretation | Restrict “orthogonal is best” to a defined pipeline comparison or add the missing resource constraints. | The repeated-measurement counterexample no longer contradicts the prose. |
| 9 | Theorem B gauge paragraph | Scope “only ambiguity” to the centered-gain estimand, not the full object. | Exchangeable-coordinate object permutations no longer contradict the claim. |
| 10 | Appendix F Poisson specialization | Use nonnegative physical masks/offsets before applying the exact Poisson formula to signed transforms. | Every displayed Poisson intensity is nonnegative by construction. |
| 11 | Corollary 2 generic-zero prose | Add a full-rank witness or downgrade the count to a prediction conditional on direct rank verification. | No theorem follows from dimension counting alone. |
| 12 | body.tex regime map | Replace “stationarity required” by “additional information required” below the local wall and isolate the open boundary. | The prose matches Theorem A-prime’s proved quantifiers. |
| 13 | Appendix D.4 statement | State cross-frame conditional independence before using the diagonal variance sum. | The exact V_n identity follows from a written hypothesis. |
| 14 | Remark D.4.1 | Use log-gain theta consistently in the safe interval and Poisson mean. | The instantiation matches lambda = Lambda0 exp(theta) b + d. |
| 15 | Theorem B / Lemma D.1 high-probability block | Restore beta0 in q or normalize it explicitly. | The advertised coupling failure probability is at most delta. |

## Suggested replacement contracts

### Corollary 2

Suggested mathematical contract:

> The support-restricted Jacobian has kernel equal to the gauge direction if and only if the pair is differentially identifiable modulo gauge. This condition implies ordinary local identifiability on a gauge slice. Ordinary local identifiability itself is equivalent to zero being an isolated zero of the gauge-fixed nonlinear support map; it can hold even when the Jacobian is singular.

The printed Taylor estimate certifies only the radius min{1, gamma / C_H}. Scope K0 >= p - 1 to the differential full-rank count; higher-order terms can identify an isolated nonlinear zero with fewer rows.

### Theorem B

Append to the array assumptions:

> Along the triangular array, sigma_abs,N squared / W_N tends to zero and L_N (W_N/N) to the power beta tends to zero. For the high-probability version, the mixing envelope, subexponential norm, and block-variance bound are uniform in N in the displayed rate.

The exact pointwise condition is that the actual variance of the claimed window tends to zero; a uniform-in-n conclusion needs the supremum of those variances to vanish. The sigma_abs condition is sufficient. If the project intends constants independent of N, say so explicitly and define the uniform class. Do not use a triangular long-run-variance limit without uniform covariance-tail tightness.

### Theorem C

Use two theorem labels or two unmistakable parts:

1. **Blind high-count stationary-carrier theorem:** log record, unknown realized carrier, Theorem B assumptions.
2. **Oracle-known-carrier Poisson theorem:** conditional on known b_k, calibrated monotone inversion, finite-window D.8; general beta <= 1 unless moment-balanced/local-polynomial conditions are supplied.

For part 2, write the optimized result as an infimum over feasible W and present the power law only under an interior optimizer and uniform sensitivity.

### Theorem D

Lowest-cost contract:

> Under iid Gaussian noise with variance sigma squared, in the interior bandwidth regime, the matched-order estimator is minimax-rate optimal over the stated gauge-fixed Hölder class.

Higher-cost contract: define a product class of drift and noise laws, normalize its noise scale, prove the upper bound uniformly, and put the noise-law supremum in the minimax risk.

### Prop. 3

Keep two arms:

- **oracle-S1 theorem check** for (F.7)–(F.8);
- **estimated-S1 practical arm** with its own empirical boundary, or a new theorem including gamma = S1hat/S1 and the induced cross terms.

Do not use scale alignment to validate a raw-MSE identity.

For the blind arm, do not substitute scale-aligned gain_rel_mse for q_delta. Export the raw residual a / a_hat - 1, its second moment, its mean, temporal covariance, and residual–record-noise cross term; otherwise label the result a corrected scalar proxy rather than a theorem identity.

### Pair read noise

One safe sentence if no new regularized derivation is desired:

> With a fixed noiseless DC normalization, independent additive read noise contributes the stated linear term. For the noisy ratio, without denominator regularization its unconditional second moment is not finite. With iid equal-variance read noise in gain-corrected units, common known unit gain, no differential pair-gain mismatch, fixed true S1, and high SNR, the first-order aggregate term is 2 sigma squared times (1 + 1 / K_eff) divided by S2. Detector-domain noise under common gain a adds a factor a to the power minus two; unequal gains need the general delta-method expression. A clipped implementation has regularization-dependent risk.

## Regression checklist after repair

1. Run the full Python suite.
2. Add a unit test for the true-S1 implementation reproducing (F.7) numerically.
3. Add a test showing the median-normalized arm is labeled as a different estimator.
4. Add theorem-level counterexample tests/notes for Corollary 2 and the triangular array.
5. Regenerate affected summaries and figures from a clean committed tree.
6. Compile main and supplement; search logs for undefined references, overfull boxes, duplicate destinations, and missing citations.
7. Search the manuscript for ordinary-local iff, exact read-noise, scalar v_blind, becomes plain log, minimax full class, exchangeable, stationarity, and raw/scale-aligned.
8. Do not restore “scientific content frozen” until an independent reader can map every main-text theorem sentence to the narrowed appendix statement.
