# R15 implementation closure ledger

## Control state

- Branch: `scgi-ceiling-diagnostic-r1`
- Baseline and current commit: `402c8d6db9d8fc4dce225700f0b6a3561885009e`
- Review basis: R14 audit directory `paper_draft/REVIEWS/GPT_R14_THEORY_AUDIT/` and the Claude decision `APPROVE WITH CONDITIONS` (C1--C6).
- Governance: this worktree is intentionally dirty for review. No commit and no push were performed. The two new empirical directories are explicitly provisional and are not submission-authoritative.

## Approved decisions implemented

| Decision | Closure |
|---|---|
| A: fixed-Gaussian Theorem D | The matching minimax statement is restricted to a separately specified iid Gaussian interior experiment with an explicit mean-zero gauge slice, bounded Hölder class, pointwise loss, feasible centered bandwidth, iid noise normalization, and matching upper/lower proof. The general mixing result remains an upper bound. The text expressly disclaims a three-segment finite-`N` equivalence outside that experiment. |
| B: known-zero rank-conditional result | Corollary 2 now separates the differential rank criterion, immersion-based local sufficiency, and the exact nonlinear isolated-zero criterion. Dimension counting is labeled a differential prediction. The ordinary-local iff and below-wall alias theorem of Theorem A′(i) are preserved unchanged in scope. |
| C: Prop. 3 dual estimators | The same-trace contract has two explicit arms: true `S1` for same-estimator theorem validation and production `median(pair_sum)` with the exact `gamma = S1_hat/S1` identity. The blind same-record arm is a projected mean/covariance diagnostic, not a scalar theorem validation. |
| D: raw theorem metric | Theorem 1, Prop. 3, and the reconstruction bridge use raw relative MSE as the theorem-validation metric. Scale-aligned MSE is retained only as a separately labeled image-quality metric. Fig. 9 was regenerated from the raw bridge output. |

## Claude conditions C1--C6

### C1 — scope protection: PASS

- The iff downgrade is confined to the known-zero/Corollary 2 discussion.
- Theorem A′(i)'s generic ordinary-local iff for `K >= 2`, including the genuine below-wall alias manifold, remains stated and proved.
- Main source: `paper_draft/latex/body.tex`; proof source: `paper_draft/latex/appendix_body.tex`; Markdown mirrors: `MANUSCRIPT_DRAFT.md`, `APPENDICES.md`.

### C2 — gamma identity hard gate: PASS

The identity entered the manuscript only after executable regression coverage was added in `tests/test_r15_theory_contract.py`:

1. coefficient-level median-pair-sum gamma identity;
2. exact reduction to F.7 when `gamma = 1`;
3. three-term gamma risk decomposition;
4. unchanged default pairwise output;
5. unchanged legacy positional AGC call;
6. validation of supplied pair total intensity.

Command and result:

```text
D:\Anacondar\anaconda3\python.exe -m pytest tests\test_r15_theory_contract.py -q -vv
6 passed in 3.35s
```

The provisional contract run gives maximum coefficient-identity error `6.0149e-7` after normalization by `S1` and maximum risk-decomposition error `3.1691e-6`; no denominator clamp fired.

### C3 — retain and rewrite the -2.11 result: PASS

The old sentence was replaced, not deleted:

- true-`S1` theorem arm: 40/40 observed crossings, median/max prediction-to-observation factors `1.020405/1.036857`, empirical pooled slope `-2.120444` versus predicted `-2.113711`;
- production median normalization: 40/40 crossings, factors `1.043940/1.199853`, empirical pooled slope `-2.006560`; explicitly labeled a robustness check governed by the gamma identity rather than the same-estimator proof.

Evidence: `results/prop3_estimator_contract_r15_provisional/pair_contract_summary.json`.

### C4 — signed-Poisson dependency scan before deletion: PASS

The active sources were scanned before and after the removal. No figure, table, or numerical claim depends on a signed coefficient being used as a Poisson mean. The surviving statements explicitly say that signed `UT` coefficients are not Poisson intensities and require a separately derived complementary-mask or positive-offset covariance before insertion into Theorem 1.

Relevant sources: `paper_draft/latex/body.tex`, `paper_draft/latex/appendix_body.tex`, and their Markdown mirrors.

### C5 — page and equivalence gates: PASS

- `main.pdf`: 13 pages.
- `supplement.pdf`: 33 pages (reported rather than hidden).
- Both logs: zero overfull boxes, zero unresolved references, and zero unresolved citations.
- The fixed-Gaussian equivalence appears only with all six experiment-defining elements and its matching proof; the general mixing law is not called minimax-equivalent.

### C6 — authority status of empirical outputs: PASS, publication rerun still required

The new outputs are deliberately named and labeled provisional:

- `results/prop3_estimator_contract_r15_provisional/`
- `results/paper_fig4_bridge_r3_raw_provisional/`

Both manifests report:

```text
authority_status = provisional_dirty_tree_qa
git_commit = 402c8d6db9d8fc4dce225700f0b6a3561885009e
git_dirty = true
git_dirty_excluding_output = true
```

Each manifest's `runner_sha256` matches the current runner. The historical `results/prop3_raw_metric_r1` is not cited as submission-authoritative. A clean-commit rerun and repository update remain a hard publication gate and require separate commit/push authorization.

