# Empirical and reproducibility QA

## Snapshot and test status

- Full SHA: 402c8d6db9d8fc4dce225700f0b6a3561885009e.
- Local HEAD, origin/scgi-ceiling-diagnostic-r1, and git ls-remote agreed.
- Full test suite: **70 passed in 42.88 s**.
- Worktree was clean before this audit package was added.

Commands used:

~~~powershell
D:\Anacondar\anaconda3\python.exe -m pytest -q
& 'D:\Program Files\texlive\2024\bin\windows\latexmk.exe' -pdf -interaction=nonstopmode -halt-on-error -outdir=C:\Temp\scgi_r14_main main.tex
& 'D:\Program Files\texlive\2024\bin\windows\latexmk.exe' -pdf -interaction=nonstopmode -halt-on-error -outdir=C:\Temp\scgi_r14_supp supplement.tex
& 'C:\Users\CYZ的computer\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'C:\Users\CYZ的computer\.codex\skills\submission-audit\scripts\check_figure_refs.py' 'paper_draft\latex\body.tex'
~~~

The LaTeX commands were run from paper_draft/latex.

## Fresh PDF preflight

The TeX sources were compiled into temporary directories so no tracked build artifact was touched.

| Deliverable | Pages | Fresh build | Undefined refs | Overfull boxes | Visual sample |
|---|---:|---|---|---|---|
| main.pdf | 13 | pass | none | none | pass |
| supplement.pdf | 32 | pass | none | none | pass |

Sampled main pages 1, 3, 5, 7, 9, 11, 13 and supplement pages 1, 4, 8, 12, 16, 20, 24, 28, 32. No clipping, overlap, black rectangles, or unreadable equations were observed. The main build retains one nonfatal font substitution warning for T1/ptm/m/scit; underfull warnings are present but not submission blockers.

The rendered files still visibly carry DRAFT / INTERNAL REVIEW status, and the author/affiliation block is incomplete. Those are deliberate author decisions, not build failures.

## Prop. 3 same-estimator numerical QA

The raw pairwise arm was recomputed on the existing 10 objects times 5 seeds and the same OU traces in two forms:

1. **current implementation:** S1 estimated by median(pair_sum);
2. **theorem-faithful QA:** true S1 supplied.

The theorem-faithful arm agreed with the exact (F.7) calculation to a maximum relative discrepancy of 1.66e-6.

### Boundary-factor comparison

| Drift sigma | current / leading | true-S1 / leading | current / true-S1 |
|---:|---:|---:|---:|
| 0.10 | 1.02396 | 1.02501 | 0.99584 |
| 0.15 | 1.01221 | 1.02468 | 0.98799 |
| 0.30 | 0.98950 | 1.02421 | 0.96643 |
| 0.50 | 0.96218 | 1.02423 | 0.93884 |

Across the 40 observed crossings on the nine-rho raw grid:

- current implementation factor: median 1.0438676, maximum 1.1998532;
- true-S1 factor: median 1.0204054, maximum 1.0368566.

### Pooled log–log slopes

| Quantity | Slope | R squared |
|---|---:|---:|
| current implementation empirical | -2.00656 | 0.97271 |
| true-S1 empirical | -2.12044 | 0.97669 |
| theorem prediction | -2.11371 | 0.97807 |

The paper’s current “empirical -2.11 versus predicted -2.07” statement came from an older scale-aligned analysis. It is not the result of the current raw-MSE implementation. The true-S1 QA supports the mathematical prediction; the current practical normalization is a different estimator.

### Raw versus scale-aligned gain residual

Median ratios q_delta_raw / aligned_gain_relMSE:

| sigma | AGC | SCGI |
|---:|---:|---:|
| 0.10 | 1.00893 | 1.00965 |
| 0.15 | 1.02045 | 1.02162 |
| 0.30 | 1.07853 | 1.09068 |
| 0.50 | 1.20850 | 1.25829 |

The direction of the no-flip result is likely robust on this panel, but the current precision and “exact validation” wording are not.

## Provenance notes

- The project guide explicitly documents several Colab-era merged directories as PROVENANCE.md exceptions to the run_manifest rule; those are not missing-manifest findings.
- Version 2.1 manifests with git_dirty = true but git_dirty_excluding_output = false correctly mean that only the run’s own outputs made the tree dirty.
- results/prop3_raw_metric_r1/run_manifest.json is version 2.1 but records an older commit and git_dirty_excluding_output = true because the runner/output were untracked at run time. If this result is submission-authoritative, rerun it from a clean committed snapshot after selecting the estimator contract.

## Cross-product consistency note

results/paper_fig7_lowphoton_r5_final/summary.md still expresses the calibration/bisection budget in squared-error units as (eps_cal + eps_bis) squared / kappa squared. For the reported RMSE budget the corresponding first-order expression is eps_cal / kappa + eps_bis. This summary should not be quoted until units are reconciled.
