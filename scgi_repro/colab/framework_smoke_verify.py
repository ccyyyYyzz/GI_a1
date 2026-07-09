from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def count_csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader)
        return sum(1 for _ in reader)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    parser = argparse.ArgumentParser(description="Colab smoke verifier for the SCGI/M3 framework patch.")
    parser.add_argument("--repo", default="https://github.com/ccyyyYyzz/GI_a1.git")
    parser.add_argument("--ref", required=True)
    parser.add_argument("--branch", default="scgi-colab-20260709")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="scgi_framework_verify_") as tmp:
        tmp_path = Path(tmp)
        repo_dir = tmp_path / "repo"
        run(["git", "clone", "--depth", "1", "--branch", args.branch, args.repo, str(repo_dir)])
        run(["git", "checkout", "--detach", args.ref], cwd=repo_dir)
        work = repo_dir / "scgi_repro"
        require(work.exists(), "missing scgi_repro directory after clone")

        docs = {
            "README.md": (work / "README.md").read_text(encoding="utf-8"),
            "REPORT.md": (work / "REPORT.md").read_text(encoding="utf-8"),
            "FINDINGS.md": (work / "FINDINGS.md").read_text(encoding="utf-8"),
            "PAPER_OUTLINE.md": (work / "PAPER_OUTLINE.md").read_text(encoding="utf-8"),
            "PROTOCOL.md": (work / "PROTOCOL.md").read_text(encoding="utf-8"),
        }
        for name, text in docs.items():
            require("phase_m2_reference_protocol_o10s5" not in text, f"stale M2 reference path in {name}")
            require("phase_m2_scgi_proxy_dense_r1_merged" not in text, f"stale M2 proxy path in {name}")
            require("stage_3_exp_residual_colab_full" not in text, f"stale Stage 3 path in {name}")
        require("Above-floor reconstruction gate" in docs["PROTOCOL.md"], "missing above-floor gate")
        require("29/45 cells are above-floor" in docs["REPORT.md"], "missing refined M2 29/45 wording")
        require("wins 28" in docs["REPORT.md"], "missing refined M2 28-win wording")
        require("Figure 8. Randomized orthogonal bases buy identifiability" in docs["PAPER_OUTLINE.md"], "missing Figure 8 frame")

        phase_rows = count_csv_rows(work / "results" / "m2_hadamard_order_dense_r1_merged" / "phase_scan.csv")
        require(phase_rows == 155250, f"unexpected dense M2 row count: {phase_rows}")

        winner_rows = read_csv_dicts(work / "results" / "m2_boundary_audit_hadamard_order_dense_r1" / "m2_winner_cells.csv")
        strict = [row for row in winner_rows if row["scope"] == "equal_frame_non_oracle"]
        require(len(strict) == 45, f"unexpected strict winner cells: {len(strict)}")
        srht_pairwise = [
            row for row in strict
            if row["basis"] == "srht_paired" and row["correction"] == "pairwise" and row["above_floor"] == "True"
        ]
        had_random_proxy = [
            row for row in strict
            if row["basis"] == "hadamard_random_paired" and row["correction"] == "scgi_proxy" and row["above_floor"] == "True"
        ]
        sub_floor = [
            row for row in strict
            if row["basis"] == "sub_floor" and row["correction"] == "noise_floor" and row["above_floor"] == "False"
        ]
        require(len(srht_pairwise) == 28, f"unexpected SRHT/pairwise strict wins: {len(srht_pairwise)}")
        require(len(had_random_proxy) == 1, f"unexpected Hadamard-random/scgi_proxy wins: {len(had_random_proxy)}")
        require(len(sub_floor) == 16, f"unexpected sub-floor strict cells: {len(sub_floor)}")

        delta_rows = read_csv_dicts(work / "results" / "srht_m3_audit_highrho_r2" / "m3_srht_delta_summary.csv")
        require(len(delta_rows) == 20, f"unexpected M3 delta rows: {len(delta_rows)}")
        agc_slow = [
            row for row in delta_rows
            if row["correction"] == "agc" and abs(float(row["rho"]) - 0.001) < 1e-12
        ]
        require(agc_slow, "missing AGC slow-drift M3 row")
        require(float(agc_slow[0]["srht_minus_ordered_db"]) > 5.4, "M3 slow-drift SRHT delta below expected")
        fast_non_oracle = [
            row for row in delta_rows
            if row["correction"] != "oracle" and float(row["rho"]) >= 1.0
        ]
        require(fast_non_oracle and all(row["above_floor"] == "False" for row in fast_non_oracle), "fast M3 rows not masked sub-floor")

        figure8 = work / "results" / "paper_figures_r2_final" / "figure8_srht_energy_ablation.svg"
        require(figure8.exists() and figure8.stat().st_size > 50000, "missing or tiny Figure 8 SVG")

        status = {
            "ref": args.ref,
            "phase_rows": phase_rows,
            "strict_srht_pairwise_wins": len(srht_pairwise),
            "strict_hadamard_random_proxy_wins": len(had_random_proxy),
            "strict_sub_floor_cells": len(sub_floor),
            "m3_delta_rows": len(delta_rows),
            "figure8_svg_bytes": figure8.stat().st_size,
            "result": "COLAB_FRAMEWORK_SMOKE_OK",
        }
        print(json.dumps(status, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"COLAB_FRAMEWORK_SMOKE_FAIL: {exc}", file=sys.stderr, flush=True)
        raise
