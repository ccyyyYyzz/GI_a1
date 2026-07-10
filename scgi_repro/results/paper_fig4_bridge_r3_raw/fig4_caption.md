# Fig. 9 Reconstruction Bridge (r3_raw)

Known residual gain variance v is injected after noiseless bucket formation. The theorem-validation metric is total raw relative MSE for every arm; scale-aligned total MSE is retained only as a secondary CSV field.
Complete orthogonal (Hadamard) and SRHT inverses are swept over transform size N in {1024,2048,4096} with 15 seeds per (object, v, N): per-v log-log slope ranges over the 5 v values are orthogonal_inverse=[-0.117, 0.112] (max|slope|=0.117), srht_inverse=[-0.014, 0.009] (max|slope|=0.014) -- both well within the deterministic-inverse flatness band, so there is no 1/N reconstruction floor for the deterministic inverse; random_dgi decays as 1/N at every v (per-v slope range [-1.005, -0.972], consistent with -1 at each v).
v=0 rows measure each fixed reconstructor's raw floor. Theory uses clean_floor_raw + B_L v, with B_L=1 for complete orthogonal/SRHT inversion and exact fixed-operator column-norm leverage for random_dgi. For random_dgi, leverage*N spans 7.53e+05-7.54e+05 across N in {1024,2048,4096}.
The clean-floor/gain cross term is exported per realization; its seed expectation is zero under the injected centered residual model. No photon noise is simulated in this bridge protocol.
Rows: 8100. Runtime seconds: 25.82.
