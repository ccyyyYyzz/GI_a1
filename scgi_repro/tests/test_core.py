"""Core smoke tests for the SCGI reproduction helpers.

The core implementation is being developed in parallel, so these tests discover
common module/function names at runtime. Missing optional basis code is skipped;
when core modules are present, the tests validate the expected numerical
contracts without depending on pytest.
"""

from __future__ import annotations

import importlib
import inspect
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

try:
    import torch
except Exception:  # pragma: no cover - torch is expected for core tests
    torch = None


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (str(ROOT), str(SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)


def _import_first(module_names: list[str]):
    last_error = None
    for name in module_names:
        try:
            return importlib.import_module(name)
        except Exception as exc:  # pragma: no cover - diagnostic fallback
            last_error = exc
    raise unittest.SkipTest(
        f"None of the candidate modules could be imported: {module_names}. "
        f"Last error: {last_error}"
    )


def _find_function(module_names: list[str], function_names: list[str]):
    module = _import_first(module_names)
    for name in function_names:
        func = getattr(module, name, None)
        if callable(func):
            return func
    raise unittest.SkipTest(
        f"{module.__name__} does not expose any of: {function_names}"
    )


def _call_candidates(func, candidates: list[tuple[tuple[object, ...], dict[str, object]]]):
    errors: list[str] = []
    for args, kwargs in candidates:
        try:
            return func(*args, **kwargs)
        except (TypeError, ValueError, AttributeError) as exc:
            errors.append(f"{args!r} {kwargs!r}: {exc}")
    joined = "\n".join(errors[-5:])
    raise AssertionError(f"Could not call {func.__name__} with supported signatures:\n{joined}")


def _extract_array(result) -> np.ndarray:
    for attr in ("signed_rows", "patterns", "basis", "matrix"):
        if hasattr(result, attr):
            value = getattr(result, attr)
            if value is not None:
                return np.asarray(value)
    if isinstance(result, tuple):
        for item in result:
            try:
                arr = np.asarray(item)
            except Exception:
                continue
            if arr.size:
                return arr
    if isinstance(result, dict):
        for key in ("image", "reconstruction", "recon", "scales", "gain", "basis", "patterns"):
            if key in result:
                return np.asarray(result[key])
    return np.asarray(result)


def _flatten_basis(arr: np.ndarray) -> np.ndarray:
    arr = np.asarray(arr)
    if arr.ndim == 3:
        return arr.reshape(arr.shape[0], -1)
    if arr.ndim == 2:
        return arr
    if arr.ndim == 1:
        side = int(math.sqrt(arr.size))
        if side * side == arr.size:
            return arr.reshape(side, side)
    raise AssertionError(f"Unexpected basis shape {arr.shape!r}")


class TestPlottingHelpers(unittest.TestCase):
    def test_pil_plotting_helpers_create_files(self):
        plotting = importlib.import_module("src.plotting")
        images = [np.eye(8), np.ones((8, 8)) * 3.0]
        series = {"loss": [1.0, 0.7, 0.5], "psnr": [12.0, 16.0, 18.0]}
        metrics = [{"name": "smoke", "psnr": 18.5, "ssim": 0.72}]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            grid = plotting.save_image_grid(tmp_path / "grid.png", images, labels=["eye", "flat"])
            line = plotting.save_series_plot(tmp_path / "series.png", series)
            table = plotting.save_metrics_table(tmp_path / "metrics.png", metrics)
            csv = plotting.save_metrics_csv(tmp_path / "metrics.csv", metrics)

            for path in (grid, line, table, csv):
                self.assertTrue(path.exists(), path)
                self.assertGreater(path.stat().st_size, 0, path)

    def test_dynamic_uint8_scaling_handles_tiny_positive_values(self):
        plotting = importlib.import_module("src.plotting")
        tiny = np.exp(np.linspace(0.0, -720.0, 4096, dtype=np.float64)).reshape(64, 64)
        scaled = plotting.normalize_to_uint8(tiny)
        self.assertEqual(scaled.dtype, np.uint8)
        self.assertEqual(scaled.shape, tiny.shape)
        self.assertTrue(np.all(np.isfinite(scaled)))
        self.assertGreater(int(scaled.max()), int(scaled.min()))


class TestCoreNumerics(unittest.TestCase):
    def setUp(self):
        if torch is None:
            self.skipTest("torch is not available for core numerical tests.")

    def test_dynamic_scaling_generation_does_not_underflow(self):
        func = _find_function(
            [
                "src.data_sim",
                "data_sim",
                "src.channels",
                "channels",
                "src.forward",
                "forward",
                "src.core",
                "core",
            ],
            [
                "dynamic_factors",
                "generate_dynamic_scaling",
                "generate_scaling_factors",
                "make_dynamic_scaling",
                "make_scaling_factors",
                "generate_gain_sequence",
                "make_gain_sequence",
                "dynamic_scaling",
            ],
        )
        n = 16_384
        lam = 0.9995
        result = _call_candidates(
            func,
            [
                ((1, n, lam, lam, torch.Generator().manual_seed(0)), {}),
                ((), {"n": n, "lambda_value": lam}),
                ((), {"n": n, "lam": lam}),
                ((), {"num_measurements": n, "lambda_value": lam}),
                ((), {"num_measurements": n, "lambda_min": lam, "lambda_max": lam, "seed": 0}),
                ((), {"length": n, "lambda_value": lam}),
                ((n, lam), {}),
                ((n,), {"lambda_range": (lam, lam), "seed": 0}),
                ((n,), {"lambda_min": lam, "lambda_max": lam, "seed": 0}),
            ],
        )
        scales = np.asarray(_extract_array(result), dtype=np.float64).reshape(-1)
        self.assertEqual(scales.size, n)
        self.assertTrue(np.all(np.isfinite(scales)))
        self.assertTrue(np.all(scales > 0.0))
        self.assertGreater(scales[-1], 0.0)

    def test_gain_corrector_range_covers_full_profile_decay(self):
        scgi_model = importlib.import_module("src.scgi_model")
        model = scgi_model.make_scgi_model(
            {
                "scgi": {
                    "model_kind": "gain_unet",
                    "unet_base_channels": 2,
                    "unet_depth": 1,
                    "use_coord_channels": False,
                    "gain_min": 1.0e-4,
                    "gain_max": 2.0,
                }
            }
        )
        full_tail_gain = 0.9995 ** (16_384 - 1)
        self.assertLess(full_tail_gain, 0.001)
        self.assertLessEqual(model.gain_min, full_tail_gain)
        self.assertGreaterEqual(model.gain_max, 1.0)

    def test_exponential_residual_model_can_remove_known_decay(self):
        scgi_model = importlib.import_module("src.scgi_model")
        model = scgi_model.make_scgi_model(
            {
                "active": {"lambda_min": 0.99, "lambda_max": 1.0},
                "scgi": {
                    "model_kind": "exponential_residual_unet",
                    "unet_base_channels": 2,
                    "unet_depth": 1,
                    "use_coord_channels": False,
                    "residual_max_blend": 0.0,
                },
            }
        )
        n = 16 * 16
        lam = 0.99
        gains = (lam ** torch.arange(n, dtype=torch.float32)).reshape(1, 1, 16, 16)
        pred = model(gains)
        self.assertLess(float(torch.mean((pred - torch.ones_like(pred)) ** 2)), 1.0e-6)

    def test_padded_scgi_correction_preserves_sequence_length(self):
        train_scgi = importlib.import_module("src.train_scgi")

        class ScaleModel(torch.nn.Module):
            def forward(self, x):
                return 0.5 * x

        seq = torch.linspace(0.0, 1.0, 10).reshape(1, 10)
        corrected = train_scgi.correct_measurements_padded(ScaleModel(), seq)
        self.assertEqual(tuple(corrected.shape), tuple(seq.shape))
        self.assertTrue(torch.allclose(corrected, 0.5 * seq))

    def test_dgi_output_shape_matches_object_shape(self):
        func = _find_function(
            [
                "src.dgi",
                "dgi",
                "src.reconstruction",
                "reconstruction",
                "src.ghost",
                "ghost",
                "src.core",
                "core",
            ],
            [
                "dgi_reconstruct",
                "reconstruct_dgi",
                "differential_ghost_imaging",
                "dgi",
                "compute_dgi",
            ],
        )
        rng = np.random.default_rng(7)
        n, h, w = 96, 12, 12
        obj = np.zeros((h, w), dtype=np.float64)
        obj[3:8, 2:7] = 1.0
        patterns = rng.random((n, h, w), dtype=np.float64)
        flat_patterns = patterns.reshape(n, -1)
        buckets = np.sum(patterns * obj[None, :, :], axis=(1, 2))
        torch_patterns = torch.from_numpy(flat_patterns).float()
        torch_buckets = torch.from_numpy(buckets).float()

        result = _call_candidates(
            func,
            [
                ((torch_buckets, torch_patterns, h), {}),
                ((patterns, buckets), {}),
                ((buckets, patterns), {}),
                ((flat_patterns, buckets), {"image_shape": (h, w)}),
                ((buckets, flat_patterns), {"image_shape": (h, w)}),
                ((), {"patterns": patterns, "buckets": buckets}),
                ((), {"patterns": patterns, "measurements": buckets}),
                ((), {"bucket": buckets, "patterns": patterns}),
                ((), {"measurements": buckets, "patterns": flat_patterns, "image_shape": (h, w)}),
            ],
        )
        recon = np.asarray(_extract_array(result), dtype=np.float64)
        if recon.ndim == 1 and recon.size == h * w:
            recon = recon.reshape(h, w)
        if recon.ndim == 3 and recon.shape[0] == 1:
            recon = recon[0]
        self.assertEqual(recon.shape, (h, w))
        self.assertTrue(np.all(np.isfinite(recon)))


class TestMetrics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.truth = np.zeros((32, 32), dtype=np.float64)
        cls.truth[8:24, 10:22] = 1.0
        rng = np.random.default_rng(11)
        cls.recon = np.clip(cls.truth + rng.normal(0.0, 0.05, cls.truth.shape), 0.0, 1.0)
        cls.signal_mask = cls.truth > 0.5
        cls.background_mask = cls.truth < 0.5
        if torch is not None:
            cls.truth_t = torch.from_numpy(cls.truth).float()
            cls.recon_t = torch.from_numpy(cls.recon).float()
            cls.measurements_t = torch.from_numpy(rng.normal(0.0, 1.0, 256)).float()

    def test_cnr_basic_validity(self):
        if torch is None:
            self.skipTest("torch is not available for metric tests.")
        func = _find_function(
            ["src.metrics", "metrics", "src.evaluation", "evaluation", "src.core", "core"],
            ["cnr", "compute_cnr", "contrast_to_noise_ratio"],
        )
        result = _call_candidates(
            func,
            [
                ((self.recon_t, self.truth_t), {}),
                ((self.recon, self.signal_mask, self.background_mask), {}),
                ((), {"image": self.recon, "signal_mask": self.signal_mask, "background_mask": self.background_mask}),
                ((self.recon[self.signal_mask], self.recon[self.background_mask]), {}),
                ((self.recon, self.signal_mask), {}),
            ],
        )
        value = float(np.asarray(result).reshape(-1)[0])
        self.assertTrue(np.isfinite(value))
        self.assertGreater(value, 0.0)

    def test_psnr_basic_validity(self):
        if torch is None:
            self.skipTest("torch is not available for metric tests.")
        func = _find_function(
            ["src.metrics", "metrics", "src.evaluation", "evaluation", "src.core", "core"],
            ["psnr", "compute_psnr", "peak_signal_to_noise_ratio"],
        )
        result = _call_candidates(
            func,
            [
                ((self.recon_t, self.truth_t), {}),
                ((self.truth, self.recon), {"data_range": 1.0}),
                ((self.recon, self.truth), {"data_range": 1.0}),
                ((self.truth, self.recon), {}),
                ((), {"reference": self.truth, "estimate": self.recon, "data_range": 1.0}),
                ((), {"target": self.truth, "prediction": self.recon, "data_range": 1.0}),
            ],
        )
        value = float(np.asarray(result).reshape(-1)[0])
        self.assertTrue(np.isfinite(value))
        self.assertGreater(value, 10.0)

    def test_ssim_basic_validity(self):
        if torch is None:
            self.skipTest("torch is not available for metric tests.")
        func = _find_function(
            ["src.metrics", "metrics", "src.evaluation", "evaluation", "src.core", "core"],
            ["ssim", "compute_ssim", "structural_similarity", "simple_ssim"],
        )
        result = _call_candidates(
            func,
            [
                ((self.recon_t, self.truth_t), {}),
                ((self.truth, self.recon), {"data_range": 1.0}),
                ((self.recon, self.truth), {"data_range": 1.0}),
                ((self.truth, self.recon), {}),
                ((), {"reference": self.truth, "estimate": self.recon, "data_range": 1.0}),
                ((), {"target": self.truth, "prediction": self.recon, "data_range": 1.0}),
            ],
        )
        value = float(np.asarray(result).reshape(-1)[0])
        self.assertTrue(np.isfinite(value))
        self.assertGreaterEqual(value, -0.01)
        self.assertLessEqual(value, 1.01)

    def test_ks_basic_validity(self):
        if torch is None:
            self.skipTest("torch is not available for metric tests.")
        func = _find_function(
            ["src.metrics", "metrics", "src.evaluation", "evaluation", "src.core", "core"],
            [
                "normal_ks_test",
                "ks_test",
                "compute_ks",
                "ks_statistic",
                "kolmogorov_smirnov",
                "two_sample_ks",
            ],
        )
        rng = np.random.default_rng(5)
        x = rng.normal(0.0, 1.0, 256)
        y = rng.normal(0.35, 1.0, 256)
        result = _call_candidates(
            func,
            [
                ((self.measurements_t,), {}),
                ((x, y), {}),
                ((), {"x": x, "y": y}),
                ((), {"sample_a": x, "sample_b": y}),
            ],
        )
        if isinstance(result, dict):
            stat = float(result.get("statistic", result.get("ks", result.get("d"))))
            p_value = result.get("pvalue", result.get("p_value", result.get("p")))
        elif isinstance(result, tuple):
            stat = float(result[0])
            p_value = result[1] if len(result) > 1 else None
        else:
            stat = float(np.asarray(result).reshape(-1)[0])
            p_value = None
        self.assertTrue(np.isfinite(stat))
        self.assertGreaterEqual(stat, 0.0)
        self.assertLessEqual(stat, 1.0)
        if p_value is not None:
            p_value = float(p_value)
            self.assertTrue(np.isfinite(p_value))
            self.assertGreaterEqual(p_value, 0.0)
            self.assertLessEqual(p_value, 1.0)


class TestChannelMechanisms(unittest.TestCase):
    def setUp(self):
        if torch is None:
            self.skipTest("torch is not available for channel tests.")
        self.mechanisms = importlib.import_module("src.mechanisms")

    def test_jitter_adjacent_pair_difference_tracks_rho(self):
        slow = self.mechanisms.make_multiplicative_channel(
            2048, model="jitter", rho=1.0e-4, sigma_a=0.25, seed=123
        ).gains
        fast = self.mechanisms.make_multiplicative_channel(
            2048, model="jitter", rho=1.0, sigma_a=0.25, seed=123
        ).gains
        slow_pair_diff = torch.mean(torch.abs(slow[0::2] - slow[1::2]) / slow[0::2].clamp_min(1.0e-8))
        fast_pair_diff = torch.mean(torch.abs(fast[0::2] - fast[1::2]) / fast[0::2].clamp_min(1.0e-8))
        self.assertLess(float(slow_pair_diff), 0.05)
        self.assertGreater(float(fast_pair_diff), 3.0 * float(slow_pair_diff))

    def test_reference_gain_interpolation_tracks_slow_channel(self):
        gains = self.mechanisms.make_multiplicative_channel(
            256, model="ou", rho=0.005, sigma_a=0.2, seed=321
        ).gains
        estimated = self.mechanisms.estimate_reference_gain(gains, period=8)
        rel_mse = torch.mean((estimated - gains) ** 2) / torch.mean(gains ** 2).clamp_min(1.0e-8)
        self.assertLess(float(rel_mse), 0.01)

    def test_noisy_reference_gain_remains_positive(self):
        gains = self.mechanisms.make_multiplicative_channel(
            128, model="ou", rho=0.01, sigma_a=0.2, seed=322
        ).gains
        estimated = self.mechanisms.estimate_reference_gain(
            gains,
            period=8,
            reference_photons=2000.0,
            reference_read_noise=0.001,
            seed=44,
        )
        self.assertEqual(tuple(estimated.shape), tuple(gains.shape))
        self.assertTrue(torch.all(torch.isfinite(estimated)))
        self.assertTrue(torch.all(estimated > 0))

    def test_reference_anchor_count_includes_terminal_anchor(self):
        self.assertEqual(self.mechanisms.reference_anchor_count(2048, 8), 257)
        self.assertEqual(self.mechanisms.reference_anchor_count(2048, 2), 1025)
        self.assertEqual(self.mechanisms.reference_anchor_count(2048, 32), 65)
        self.assertEqual(self.mechanisms.reference_anchor_count(2049, 8), 257)

    def test_slm_quantization_and_timing_jitter_are_bounded(self):
        patterns = torch.tensor([0.0, 0.2, 0.7, 1.0])
        quantized = self.mechanisms.quantize_slm_patterns(patterns, levels=4, contrast_ratio=1000.0)
        self.assertTrue(torch.all(quantized >= 0.001))
        self.assertTrue(torch.all(quantized <= 1.0))
        self.assertLessEqual(int(torch.unique(quantized).numel()), 4)

        gains = torch.linspace(0.5, 1.5, 64)
        jittered = self.mechanisms.apply_frame_timing_jitter(gains, jitter_std_frames=0.2, seed=9)
        self.assertEqual(tuple(jittered.shape), tuple(gains.shape))
        self.assertTrue(torch.all(torch.isfinite(jittered)))
        self.assertAlmostEqual(float(jittered.mean()), 1.0, places=5)

    def test_detector_noise_is_seeded_and_finite(self):
        signal = torch.full((64,), 0.5)
        noisy_a = self.mechanisms.apply_detector_noise(signal, photon_count=1000.0, read_noise=0.001, seed=11)
        noisy_b = self.mechanisms.apply_detector_noise(signal, photon_count=1000.0, read_noise=0.001, seed=11)
        self.assertTrue(torch.all(torch.isfinite(noisy_a)))
        self.assertTrue(torch.allclose(noisy_a, noisy_b))
        self.assertGreater(float(torch.std(noisy_a)), 0.0)

    def test_scgi_proxy_gain_is_blind_positive_and_tracks_slow_channel(self):
        gains = self.mechanisms.make_multiplicative_channel(
            256, model="ou", rho=0.005, sigma_a=0.2, seed=456
        ).gains
        observed = 3.0 * gains
        estimated = self.mechanisms.estimate_scgi_proxy_gain(observed, window=33)
        rel_mse = torch.mean((estimated - gains) ** 2) / torch.mean(gains ** 2).clamp_min(1.0e-8)
        self.assertEqual(tuple(estimated.shape), tuple(gains.shape))
        self.assertTrue(torch.all(torch.isfinite(estimated)))
        self.assertTrue(torch.all(estimated > 0))
        self.assertAlmostEqual(float(estimated.mean()), 1.0, places=5)
        self.assertLess(float(rel_mse), 0.05)

    def test_scgi_proxy_apply_correction_does_not_require_true_gains(self):
        observed = torch.linspace(0.5, 2.0, 64)
        corrected = self.mechanisms.apply_correction(observed, correction="scgi_proxy", true_gains=None)
        self.assertFalse(corrected.values_are_coefficients)
        self.assertIsNotNone(corrected.gain_hat)
        self.assertEqual(tuple(corrected.values.shape), tuple(observed.shape))
        self.assertTrue(torch.all(torch.isfinite(corrected.values)))

    def test_scgi_frozen_apply_correction_uses_callable(self):
        observed = torch.linspace(0.2, 1.0, 10)
        corrected = self.mechanisms.apply_correction(
            observed,
            correction="scgi_frozen",
            true_gains=None,
            scgi_corrector=lambda values: values * 0.25,
        )
        self.assertFalse(corrected.values_are_coefficients)
        self.assertIsNone(corrected.gain_hat)
        self.assertTrue(torch.allclose(corrected.values, observed * 0.25))


class TestBasisGeneration(unittest.TestCase):
    def setUp(self):
        if not (SRC / "basis.py").exists():
            self.skipTest("src/basis.py is not present yet; basis generation tests skipped.")
        self.basis = importlib.import_module("src.basis")

    def test_hadamard_generation_shape_and_values(self):
        func = None
        for name in (
            "hadamard_matrix",
            "generate_hadamard_basis",
            "make_hadamard_basis",
            "make_hadamard_paired_basis",
            "hadamard_basis",
            "walsh_hadamard_basis",
        ):
            candidate = getattr(self.basis, name, None)
            if callable(candidate):
                func = candidate
                break
        if func is None:
            self.fail("basis.py exists but does not expose a Hadamard generation function.")

        h, w = 8, 8
        p = h * w
        result = _call_candidates(
            func,
            [
                ((p,), {}),
                ((), {"n": p}),
                ((), {"order": p}),
                ((), {"size": p}),
                ((), {"image_shape": (h, w)}),
                (((h, w),), {}),
            ],
        )
        basis = _flatten_basis(_extract_array(result).astype(np.float64))
        self.assertIn(basis.shape, {(p, p), (p, h, w)})
        flat = _flatten_basis(basis)
        self.assertEqual(flat.shape[1], p)
        self.assertTrue(np.all(np.isfinite(flat)))
        self.assertLessEqual(np.max(np.abs(flat)), 1.0 + 1e-9)

    def test_srht_generation_shape_and_values(self):
        func = None
        for name in (
            "srht_matrix",
            "generate_srht_basis",
            "make_srht_basis",
            "make_srht_paired_basis",
            "srht_basis",
            "subsampled_randomized_hadamard",
        ):
            candidate = getattr(self.basis, name, None)
            if callable(candidate):
                func = candidate
                break
        if func is None:
            self.fail("basis.py exists but does not expose an SRHT generation function.")

        h, w = 8, 8
        p = h * w
        m = 16
        result = _call_candidates(
            func,
            [
                ((p,), {"num_coefficients": m, "seed": 123}),
                ((p,), {"num_coefficients": m, "seed": 123, "permute_rows": True}),
                ((m, p), {"seed": 123}),
                ((p,), {"m": m, "seed": 123}),
                ((p,), {"num_patterns": m, "seed": 123}),
                ((), {"n": p, "m": m, "seed": 123}),
                ((), {"size": p, "num_patterns": m, "seed": 123}),
                ((), {"image_shape": (h, w), "num_patterns": m, "seed": 123}),
                ((), {"image_shape": (h, w), "m": m, "seed": 123}),
            ],
        )
        basis = _flatten_basis(_extract_array(result).astype(np.float64))
        self.assertEqual(basis.shape[1], p)
        self.assertIn(basis.shape[0], {m, p, 2 * m})
        self.assertTrue(np.all(np.isfinite(basis)))
        self.assertGreater(np.linalg.norm(basis), 0.0)

    def test_dct_and_fourier_static_roundtrip(self):
        p = 16
        x = torch.linspace(0.0, 1.0, p)
        for name in ("dct_paired", "fourier_fourstep"):
            basis = self.basis.make_basis(name, num_pixels=p)
            y = basis.measure(x)
            recon = basis.reconstruct(y)
            self.assertEqual(tuple(recon.shape), (p,))
            self.assertTrue(torch.all(torch.isfinite(recon)))
            self.assertLess(float(torch.mean((recon - x) ** 2)), 1.0e-10, name)


if __name__ == "__main__":
    unittest.main()
