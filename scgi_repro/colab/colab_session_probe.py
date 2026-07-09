from __future__ import annotations

import subprocess
import sys
import time


def run(command: str) -> None:
    print(f"$ {command}", flush=True)
    proc = subprocess.run(command, shell=True, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout.rstrip(), flush=True)
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr, flush=True)
    print(f"exit={proc.returncode}", flush=True)


print("COLAB_SESSION_PROBE", time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
run("nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total --format=csv,noheader")
run("ps -eo pid,ppid,etime,pcpu,pmem,args | grep -E 'python|run_stage0|colab' | grep -v grep | head -20")
