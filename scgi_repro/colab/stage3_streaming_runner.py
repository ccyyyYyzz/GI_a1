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
    parser.add_argument("--run-id", default="stage3_streaming_colab_r1")
    parser.add_argument("--pattern-factors", default="4,8,16,32,64")
    parser.add_argument("--chunk-patterns", default="1024")
    args = parser.parse_args()

    print("COLAB_STAGE3_STREAMING_BEGIN", args.run_id, flush=True)
    print("PYTHON", sys.version.replace("\n", " "), flush=True)
    try:
        import torch

        print("TORCH", torch.__version__, flush=True)
        print("CUDA_AVAILABLE", torch.cuda.is_available(), flush=True)
        if torch.cuda.is_available():
            print("CUDA_DEVICE_NAME", torch.cuda.get_device_name(0))
    except Exception as exc:
        print("TORCH_IMPORT_ERROR", repr(exc), flush=True)

    started = time.time()
    with tempfile.TemporaryDirectory(prefix="gi_a1_stage3_") as tmp:
        repo_dir = Path(tmp) / "repo"
        run(["git", "clone", "--depth", "1", args.repo, str(repo_dir)])
        run(["git", "fetch", "--depth", "1", "origin", args.ref], cwd=repo_dir)
        run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=repo_dir)
        run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir)
        workdir = repo_dir / "scgi_repro"
        run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], cwd=workdir)
        output_dir = Path("results/stage3_static_dgi_streaming_colab_r1")
        run(
            [
                sys.executable,
                "run_stage3_static_dgi_streaming_audit.py",
                "--profile",
                "full",
                "--heldout-count",
                "4",
                "--pattern-factors",
                args.pattern_factors,
                "--chunk-patterns",
                args.chunk_patterns,
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
            "pattern_factors": args.pattern_factors,
            "chunk_patterns": int(args.chunk_patterns),
        }
        print("COLAB_STAGE3_STREAMING_SUMMARY_BEGIN", flush=True)
        print(json.dumps(summary, indent=2), flush=True)
        print("COLAB_STAGE3_STREAMING_SUMMARY_END", flush=True)
        print_file_marker("COLAB_STAGE3_STREAMING_CSV", result_root / "stage3_static_dgi_streaming_audit.csv")
        print_file_marker("COLAB_STAGE3_STREAMING_REPORT", result_root / "stage3_static_dgi_audit_report.md")
        print_file_marker("COLAB_STAGE3_STREAMING_MANIFEST", result_root / "run_manifest.json")
        print_file_marker("COLAB_STAGE3_STREAMING_PROGRESS", result_root / "progress.json")
    print("COLAB_STAGE3_STREAMING_END", args.run_id, flush=True)


if __name__ == "__main__":
    main()
