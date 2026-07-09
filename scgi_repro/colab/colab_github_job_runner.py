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
import threading
import time
import zipfile
from datetime import datetime, timezone


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print("RUN", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout.rstrip(), flush=True)
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr, flush=True)
    proc.check_returncode()
    return proc


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def estimate_cu_hours(elapsed_seconds: float, cu_per_hour: float) -> float | None:
    if cu_per_hour <= 0.0:
        return None
    return elapsed_seconds / 3600.0 * cu_per_hour


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def sync_artifacts(source: Path, persist_root: Path | None, run_id: str) -> dict | None:
    if persist_root is None or not source.exists():
        return None
    target = persist_root / run_id
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    return {"source": str(source), "target": str(target), "time_utc": utc_now()}


def stream_shell(
    command: str,
    cwd: Path,
    status_path: Path,
    status_base: dict,
    heartbeat_seconds: float,
    cu_per_hour: float,
    sync_source: Path,
    persist_root: Path | None,
    sync_seconds: float,
) -> int:
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
    start = time.time()

    def forward_output() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line.rstrip(), flush=True)

    thread = threading.Thread(target=forward_output, daemon=True)
    thread.start()
    last_sync = 0.0
    while proc.poll() is None:
        elapsed = time.time() - start
        payload = {
            **status_base,
            "state": "running",
            "pid": proc.pid,
            "updated_time_utc": utc_now(),
            "elapsed_seconds": round(elapsed, 3),
            "estimated_cu_hours": None
            if estimate_cu_hours(elapsed, cu_per_hour) is None
            else round(float(estimate_cu_hours(elapsed, cu_per_hour)), 6),
        }
        now = time.time()
        if persist_root is not None and sync_seconds > 0.0 and now - last_sync >= sync_seconds:
            payload["last_persist_sync"] = sync_artifacts(sync_source, persist_root, status_base["run_id"])
            last_sync = now
        write_json_atomic(status_path, payload)
        time.sleep(max(1.0, float(heartbeat_seconds)))
    thread.join(timeout=5.0)
    return int(proc.returncode)


def collect_text_outputs(root: Path, limit_bytes: int) -> dict[str, str]:
    out: dict[str, str] = {}
    names = [
        "metrics.json",
        "acceptance.csv",
        "stage3_acceptance.csv",
        "stage3_metrics.csv",
        "run_manifest.json",
        "colab_job_status.json",
        "progress.json",
        "baseline_metrics.csv",
        "ured_sweep_metrics.csv",
        "ured_sweep_summary.csv",
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
    parser.add_argument("--accelerator", default="unknown")
    parser.add_argument("--cu-per-hour", type=float, default=0.0)
    parser.add_argument("--heartbeat-seconds", type=float, default=60.0)
    parser.add_argument("--persist-root", default="", help="Optional mounted directory for periodic artifact copies.")
    parser.add_argument("--sync-seconds", type=float, default=300.0, help="Artifact sync interval when --persist-root is set.")
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
        status_root = workdir / args.artifact_root if args.artifact_root else workdir / "results" / "colab_runs" / args.run_id
        status_root.mkdir(parents=True, exist_ok=True)
        status_path = status_root / "colab_job_status.json"
        persist_root = Path(args.persist_root).expanduser() if str(args.persist_root).strip() else None
        status_base = {
            "schema_version": 1,
            "run_id": args.run_id,
            "ref": args.ref,
            "command": args.command,
            "workdir": args.workdir,
            "accelerator": args.accelerator,
            "cu_per_hour": args.cu_per_hour,
            "persist_root": None if persist_root is None else str(persist_root),
            "start_time_utc": utc_now(),
        }
        write_json_atomic(status_path, {**status_base, "state": "starting", "updated_time_utc": utc_now()})
        command_start = time.time()
        exit_code = stream_shell(
            args.command,
            cwd=workdir,
            status_path=status_path,
            status_base=status_base,
            heartbeat_seconds=float(args.heartbeat_seconds),
            cu_per_hour=float(args.cu_per_hour),
            sync_source=status_root,
            persist_root=persist_root,
            sync_seconds=float(args.sync_seconds),
        )
        command_elapsed = time.time() - command_start
        summary = {
            "run_id": args.run_id,
            "ref": args.ref,
            "command": args.command,
            "exit_code": exit_code,
            "elapsed_seconds": round(time.time() - start, 3),
            "command_elapsed_seconds": round(command_elapsed, 3),
            "accelerator": args.accelerator,
            "cu_per_hour": args.cu_per_hour,
            "estimated_cu_hours": None
            if estimate_cu_hours(command_elapsed, float(args.cu_per_hour)) is None
            else round(float(estimate_cu_hours(command_elapsed, float(args.cu_per_hour))), 6),
            "status_path": str(status_path.relative_to(workdir)),
            "workdir": args.workdir,
        }
        final_status = {
            **status_base,
            "state": "success" if exit_code == 0 else "failed",
            "return_code": exit_code,
            "updated_time_utc": utc_now(),
            "end_time_utc": utc_now(),
            "elapsed_seconds": round(command_elapsed, 3),
            "estimated_cu_hours": summary["estimated_cu_hours"],
        }
        write_json_atomic(status_path, final_status)
        final_sync = sync_artifacts(status_root, persist_root, args.run_id)
        if final_sync is not None:
            final_status["last_persist_sync"] = final_sync
            write_json_atomic(status_path, final_status)
            sync_artifacts(status_root, persist_root, args.run_id)
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
