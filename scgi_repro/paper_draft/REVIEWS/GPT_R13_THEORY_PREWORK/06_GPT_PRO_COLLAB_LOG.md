# GPT Pro collaboration trace

Conversation:
`https://chatgpt.com/c/6a50f91d-88a0-83eb-8c24-782866fe8324`.

Account/model surface: existing signed-in ChatGPT Pro session.  The primary
R13 response reported `Worked for 17m 21s`.

## Task given to GPT Pro

GPT Pro was pointed directly at the public GitHub repository, branch, commit,
and the exact Appendix D/body/runner files.  It was asked to rebuild rather
than defend the existing theorem and to provide:

- a finite-window known-carrier soft-log theorem;
- the corrected true-path/anchor-path low-photon term;
- beta scope and first-moment obstruction;
- oracle/known-law/blind separation;
- calibration/bisection units;
- Fisher scope;
- ready-to-paste LaTeX and adversarial checks.

## Consensus

GPT Pro independently agreed that:

1. the current unconditional `1/(W lambda_bar)` corollary is fatal as stated;
2. the general leading term must retain actual `lambda_k(ell_k)` in its
   numerator and anchor `lambda_k(ell_n)` in its sensitivity denominator;
3. arbitrary-carrier smoothness is general only for `beta <= 1`;
4. `beta > 1` needs sensitivity-weighted moment balance and does not cover
   the current truncated boundary windows;
5. the implemented low-photon arm is oracle-known-carrier;
6. unknown carrier law produces an unknown nonlinear response, not one gauge
   scalar;
7. the plotted `sum lambda` line is an oracle common-shift benchmark rather
   than a nuisance-path quotient CRB;
8. response-domain calibration error and log-parameter bisection error cannot
   be added before division by sensitivity;
9. the midpoint calibration probe is empirical rather than a theorem-level
   uniform certificate.

## GPT Pro additions adopted here

- explicit calibration-safe interval and the possibility that it is empty;
- a log-intensity interpolation certificate
  `Delta_x^2 * sup|f''| / 8`, with Poisson-difference expression for `f''`;
- the need to certify Poisson tail/tabulation error separately;
- a known-carrier-law mixed-Poisson extension distinct from the realized
  known-carrier estimator;
- explicit warning that low total information leads to clamp saturation,
  so the inverse-information expression is only a localized variance regime.

## One proof divergence and its resolution

GPT Pro's first response retained an explicit clamp-event residual because it
analyzed the approximate inverse only on a no-clamp event.  Two independent
local derivations and a separate formula QA established a stronger result:

For continuous strictly increasing `M` on one compact interval with
`inf M' >= kappa`, the endpoint-clamped inverse

\[
G(y)=M^{-1}(\Pi_{M(\Theta)}y)
\]

is globally `1/kappa`-Lipschitz.  If `M_tilde` uses the same interval and
inverse convention and `sup|M_tilde-M| <= epsilon`, inverse bracketing gives

\[
G(y-\epsilon)\le \widetilde G(y)\le G(y+\epsilon),
\qquad
\sup_y|\widetilde G(y)-G(y)|\le\epsilon/\kappa.
\]

Therefore the global RMSE bound in file 01 needs no separate clamp-event
risk.  This stronger conclusion fails only if the safe interval is empty,
the numerical curve is not monotone, the two inverses use incompatible
endpoint conventions, or the stated uniform response bound is unavailable.
Clamp probability remains useful as a diagnostic.

A targeted browser follow-up asking GPT Pro to adjudicate this stronger lemma
could not be completed after the Chrome extension connection became unstable.
The sidecar package therefore records both the first-response provenance and
the independently checked stronger proof instead of implying GPT Pro endorsed
the final strengthening.

## Work discovered after the GPT Pro D.4 task

The F.8/Prop. 3 raw-versus-aligned metric audit in file 04 was performed and
independently reproduced after the D.4 prompt.  It was not part of GPT Pro's
17-minute response, so no GPT Pro endorsement is claimed for those numerical
recomputations.
