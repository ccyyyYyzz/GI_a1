from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


CONFIG_PATH = Path("/content/background_command_config.json")


def sh_quote(value: object) -> str:
    text = str(value)
    return "'" + text.replace("'", "'\"'\"'") + "'"


def main() -> None:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    run_id = str(cfg["run_id"])
    repo = str(cfg["repo"])
    ref = str(cfg["ref"])
    workdir_name = str(cfg.get("workdir", "scgi_repro"))
    command = str(cfg["command"])
    artifact_root = str(cfg.get("artifact_root", "")).strip()
    install_requirements = bool(cfg.get("install_requirements", True))

    content = Path("/content")
    root = content / f"{run_id}_bg"
    log_path = content / f"{run_id}.log"
    status_path = content / f"{run_id}.status.json"
    archive_path = content / f"{run_id}_artifacts.zip"
    script_path = content / f"{run_id}_bg.sh"
    repo_dir = root / "repo"
    workdir = repo_dir / workdir_name
    artifact_dir = workdir / artifact_root if artifact_root else workdir / "results" / run_id

    shell = f"""#!/usr/bin/env bash
set -uo pipefail
export PYTHONUNBUFFERED=1
export RUN_ID={sh_quote(run_id)}
export STATUS_PATH={sh_quote(status_path)}
export ARCHIVE_PATH={sh_quote(archive_path)}
export ARTIFACT_DIR={sh_quote(artifact_dir)}
exec > >(tee -a {sh_quote(log_path)}) 2>&1

write_status() {{
  local state="$1"
  local rc="${{2:-}}"
  python3 - "$state" "$rc" <<'PY'
import json, os, sys, time
payload = {{
    "run_id": os.environ["RUN_ID"],
    "state": sys.argv[1],
    "return_code": None if not sys.argv[2] else int(sys.argv[2]),
    "time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "artifact_dir": os.environ["ARTIFACT_DIR"],
    "archive_path": os.environ["ARCHIVE_PATH"],
}}
with open(os.environ["STATUS_PATH"], "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2, sort_keys=True)
    fh.write("\\n")
PY
}}

echo "BG_COMMAND_BEGIN $RUN_ID $(date -u +%Y-%m-%dT%H:%M:%SZ)"
write_status running
rm -rf {sh_quote(root)}
mkdir -p {sh_quote(root)}
cd {sh_quote(root)}

echo "BG_CLONE_BEGIN"
git clone --depth 1 {sh_quote(repo)} repo
cd repo
git fetch --depth 1 origin {sh_quote(ref)}
git checkout --detach FETCH_HEAD
git rev-parse --short HEAD
cd {sh_quote(workdir)}
"""
    if install_requirements:
        shell += """
if [ -f requirements-colab.txt ]; then
  echo "BG_INSTALL_BEGIN"
  python3 -m pip install -q -r requirements-colab.txt
fi
"""
    shell += f"""
echo "BG_RUN_BEGIN"
set +e
bash -lc {sh_quote(command)}
rc=$?
set -e
echo "BG_RUN_EXIT $rc"

echo "BG_ZIP_BEGIN"
python3 - <<'PY'
import os
from pathlib import Path
import zipfile

source = Path(os.environ["ARTIFACT_DIR"])
archive = Path(os.environ["ARCHIVE_PATH"])
if archive.exists():
    archive.unlink()
if source.exists():
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in source.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(source).as_posix())
    print(f"BG_ARCHIVE {{archive}} {{archive.stat().st_size}}")
else:
    print(f"BG_ARCHIVE_MISSING {{source}}")
PY

if [ "$rc" -eq 0 ]; then
  write_status success "$rc"
else
  write_status failed "$rc"
fi
echo "BG_COMMAND_END $RUN_ID rc=$rc $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit "$rc"
"""

    script_path.write_text(shell, encoding="utf-8")
    os.chmod(script_path, 0o755)
    proc = subprocess.Popen(
        ["bash", str(script_path)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )
    print("BG_COMMAND_LAUNCHER_OK")
    print(
        json.dumps(
            {
                "archive": str(archive_path),
                "artifact_dir": str(artifact_dir),
                "log": str(log_path),
                "pid": proc.pid,
                "run_id": run_id,
                "script": str(script_path),
                "status": str(status_path),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
