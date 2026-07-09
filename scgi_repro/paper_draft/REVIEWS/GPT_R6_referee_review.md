# Paper review R6: convergence check on the R5 revision

> Provenance: GPT-5 Pro, 2026-07-10, chat "Paper review R6 summary" (review output in-chat; connector write
> surface unavailable — this file is the ledger). Reviewed commit a5d777d1 (MANUSCRIPT_DRAFT.md + APPENDICES.md
> + the R5 ledger).

## Executive judgment

**MINOR REVISION — accept after one tightly-scoped R7 correctness/integration round.** No further conceptual
or experimental work demanded. The revision substantively meets IEEE-TCI standards on concept, technical
depth, and reproducibility (appendices as archival proof package; convention box; bucket models; conditional
SRHT; broadened positioning; protocol enumerables; Fig. 3 uncertainty replication; new artifacts of real
scientific value — threshold panel separating rank wall from solver recovery, coherent-residual validation,
C0 audit, oracle/metered/blind baselines).

## B1–B10 verification

- B1 self-contained proofs: **resolved structurally** (remaining low-pass quantifier issue is a correctness
  point, R6-1, not a missing appendix).
- B2 conventions: **resolved.**
- B3 theorem-grade (★)/Thm B: **partial** — main-text Thm B omits the appendix's necessary asymptotic
  condition L·W^β→0 (or normalized-time equivalent). → R6-2.
- B4 bucket conventions: **resolved.**
- B5 conditional SRHT: **resolved.**
- B6 rho_pair/rho_bw: **not fully** — Sec. 8 still says the fast-drift noise-floor convergence happens
  "exactly as Theorem A′ demands" for a rho_pair sweep. → minor fix 5.
- B7 phase-diagram constants: **partial** — Table 1 reports leverage×N not C0 directly; no panel D_H range;
  boundary CIs deferred (acceptable if stated). → minor fix 6.
- B8 uncertainty: **partial** — Fig. 3 replication excellent; +5.45 dB ablation, winner maps, Brown–Forsythe
  proportions, correlation claims, flip-boundary locations still without intervals → label descriptive or add
  resampled summaries. → minor fix 8.
- B9 positioning: **resolved.**
- B10 hooks: **resolved** (the one leftover sentence falls under B6).

## Remaining blockers (R7 scope)

- **R6-1 (low-pass transfer quantifier gap).** Prop B.7 claims for generic M *every* nonconstant s∈S_LP has
  full rank; the proof establishes fixed-s genericity, and the union over the (p−1)-dim ratio family is not
  handled (positive-codimension bad sets can accumulate). Resolve by uniform avoidance/transversality OR
  weaken to the explicit hierarchy: generic-pair/local [proven] vs generic-object exact vs uniform per-object
  [dimension-count/heuristic + numerics]. Adjust every main-text sentence deriving from it.
- **R6-2 (Thm B scaling).** Add the normalized-time Hölder form |ℓ_j−ℓ_k| ≤ L(|j−k|/N)^β with bias
  O(L(W/N)^β), W→∞, W/N→0 (or triangular-array L_a with L_a W^β→0). Also separate Σ|γ(h)| (non-asymptotic
  bound) from the signed long-run variance γ(0)+2Σ_{h≥1}γ(h).
- **R6-3 (Thm 1 cross-covariance).** State the δ⟂ξ (uncorrelated) hypothesis in the main text; give the
  general identity with the cross term (2/S₂)tr[L diag(b) C_δξ Lᵀ]; keep the (a_n/â_n)² factor before the
  post-calibration simplification; scope E4 as validating injected residuals (not same-record dependence).
- **R6-4 (integration).** The new experiments exist as artifacts but are not integrated into Sec. 9 text
  (threshold scan, permutation power, E4, C0 audit, oracle baselines) — add passages/figure refs with correct
  theorem-level interpretation and uncertainty-or-descriptive labeling. NUMBER FIX: permutation-power mean
  rejection is 5.9% over the 320 permuted draws (70% for the 10-object ordered reference arm); the earlier
  7.9% pooled both arms — quote 5.9% with its exact denominator. Also: no predictive relation between the
  Walsh-flatness scalar and levene_p (Spearman 0.092, p=0.10).

## Minor fixes (12)

1. Threshold caption: N=K+p−1 transition verifies the LOCAL differential rank threshold (not generic-exact
   uniqueness N=K+p); solver wall = algorithmic recovery observation, not a uniqueness test.
2. (★): distinguish pointwise consistency from the displayed global max criterion (uniformity typically costs
   a log N / high-probability term).
3. Fig. 2 wording: tests the variance-stationarity CONSEQUENCE/diagnostic, not (★) directly (Brown–Forsythe
   tests chunk-variance equality; (★) concerns windowed log-carrier means).
4. Secs. 7/10 summary alignment: permutation ⇒ exchangeability; Walsh-flatness covariance guarantee is the
   sign-randomization statement after permutation; unpack the compressed Sec. 10 phrasing.
5. Sec. 8: delete/soften the remaining "exactly as Theorem A′ demands" sentence (use the Sec. 9 wording).
6. Table 1: report C0 itself (or state C0 = leverage×N − 1); give min/median/max of D_H over the panel
   [measured: 0.971/0.988/0.999]; prefer Var(δ) for v_blind rather than equating it to the squared
   scale-aligned gain-error norm.
7. Sec. 8/Fig. 4: separate identity verification (raw MSE) from the scale-aligned image metric; let the E4
   raw-residual panel carry the identity-verification role.
8. Sec. 9 uncertainty: intervals or resampled summaries for +5.45 dB, rejection proportions, winner/boundary
   summaries — else present as descriptive results of the specified grid.
9. Fig. 7 bias/variance decomposition below crossover: either add it or drop any wording implying all 28 R5
   fixes are complete (the deferral note stands, but R5 fix #17 is then open).
10. Remove "/ issue #N" development pointers from proof references (archival: "Proof: Appendix X" only).
11. Appendix F / Prop 3: replace the unconditional monotone-crossing claim with an explicit single-crossing
    assumption (v_blind(ρ,N) also varies with ρ; the existence/uniqueness step is heuristic).
12. References: normalize to IEEE format; use journal/conference metadata over arXiv where final versions exist.

## Convergence verdict

**Needs R7** for: the low-pass quantifier, the missing Thm B scaling, the Thm 1 cross-covariance condition,
and the integration + uncertainty labeling of the newly completed experiments. "This should be a narrow
verification round, not another open-ended review cycle. Once these four are confirmed, I support submission
to IEEE-TCI without demanding additional conceptual experiments."
