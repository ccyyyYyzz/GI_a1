from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print("RUN", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout.rstrip(), flush=True)
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr, flush=True)
    proc.check_returncode()
    return proc


def stream_shell(command: str, cwd: Path) -> int:
    print("RUN_SHELL", command, flush=True)
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line.rstrip(), flush=True)
    return proc.wait()


def collect_text_outputs(root: Path, limit_bytes: int) -> dict[str, str]:
    out: dict[str, str] = {}
    names = [
        "metrics.json",
        "acceptance.csv",
        "stage3_acceptance.csv",
        "stage3_metrics.csv",
        "run_manifest.json",
        "best_equal_frame_blind_methods.csv",
        "best_reference_methods.csv",
        "flip_boundary.csv",
    ]
    for path in root.rglob("*"):
        if path.name not in names or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if len(data) <= limit_bytes:
            out[rel] = data.decode("utf-8", errors="replace")
    return out


def zip_artifacts(root: Path, artifact_root: Path, max_bytes: int) -> tuple[str | None, int]:
    if not artifact_root.exists():
        return None, 0
    zip_path = root / "colab_artifacts.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in artifact_root.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(artifact_root).as_posix())
    size = zip_path.stat().st_size
    if size > max_bytes:
        return None, size
    encoded = base64.b64encode(zip_path.read_bytes()).decode("ascii")
    return encoded, size


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--workdir", default="scgi_repro")
    parser.add_argument("--command", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--install-requirements", action="store_true")
    parser.add_argument("--artifact-root", default="")
    parser.add_argument("--emit-zip", action="store_true")
    parser.add_argument("--max-zip-mb", type=float, default=8.0)
    parser.add_argument("--text-limit-kb", type=int, default=256)
    args = parser.parse_args()

    print("COLAB_JOB_BEGIN", args.run_id, flush=True)
    print("PYTHON", sys.version.replace("\n", " "), flush=True)
    try:
        import torch

        print("TORCH", torch.__version__, flush=True)
        print("CUDA_AVAILABLE", torch.cuda.is_available(), flush=True)
        if torch.cuda.is_available():
            print("CUDA_DEVICE_NAME", torch.cuda.get_device_name(0), flush=True)
    except Exception as exc:
        print("TORCH_IMPORT_ERROR", repr(exc), flush=True)

    start = time.time()
    with tempfile.TemporaryDirectory(prefix="scgi_colab_") as tmp:
        tmp_path = Path(tmp)
        repo_dir = tmp_path / "repo"
        run(["git", "clone", "--depth", "1", args.repo, str(repo_dir)])
        run(["git", "fetch", "--depth", "1", "origin", args.ref], cwd=repo_dir)
        run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=repo_dir)
        run(["git", "rev-parse", "--short", "HEAD"], cwd=repo_dir)
        workdir = repo_dir / args.workdir
        if not workdir.exists():
            raise FileNotFoundError(workdir)
        if args.install_requirements and (workdir / "requirements-colab.txt").exists():
            run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements-colab.txt"], cwd=workdir)
        exit_code = stream_shell(args.command, cwd=workdir)
        summary = {
            "run_id": args.run_id,
            "ref": args.ref,
            "command": args.command,
            "exit_code": exit_code,
            "elapsed_seconds": round(time.time() - start, 3),
            "workdir": args.workdir,
        }
        print("COLAB_JOB_SUMMARY_BEGIN", flush=True)
        print(json.dumps(summary, indent=2), flush=True)
        print("COLAB_JOB_SUMMARY_END", flush=True)
        texts = collect_text_outputs(workdir, args.text_limit_kb * 1024)
        print("COLAB_TEXT_OUTPUTS_BEGIN", flush=True)
        print(json.dumps(texts, indent=2), flush=True)
        print("COLAB_TEXT_OUTPUTS_END", flush=True)
        if args.emit_zip and args.artifact_root:
            encoded, size = zip_artifacts(workdir, workdir / args.artifact_root, int(args.max_zip_mb * 1024 * 1024))
            print("COLAB_ZIP_INFO_BEGIN", flush=True)
            print(json.dumps({"artifact_root": args.artifact_root, "zip_bytes": size, "emitted": encoded is not None}), flush=True)
            print("COLAB_ZIP_INFO_END", flush=True)
            if encoded is not None:
                print("COLAB_ZIP_BASE64_BEGIN", flush=True)
                print(encoded, flush=True)
                print("COLAB_ZIP_BASE64_END", flush=True)
        if exit_code != 0:
            raise SystemExit(exit_code)
    print("COLAB_JOB_END", args.run_id, flush=True)


if __name__ == "__main__":
    main()
