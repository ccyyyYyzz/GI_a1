# Prompt for the final read-only R15 reviewer

You are the final audit agent. **Review only; do not edit, commit, or push.**

Repository:

- root: `E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro`
- branch: `scgi-ceiling-diagnostic-r1`
- baseline/current HEAD: `402c8d6db9d8fc4dce225700f0b6a3561885009e`
- the worktree is intentionally dirty because it contains the proposed R15 implementation and provisional evidence.

Read, in this order:

1. `paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/00_README.md` through `07_IMPLEMENTATION_PROPOSAL_FOR_AUDITOR_APPROVAL.md`;
2. `paper_draft/REVIEWS/GPT_R15_IMPLEMENTATION/00_R15_CLOSURE_LEDGER.md`;
3. the full `git diff` and all newly added files;
4. active manuscript sources and outputs:
   - `paper_draft/latex/body.tex`
   - `paper_draft/latex/appendix_body.tex`
   - `paper_draft/latex/supplement.tex`
   - `paper_draft/MANUSCRIPT_DRAFT.md`
   - `paper_draft/APPENDICES.md`
   - `paper_draft/latex/main.pdf`
   - `paper_draft/latex/supplement.pdf`
5. implementation/evidence:
   - `run_prop3_estimator_contract_r15.py`
   - `run_paper_fig4_bridge.py`
   - `src/mechanisms.py`
   - `src/paper_experiments.py`
   - `tests/test_r15_theory_contract.py`
   - `results/prop3_estimator_contract_r15_provisional/`
   - `results/paper_fig4_bridge_r3_raw_provisional/`

Audit the four approved decisions and every Claude condition:

- **C1:** the iff downgrade applies only to known-zero/Corollary 2; Theorem A′(i)'s ordinary-local iff and below-wall exact-alias theorem are protected.
- **C2:** the estimated-`S1` gamma identity is algebraically correct and passed a coefficient-level numerical regression before being used in prose.
- **C3:** the old `-2.11/-2.07` sentence was replaced with true-`S1` `-2.12044` vs predicted `-2.11371`, while production `-2.00656` is retained as a robustness check.
- **C4:** no surviving figure/table/number depends on treating a signed coefficient as a Poisson intensity; complementary masks/positive offsets are routed through separately derived covariance.
- **C5:** main is at most 13 pages; Theorem D minimax equivalence appears only after gauge slice, parameter class, loss, feasible bandwidth, noise normalization, and matching lower/upper proof are all explicit.
- **C6:** both R15 output directories remain unmistakably provisional/dirty-tree and the historical raw directory is not used as submission-authoritative evidence.

Also test these common regression risks:

1. condition (star) is not generalized from the stated log-window estimator to ratio AGC/all windowed methods;
2. masked signed arms are called diagnostics, not Theorem-B tests;
3. Brown--Forsythe is not presented as a necessary test of (star);
4. known-carrier Theorem C does not retain a false absolute-scale gauge;
5. Fisher/CR diagnostics are not conflated with minimax lower bounds;
6. `rho_bw -> 1` does not automatically imply Theorem B remains feasible;
7. `Keff`, `K_infinity`, and `K4` have non-overlapping roles and Proposition 1's log expansion retains its positivity/integrability/lower-tail hypotheses;
8. Appendix E.3/E.4 constants and assumptions are correct;
9. Theorem 1/Prop. 3/Fig. 9 compare raw with raw;
10. no commit or push has occurred.

You may rerun read-only diagnostics and tests. Suggested commands:

```powershell
git rev-parse HEAD
git status --short
D:\Anacondar\anaconda3\python.exe -m pytest -q
cd paper_draft\latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

Deliver a formal verdict in this exact order:

1. `APPROVE`, `APPROVE WITH CONDITIONS`, or `REJECT`;
2. C1--C6 pass/fail table with file/line evidence;
3. any remaining High/Medium/Low findings, each with the smallest safe correction;
4. page/test/manifest/provenance checks;
5. explicit confirmation that the clean-commit rerun remains pending and that approval is **not** commit/push authorization.

