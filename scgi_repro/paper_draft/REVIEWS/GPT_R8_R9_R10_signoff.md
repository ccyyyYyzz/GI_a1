# Paper review R8–R10: final sign-off sequence

> Provenance: GPT-5 Pro, 2026-07-10, chats "Paper review R8 final check" and "Paper review R9 verification"
> (verdicts in-chat; this file is the ledger).

## R8 (at commit 4b63e061)

Verified R6-1/R6-2/R6-4 RESOLVED (three-level low-pass hierarchy; normalized-time Thm B with W/N→0;
new-experiment integration incl. the double-K threshold replication and the corrected 5.9%/320
permutation figure). R6-3 nearly resolved (one main-text exactness qualifier missing). Of the 12 minors:
10 resolved; #10 (issue-# pointers in appendices) and #12 (arXiv-only references) open.
**Verdict: NOT YET — three text-only items; "no further theorem development, simulation, or new
experiment is required."**

## R9 (at commit 2da791c9)

1. PASS — Poisson/read-noise post-calibration qualifier (main text + Appendix F consistent).
2. FAIL — five residual working-record phrases in APPENDICES.md ("The source states…", "asserted …
   in the source", "In the source derivation", "earlier round-1 slogan", "as in the source").
3. PASS — five theory references at verified final journal metadata (Ahmed–Recht–Romberg IEEE TIT
   60(3) 2014; Li–Lee–Bresler IEEE TIT 63(2) 2017 under the changed published title; Kech–Krahmer
   SIAM J. Appl. Algebra Geom. 1(1) 2017; Kueng–Rauhut–Terstiege ACHA 42(1) 2017; Choudhary–Mitra
   arXiv-only with explicit note).

## R10 (at commit c15244c2)

The five phrases rewritten to archival wording; grep returns zero. GPT re-fetched the file at the
commit and inspected content.

**FINAL VERDICT: "ACCEPT — submittable to IEEE-TCI after figure assembly."**

## Loop summary (R5→R10)

R5 major revision (10 blockers, 28 minors, 12 missing experiments) → revision + appendices A–F +
verified bibliography + protocol + E12 CIs → R6 minor revision (4 items + 12 minors) → R7 (three-level
low-pass hierarchy, Thm B scaling, Thm 1 cross-covariance, experiment integration) + K=128 replication
→ R8 (3 text items) → fixes → R9 (1 residual) → fix → **R10 ACCEPT**.
Remaining before submission: publication figure assembly (rendering Figs. 1–8 + supplementary panels
from the existing result PNGs/CSVs) and LaTeX/IEEE-template conversion — both mechanical.
