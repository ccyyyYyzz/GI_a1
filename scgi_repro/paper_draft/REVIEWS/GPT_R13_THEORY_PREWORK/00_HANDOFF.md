# R13 theory prework handoff

This directory is an additive, sidecar-only deliverable.  No existing
manuscript, code, test, result, manifest, or review-ledger file was modified.

Repository baseline:

- repository: `https://github.com/ccyyyYyzz/GI_a1`
- branch: `scgi-ceiling-diagnostic-r1`
- audited commit: `bcbb31254c343eb04e8cb96d7c3157bfc9818b36`
- GPT Pro conversation:
  `https://chatgpt.com/c/6a50f91d-88a0-83eb-8c24-782866fe8324`

The material is intentionally not included from `main.tex` or
`supplement.tex`.  It is a reviewed source packet for the primary project
agent to move selectively into the active manuscript.

## Files

| file | purpose |
|---|---|
| `01_D8_KNOWN_CARRIER_REPLACEMENT.tex` | Stronger finite-window soft-log theorem, global clamped-inverse bound, calibration stability/certificate, corrected low-photon term, beta scope, oracle/known-law/blind split |
| `02_F8_PROP3_REPLACEMENT.tex` | Correct pairwise second moment, OU moments, three-way constant bookkeeping, raw-MSE Prop. 3, OU window risk, metric cautions |
| `03_IDENTIFIABILITY_LOWER_FISHER_PERMUTATION.tex` | Exact gauge collision, quotient Fisher, pointwise Le Cam, integrated Assouad, oracle local-shift Fisher, row/pixel permutation distinction |
| `04_C0_METRIC_REAUDIT.md` | Independent reproduction showing that the former factor 1.54 is a raw/aligned metric mismatch; raw-vs-raw median factor 1.044 |
| `05_MAIN_AGENT_PATCH_MAP.md` | Ordered integration map, source line targets, required exports/tests, and acceptance gates |
| `06_GPT_PRO_COLLAB_LOG.md` | GPT Pro task trace, consensus, additions, and the one resolved proof divergence |
| `07_READY_TO_SEND_MAIN_AGENT_PROMPT.md` | Complete Chinese execution prompt that can be sent directly to the primary project agent |
| `99_FRAGMENT_SMOKE.tex` | Standalone syntax harness for the three additive LaTeX fragments; not part of either manuscript build |

## Load-bearing conclusions

1. The exact endpoint-clamped inverse is globally
   `1 / kappa`-Lipschitz.  Its exact finite-window risk is
   \[
   (B_n^2+V_n)/\underline\kappa_n^2,
   \]
   with no separate clamp-event risk.  Under a monotone approximate curve,
   a uniform response error contributes
   `epsilon_cal / kappa`; a log-parameter bisection error contributes
   `epsilon_bis` directly.
2. The general low-photon stochastic term is
   \[
   {\sum_k w_{nk}^2\lambda_k(\ell_k)
    \over
    [\sum_k w_{nk}\lambda_k(\ell_n)]^2},
   \]
   not unconditionally `1 / (W * lambda_bar)`.  The two-frame
   `ell=(0, log 2)` example produces a persistent factor `3/2`.
3. The arbitrary-carrier theorem is general only for `0 < beta <= 1`.
   For `1 < beta <= 2`, sensitivity-weighted first-moment balance is
   required.  Current truncated edge windows fail this balance even under a
   homogeneous carrier.
4. The low-photon implemented estimator is oracle-known-carrier.  A known
   carrier law yields a different law-calibrated estimator; an unknown law
   leaves an unknown nonlinear response and is not covered by the current
   proof.
5. F.8 must use `E[Delta^2]`, not `Var(Delta)`, unless `E[Delta]=0` is
   separately assumed.  The OU leading term survives because the omitted
   mean-square term is higher order.
6. Prop. 3 needs raw risk throughout.  The former `C0=624--715` is an
   aligned floor, while the theorem-compatible fixed-design raw floor is
   `980--1115`.  Reconstructing raw-vs-raw crossings changes the median
   factor from about `1.54` to `1.04387`.
7. The OU path is not Lipschitz.  An interior centered window has stochastic
   drift error `s^2 rho W / 6` to first order and optimized risk proportional
   to `rho^(1/2)`, not `rho^(2/3)`.
8. The plotted `sum lambda_k` line is an oracle common-shift reference, not
   the nuisance-path quotient CRB; position above it cannot establish
   unbiasedness.
9. Acquisition-order permutation is exchangeable over its randomization
   draw.  One common pixel permutation gives equal non-DC marginals and the
   stated variance, but not full joint row exchangeability.

## What does and does not require computation

No new physical simulation is needed for the proof repairs.  One small
provenance-bearing re-export is needed if the paper keeps the strict
no-free-parameter Prop. 3 claim: compute raw reconstruction risk and raw
crossings from the already generated trajectories.  A separate interval or
analytic certificate is needed before the empirical midpoint calibration
error is inserted as a theorem-level uniform bound.

The equation tags in the `.tex` fragments end in `-R13` to avoid pretending
they are final manuscript numbers.  The integrating agent must renumber them,
add `\label`/`\ref`, and synchronize the Markdown mirrors.

## Integration status

- proof derivations: independently reproduced;
- formula/assumption QA: completed;
- standalone fragment compile: passed (14-page smoke PDF, no undefined control sequence; temporary output generated outside the repository and cleaned);
- GPT Pro comparison: completed for Appendix D;
- active manuscript integration: deliberately not performed;
- commit/push: deliberately not performed.
