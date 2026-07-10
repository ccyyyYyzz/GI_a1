# FIX NOTE — Fig. 5 / Prop 3 (audit blocker P0-4)

Status: analysis complete; evidence in `results/prop3_nofreeparam_r1/`
(`summary.md` there has the full numbers). This note gives the drafting pass
exact replacement text. No manuscript/LaTeX files were edited.

All four audit sub-findings are CONFIRMED:
(a) every R^2 >= 0.9 crossing in Fig. 5 is SRHT-paired vs ordered Hadamard
    (within-correction strata: none / reference_k8 / reference_k32 /
    scgi_proxy) — the Prop-3 arm pair (pairwise Hadamard vs blind random+DGI)
    is never compared anywhere in the published boundary tables, because the
    audit script only compares arms within the same correction and
    `pairwise` exists only for paired bases;
(b) the plotted curves are two-free-parameter power-law fits
    rho* ~ sigma_a^a with fitted exponents -0.94, -1.10, -1.93, -1.59 — not a
    prediction from measured constants (and not even consistently the
    sigma^-2 form Prop 3 implies);
(c) the counts are wrong: the grid is 45 cells, 29 above-floor, 28 won by
    SRHT-paired+pairwise, 1 by hadamard_random_paired+scgi_proxy, 16 floor;
(d) no winner/phase-map panel exists — Fig. 5 is only the rho*-vs-sigma_a
    fit scatter.

## 1. Corrected counts — exact replacement text

WRONG sentence (MANUSCRIPT_DRAFT.md, "Phase diagram and ablation" paragraph,
~line 254):

> "It is numerically demonstrated that SRHT-paired acquisition with pairwise
> correction wins all 28 above-floor cells of the 44-cell winner map; the
> remaining 16 cells are honestly labeled noise floor rather than assigned a
> winner, and the flip-boundary fits reach $R^2 = 0.989$–$0.9995$ against the
> closed form of Prop 3 (...)"

REPLACEMENT:

> "The equal-frame winner map has 45 cells (9 drift rates $\times$ 5 noise
> levels), of which 29 are above floor: SRHT-paired acquisition with pairwise
> correction wins 28 of the 29; one cell ($\rho_{\mathrm{pair}}=0.3$,
> $\sigma_a=0.15$) goes to randomly ordered pairwise Hadamard with the
> SCGI-proxy correction; the remaining 16 cells are labeled noise floor rather
> than assigned a winner. The boundary curves shown are two-parameter
> power-law fits ($R^2=0.989$–$0.9995$, fitted exponents $-0.94$ to $-1.93$)
> to the empirical SRHT-paired-versus-ordered-Hadamard crossovers — a
> descriptive summary of a comparison that Prop 3 explicitly does not rank,
> not a test of Prop 3's closed form."

If the drafting pass also wants the positive result, append:

> "The no-free-parameter test of Prop 3 is reported separately: on the same
> grid, with every constant measured ($C_0$, $K_{\mathrm{eff}}$, $D_H$, $s$,
> $N$) and a gain-known random arm ($v=0$), the predicted boundary
> $\rho^*=-\log\big(1-2(C_0/N)/(K_{\mathrm{eff}}D_Hs^2)\big)$ lands within a
> median factor 1.5 of the 42 observed crossings (all within factor 2 for
> $\sigma_a\ge0.1$; empirical $\sigma$-exponent $-2.11$ vs. $-2.07$
> predicted), systematically early. For the blind random arm, the
> residual-gain leverage in (F.11) must carry the raw-correlator constant
> $1+C_0^{\mathrm{raw}}$ of (F.10) ($\approx10^6$), not the mean-subtracted
> pipeline $C_0$ ($\approx7\times10^2$): mean subtraction removes the
> $K_{\mathrm{eff}}K(\mu/\sigma)^2$ background penalty from the sampling floor
> but not from the drift leverage, a $\sim1.4\times10^3$ correction verified
> to 5% at white drift. With the corrected constant the theory predicts —
> and the data confirm, 100/100 cells — that blind random+DGI never overtakes
> ordered pairwise Hadamard anywhere on this grid; the intermediate-drift
> winner is SRHT-paired acquisition, which avoids the $C_0/N$ floor entirely."

## 2. Other passages that must change

- Table 1 row "Flip-boundary fit to Prop 3 | $R^2=0.989$–$0.9995$": relabel to
  "Empirical SRHT-vs-ordered crossover, power-law fit" and add a new row
  "Prop 3 boundary, no-free-parameter (gain-known arm): median factor 1.5,
  40/40 within factor 2 for $\sigma_a\ge0.1$" citing
  `results/prop3_nofreeparam_r1/`.
