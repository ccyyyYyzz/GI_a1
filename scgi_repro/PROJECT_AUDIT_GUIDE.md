# Project Audit Guide — identifiability paper (code / results / manuscript)

> Written 2026-07-10 as the single entry point for a full human audit.
> **GitHub**: https://github.com/ccyyyYyzz/GI_a1 — branch **`scgi-ceiling-diagnostic-r1`** (HEAD `0d23e59a`).
> **Local**: `E:\GAN_FCC_WORK\github_sync\GI_a1_scgi_20260709_014434\scgi_repro`
> Theory-development side branch: **`mathdive-note`** (notes v2–v5; superseded by the paper but kept as ledger).
> Python for any re-run: `D:\Anacondar\anaconda3\envs\pytorch\python.exe` (never the bare `python`).

## 1. The paper (read first)

| What | Where |
|---|---|
| **Compiled PDF (32 pp, IEEE two-column)** | `paper_draft/latex/main.pdf` |
| Manuscript master (markdown, source of truth) | `paper_draft/MANUSCRIPT_DRAFT.md` |
| Appendices A–F (archival proofs) | `paper_draft/APPENDICES.md` |
| LaTeX sources | `paper_draft/latex/` (`main.tex` + `abstract/body/bibliography/appendix_body.tex`; rebuild: `latexmk -pdf main.tex`) |
| Publication figures + generator | `paper_draft/latex/figs/` + `paper_draft/latex/make_pub_figures.py` (all figures regenerable from CSVs) |
| Chen-group style profile applied to the text | `paper_draft/STYLE_PROFILE_GIU.md` |

## 2. The review trail (how the paper converged)

| Round | Verdict | Ledger |
|---|---|---|
| Math deep-dives R1–R3 | theory matured | GitHub **issues #1, #2, #3** |
| Framing R4 | narrative | GitHub **issue #4** |
| Referee R5 | major revision | `paper_draft/REVIEWS/GPT_R5_referee_review.md` |
| Referee R6 | minor revision | `paper_draft/REVIEWS/GPT_R6_referee_review.md` |
| R8→R10 | **ACCEPT** (final: "submittable to IEEE-TCI after figure assembly") | `paper_draft/REVIEWS/GPT_R8_R9_R10_signoff.md` |
| Residual editor flags from drafting | `paper_draft/REVIEW_FLAGS.md` (all resolved) |

Theory notes (development history, superseded by the paper): branch `mathdive-note`,
`scgi_repro/THEORY_IDENTIFIABILITY_v2..v5.md` (v5 = capstone).

## 3. Paper experiments — code ↔ results ↔ manuscript section

Every runner writes `run_manifest.json` (UTC time, git commit, host, args) into its result dir.

| Paper item | Runner (repo root) | Authoritative result dir | Manuscript |
|---|---|---|---|
| Fig. 2 carrier stationarity | `run_paper_fig2_stationarity.py` | `results/paper_fig2_stationarity_r2b` (8192 frames; `_r2` = 2048-frame first pass) | Sec. 9.1 |
| Fig. 3 blind gain error (core) | `run_paper_fig3_gain_error.py` | `results/paper_fig3_gain_error_e12_local_r1` (20 seeds, 24,400 rows; `_r2` = 5-seed exploration) | Sec. 9.2 |
| Fig. 4 reconstruction bridge | `run_paper_fig4_bridge.py` | `results/paper_fig4_bridge_r2b` (15 seeds, 8100 rows) | Sec. 9.3 |
| Fig. 5 flip boundary / phase diagram | (M2 audit pipeline) | `results/m2_boundary_audit_hadamard_order_dense_r1` | Sec. 9.4 |
| Fig. 6 SRHT ablation | (M3 audit pipeline) | `results/srht_m3_audit_highrho_r2` | Sec. 9.4 |
| Fig. 7 low-photon estimators | `run_paper_fig7_lowphoton.py` | `results/paper_fig7_lowphoton_r2` (+ `fig7_lowphoton_floorprobe.csv`) | Sec. 9.5 |
| Fig. 8 tall-design threshold (flagship) | `run_tall_design_threshold.py` | `results/tall_design_threshold_full_r1_merged` (K=64, 1300 cells) + `results/tall_design_threshold_K128_r1_merged` (K=128, 1950 cells) | Secs. 4, 9.6 |
| Permutation whitening power | `run_perm_whitening_power.py` | `results/perm_whitening_power_r1` (320 draws; 5.9% vs 70%) | Sec. 9.6 |
| E4 coherent-residual validation of Thm 1 | `run_coherent_residual_e4.py` | `results/coherent_residual_e4_r1` | Sec. 9.6 |
| C0 audit | `run_c0_audit_e9.py` | `results/c0_audit_e9_r1` | Sec. 9.6 / Table 1 |
| Oracle/metered/blind baselines | `run_oracle_baselines_e11.py` | `results/oracle_baselines_e11_r1` | Sec. 9.6 |
| Static-ceiling gap decomposition | `run_ceiling_diagnostic.py` | `results/ceiling_diagnostic_r1` | (repro framing; Sec. 1/10 honesty) |

