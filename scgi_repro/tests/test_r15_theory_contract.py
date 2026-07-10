"""R15 regression tests for the paired-normalization theory contract."""

from __future__ import annotations

import sys
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (str(ROOT), str(SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

from mechanisms import apply_correction  # noqa: E402
from paper_experiments import classify_run_authority  # noqa: E402


def _pair_fixture() -> tuple[torch.Tensor, torch.Tensor, float, torch.Tensor]:
    dtype = torch.float64
    s1 = 10.0
    coefficients = torch.tensor([-6.0, -2.0, 0.5, 4.0], dtype=dtype)
    gain_plus = torch.tensor([1.10, 0.90, 1.25, 0.82], dtype=dtype)
    delta = torch.tensor([-0.12, 0.18, 0.07, -0.09], dtype=dtype)
    gain_minus = gain_plus * (1.0 + delta)
    bucket_plus = 0.5 * (s1 + coefficients)
    bucket_minus = 0.5 * (s1 - coefficients)
    observed = torch.empty(2 * coefficients.numel(), dtype=dtype)
    observed[0::2] = gain_plus * bucket_plus
    observed[1::2] = gain_minus * bucket_minus
    return observed, coefficients, s1, delta


def _f7_error(coefficients: torch.Tensor, s1: float, delta: torch.Tensor) -> torch.Tensor:
    x = coefficients / s1
    return -s1 * delta * (1.0 - x.square()) / (2.0 + delta * (1.0 - x))


def test_median_pair_sum_gamma_identity_float64() -> None:
    observed, coefficients, s1, delta = _pair_fixture()
    pair_sum = observed[0::2] + observed[1::2]
    assert int((pair_sum <= 1.0e-8).sum()) == 0

    corrected = apply_correction(observed, "pairwise", paired=True)
    s1_hat = pair_sum.median().abs()
    gamma = s1_hat / s1
    x = coefficients / s1
    expected_error = s1 * (
        2.0 * x * (gamma - 1.0)
        - delta * (1.0 - x) * (gamma + x)
    ) / (2.0 + delta * (1.0 - x))

    actual_error = corrected.values - coefficients
    assert torch.allclose(actual_error, expected_error, rtol=2.0e-14, atol=2.0e-14)
    assert float((actual_error - expected_error).abs().max() / s1) < 2.0e-15


def test_true_s1_reduces_exactly_to_f7() -> None:
    observed, coefficients, s1, delta = _pair_fixture()
    corrected = apply_correction(
        observed,
        "pairwise",
        paired=True,
        pair_total_intensity=s1,
    )
    expected_error = _f7_error(coefficients, s1, delta)
    assert torch.allclose(
        corrected.values - coefficients,
        expected_error,
        rtol=2.0e-14,
        atol=2.0e-14,
    )


def test_gamma_risk_three_term_decomposition() -> None:
    observed, coefficients, s1, delta = _pair_fixture()
    corrected = apply_correction(observed, "pairwise", paired=True)
    pair_sum = observed[0::2] + observed[1::2]
    gamma = pair_sum.median().abs() / s1
    e_f7 = _f7_error(coefficients, s1, delta)
    e_gamma = corrected.values - coefficients

    k = coefficients.numel()
    s2 = coefficients.square().sum() / k
    measured = e_gamma.square().sum() / (k * s2)
    f7_component = gamma.square() * e_f7.square().sum() / (k * s2)
    gauge_component = (gamma - 1.0).square()
    cross_component = (
        2.0
        * gamma
        * (gamma - 1.0)
        * torch.dot(e_f7, coefficients)
        / (k * s2)
    )
    assert torch.allclose(
        measured,
        f7_component + gauge_component + cross_component,
        rtol=2.0e-14,
        atol=2.0e-14,
    )


def test_default_pairwise_output_unchanged() -> None:
    observed, _, _, _ = _pair_fixture()
    plus = observed[0::2]
    minus = observed[1::2]
    pair_sum = plus + minus
    legacy = pair_sum.median().abs().clamp_min(1.0e-8) * (
        plus - minus
    ) / pair_sum.clamp_min(1.0e-8)
    corrected = apply_correction(observed, "pairwise", paired=True)
    assert torch.equal(corrected.values, legacy)


def test_legacy_positional_agc_window_is_unchanged() -> None:
    observed = torch.linspace(0.8, 1.2, 31, dtype=torch.float64)
    positional = apply_correction(observed, "agc", None, False, 7)
    keyword = apply_correction(observed, "agc", agc_window=7)
    assert torch.equal(positional.values, keyword.values)
    assert torch.equal(positional.gain_hat, keyword.gain_hat)


def test_pair_total_intensity_validation() -> None:
    observed, _, _, _ = _pair_fixture()
    for invalid in (0.0, -1.0, float("nan"), float("inf")):
        try:
            apply_correction(
                observed,
                "pairwise",
                paired=True,
                pair_total_intensity=invalid,
            )
        except ValueError:
            continue
        raise AssertionError(f"Expected ValueError for {invalid!r}")


def test_clean_committed_manifest_is_authoritative() -> None:
    manifest = {
        "git_commit_full": "a" * 40,
        "git_dirty": True,
        "git_dirty_excluding_output": False,
    }
    assert classify_run_authority(manifest) == "submission_authoritative_clean_commit"


def test_manifest_without_commit_is_provisional() -> None:
    manifest = {
        "git_commit_full": None,
        "git_dirty_excluding_output": False,
    }
    assert classify_run_authority(manifest) == "provisional_dirty_tree_qa"


def test_manifest_with_external_or_unknown_dirt_is_provisional() -> None:
    for external_dirty in (True, None):
        manifest = {
            "git_commit_full": "b" * 40,
            "git_dirty_excluding_output": external_dirty,
        }
        assert classify_run_authority(manifest) == "provisional_dirty_tree_qa"
