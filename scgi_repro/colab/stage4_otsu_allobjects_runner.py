from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print("RUN", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout.rstrip(), flush=True)
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr, flush=True)
    proc.check_returncode()
    return proc


def print_file_marker(label: str, path: Path) -> None:
    print(f"{label}_BEGIN", flush=True)
    if path.exists():
        print(path.read_text(encoding="utf-8"), flush=True)
    else:
        print(f"MISSING {path}", flush=True)
    print(f"{label}_END", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--run-id", default="stage4_otsu_allobjects_colab_r1")
    args = parser.parse_args()

    print("COLAB_STAGE4_BEGIN", args.run_id, flush=True)
    print("PYTHON", sys.version.replace("\n", " "), flush=True)
    try:
        import torch

        print("TORCH", torch.__version__, flush=True)
        print("CUDA_AVAILABLE", torch.cuda.is_available(), flush=True)
        if torch.cuda.is_available():
            print("CUDA_DEVICE_NAME", torch.cuda.get_device_name(0), flush=True)
    except Exception as exc:
        print("TORCH_IMPORT_ERROR", repr(exc), flush=True)

    started = time.time()
    with tempfile.TemporaryDirectory(prefix="gi_a1_stage4_") as tmp:
        repo_dir = Path(tmp) / "repo"
        run(["git", "clone", "--depth", "1", args.repo, str(repo_dir)])
        run(["git", "fetch", "--depth", "1", "origin", args.ref], cwd=repo_dir)
        run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=repo_dir)
        run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir)
        workdir = repo_dir / "scgi_repro"
        run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], cwd=workdir)
        output_dir = Path("results/stage4_ured_otsu_soft_colab_allobjects_r1")
        run(
            [
                sys.executable,
                "run_stage4_ured_sweep.py",
                "--profile",
                "full",
                "--checkpoint",
                "results/colab_imports/pro2_full_exp_residual_e2_r1/artifacts/model_checkpoint.pt",
                "--model-kind",
                "exponential_residual_unet",
                "--steps-values",
                "15",
                "--lr-values",
                "0.0005",
                "--beta-values",
                "0.4",
                "--xi-values",
                "0.5",
                "--x-step-values",
                "0.1",
                "--channels-values",
                "24",
                "--blocks-values",
                "3",
                "--residual-scale-values",
                "0.08",
                "--denoiser-values",
                "nlm_otsu_soft",
                "--denoise-kernel-values",
                "3",
                "--nlm-h-values",
                "0.062",
                "--nlm-patch-size-values",
                "5",
                "--nlm-patch-distance-values",
                "6",
                "--otsu-temperature-values",
                "0.04",
                "--binary-prior-values",
                "0",
                "--fixed-init-seed",
                "20240709",
                "--output-dir",
                str(output_dir),
            ],
            cwd=workdir,
        )
        result_root = workdir / output_dir
        summary = {
            "run_id": args.run_id,
            "ref": args.ref,
            "elapsed_seconds": round(time.time() - started, 3),
            "result_root": str(output_dir),
        }
        print("COLAB_STAGE4_SUMMARY_BEGIN", flush=True)
        print(json.dumps(summary, indent=2), flush=True)
        print("COLAB_STAGE4_SUMMARY_END", flush=True)
        print_file_marker("COLAB_STAGE4_METRICS_CSV", result_root / "ured_sweep_metrics.csv")
        print_file_marker("COLAB_STAGE4_SUMMARY_CSV", result_root / "ured_sweep_summary.csv")
        print_file_marker("COLAB_STAGE4_BASELINE_CSV", result_root / "baseline_metrics.csv")
        print_file_marker("COLAB_STAGE4_MANIFEST_JSON", result_root / "run_manifest.json")
    print("COLAB_STAGE4_END", args.run_id, flush=True)


if __name__ == "__main__":
    main()