## Additional theoretical hygiene completed

- Proposition 1: `K_infinity` is only the Gaussian/Lindeberg gate. The log expansion now separately assumes carrier positivity, log-integrability, third-order control, and an explicit lower-tail condition; higher cumulants may affect log variance and tails.
- Proposition 2/Theorem B: condition (star) is an iff only for the stated windowed log estimator. Stationarity alone is not sufficient, iid needs the log-tail and `W >> log N` uniformity scaling, and the SCGI likelihood needs a separate M-estimation argument.
- Masked log implementation: it is Theorem-B-faithful only when the original carrier is strictly positive and the mask is all one. Signed/nonpositive arms are consistently labeled endogenous masked diagnostics in the manuscript, runner, source docstring, figure source, and caption.
- Brown--Forsythe: chunk-variance equality is labeled a screen of the stronger strict-stationarity sufficient model B2, not a necessary test of condition (star).
- Fast drift: `rho_bw -> 1` no longer “forces Theorem B”; it requires an external reference, a prior, or another non-algebraic source, and Theorem B is available only if B3--B4 still admit a coherence window.
- Theorem C: known `Lambda0` and carriers identify absolute log-gain scale; record centering is an evaluation choice. The Fisher diagnostic is separated from the all-estimator minimax lower bound. Information is said to vanish as expected intensity `lambda -> 0`, not when a particular count happens to be zero.
- Proposition 2 counterexamples: iid log-tail/window conditions are explicit; a row-permuted full square Hadamard remains invertible, so Theorem A supplies the algebraic alias. Nonpositive buckets invalidate the log argument.
- Appendix E: the without-replacement variance and doubled Walsh-coefficient variance are corrected and line-broken; the permutation-only bound is conditioned on `S1 != 0` and `Keff >= 1` (with nonnegative physical objects as a sufficient regime).
- OU window lemma: the interior formula is explicitly restricted to `1 << W* << min(N, 1/rho)`; outside this range a boundary window applies.

## Empirical and implementation evidence

### Prop. 3 contract

- Runner: `run_prop3_estimator_contract_r15.py`
- Output rows: `pair_contract_scan.csv` 4500; `blind_projection_diagnostics.csv` 900.
- Blind projected identity maximum absolute error: `1.7337e-5`.
- Median raw `q_delta` / aligned gain-error ratio: `1.01879`.
- Median lag-one residual correlation: `0.88215`, supporting the decision not to replace the same-record blind arm by a scalar iid residual theorem.

### Raw reconstruction bridge

- Runner: `run_paper_fig4_bridge.py`
- Output: 8100 rows over three reconstructors, three `N` values, six residual-variance levels (including zero), ten objects, and fifteen seeds.
- Maximum raw per-realization decomposition error: `2.2776e-7`.
- Measured/theory aggregate ratios: orthogonal `[0.913, 1.163]`, SRHT `[0.992, 1.021]`, random/DGI `[0.982, 1.010]`.
- Per-`v` slopes: orthogonal `[-0.117, 0.112]`, SRHT `[-0.014, 0.009]`, random/DGI `[-1.005, -0.972]`.
- Exact random/DGI leverage gives `N B_L` in `[7.527, 7.544]e5`.

## Verification record

```text
D:\Anacondar\anaconda3\python.exe -m pytest -q
76 passed in 55.40s

py_compile on all edited runners/helpers
PASS

latexmk -pdf main.tex
13 pages; zero overfull/undefined reference/citation warnings

latexmk -pdf supplement.tex
33 pages; zero overfull/undefined reference/citation warnings
```

All 13 publication PNGs were regenerated. Visual PDF QA covered the changed main-text Fig. 3/Theorems C--D/discussion pages and supplementary Theorem C, E.3, Prop. 3, and OU-window pages; no clipping or overlap was found.

Two independent read-only hard scans were then run on the stable worktree. The first found no High/Medium regression and two Low source-hygiene remnants (a duplicated word in a docstring and an unrendered Fig. 1 placeholder fallback); both were removed and the main PDF was recompiled. The second returned C1--C6 `PASS`, no additional High/Medium finding, `git diff --check` clean, and confirmed local/origin HEAD `402c8d6` with no new commit or push.

## Files added for R15

- `run_prop3_estimator_contract_r15.py`
- `tests/test_r15_theory_contract.py`
- `results/prop3_estimator_contract_r15_provisional/`
- `results/paper_fig4_bridge_r3_raw_provisional/`
- `paper_draft/REVIEWS/GPT_R15_IMPLEMENTATION/00_R15_CLOSURE_LEDGER.md`
- `paper_draft/REVIEWS/GPT_R15_IMPLEMENTATION/01_FINAL_REVIEW_PROMPT.md`

Existing source files and publication artifacts were edited only within the approved R15 scope. The pre-existing untracked R14 audit directory was preserved.

## Remaining user/publication decisions

1. Final author and affiliation block (the review build still carries the draft/internal-review block).
2. Supplement-length strategy: submit as-is, request editor approval, or host the long proof appendix separately.
3. MIT license confirmation.
4. After review approval and explicit commit authorization: make a clean commit, rerun both R15 result directories from that clean commit, update their manifests/status to submission-authoritative, regenerate figures/PDFs, and only then push if separately authorized.
