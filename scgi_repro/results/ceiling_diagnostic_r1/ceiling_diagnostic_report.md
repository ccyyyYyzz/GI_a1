# Ceiling Diagnostic Report

This is a pure static-channel diagnostic. It does not train SCGI/UNN/URED, does not use Otsu or binary postprocessing, and uses the repository CNR definition with the ground-truth `target > 0.5` mask.

## Premise

The authoritative Stage 3 matrix shows `static ~= SCGI ~= analytic ~= oracle`, so the residual SCGI correction gap is effectively zero. The bottleneck for the SCGI CNR gate is the static random-DGI ceiling, especially `stripe_target` and `ring`.

## Manifest

- `profile`: full
- `image_size`: 128
- `num_pixels`: 16384
- `base_patterns`: 16384
- `device`: cuda
- `pattern_distribution`: uniform
- `chunk_patterns`: 512
- `heldout_count`: 8
- `keff_objects`: ['letter_A', 'stripe_target', 'letter_L', 'ring', 'mnist_like_0', 'mnist_like_1', 'mnist_like_2', 'mnist_like_3', 'mnist_like_4', 'mnist_like_5', 'mnist_like_6', 'mnist_like_7', 'filled_disk', 'filled_square', 'usaf_like_bars', 'grayscale_gradient', 'grayscale_blob', 'fat_cross']
- `n_scan_objects`: ['stripe_target', 'ring']
- `n_factors`: [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0]
- `n_counts`: [16384, 32768, 65536, 131072, 262144, 524288, 1048576]
- `gate_cnr`: 3.39
- `read_noise_std`: 0.0
- `random_ls_max_pixels`: 4096
- `random_ls_image_size`: 64
- `random_ls_pixels`: 4096
- `random_ls_frame_counts`: [4096, 8192]
- `elapsed_seconds`: 127.22
- `figures`: ['ceiling_vs_keff.png', 'ceiling_vs_N.png']

## Lever A - Object K_eff

- At N=K=16384, the smallest observed object support that clears CNR 3.39 is `mnist_like_0` with K_eff=1117.5 and CNR=3.783.

object,K_eff,bright_px,cnr,psnr,rel_mse,affine_rel_mse
letter_L,1440.0,1440,3.4898548126220703,8.135940551757812,1.7476859092712402,0.46052688360214233
letter_A,1488.3050471268934,1452,3.3770549297332764,8.047524452209473,1.8540314435958862,0.4557774066925049
ring,2148.0,2148,2.9727885723114014,7.659852981567383,1.3073756694793701,0.43461284041404724
stripe_target,3485.0,3485,2.4749419689178467,8.209062576293945,0.7100858688354492,0.3882621228694916

## Lever B - Oversampling N

- `stripe_target` first clears CNR 3.39 at N=32768 (2.0x K), CNR=3.477.
  Calibration-aligned `affine_rel_mse` log-log slope for `stripe_target`: -0.846 (ideal random-DGI variance floor is about -1; finite-target bias and min-max display metrics are reported separately).
- `ring` first clears CNR 3.39 at N=32768 (2.0x K), CNR=4.233.
  Calibration-aligned `affine_rel_mse` log-log slope for `ring`: -0.844 (ideal random-DGI variance floor is about -1; finite-target bias and min-max display metrics are reported separately).

## Lever C - Estimator / Inverse Upper Bound

- `ring` `hadamard_paired/exact_inverse_off_protocol`: CNR=200000000.000, PSNR=80.000, N=32768. This is off-protocol exact-inverse ceiling evidence.
- `ring` `srht_paired/exact_inverse_off_protocol`: CNR=200000000.000, PSNR=80.000, N=32768. This is off-protocol exact-inverse ceiling evidence.
- `stripe_target` `hadamard_paired/exact_inverse_off_protocol`: CNR=200000000.000, PSNR=80.000, N=32768. This is off-protocol exact-inverse ceiling evidence.
- `stripe_target` `srht_paired/exact_inverse_off_protocol`: CNR=200000000.000, PSNR=80.000, N=32768. This is off-protocol exact-inverse ceiling evidence.

- Random-basis LS is computed as a real budgeted pseudoinverse, not a skipped row: 64x64 downsampled objects, N in [4096, 8192]. It is off-protocol and only tests the estimator ceiling.

object,basis_image_size,basis_pixels,estimator,N,cnr,psnr,rel_mse,affine_rel_mse
ring,64,4096,dgi_protocol_compare,4096,2.8926877975463867,8.61270523071289,1.1105713844299316,0.43821948766708374
ring,64,4096,least_squares_off_protocol,4096,14.345344543457031,52.17422866821289,4.8909565521171317e-05,9.540788596495986e-05
ring,64,4096,dgi_protocol_compare,8192,4.05849552154541,10.354155540466309,0.743706226348877,0.2825966477394104
ring,64,4096,least_squares_off_protocol,8192,14.344376564025879,80.0,6.724282286540983e-08,1.2718818709345214e-07
stripe_target,64,4096,dgi_protocol_compare,4096,2.3427329063415527,9.179481506347656,0.7206622362136841,0.3626484274864197
stripe_target,64,4096,least_squares_off_protocol,4096,8.836052894592285,50.381736755371094,5.463944035000168e-05,9.168704855255783e-05
stripe_target,64,4096,dgi_protocol_compare,8192,3.0819811820983887,10.495661735534668,0.5322476029396057,0.24239537119865417
stripe_target,64,4096,least_squares_off_protocol,8192,8.931638717651367,78.0714340209961,9.301135861505827e-08,1.5087167071214935e-07

## Bottom Line

- Cheapest protocol-preserving route for the two hard Stage 3 objects is random-DGI oversampling to `2.0x K` frames; in this run both stripe and ring clear at 2.0x K.
- Off-protocol exact inverse also clears both objects at the paired orthogonal 2K-frame budget; use it only as an information-ceiling proof, not as a paper-protocol reproduction.
- SCGI correction itself does not need another training pass for this bottleneck; URED high CNR is denoising/regularization-driven and is separate from the static DGI ceiling.