- Sec. 8 narrative (~line 218) "Figure 5 assembles the payoff: the phase
  diagram ... with the $\rho^{*}$ curve overlaid": currently false (no phase
  map panel, no rho* overlay). Either build the panel (Sec. 4 below) or soften
  to match what is drawn.
- Discussion (~line 278) "a prediction the diagram exposes to falsification,
  not a fitted curve": as published the diagram contains ONLY fitted curves.
  Rewrite around the skeleton test + corrected-leverage result: the prediction
  WAS exposed to falsification and the blind-arm version of (F.11) was
  falsified as written (constant, not form).
- Appendix F.3.3/F.4 (later pass, math edit): the gain term of (F.11) needs
  the pipeline-C0-vs-raw-C0 distinction made explicit; Prop 3's bracket
  should read $(1+C_0^{\mathrm{raw}})v_{\mathrm{blind}}/N$ for mean-subtracted
  DGI pipelines. Note this VINDICATES the "no universal C0" warning — but the
  paper currently applies the warning to the floor term only.

## 3. Caption-ready sentences (downgraded Fig. 5)

> "Fig. 5. Empirical winner map and SRHT crossover at equal frame budget
> ($N=2048$, $K=1024$, OU drift, blind corrections only). (a) Winner per
> $(\rho_{\mathrm{pair}},\sigma_a)$ cell by mean PSNR among candidates with
> relMSE $<0.5$; SRHT-paired+pairwise wins 28 of 29 above-floor cells, one
> cell goes to randomly ordered paired Hadamard + SCGI proxy, grey cells are
> at the noise floor. (b) Interpolated SRHT-paired-vs-ordered-Hadamard
> crossover $\rho^{*}_{\mathrm{SRHT}}(\sigma_a)$ with two-parameter power-law
> fits ($R^2=0.989$–$0.9995$); these are descriptive fits, not the Prop-3
> boundary, which addresses random+DGI and predicts no flip for the blind
> pipeline on this grid. (c) No-free-parameter Prop-3 skeleton test
> (gain-known random arm): predicted $\rho^{*}$ from measured
> $(C_0,K_{\mathrm{eff}},D_H,s,N)$ versus observed crossings; median
> agreement factor 1.5, all cells within factor 2 for $\sigma_a\ge0.1$,
> $\sigma$-exponent $-2.11$ measured vs. $-2.07$ predicted."

## 4. Spec for the winner/phase-map panel (a later pass draws it)

Panel (a) — winner map (the panel promised at line 218 but never drawn):
- Axes: x = $\rho_{\mathrm{pair}}$ (log, 9 grid values 1e-3..10), y =
  $\sigma_a$ (log, 5 values 0.05..0.5). 45 cells.
- Cell fill: categorical — SRHT-paired+pairwise (28), hadamard_random_paired+
  scgi_proxy (1, hatch or outline since it is a single marginal cell,
  relMSE 0.468), noise floor (16, grey). Data:
  `results/prop3_nofreeparam_r1/winner_table_cells.csv`, scope
  `equal_frame_non_oracle`.
- Overlay 1: the above-floor gate boundary (relMSE = 0.5 contour).
- Overlay 2 (optional, dashed): predicted skeleton boundary
  $\rho^*(\sigma_a)$ using median object constants ($C_0/N=0.329$,
  $K_{\mathrm{eff}}D_H\approx306$) — label clearly "Prop 3, gain-known arm";
  do NOT draw a blind-arm Prop-3 curve (no flip exists).
- Axis label MUST say $\rho_{\mathrm{pair}}$ (adjacent-pair decorrelation,
  simulator OU rate), per the manuscript's own convention warning.

Panel (c) — skeleton test: scatter $\rho^*_{\mathrm{emp}}$ vs
$\rho^*_{\mathrm{pred}}$ (42 points from
`prop3_skeleton_oracle_test.csv`), identity line, factor-2 band; or
$\rho^*$ vs $\sigma_a$ with predicted curve per object band. Mark the
$\sigma_a=0.05$ censored cells at the top axis.

## 5. Evidence trail

- `results/prop3_nofreeparam_r1/summary.md` — full numbers and verdict.
- Reproduction: local rerun matches the Colab dense grid to 6 decimals
  (same objects, patterns, channel seeds; `reproduction_check.csv`).
- The Prop-3 ingredients separately: F.8 pair law exact (median ratio 0.997);
  C0/N floor exact (oracle arm flat at 0.3286 = C0/N); the blind-arm
  leverage constant wrong by ~1.4e3, corrected version exact to 5%.
