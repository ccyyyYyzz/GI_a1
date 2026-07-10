# GPT Pro collaboration log

Date: 2026-07-10  
Pinned repository snapshot: 402c8d6db9d8fc4dce225700f0b6a3561885009e  
Access mode: the user's logged-in Chrome Pro session, with the GitHub plugin used to inspect the named branch/files.

The browser discussions were independent adversarial checks, not the source of record. Every central conclusion below was also checked against the local immutable snapshot, by direct algebra/numerics, or by an independent R14 QA pass.

## Session A — Theorems B–D and Corollary 2

Conversation: https://chatgpt.com/c/6a5149b6-e600-83ed-a8d4-1ed124574022  
Title: Proof check and analysis

### Prompt A1 — Theorem C/D scope and finite-N minimax rate

> Independent proof check. Public repo ccyyyYyzz/GI_a1, branch scgi-ceiling-diagnostic-r1, HEAD 402c8d6. Inspect body.tex Theorem C/D and appendix D.1–D.4. The main theorem appears to omit beta/window/known-carrier restrictions; D.9/D.5 optimize an unconstrained interior bandwidth and the Gaussian-submodel argument may not define the noise-law supremum. Re-derive the finite-window result, beta greater than one scope, finite-N lower bound, and the exact experiment over which minimaxity follows. Give minimal safe replacement statements.

### A1 conclusion

GPT Pro agreed that the main-text theorem contract is broader than the proofs and recommended:

- split blind high-count estimation from the oracle-known-carrier Poisson experiment;
- keep D.8 as the finite-window master result;
- optimize only over feasible windows with positive sensitivity and present D.9 only in its interior regime;
- use the finite-N lower envelope

\[
c_\beta\sup_{1\le W\le W_{\max}}
\min\{L_a^2W^{2\beta},\sigma^2/W\},
\]

or the equivalent one-frame/interior/full-record three-regime form;
- restrict the general arbitrary-carrier/simple-window theorem to beta <= 1, with balanced-window or proved local-polynomial statements treated separately;
- state Theorem D either for fixed iid Gaussian noise or define a normalized product minimax class with an explicit supremum over noise laws.

It also confirmed that a Gaussian lower bound does not establish minimaxity for every fixed non-Gaussian mixing law.

### Prompt A2 — Theorem B triangular array and Corollary 2

> Second independent check. At appendix_body.tex 374/465/471 Theorem B is triangular-array but only requires sigma_abs,N squared finite rowwise. Counterexample: z_{N,n} iid N(0,N), ell=0, W=floor(sqrt N); all stated rowwise mixing/moment and W conditions hold, yet Var(window mean)=N/W tends to infinity. Is the consistency theorem false without sigma_abs,N squared / W_N tending to zero or uniform envelopes? Also audit Corollary 2 lines 65–107: H=[[1,0,0],[0,1,0],[-1,2,1]], T=(1,1,0), Omega={1,2}, u=(-1,0,1), S=span{1,u}. The linear kernel has u, but F(tu)=2(cosh t-1)>0 for nonzero t. Does this disprove the claimed ordinary-local iff while preserving differential iff and rank sufficiency? Give exact minimal replacements.

### A2 conclusion

GPT Pro's opening verdict was “yes on both points.”

For Theorem B it confirmed:

- the literal triangular-array consistency conclusion is false;
- the exact pointwise L2 condition is vanishing actual window variance plus vanishing smoothing bias;
- sigma_abs,N squared / W_N tending to zero is sufficient but not necessary because signed covariance cancellation can help;
- a uniform-in-n claim needs the supremum of window variances to vanish;
- the high-probability constants/envelopes must be uniform in N;
- a triangular long-run-variance limit needs uniform covariance-tail tightness, otherwise the exact finite-window covariance sum must be retained.

For Corollary 2 it independently multiplied the matrices and confirmed:

- the extra direction u lies in the first-order kernel;
- every s in S can be written a times the all-ones vector plus t u;
- the exact support map is 2 exp(-a) times (cosh t minus 1), so its only zero is the gauge line;
- the example is ordinarily identifiable modulo gauge even though differential identifiability fails.

It recommended the exact split:

1. differential identifiability iff the quotient Jacobian has full column rank;
2. that rank condition implies ordinary local identifiability;
3. ordinary local identifiability iff zero is an isolated zero of the gauge-fixed nonlinear support map.

It also caught two refinements incorporated into this package: the appendix's Taylor estimate certifies min{1, gamma / C_H}, and K0 >= p - 1 is only a differential full-rank count, not a necessary count for higher-order ordinary identifiability.

