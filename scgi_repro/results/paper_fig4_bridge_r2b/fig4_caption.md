# Fig. 4 Reconstruction Bridge (r2b)

Known residual gain variance v is injected after noiseless bucket formation; relMSE is scale-aligned to the object.
Complete orthogonal (Hadamard) and SRHT inverses are swept over transform size N in {1024,2048,4096} with 15 seeds per (object, v, N): per-v log-log slope ranges over the 5 v values are orthogonal_inverse=[-0.074, 0.062] (max|slope|=0.074), srht_inverse=[-0.014, 0.008] (max|slope|=0.014) -- both well within the deterministic-inverse flatness band, so there is no 1/N reconstruction floor for the deterministic inverse; random_dgi decays as 1/N at every v (per-v slope range [-1.031, -0.974], consistent with -1 at each v).
v=0 rows give C0_measured = relMSE(v=0)*N, which is identically 0 by residual construction for random_dgi (the v=0 residual is recon(v=0) - clean_recon = 0) -- so C0_measured is NOT the right constant to quote for this arm. The deterministic orthogonal/SRHT inverses instead satisfy relMSE = (1+C0)*v with C0_measured ~ 0 (exact inversion, no range-ledger floor); random_dgi is governed by relMSE = leverage*v with leverage*N ~ 7.38e+05-7.68e+05 across N in {1024,2048,4096} (the correct N-scaling constant for this arm).
Theory line kept at theory=v for the orthogonal/SRHT arms (option B). DC-dominated objects (natural_patch, stripe) fall below the v line because the scale alignment absorbs the co-linear gain component; this is an alignment effect, not a model failure.
random_dgi leg is unchanged in mechanism from r1 (1/N leverage law); only the seed count increased.
Rows: 8100. Runtime seconds: 32.22.
