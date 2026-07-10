"""Tests for run-manifest v2 provenance and the deterministic shard merge.

Covers:
* ``build_run_manifest`` returns schema v2 with the new keys at the correct
  types (and preserves the v1 keys);
* ``sha256_file`` matches an independent hash (the mechanism behind
  ``runner_sha256``);
* the merge is deterministic (same inputs -> same output bytes);
* the merge refuses on conflicting duplicates and drops exact duplicates;
* (regression, when the shard data is present) the merge content-reproduces the
  two flagship threshold CSVs.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
for path in (str(ROOT), str(ROOT / "src")):
    if path not in sys.path:
        sys.path.insert(0, path)

from src.paper_experiments import build_run_manifest, sha256_file  # noqa: E402
import merge_result_shards as mrs  # noqa: E402


V1_KEYS = {
    "utc_timestamp",
    "git_commit",
    "hostname",
    "python_version",
    "torch_version",
    "numpy_version",
    "args",
}


class TestManifestV2(unittest.TestCase):
    def _manifest(self):
        args = argparse.Namespace(alpha=1, beta="x", flag=True)
        return build_run_manifest(args, ROOT, extra={"rows": 7})

    def test_v1_keys_preserved(self):
        manifest = self._manifest()
        for key in V1_KEYS:
            self.assertIn(key, manifest, f"v1 key {key} dropped -> breaks old consumers")
        self.assertEqual(manifest["args"], {"alpha": 1, "beta": "x", "flag": True})
        self.assertEqual(manifest["rows"], 7)  # extra merged through

    def test_v2_new_keys_and_types(self):
        manifest = self._manifest()
        self.assertEqual(manifest["manifest_version"], 2)

        # git provenance
        for key in ("git_commit_full", "git_branch", "git_diff_sha256"):
            self.assertIn(key, manifest)
            self.assertTrue(manifest[key] is None or isinstance(manifest[key], str))
        self.assertIsInstance(manifest["git_dirty"], bool)
        self.assertIsInstance(manifest["git_status_porcelain"], list)
        for line in manifest["git_status_porcelain"]:
            self.assertIsInstance(line, str)

        # runner + argv + env
        self.assertTrue(manifest["runner_path"] is None or isinstance(manifest["runner_path"], str))
        self.assertTrue(manifest["runner_sha256"] is None or isinstance(manifest["runner_sha256"], str))
        self.assertIsInstance(manifest["argv"], list)
        for key in ("python_version", "torch_version", "numpy_version", "platform"):
            self.assertIsInstance(manifest[key], str)
            self.assertTrue(manifest[key])

        # git_commit and git_commit_full agree (both = full HEAD SHA)
        self.assertEqual(manifest["git_commit"], manifest["git_commit_full"])

        # when a diff fingerprint is present it is a 64-hex sha256
        if manifest["git_diff_sha256"] is not None:
            self.assertEqual(len(manifest["git_diff_sha256"]), 64)
            int(manifest["git_diff_sha256"], 16)  # raises if not hex

    def test_runner_sha256_matches_runner_path(self):
        manifest = self._manifest()
        if manifest["runner_path"] is not None:
            self.assertEqual(manifest["runner_sha256"], sha256_file(manifest["runner_path"]))


class TestSha256File(unittest.TestCase):
    def test_matches_independent_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "payload.bin"
            payload = b"provenance-v2\x00\x01\x02 abc"
            target.write_bytes(payload)
            self.assertEqual(sha256_file(target), hashlib.sha256(payload).hexdigest())

    def test_missing_file_returns_none(self):
        self.assertIsNone(sha256_file(Path(tempfile.gettempdir()) / "does-not-exist-xyz.bin"))


def _shard_frames():
    """Two synthetic shards with an interleaved cell index (like the flagships)."""
    s0 = pd.DataFrame(
        {
            "K": [64, 64, 64],
            "seed": [0, 2, 4],
            "unit_index": [0, 2, 4],
            "object_kind": ["a", "b", "c"],
            "score": [0.1, 0.2, 0.3],
        }
    )
    s1 = pd.DataFrame(
        {
            "K": [64, 64, 64],
            "seed": [1, 3, 5],
            "unit_index": [1, 3, 5],
            "object_kind": ["a", "b", "c"],
            "score": [0.15, 0.25, 0.35],
        }
    )
    return s0, s1


class TestMergeDeterminism(unittest.TestCase):
    def test_key_resolution(self):
        s0, _ = _shard_frames()
        keys = mrs.resolve_key_columns(s0.columns)
        self.assertEqual(keys, ["K", "seed", "object_kind", "unit_index"])
        self.assertNotIn("score", keys)  # measured value column excluded

    def test_same_inputs_same_bytes(self):
        s0, s1 = _shard_frames()
        keys = mrs.resolve_key_columns(s0.columns)
        m1, stats1 = mrs.merge_frames([s0, s1], keys, order="sort")
        m2, stats2 = mrs.merge_frames([s0, s1], keys, order="sort")
        self.assertEqual(mrs.dataframe_to_csv_bytes(m1), mrs.dataframe_to_csv_bytes(m2))
        self.assertEqual(stats1, stats2)
        self.assertEqual(stats1["merged_rows"], 6)
        self.assertEqual(stats1["exact_duplicates_dropped"], 0)
        # sort mode is order-independent of shard supply order
        m_rev, _ = mrs.merge_frames([s1, s0], keys, order="sort")
        self.assertEqual(mrs.dataframe_to_csv_bytes(m1), mrs.dataframe_to_csv_bytes(m_rev))

    def test_exact_duplicate_rows_dropped(self):
        s0, _ = _shard_frames()
        dup = pd.concat([s0, s0.iloc[[0]]], ignore_index=True)  # repeat row 0 verbatim
        keys = mrs.resolve_key_columns(dup.columns)
        merged, stats = mrs.merge_frames([dup], keys, order="sort")
        self.assertEqual(stats["exact_duplicates_dropped"], 1)
        self.assertEqual(stats["merged_rows"], 3)


class TestMergeConflictRefusal(unittest.TestCase):
    def test_conflicting_duplicate_raises(self):
        s0, _ = _shard_frames()
        conflict = s0.iloc[[0]].copy()
        conflict.loc[:, "score"] = 999.0  # same key, different value column
        combined = [s0, conflict]
        keys = mrs.resolve_key_columns(s0.columns)
        with self.assertRaises(mrs.MergeConflictError):
            mrs.merge_frames(combined, keys, order="sort")

    def test_column_mismatch_raises(self):
        s0, s1 = _shard_frames()
        s1_bad = s1.rename(columns={"score": "value"})
        with self.assertRaises(ValueError):
            mrs.merge_frames([s0, s1_bad], ["K", "seed"], order="sort")


class TestFlagshipContentIdentity(unittest.TestCase):
    """Regression: T2 merge content-reproduces the published flagship CSVs."""

    FLAGSHIPS = {
        "full": (
            "results/tall_design_threshold_full_r1_merged/threshold_scan.csv",
            "results/colab_imports/pro1_threshold_full_shard0of2_r1/artifacts/threshold_scan_shard0of2.csv",
            "results/colab_imports/pro2_threshold_full_shard1of2_r1/artifacts/threshold_scan_shard1of2.csv",
        ),
        "K128": (
            "results/tall_design_threshold_K128_r1_merged/threshold_scan.csv",
            "results/colab_imports/pro1_threshold_K128_shard0/artifacts/threshold_scan_shard0of2.csv",
            "results/colab_imports/pro2_threshold_K128_shard1/artifacts/threshold_scan_shard1of2.csv",
        ),
    }

    @staticmethod
    def _sorted_row_hash(text: str) -> str:
        lines = text.split("\n")
        header = lines[0]
        rows = sorted(line for line in lines[1:] if line != "")
        return hashlib.sha256(("\n".join([header] + rows)).encode("utf-8")).hexdigest()

    def test_flagships_reproduce(self):
        for name, (merged_rel, s0_rel, s1_rel) in self.FLAGSHIPS.items():
            merged_path = ROOT / merged_rel
            s0_path, s1_path = ROOT / s0_rel, ROOT / s1_rel
            if not (merged_path.exists() and s0_path.exists() and s1_path.exists()):
                self.skipTest(f"flagship shard data absent for {name}")
            s0, s1 = pd.read_csv(s0_path), pd.read_csv(s1_path)
            keys = mrs.resolve_key_columns(s0.columns)
            # input order -> byte identity
            merged_input, _ = mrs.merge_frames([s0, s1], keys, order="input")
            existing_bytes = merged_path.read_bytes()
            self.assertEqual(
                mrs.dataframe_to_csv_bytes(merged_input), existing_bytes,
                f"{name}: --order input should be byte-identical",
            )
            # sort order -> content identity (row-order-independent)
            merged_sort, _ = mrs.merge_frames([s0, s1], keys, order="sort")
            self.assertEqual(
                self._sorted_row_hash(mrs.dataframe_to_csv_bytes(merged_sort).decode("utf-8")),
                self._sorted_row_hash(existing_bytes.decode("utf-8")),
                f"{name}: --order sort should be content-identical",
            )


if __name__ == "__main__":
    unittest.main()