## Session B — Prop. 3, read noise, and reconstruction bridge

Conversation: https://chatgpt.com/c/6a514ec1-97f8-83eb-845b-a97d22d6fde4  
Title: Independent adversarial proof check

### Prompt B1

> Independent adversarial proof check. Repo ccyyyYyzz/GI_a1, branch scgi-ceiling-diagnostic-r1, HEAD 402c8d6. Inspect appendix_body.tex F.3.2/F.4 and src/mechanisms.py:480–490 plus run_prop3_raw_metric_export.py. (1) F.7 uses true S1 but code sets S1hat=median(pair_sum). Derive the exact coefficient error for S1hat=gamma*S1 and decide whether the current raw-MSE crossing is a same-estimator validation. QA facts: true-S1 exact-law max relative error 1.66e-6; current versus true-S1 nine-point median/max boundary factor 1.0439/1.1999 versus 1.0204/1.0369; slopes current -2.0066, true-S1 -2.1204, predicted -2.1137. (2) Is appendix:1433 exact read-noise risk 2*sigma squared/S2 valid for an unregularized ratio with Gaussian noise in the denominator? (3) Can body:245 scalar v_blind apply to a same-record overlapping-window estimator given Appendix:1512? (4) Is body:241 “orthogonal inversion is the best conduit” universal? Test K=1, A=(1,1) transpose, L=(1/2,1/2). Give exact verdicts and minimal safe wording/experiment.

In the submitted prompt, “nine-point” was shorthand for the nine-rho grid; the median/max factors aggregate 40 observed crossings on that grid.

### B1 conclusion

GPT Pro independently inspected the files, symbolically checked the normalization algebra, and returned four exact verdicts:

1. **Estimator mismatch confirmed.** For S1hat = gamma S1,

\[
\widehat c_k-c_k
=S_1\frac{2x_k(\gamma-1)-\Delta_k(1-x_k)(\gamma+x_k)}
{2+\Delta_k(1-x_k)}
=\gamma e_{k,\mathrm{F.7}}+(\gamma-1)c_k.
\]

Thus the raw risk contains the global scale error, a changed F.7 term, and their cross term. The current median-normalized crossing is a production-estimator robustness check, not a same-estimator validation. GPT Pro accepted the true-S1 QA numbers as the matched validation.

2. **Exact Gaussian ratio-risk claim rejected.** With iid equal-variance Gaussian read noises, the pair sum and difference noises are independent; the denominator has positive density at zero while the conditional numerator variance is positive. The unregularized ratio has infinite MSE. In gain-corrected units, with common known unit gain, no differential pair-gain mismatch, fixed true S1, and high SNR, the first-order aggregate term is

\[
\frac{2\sigma_{\mathrm{read}}^2}{S_2}
\left(1+\frac{1}{K_{\mathrm{eff}}}\right),
\]

while a clipped implementation has regularization-dependent risk. The displayed product is intended as 2 sigma-read squared divided by S2, multiplied by the parenthesis. Detector-domain noise under a common gain a adds a factor a to the power minus two; unequal pair gains require the general delta-method expression.

3. **Scalar blind term rejected as an identity for the implemented estimator.** The body should use a general Gamma_blind. The scalar specialization is valid only for exogenous, centered, frame-uncorrelated residuals. A same-record overlapping-window estimator needs residual mean, projected temporal covariance, and residual–record-noise cross terms. GPT Pro also confirmed that the runner substitutes scale-aligned gain error for raw q_delta.

4. **Universal “best conduit” claim refuted.** For K=1, A=(1,1) transpose and L=(1/2,1/2), LA=1, the reconstruction floor is zero, and B_L=1/2. More generally N repeated scalar measurements averaged by a left inverse give B_L=1/N under independent per-frame residuals.

The proposed minimum experiment is exactly the handoff in 04_PATCH_MAP.md: export true-S1 and median-normalized arms on identical objects/OU paths, test each against its own exact law, log gamma and the normalization cross term, and use projected covariance components rather than a full dense covariance matrix for the blind bridge.

## Cross-session consensus

The webpage collaborator and the local R14 reviewers independently converged on the same publication disposition:

- current snapshot is not science-frozen;
- the central ideas survive, but theorem quantifiers and estimator/metric identities must be narrowed;
- the most efficient repair is statement-level honesty plus two matched QA arms, not another broad theorem;
- D.8, the direct Poisson lower-bound route, Theorem A/A-prime's proved scopes, and the true-S1 F.7 algebra should be preserved.
