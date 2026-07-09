# Fig. 4 Reconstruction Bridge (r2)

Known residual gain variance v is injected after noiseless bucket formation; relMSE is scale-aligned to the object.
Complete orthogonal (Hadamard) and SRHT inverses are now swept over transform size N in {1024,2048,4096}: their relMSE is flat in N (median log-log slopes orthogonal_inverse=-0.041, srht_inverse=-0.006), so there is no 1/N reconstruction floor for the deterministic inverse; random_dgi decays as 1/N (median slope -0.996).
v=0 rows give C0_measured = relMSE(v=0)*N. For the orthogonal/SRHT inverses C0_measured ~ 0 (exact inversion, no range-ledger floor); random_dgi carries its N-dependence through measured_leverage (leverage*N ~ const, drifting ~9% over N) rather than through a v=0 floor, which is zero by residual construction.
Theory line kept at theory=v for the orthogonal/SRHT arms (option B). DC-dominated objects (natural_patch, stripe) fall below the v line because the scale alignment absorbs the co-linear gain component; this is an alignment effect, not a model failure.
random_dgi leg is unchanged from r1 (1/N leverage law).
Rows: 2700. Runtime seconds: 8.16.
