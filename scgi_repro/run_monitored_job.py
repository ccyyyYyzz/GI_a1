from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Any, TextIO


DEFAULT_CU_RATES = {
    "t4": 1.76,
    "a100": 15.0,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def run_capture(cmd: list[str], cwd: Path) -> str | None:
    try:
        proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def git_info(cwd: Path) -> dict[str, str | None]:
    branch = run_capture(["git", "branch", "--show-current"], cwd)
    return {
        "branch": branch or None,
        "head": run_capture(["git", "rev-parse", "HEAD"], cwd),
        "origin_head": run_capture(["git", "rev-parse", f"origin/{branch}"], cwd) if branch else None,
        "status_short": run_capture(["git", "status", "--short"], cwd),
    }


def torch_info() -> dict[str, Any]:
    try:
        import torch
    except Exception as exc:
        return {"available": False, "import_error": repr(exc)}
    info: dict[str, Any] = {
        "available": True,
        "version": getattr(torch, "__version__", None),
        "cuda_available": bool(torch.cuda.is_available()),
    }
    if torch.cuda.is_available():
        try:
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
        except Exception as exc:
            info["cuda_device_error"] = repr(exc)
    return info


def cu_rate_for_accelerator(accelerator: str, explicit_rate: float | None) -> float | None:
    if explicit_rate is not None:
        return float(explicit_rate)
    key = accelerator.strip().lower()
    return DEFAULT_CU_RATES.get(key)


def estimate_cu_hours(elapsed_seconds: float, cu_per_hour: float | None) -> float | None:
    if cu_per_hour is None:
        return None
    return elapsed_seconds / 3600.0 * float(cu_per_hour)


def command_display(command: list[str], shell: bool) -> str:
    if shell:
        return " ".join(command)
    return " ".join(shlex.quote(part) for part in command)


def strip_remainder_separator(command: list[str]) -> list[str]:
    if command and command[0] == "--":
        return command[1:]
    return command


def reader_thread(stream: TextIO, sink: TextIO, log_file: TextIO) -> None:
    for line in iter(stream.readline, ""):
        sink.write(line)
        sink.flush()
        log_file.write(line)
        log_file.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run any SCGI/measurement-basis command with durable logs, status, and CU accounting."
    )
    parser.add_argument("--run-id", required=True, help="Stable run identifier used in manifests.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for logs and status files.")
    parser.add_argument("--cwd", type=Path, default=Path("."), help="Working directory for the wrapped command.")
    parser.add_argument("--accelerator", default="unknown", help="Accelerator label, e.g. t4, a100, l4, cpu.")
    parser.add_argument("--cu-per-hour", type=float, default=None, help="Explicit Colab compute-unit rate per hour.")
    parser.add_argument("--heartbeat-seconds", type=float, default=30.0, help="Status refresh interval while running.")
    parser.add_argument("--resume-skip-success", action="store_true", help="Exit 0 if status.json already records success.")
    parser.add_argument("--shell", action="store_true", help="Run the remainder as a shell command string.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --.")
    return parser


def run_monitored(args: argparse.Namespace) -> int:
    command = strip_remainder_separator(list(args.command))
    if not command:
        raise SystemExit("Missing wrapped command. Put it after --.")
    cwd = args.cwd.resolve()
    out_dir = (args.output_dir or Path("results") / "cli_runs" / args.run_id).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    status_path = out_dir / "status.json"
    manifest_path = out_dir / "run_manifest.json"
    stdout_path = out_dir / "stdout.log"
    stderr_path = out_dir / "stderr.log"
    command_path = out_dir / "command.txt"

    if args.resume_skip_success and status_path.exists():
        try:
            previous = json.loads(status_path.read_text(encoding="utf-8"))
        except Exception:
            previous = {}
        if previous.get("state") == "success":
            print(f"MONITORED_JOB_SKIP_SUCCESS {args.run_id} {status_path}")
            return 0

    cu_per_hour = cu_rate_for_accelerator(args.accelerator, args.cu_per_hour)
    command_text = command_display(command, args.shell)
    command_path.write_text(command_text + "\n", encoding="utf-8")
    start_monotonic = time.monotonic()
    base_payload: dict[str, Any] = {
        "schema_version": 1,
        "run_id": args.run_id,
        "command": command_text,
        "shell": bool(args.shell),
        "cwd": str(cwd),
        "start_time_utc": utc_now(),
        "accelerator": args.accelerator,
        "cu_per_hour": cu_per_hour,
        "git": git_info(cwd),
        "python": sys.version.replace("\n", " "),
        "torch": torch_info(),
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
    }
    write_json_atomic(manifest_path, base_payload)

    def status_payload(state: str, pid: int | None, return_code: int | None = None) -> dict[str, Any]:
        elapsed = time.monotonic() - start_monotonic
        return {
            **base_payload,
            "state": state,
            "pid": pid,
            "return_code": return_code,
            "updated_time_utc": utc_now(),
            "elapsed_seconds": round(elapsed, 3),
            "estimated_cu_hours": None
            if estimate_cu_hours(elapsed, cu_per_hour) is None
            else round(float(estimate_cu_hours(elapsed, cu_per_hour)), 6),
        }

    with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_log, stderr_path.open(
        "w", encoding="utf-8", errors="replace"
    ) as stderr_log:
        popen_cmd: str | list[str] = command_text if args.shell else command
        proc = subprocess.Popen(
            popen_cmd,
            cwd=cwd,
            shell=bool(args.shell),
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )
        write_json_atomic(status_path, status_payload("running", proc.pid))
        assert proc.stdout is not None
        assert proc.stderr is not None
        threads = [
            threading.Thread(target=reader_thread, args=(proc.stdout, sys.stdout, stdout_log), daemon=True),
            threading.Thread(target=reader_thread, args=(proc.stderr, sys.stderr, stderr_log), daemon=True),
        ]
        for thread in threads:
            thread.start()
        try:
            while True:
                code = proc.poll()
                if code is not None:
                    break
                write_json_atomic(status_path, status_payload("running", proc.pid))
                time.sleep(max(1.0, float(args.heartbeat_seconds)))
        except KeyboardInterrupt:
            proc.terminate()
            write_json_atomic(status_path, status_payload("interrupted", proc.pid))
            raise
        for thread in threads:
            thread.join(timeout=5.0)
    final_state = "success" if int(proc.returncode) == 0 else "failed"
    final_payload = status_payload(final_state, proc.pid, int(proc.returncode))
    final_payload["end_time_utc"] = utc_now()
    write_json_atomic(status_path, final_payload)
    print("MONITORED_JOB_SUMMARY_BEGIN", flush=True)
    print(json.dumps(final_payload, indent=2, sort_keys=True), flush=True)
    print("MONITORED_JOB_SUMMARY_END", flush=True)
    return int(proc.returncode)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(run_monitored(args))


if __name__ == "__main__":
    main()