Shared library: `src/paper_experiments.py` (objects, bases, channel, metrics helpers), plus the
project core `src/basis.py`, `src/dgi.py`, `src/mechanisms.py`, `src/metrics.py`, `src/data_sim.py`.
Tests: `pytest tests/test_core.py -q` (34 tests, green at HEAD).

Colab execution evidence (threshold shards etc.): `results/colab_runs/*.log` +
`results/colab_imports/pro*_threshold_*` ; launchers `launch_colab_threshold_shards.sh`,
`launch_colab_threshold_K128.sh`, `launch_colab_e12_fig3_shards.sh`.

## 4. SCGI reproduction line (the original prompt-1 work — kept honest, not a paper claim)

- Status/audits: `PAPER_DRIVEN_EXPERIMENT_STATUS.md`, `COMPLETION_AUDIT.md`, `REPORT.md`, `FINDINGS.md`, `SURPRISES.md`, `PROTOCOL.md`.
- Key honest artifacts: `results/stage3_threshold_matrix_full_r2_authoritative` (SCGI=oracle=static),
  `results/stage3_static_dgi_streaming_colab_r2`, `results/stage4_ured_*` (strict URED best 9.93 < 10.43),
  `results/ceiling_diagnostic_r1` (why: object static ceiling, not correction).
- Verdict recorded: strict APL thresholds remain partial/blocked; reproduction is framed in the paper
  as an executable testbed, not a claim.

## 5. Suggested audit order

1. `paper_draft/latex/main.pdf` — read the paper.
2. `paper_draft/REVIEWS/` R5→R10 — check the convergence trail matches the text.
3. Spot-verify numbers: pick any Sec. 9 number → find its CSV per the table above → recompute
   (every headline number was independently recomputed at least once; manifests give commit/args).
4. `paper_draft/APPENDICES.md` — proofs; heuristic/genericity steps are explicitly labeled.
5. Re-run anything cheap: e.g. `& $py run_oracle_baselines_e11.py` or `& $py run_paper_fig2_stationarity.py --num-frames 8192` and diff against the stored CSVs.
6. Rebuild figures/PDF: `& $py paper_draft/latex/make_pub_figures.py` then `latexmk -pdf` in `paper_draft/latex/`.

## 6. Known open items (deliberate)

- Author/affiliation block in `main.tex` is a placeholder (awaiting the author's final wording).
- Fig. 2 caption count 5/10 (r2 caption) vs 7/10 (r2b, quoted in text) — text quotes the r2b
  high-power run; the r2 dir is the exploration pass. Both dirs kept.
- 8 residual Overfull ≤ 14.5pt (cosmetic; IEEE columns).
- Choudhary–Mitra reference is arXiv-only (no journal version exists — verified).
