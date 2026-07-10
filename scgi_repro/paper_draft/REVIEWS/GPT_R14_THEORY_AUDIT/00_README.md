# R14 theory and submission audit

Base snapshot: 402c8d6db9d8fc4dce225700f0b6a3561885009e  
Branch: scgi-ceiling-diagnostic-r1  
Audit date: 2026-07-10  
Repository: https://github.com/ccyyyYyzz/GI_a1

## Verdict

**NO-GO for declaring the scientific content frozen or submission-ready.**

The implementation, tests, LaTeX build, and rendered PDFs are healthy. The blocker is the mathematical contract: several current statements are broader than their proofs, and two statements admit explicit finite-dimensional or triangular-array counterexamples. The most important issues are:

1. Corollary 2 conflates differential and ordinary local identifiability; its ordinary-local “if and only if” necessity is false.
2. Theorem B is stated for a triangular array but lacks a uniform variance/tail condition; its displayed convergence need not hold.
3. Theorem C/D optimize interior asymptotic rates without consistently carrying finite-window feasibility, class-diameter saturation, beta/window-order restrictions, sensitivity bounds, and the statistical experiment over which minimaxity is claimed.
4. The raw-MSE Prop. 3 validation does not use the estimator assumed by (F.7): the proof uses the true S1, while the implementation estimates S1 by the median pair sum.
5. The claimed exact Gaussian read-noise risk for a ratio estimator is not finite without regularization of the random denominator.
6. The main-text scalar v_blind formula is not valid for the same-record overlapping-window estimator; Appendix F already says the full covariance and cross terms are required.

These are repairable. The shortest safe path is to narrow the statements to what is proved, add the missing uniform/finite-sample hypotheses, and either add an oracle-S1 QA arm or extend the Prop. 3 theorem to the implemented normalization.

## Contents

- 01_BLOCKING_FINDINGS.md — severity-ranked findings with impact and minimum fix.
- 02_COUNTEREXAMPLES_AND_PROOF_NOTES.md — self-contained counterexamples and corrected theorem forms.
- 03_EMPIRICAL_AND_REPRO_QA.md — test, PDF, provenance, and Prop. 3 numerical QA.
- 04_PATCH_MAP.md — file-by-file minimum repair map; no source file was edited by this audit.
- 05_GPT_PRO_COLLAB_LOG.md — prompts and independent conclusions from the GPT Pro browser session.
- 06_READY_TO_SEND_MAIN_AGENT_PROMPT.md — a prompt that can be sent directly to the main project agent.

## Audit boundary

This audit added only files under this directory. It did not modify, commit, or push any existing project file. All line references point to the base snapshot above and may move after repair.

## Checks that passed

- Local HEAD, origin tracking ref, and remote ls-remote all matched the full base SHA.
- Full Python test suite: 70 passed.
- Fresh LaTeX builds: main 13 pages; supplement 32 pages.
- No undefined references and no overfull boxes in the fresh builds.
- Sampled-page visual QA found no clipping, overlap, black boxes, or illegible equations.
- D.8/D.8b clamped-inverse argument, D.10 local-flat Poisson simplification, D.11–D.12 Poisson lower-bound route, Theorem A, the proved Theorem A-prime thresholds, and the noiseless algebra of (F.7)–(F.8) survived targeted review within their stated scopes.

## Non-theory submission decisions still open

- Final author and affiliation block.
- Supplement length strategy/editorial approval.
- MIT licence confirmation.
- Removal of DRAFT / INTERNAL REVIEW labels when and only when the mathematical blockers are closed.

