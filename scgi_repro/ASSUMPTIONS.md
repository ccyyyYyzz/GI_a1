# Assumptions

These assumptions make the APL 2024 numerical study executable without official
code or raw data.

1. Random amplitude-only patterns are sampled i.i.d. uniform on `[0, 1]`.
2. Measurements are normalized per sequence by the sequence maximum unless stated
   otherwise.
3. The dynamic scaling factor is generated as `a_n = exp(n log(lambda))` in
   float64, with `lambda` sampled per object from `[0.9995, 1.0]`.
4. The SCGI loss weight defaults to `gamma = 1.0`; sweep values are
   `{0, 0.1, 1, 10}`.
5. The default U-Net is smaller than the paper-scale network in CPU smoke runs:
   base channels 16, depth 4. The profile can be enlarged for GPU runs.
6. If torchvision/MNIST is unavailable, synthetic MNIST-like digits and simple
   binary objects are generated with PIL. This fallback is for pipeline
   verification, not final paper claims.
7. SCGI-URED uses a NAFNet-style untrained network. Where `skimage` non-local
   means is unavailable, the denoiser fallback is a small Gaussian/box smoothing
   step under `torch.no_grad()`.
8. The USAF target is approximated by binary stripe targets in synthetic tests.
9. Mechanism-study DCT uses full-contrast cosine rows with row-energy inverse
   reconstruction. Fourier uses four non-negative phase-shift frames per
   coefficient. In equal-frame M2 scans, Fourier uses `N_frames/4` coefficients
   rather than a full `4P`-frame transform.
10. Current local verification uses the CUDA conda environment on the RTX 4060
    Laptop GPU. Colab L4 has run the `full` paper-scale profile for 20 and 100
    SCGI epochs, but the current training configuration does not converge to the
    prompt thresholds.
11. `scgi.use_coord_channels` adds normalized row/column coordinates to the
    SCGI U-Net. This is an engineering aid for small smoke runs because the
    dynamic correction is measurement-index dependent after reshaping the
    1-D sequence into a 2-D tensor, while plain convolutions are translation
    equivariant. Disable it for a stricter architecture-only reproduction.
12. `scgi.model_kind: gain_unet` makes the U-Net predict a positive gain map
    and returns `R/gain` rather than directly synthesizing `B`. This preserves
    high-frequency bucket fluctuations needed by DGI and matches the paper's
    interpretation as dynamic scaling-factor correction. Use `direct_unet` for
    the literal direct-output baseline.
13. `reference_kK` mechanism scans assume an inserted reference pattern with a
    known ideal bucket value, giving a direct gain sample every `K` measurement
    frames. The ideal M2 protocol linearly interpolates noiseless gain samples
    and records the extra reference frames. The nonideal M2 runner additionally
    supports shot/read noise on reference samples.
14. The compact nonideal digital-twin scan uses normalized detector units rather
    than a calibrated PDA100A2 electronics model: default photon count is
    `1e4`, additive read noise is `0.002` times the mean signal, SLM quantization
    is 8-bit, finite contrast ratio is `1000:1`, and timing jitter is
    `0.05` frame. These are engineering placeholders until published-curve or
    hardware-calibrated parameters are digitized.
