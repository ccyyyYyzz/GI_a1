# SCGI Reproduction And Measurement-Basis Mechanism Study

This repository implements the two requested tasks:

1. A reproducible numerical framework for Peng and Chen, APL 124, 181104 (2024):
   supervised correction of dynamic scaling factors for ghost imaging (SCGI),
   DGI reconstruction, and SCGI-UNN/SCGI-URED style refinement.
2. A mechanism-study framework for why i.i.d. random measurement bases can support
   blind gain correction in time-varying multiplicative channels while deterministic
   orthogonal bases often fail.

The verified local CUDA runtime is `D:\Anacondar\anaconda3\envs\pytorch\python.exe`
with PyTorch CUDA 12.1 on an RTX 4060 Laptop GPU. The code also keeps internal
fallbacks for synthetic MNIST-like objects, KS testing, simple SSIM, and PIL-based
figures so the smoke tests remain portable.

## Quick Start

```powershell
cd E:\GAN_FCC_WORK\scgi-repro
$py = 'D:\Anacondar\anaconda3\envs\pytorch\python.exe'
& $py run_stage0.py --profile smoke
& $py run_stage1_diagnostics.py --profile smoke --samples 3
& $py run_stage3_tests.py --profile smoke
& $py run_gamma_sweep.py --profile smoke --epochs 2
& $py run_mechanism_m1.py --profile smoke --objects 1 --seeds 1 --reconstruction correlation --no-findings --output-dir results\mechanism_m1_basis_expanded_quick
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --no-findings --output-dir results\phase_m2_basis_expanded_quick
& $py run_srht_m3.py --profile smoke --objects 1 --seeds 1 --no-findings --output-dir results\srht_m3_quick
& $py run_make_figures.py --output-dir results\figures
& $py -m unittest discover tests -v
```

M2 scans can be split across Colab or local workers:

```powershell
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 0/2 --no-findings --output-dir results\phase_m2_shard_0of2
& $py run_phase_m2.py --profile smoke --objects 1 --seeds 1 --shard 1/2 --no-findings --output-dir results\phase_m2_shard_1of2
& $py merge_phase_m2_shards.py --inputs results\phase_m2_shard_0of2 results\phase_m2_shard_1of2 --output-dir results\phase_m2_shard_merged
```

For a closer-to-prompt debug run, use `--profile debug`. For the paper-scale run, use
`--profile full` on a GPU machine with torchvision/scipy/skimage/matplotlib installed.
The verified local CUDA environment is `D:\Anacondar\anaconda3\envs\pytorch\python.exe`.

## Main Outputs

- `REPORT.md`: SCGI reproduction status, Colab runs, and mechanism-study summary.
- `COMPLETION_AUDIT.md`: strict prompt-requirement audit with done/partial/open status.
- `ASSUMPTIONS.md`: every implementation assumption for undisclosed paper details.
- `PROTOCOL.md`: fair-comparison rules for basis/channel studies.
- `THEORY.md`: derivations and theory hooks for H1-H4 and SRHT.
- `FINDINGS.md`: mechanism-study results in experiment-prediction-result format.
- `PAPER_OUTLINE.md`: theory/numerics paper outline and target venues.
- `results/stage_0/`: SCGI smoke run figures and metrics.
- `results/stage_1/smoke/`: Stage 1 B histogram, dynamic curve, gain curve, and
  lambda distribution diagnostics.
- `results/stage_3/smoke/`: held-out target reconstructions and Stage 3
  acceptance checks using the saved Stage 0 checkpoint.
- `results/mechanism_m1_basis_expanded_quick/`: compact M1 output with random,
  Hadamard, DCT, Fourier, and SRHT bases.
- `results/phase_m2_basis_expanded_quick/`: compact fair-frame M2 output with
  frame-count audit columns.
- `results/phase_m2_reference_protocol_o10s5/`: 68,250-row dense 7x5 M2
  protocol output with `reference_k2/k8/k32` calibration, equal-frame blind
  summaries, and flip-boundary diagnostics.
- `results/mechanism_m1_protocol_o10s5/`,
  `results/phase_m2_reference_protocol_o10s5/`, and
  `results/srht_m3_protocol_o10s5/`: 10-object x 5-seed mechanism outputs used
  by the latest figure rendering.
- `results/srht_m3_quick/`: compact SRHT ablation plumbing output.
- `results/figures/`: compact M1-M3 rendered figure outputs.

## Tests

Run the unittest suite with the CUDA conda runtime rather than the system `python`
on this machine:

```powershell
cd E:\GAN_FCC_WORK\scgi-repro
& 'D:\Anacondar\anaconda3\envs\pytorch\python.exe' -m unittest discover tests -v
```
