# Main-agent integration map

All line numbers refer to commit
`bcbb31254c343eb04e8cb96d7c3157bfc9818b36`.  Apply the steps in order;
later steps depend on notation introduced earlier.

## 1. Rebuild Appendix D.4 first

Target:

- `paper_draft/latex/appendix_body.tex:589--700`
- `paper_draft/latex/appendix_body.tex:780--853`
- `paper_draft/latex/appendix_body.tex:795`
- corresponding sections of `paper_draft/APPENDICES.md`

Source material: `01_D8_KNOWN_CARRIER_REPLACEMENT.tex`.

Required actions:

1. Replace event-split inversion by the globally Lipschitz endpoint-clamped
   inverse.  Keep a clamp probability only as a diagnostic, not an added risk
   term.
2. Define the calibration-safe interval and explicitly require it to be
   nonempty.
3. Keep `B_n` and `V_n` evaluated at the actual path.  Replace every
   unconditional `1/(W lambda_bar_n)` display by the `D_n/A_n^2` expression;
   add local gain flatness before simplifying it.
4. Restrict the arbitrary-carrier theorem to `beta <= 1`.  For `1 < beta <=
   2`, state an interior sensitivity-balance result only.  Current truncated
   edge windows are not covered.
5. Use
   `(epsilon_cal/kappa + epsilon_bis)^2` or the RMSE/Minkowski version.
   `epsilon_bis` is already in log-parameter units.
6. Replace literal calibration placeholders with measured values only as
   empirical diagnostics.  Add the interpolation certificate before calling
   `epsilon_cal` a uniform theorem-level bound.
7. State conditional count independence in the theorem assumptions.
8. Separate oracle-known-carrier, known-law, and unknown-law cases.

Acceptance checks:

- the `W=2`, `ell=(0,log 2)` calculation yields `3/(4 epsilon)`;
- an all-zero window remains finite without a separate risk event;
- internal equal-carrier windows recover the nominal term under local
  flatness;
- the first truncated window does not receive a `beta > 1` claim.

## 2. Synchronize the main Theorem C narrative

Targets:

- `paper_draft/latex/body.tex:14`
- `paper_draft/latex/body.tex:167--181`
- `paper_draft/latex/body.tex:304--309`
- `paper_draft/latex/body.tex:344`
- `paper_draft/MANUSCRIPT_DRAFT.md`

Required actions:

1. Keep Theorem B as the blind high-count stationary-carrier result.
2. Label the Poisson theorem and current Fig. 5 arm
   `oracle-known-carrier` (or known-law if that separate estimator is
   introduced).  Do not fold it into an unknown-law blind claim.
3. Replace the invalid vector expression `(a,T)->(a s^{-1},sT)` by the
   collision curve from file 03.
4. Call `mean_n[1/I_n]` an oracle common-shift diagnostic.  Delete
   `no bias crossover`, `Fisher-matched`, and `only arm` interpretations.
5. State that the actual figure contains five methods, define the error bars
   as SD over 50 object-by-seed cells, and distinguish requested width 64
   from effective interior width 65.
6. Narrow the conclusion: blind high-count minimax rate plus a separate
   known-carrier/known-law Poisson bound.

## 3. Replace F.8 and restructure Prop. 3

Targets:

- `paper_draft/latex/appendix_body.tex:1267--1278`
- `paper_draft/latex/appendix_body.tex:1280--1316`
- `paper_draft/latex/body.tex:261--302`
- corresponding Markdown mirrors

Source material: `02_F8_PROP3_REPLACEMENT.tex`.

Required actions:

1. Replace `Var(Delta)` by `E[Delta^2]`; add the exact OU lognormal moments.
2. Reserve distinct names for:
   - raw fixed-design sampling floor;
   - residual/Poisson leverage `Lambda_lev = N B_L`;
   - population raw-moment constant.
3. In Table I relabel `7.38--7.68e5` as `Lambda_lev`, not pipeline sampling
   `C0`; describe it as a Monte Carlo residual-probe mean, not deterministic.
4. Make the gain-known raw-MSE skeleton the rigorous proposition.  Treat a
   scalar blind term as conditional on exogenous, centered, frame-uncorrelated
   residuals.  Same-record blind estimation requires the full covariance and
   cross terms.
5. If `Q` depends on `rho`, call the logarithmic equation a fixed point, not
   an explicit solution.  State `A_T>0`, continuity, and single-crossing
   assumptions.
6. Do not attribute a `rho^(2/3)` estimator rate to OU paths.  Either use the
   OU lemma or treat blind residual risk as an externally measured function.

## 4. Correct the Prop. 3 validation metric

Evidence: `04_C0_METRIC_REAUDIT.md`.

Source locations:

- `run_prop3_boundary.py:132--137`
- `run_mechanism_m1.py:77--86`
- `results/prop3_nofreeparam_r1/prop3_constants.csv`

Required decision:

- Preferred: add a raw-risk export from existing generated reconstructions,
  regenerate raw crossings, and report `40/40`, median factor `1.04387`, max
  factor `1.19985` for `sigma_a >= 0.1`.
- Lowest-change alternative: keep the aligned output but call it a
  `scale-aligned empirical analogue`; it is not a direct validation of the
  raw theorem.

In either case delete the statement that factor `1.54` is consistent with the
F.8 cubic remainder.  The raw/aligned floor ratio itself is `1.5398517`.

## 5. Move gauge, lower-bound, Fisher, and permutation material

Source material: `03_IDENTIFIABILITY_LOWER_FISHER_PERMUTATION.tex`.

Targets:

- main-text gauge sentence: `body.tex:181`;
- quotient Fisher discussion: `appendix_body.tex:565--585`;
- direct Poisson lower bound: `appendix_body.tex:702--778`;
- pixel-permutation claim: `appendix_body.tex:1121` and Appendix E narrative.

Required actions:

1. Use the exact square-design collision and its tall-design range condition.
2. Keep Le Cam for pointwise loss; use the guarded Assouad hypercube for
   integrated quotient loss.
3. Keep all lower-bound alternatives independent of realized random carriers;
   use joint-oracle expected KL before marginalization.
4. Retain the oracle local-shift Fisher formula only with its restricted
   parametric meaning; use the Schur complement for an explicitly chosen
   nuisance model.
5. Attribute full exchangeability to acquisition-order randomization.  For
   pixel permutation retain equal non-DC marginals/variance and the Walsh
   triple-moment counterexample.

## 6. Minimal computation and tests

No physics rerun is required.  The main agent should add:

1. a provenance-bearing raw floor/raw crossing export;
2. a certified calibration-envelope artifact or explicitly retain the
   empirical label;
3. unit tests for exact root, all-zero clamp, edge membership/interior
   identity, centered-log projection, and local Fisher;
4. a regression test distinguishing raw and scale-aligned Prop. 3 constants;
5. a small symbolic/numeric test for the F.8 deterministic-Delta
   counterexample.

## 7. Final acceptance gates

- all equation tags from the sidecar fragments have been renumbered and
  referenced;
- LaTeX and Markdown mirrors agree on figure/table numbering and theorem
  scope;
- no `XX...XX`, old Fig. 7/S2/S3 reference, or `only arm` claim remains;
- the abstract and conclusion no longer merge blind high-count and oracle
  low-photon results;
- Table I cannot be misread as supplying the Prop. 3 floor constant;
- every Prop. 3 prediction and observation uses the same raw/aligned metric;
- full tests and both PDFs compile cleanly.

