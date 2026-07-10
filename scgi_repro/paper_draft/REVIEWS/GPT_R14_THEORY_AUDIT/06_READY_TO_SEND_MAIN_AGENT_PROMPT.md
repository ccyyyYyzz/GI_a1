# Prompt to send directly to the main project agent

You are repairing the SCGI manuscript and its theorem-validation contract after an independent R14 audit.

Repository: https://github.com/ccyyyYyzz/GI_a1  
Branch: scgi-ceiling-diagnostic-r1  
Required base: 402c8d6db9d8fc4dce225700f0b6a3561885009e

Read these new audit files first:

1. paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/00_README.md
2. paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/01_BLOCKING_FINDINGS.md
3. paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/02_COUNTEREXAMPLES_AND_PROOF_NOTES.md
4. paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/03_EMPIRICAL_AND_REPRO_QA.md
5. paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/04_PATCH_MAP.md
6. paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/05_GPT_PRO_COLLAB_LOG.md

The current snapshot is **not science-frozen**. Items 1–6 below are hard blockers; the remainder are important scope and consistency repairs. This summary is not a substitute for the ledger: close **every High and Medium finding in 01_BLOCKING_FINDINGS.md, including M1–M15**.

1. Corollary 2’s ordinary-local iff necessity is refuted by the explicit H, T, u counterexample. Split differential identifiability from ordinary local identifiability.
2. Theorem B’s triangular-array convergence is false without sigma_abs,N squared / W_N tending to zero or equivalent uniform assumptions. The iid N(0,N), W=sqrt(N) example must violate a stated hypothesis after repair.
3. Theorems C–D must carry finite-window feasibility/saturation, beta/window-order, sensitivity, and statistical-experiment scope. Split blind high-count from oracle-known-carrier Poisson. State minimaxity either for fixed iid Gaussian noise or with an explicit supremum over a normalized noise-law class.
4. (F.7) assumes true S1, but mechanisms.py uses median(pair_sum). Add an oracle-true-S1 QA arm or extend the theorem to the implemented normalization; do not call the current raw export a same-estimator exact validation.
5. The unregularized Gaussian random-denominator ratio has infinite second moment. Remove “exact 2 sigma_read squared / S2” unless normalization is fixed/noiseless or a regularized estimator is defined and analysed.
6. Restrict scalar v_blind to exogenous centered frame-uncorrelated residuals. A same-record overlapping-window estimator requires Theorem 1’s full covariance, mean, and residual–noise cross terms. The current runners also substitute scale-aligned gain_rel_mse for raw q_delta; export the actual residual a / a_hat - 1 and do not call the proxy exact.
7. Remove or scope the claim that orthogonal inversion is universally the best conduit: the K = 1 repeated-measurement left inverse in the audit has B_L = 1/2 with zero floor.
8. Scope Theorem B’s “only ambiguity” to centered gain in its bucket-only marginal experiment; exchangeable-coordinate object permutations remain marginally indistinguishable. Do not apply that example to a joint experiment where realized patterns are observed.
9. Do not apply a direct Poisson intensity model to signed orthogonal coefficients without physical pairing or an offset.
10. Either prove the K0 >= p - 1 generic known-zero sufficiency with an explicit full-rank witness or downgrade it to a dimension-count prediction conditional on the rank test.
11. Treat N = K + p - 1 separately from genuine below-wall failure. Below the local wall say that additional information is required, with stationarity/support/sparsity as nonexhaustive examples.
12. Add cross-frame conditional independence to D.4, correct the log-gain parameterization in Remark D.4.1, and restore beta0 in the high-probability block length.

Work requirements:

- Preserve all correct R13 repairs, especially D.8/D.8b, D.10, D.11–D.12, D.4.3, D.4.4, the beta-greater-than-one obstruction and partial repair in Remark D.4.2/(D.14), oracle-versus-blind separation, Theorem A-prime’s proved thresholds, and the P_col/D versus P_row distinction.
- Modify all synchronized sources: LaTeX, Markdown masters, captions, summaries, runners, tests, and manifests where the estimator or metric changes.
- Prefer narrowing a theorem over adding an unproved claim.
- For every claimed validation, make equation, estimator, normalization, loss, and data product identical.
- Add regression tests for the true-S1 (F.7) arm and preserve the practical median-normalized arm under a distinct label.
- Rerun affected authoritative results from a clean committed snapshot; do not reuse the dirty older Prop. 3 manifest as final evidence.
- Recompile main and supplement and rerun the full test suite.

Deliverables:

1. A finding-by-finding closure ledger quoting the exact new theorem wording and proof location.
2. The corrected finite-window and minimax statements, including all quantifiers.
3. A regenerated Prop. 3 QA table showing theorem-faithful and practical estimators separately.
4. Fresh manifests and exact commands for every changed result.
5. Full test and LaTeX logs, plus page counts.
6. A final grep-based claim audit for the risky phrases listed in 04_PATCH_MAP.md.

Do not mark the work complete merely because tests compile. Completion means each explicit counterexample is excluded by a stated hypothesis or the contradicted claim has been removed, and every empirical validation is for the same estimator and metric as its theorem.
