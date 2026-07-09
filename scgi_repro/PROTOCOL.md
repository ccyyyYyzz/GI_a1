# Protocol For Fair Measurement-Basis Comparisons

All basis/channel comparisons in this project follow these rules.

1. **Equal SLM frame budget.** Two-frame differential Hadamard/DCT/SRHT and
   four-step Fourier measurements count all physical frames. A fair 2048-frame
   scan therefore compares 1024 paired coefficients with 512 Fourier four-step
   coefficients and 2048 random frames.
2. **Equal mean optical throughput.** Amplitude-only frames are normalized to
   comparable mean transmittance, usually near 0.5.
3. **Shared channel instances.** A given seed generates one multiplicative channel
   sequence and the same sequence is applied across competing methods.
4. **Shared additive noise model.** Detector read noise and optional shot-noise
   approximations are held fixed across methods.
5. **Repeated objects and seeds.** Main scans should use at least 10 objects and
   5 channel seeds per grid point. Smoke runs use fewer but keep the same API.
6. **Report uncertainty.** CSV outputs store per-object/per-seed rows so downstream
   scripts can report mean and standard deviation.
7. **Declare reconstruction path.** Random bases use correlation/DGI-style
   reconstruction. Orthogonal bases use paired measurements and exact inverse
   transforms when possible.
8. **Oracle is mandatory.** Every basis comparison includes oracle correction
   `R_n / a_n`; if oracle fails, do not interpret blind-correction failures as
   identifiability failures.
9. **Frame counts must be auditable.** Raw scan CSVs should include
   `num_frames`, `num_coefficients`, and `num_pixels` whenever bases with
   different physical frame costs are compared.
10. **Reference calibration is not free.** `reference_kK` corrections model one
   inserted fixed-reference frame every `K` measurement frames. Scan CSVs must
   report `reference_frames` and `total_physical_frames` so reference-calibrated
   methods can be separated from strict equal-measurement-frame methods.
11. **Long scans may be sharded.** M2 accepts `--shard i/k` with zero-based
    shard indices. Sharding is applied to complete `(basis, rho, sigma, seed,
    object)` units so all corrections for a physical condition remain together.
    Merge shards with `merge_phase_m2_shards.py`, which recomputes all summary,
    best-method, reference, equal-frame, and flip-boundary CSVs from the merged
    `phase_scan.csv`.
12. **SCGI-style blind proxies must be labeled as proxies.** `scgi_proxy`
    estimates a smooth gain envelope from observed measurements only and adds no
    reference frames. It is an equal-frame blind correction, not a trained SCGI
    network, and should not be reported as a paper-level SCGI-network result.
