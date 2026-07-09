from __future__ import annotations

import argparse
import base64
import json
import re
import zipfile
from pathlib import Path


def extract_between(text: str, begin: str, end: str) -> list[str]:
    pattern = re.compile(re.escape(begin) + r"\n(.*?)\n" + re.escape(end), re.S)
    return [match.group(1).strip() for match in pattern.finditer(text)]


def read_log_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if "COLAB_JOB_SUMMARY_BEGIN" in text or "COLAB_TEXT_OUTPUTS_BEGIN" in text:
        return text
    return path.read_text(encoding="utf-16", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    text = read_log_text(args.log)
    args.out.mkdir(parents=True, exist_ok=True)

    summaries = extract_between(text, "COLAB_JOB_SUMMARY_BEGIN", "COLAB_JOB_SUMMARY_END")
    if summaries:
        (args.out / "colab_job_summary.json").write_text(summaries[-1] + "\n", encoding="utf-8")

    text_blocks = extract_between(text, "COLAB_TEXT_OUTPUTS_BEGIN", "COLAB_TEXT_OUTPUTS_END")
    if text_blocks:
        outputs = json.loads(text_blocks[-1])
        text_root = args.out / "text_outputs"
        text_root.mkdir(exist_ok=True)
        for rel, content in outputs.items():
            target = text_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        (args.out / "colab_text_outputs.json").write_text(
            json.dumps(outputs, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    zip_infos = extract_between(text, "COLAB_ZIP_INFO_BEGIN", "COLAB_ZIP_INFO_END")
    if zip_infos:
        (args.out / "colab_zip_info.json").write_text(zip_infos[-1] + "\n", encoding="utf-8")

    zip_blocks = extract_between(text, "COLAB_ZIP_BASE64_BEGIN", "COLAB_ZIP_BASE64_END")
    if zip_blocks:
        zip_bytes = base64.b64decode(zip_blocks[-1])
        zip_path = args.out / "colab_artifacts.zip"
        zip_path.write_bytes(zip_bytes)
        unzip_dir = args.out / "artifacts"
        unzip_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(unzip_dir)

    print(f"extracted={args.out}")


if __name__ == "__main__":
    main()
