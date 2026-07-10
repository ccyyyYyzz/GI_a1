"""R13 theory-repair regression tests.

Covers the checks mandated by the R13 integration (paper_draft/REVIEWS/
GPT_R13_THEORY_PREWORK/05_MAIN_AGENT_PATCH_MAP.md, Sec. 6):

* exact carrier root of the calibrated soft-log estimator (Theorem C');
* all-zero window clamps to the lower endpoint (finite, no divergence);
* truncated-edge first-moment failure vs. interior identity (Remark D.4.2);
* centered-log projection / gauge invariance (quotient loss);
* oracle local-shift Fisher information (D.13);
* deterministic-Delta counterexample to a Var(Delta)-only pair law (F.8);
* raw vs scale-aligned metric relation (F.17) and non-proportionality;
* Walsh triple-moment counterexample to joint row exchangeability (E.9);
* data integrity + provenance of the raw-metric export
  (results/prop3_raw_metric_r1/, written by run_prop3_raw_metric_export.py).
"""

from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "results" / "prop3_raw_metric_r1"
ALIGNED_DIR = ROOT / "results" / "prop3_nofreeparam_r1"


# ---------------------------------------------------------------------------
# Small exact helpers (numpy-only; no torch needed for the pure-math checks)
# ---------------------------------------------------------------------------

def m_alpha(lam: float, alpha: float = 0.5, tail: float = 1e-14) -> float:
    """E[log(C + alpha)] for C ~ Pois(lam), truncated Poisson summation."""
    if lam <= 0.0:
        return math.log(alpha)
    cmax = int(max(20, lam + 12.0 * math.sqrt(lam) + 20))
    c = np.arange(cmax + 1)
    logpmf = -lam + c * math.log(lam) - np.array([math.lgamma(k + 1) for k in c])
    pmf = np.exp(logpmf)
    assert 1.0 - pmf.sum() < tail, "Poisson tail not negligible"
    return float((pmf * np.log(c + alpha)).sum())


def window_curve(theta: float, carriers: np.ndarray, weights: np.ndarray,
                 alpha: float = 0.5) -> float:
    """M_n(theta) = sum_k w_k m_alpha(e^theta * b_k)."""
    return float(sum(w * m_alpha(math.exp(theta) * b, alpha)
                     for w, b in zip(weights, carriers)))


def clamped_root(y: float, carriers: np.ndarray, weights: np.ndarray,
                 lo: float, hi: float, alpha: float = 0.5,
                 iters: int = 80) -> float:
    """Endpoint-clamped generalized inverse of the strictly increasing M_n."""
    m_lo = window_curve(lo, carriers, weights, alpha)
    m_hi = window_curve(hi, carriers, weights, alpha)
    if y <= m_lo:
        return lo
    if y >= m_hi:
        return hi
    a, b = lo, hi
    for _ in range(iters):
        mid = 0.5 * (a + b)
        if window_curve(mid, carriers, weights, alpha) < y:
            a = mid
        else:
            b = mid
    return 0.5 * (a + b)


class TestExactCarrierRoot(unittest.TestCase):
    """The calibrated estimator inverts its own forward curve exactly."""

    def test_exact_root_recovery(self):
        rng = np.random.default_rng(1234)
        carriers = rng.uniform(0.2, 2.0, size=7)
        weights = np.full(7, 1.0 / 7)
        lo, hi = -2.0, 2.0
        for theta_true in [-1.3, -0.25, 0.0, 0.6, 1.7]:
            y = window_curve(theta_true, carriers, weights)
            theta_hat = clamped_root(y, carriers, weights, lo, hi)
            self.assertLess(abs(theta_hat - theta_true), 1e-10,
                            f"root mismatch at theta={theta_true}")

    def test_monotone_curve(self):
        carriers = np.array([0.5, 1.0, 1.5])
        weights = np.full(3, 1.0 / 3)
        grid = np.linspace(-2.0, 2.0, 41)
        vals = [window_curve(t, carriers, weights) for t in grid]
        self.assertTrue(np.all(np.diff(vals) > 0), "M_n must be strictly increasing")


class TestAllZeroClamp(unittest.TestCase):
    """An all-zero window gives y = log(alpha) and clamps to theta_min, finite."""

    def test_all_zero_window_clamps_low(self):
        alpha = 0.5
        carriers = np.array([0.5, 1.0, 1.5])
        weights = np.full(3, 1.0 / 3)
        counts = np.zeros(3)
        y = float(np.sum(weights * np.log(counts + alpha)))
        self.assertAlmostEqual(y, math.log(alpha), places=12)
        lo, hi = -2.0, 2.0
        theta_hat = clamped_root(y, carriers, weights, lo, hi, alpha)
        self.assertEqual(theta_hat, lo)
        self.assertTrue(np.isfinite(theta_hat))

    def test_huge_window_clamps_high(self):
        alpha = 0.5
        carriers = np.array([0.5, 1.0, 1.5])
        weights = np.full(3, 1.0 / 3)
        theta_hat = clamped_root(1e6, carriers, weights, -2.0, 2.0, alpha)
        self.assertEqual(theta_hat, 2.0)


class TestEdgeWindowFirstMoment(unittest.TestCase):
    """Remark D.4.2: truncated edge window fails the first-moment balance even
    with a homogeneous carrier; an interior symmetric window satisfies it."""

    def test_truncated_edge_moment_is_16_over_N(self):
        n_frames = 2048
        members = np.arange(0, 33)  # first truncated window, target n = 0
        u = (members - 0) / n_frames
        first_moment = float(np.mean(u))
        self.assertAlmostEqual(first_moment, 16.0 / n_frames, places=15)
        # first order in the window radius (32/N), NOT o(W/N):
        self.assertGreater(first_moment, 0.4 * (32.0 / n_frames))

    def test_interior_symmetric_identity(self):
        n_frames = 2048
        center = 1000
        members = np.arange(center - 32, center + 33)
        u = (members - center) / n_frames
        self.assertAlmostEqual(float(np.mean(u)), 0.0, places=18)


class TestCenteredLogProjection(unittest.TestCase):
    """Centered-log quotient loss: orthogonal projection is nonexpansive and
    the loss is invariant under the additive gauge."""

    def test_projection_nonexpansive_and_gauge_invariant(self):
        rng = np.random.default_rng(7)
        n = 64
        e = rng.normal(size=n)
        p_e = e - e.mean()
        self.assertLessEqual(np.sum(p_e ** 2), np.sum(e ** 2) + 1e-12)
        # gauge invariance: adding c * 1 changes nothing after centering
        for c in [-3.0, 0.4, 12.5]:
            shifted = e + c
            self.assertAlmostEqual(
                float(np.sum((shifted - shifted.mean()) ** 2)),
                float(np.sum(p_e ** 2)), places=8)

    def test_projection_idempotent(self):
        rng = np.random.default_rng(8)
        e = rng.normal(size=32)
        p1 = e - e.mean()
        p2 = p1 - p1.mean()
        np.testing.assert_allclose(p1, p2, atol=1e-15)


class TestOracleLocalShiftFisher(unittest.TestCase):
    """(D.13): I_A(t) = sum_k s_k^2 e^{2t} / (s_k e^t + d_k); = sum lambda at d=0."""

    @staticmethod
    def fisher_formula(s, d, t):
        lam = s * math.exp(t) + d
        return float(np.sum((s * math.exp(t)) ** 2 / lam))

    def test_d_zero_equals_sum_lambda(self):
        rng = np.random.default_rng(11)
        s = rng.uniform(0.1, 3.0, size=9)
        d = np.zeros(9)
        for t in [-0.5, 0.0, 0.8]:
            lam = s * math.exp(t)
            self.assertAlmostEqual(self.fisher_formula(s, d, t),
                                   float(lam.sum()), places=10)

    def test_matches_score_variance_analytically(self):
        # Var(score) = sum Var(C_k) (s_k e^t / lambda_k)^2 = sum s_k^2 e^{2t}/lambda_k
        rng = np.random.default_rng(12)
        s = rng.uniform(0.1, 3.0, size=6)
        d = rng.uniform(0.0, 0.5, size=6)
        t = 0.3
        lam = s * math.exp(t) + d
        var_score = float(np.sum(lam * (s * math.exp(t) / lam) ** 2))
        self.assertAlmostEqual(var_score, self.fisher_formula(s, d, t), places=10)

    def test_monte_carlo_score_variance(self):
        rng = np.random.default_rng(13)
        s = np.array([0.5, 1.0, 2.0])
        d = np.array([0.1, 0.0, 0.3])
        t = 0.0
        lam = s * math.exp(t) + d
        n_mc = 200_000
        counts = rng.poisson(lam, size=(n_mc, 3))
        scores = ((counts - lam) * (s * math.exp(t) / lam)).sum(axis=1)
        i_mc = float(scores.var())
        i_th = self.fisher_formula(s, d, t)
        self.assertLess(abs(i_mc / i_th - 1.0), 0.02)


class TestDeterministicDeltaCounterexample(unittest.TestCase):
    """F.8: a deterministic mismatch Delta == eps has Var(Delta)=0 but a strictly
    positive exact pairwise risk ~ (K_eff/4) D_H eps^2 (E[Delta^2] version)."""

    @staticmethod
    def hadamard(k):
        h = np.array([[1.0]])
        while h.shape[0] < k:
            h = np.block([[h, h], [h, -h]])
        return h

    def test_var_zero_but_risk_positive(self):
        k = 16
        rng = np.random.default_rng(5)
        t = rng.uniform(0.0, 1.0, size=k)
        h = self.hadamard(k)
        c = h @ t
        s1, s2 = float(t.sum()), float(np.sum(t ** 2))
        x = c / s1
        eps = 1e-3
        # exact coefficient error (F.7)
        e = -s1 * eps * (1 - x ** 2) / (2 + eps * (1 - x))
        risk_exact = float(np.sum(e ** 2)) / (k * s2)
        self.assertEqual(np.var(np.full(k, eps)), 0.0)
        self.assertGreater(risk_exact, 0.0)
        # leading term (K_eff/4) D_H eps^2 with E[Delta^2] = eps^2
        k_eff = s1 ** 2 / s2
        d_h = float(np.mean((1 - x ** 2) ** 2))
        risk_lead = (k_eff / 4.0) * d_h * eps ** 2
        self.assertLess(abs(risk_exact / risk_lead - 1.0), 10 * eps)

    def test_direct_reconstruction_matches_formula(self):
        k = 16
        rng = np.random.default_rng(6)
        t = rng.uniform(0.0, 1.0, size=k)
        h = self.hadamard(k)
        c = h @ t
        s1 = float(t.sum())
        eps = 1e-3
        b_plus = (s1 + c) / 2.0
        b_minus = (s1 - c) / 2.0
        r_plus = 1.0 * b_plus            # gain a+ = 1
        r_minus = (1.0 + eps) * b_minus  # gain a- = (1+eps)
        c_hat = s1 * (r_plus - r_minus) / (r_plus + r_minus)
        x = c / s1
        e_formula = -s1 * eps * (1 - x ** 2) / (2 + eps * (1 - x))
        np.testing.assert_allclose(c_hat - c, e_formula, rtol=1e-10, atol=1e-12)


class TestRawVsAlignedMetric(unittest.TestCase):
    """(F.17): aligned error is (b - a^2)/(1 + 2a + b); raw is b; not proportional."""

    def test_formula_matches_object_metrics(self):
        import torch
        from run_mechanism_m1 import object_metrics
        rng = np.random.default_rng(21)
        t = rng.uniform(0.1, 1.0, size=200)
        e = 0.3 * rng.normal(size=200)
        t_hat = t + e
        s2 = float(np.sum(t ** 2))
        a = float(np.dot(e, t)) / s2
        b = float(np.sum(e ** 2)) / s2
        aligned_formula = (b - a ** 2) / (1 + 2 * a + b)
        m = object_metrics(torch.tensor(t_hat), torch.tensor(t))
        self.assertLess(abs(m["rel_mse"] - aligned_formula), 1e-9)

    def test_orthogonal_error_gives_b_over_1_plus_b(self):
        rng = np.random.default_rng(22)
        t = rng.uniform(0.1, 1.0, size=100)
        e = rng.normal(size=100)
        e -= (np.dot(e, t) / np.dot(t, t)) * t  # exactly orthogonal to T
        s2 = float(np.sum(t ** 2))
        b = float(np.sum(e ** 2)) / s2
        a = 0.0
        aligned = (b - a ** 2) / (1 + 2 * a + b)
        self.assertAlmostEqual(aligned, b / (1 + b), places=12)
        self.assertNotAlmostEqual(aligned, b, places=3)


class TestWalshTripleMoment(unittest.TestCase):
    """(E.9): relational Walsh triples have third moment K^2 S3c/((K-1)(K-2));
    linearly independent triples have zero."""

    def test_triple_moment_exhaustive_K8(self):
        from itertools import permutations
        k = 8
        rng = np.random.default_rng(31)
        t = rng.uniform(0.0, 1.0, size=k)
        # Walsh characters chi_g(j) = (-1)^{popcount(g & j)}
        chi = np.array([[(-1) ** bin(g & j).count("1") for j in range(k)]
                        for g in range(k)], dtype=float)
        s3c = float(np.sum((t - t.mean()) ** 3))
        g, h, r_rel = 1, 2, 3          # 1 ^ 2 ^ 3 == 0 -> relational triple
        r_ind = 4                      # 1, 2, 4 linearly independent
        acc_rel, acc_ind, n_perm = 0.0, 0.0, 0
        for p in permutations(range(k)):
            tp = t[list(p)]
            zg, zh = chi[g] @ tp, chi[h] @ tp
            acc_rel += zg * zh * (chi[r_rel] @ tp)
            acc_ind += zg * zh * (chi[r_ind] @ tp)
            n_perm += 1
        mean_rel = acc_rel / n_perm
        mean_ind = acc_ind / n_perm
        pred = k ** 2 / ((k - 1) * (k - 2)) * s3c
        self.assertLess(abs(mean_rel - pred), 1e-9 * max(1.0, abs(pred)))
        self.assertLess(abs(mean_ind), 1e-9)
        self.assertNotAlmostEqual(pred, 0.0, places=3)  # generic object: S3c != 0


class TestRawMetricExportIntegrity(unittest.TestCase):
    """Data integrity + provenance of results/prop3_raw_metric_r1/."""

    @classmethod
    def setUpClass(cls):
        if not RAW_DIR.exists():
            raise unittest.SkipTest("raw-metric export not present; run "
                                    "run_prop3_raw_metric_export.py first")

    def test_summary_headline_numbers(self):
        summary = json.loads((RAW_DIR / "prop3_raw_summary.json").read_text())
        skel = summary["raw_skeleton_sigma_ge_0p1"]
        self.assertEqual(skel["n_cells"], 40)
        self.assertEqual(skel["n_observed_crossings"], 40)
        self.assertAlmostEqual(skel["factor_median"], 1.04387, places=4)
        self.assertAlmostEqual(skel["factor_max"], 1.19985, places=4)
        self.assertEqual(skel["frac_within_factor2"], 1.0)
        self.assertAlmostEqual(summary["raw_over_aligned_ratio_median"],
                               1.5398517, places=5)
        self.assertAlmostEqual(summary["raw_floor_median"], 1026.470, places=2)
        lo, hi = summary["raw_floor_range"]
        self.assertAlmostEqual(lo, 980.110, places=2)
        self.assertAlmostEqual(hi, 1114.529, places=2)
        self.assertAlmostEqual(summary["moment_prediction_K_beta4_minus_2"],
                               1023.800, places=2)
        # sigma = 0.05 cells: Q_raw >= 1, no raw crossing
        s005 = summary["sigma_0p05_cells"]
        self.assertEqual(s005["n_Q_raw_ge_1"], s005["n_cells"])
        self.assertEqual(s005["n_raw_crossing_observed"], 0)

    def test_constants_csv_consistent_with_aligned_run(self):
        import pandas as pd
        raw = pd.read_csv(RAW_DIR / "prop3_raw_constants.csv")
        self.assertEqual(len(raw), 10)
        self.assertTrue((raw.C0_floor_raw_fix > raw.C0_floor_align_fix).all())
        aligned = pd.read_csv(ALIGNED_DIR / "prop3_constants.csv")
        merged = raw.merge(aligned[["object", "C0_pipeline"]], on="object")
        # the aligned floor re-derived here must equal the authoritative
        # aligned constant (same deterministic basis/objects/metric)
        np.testing.assert_allclose(merged.C0_floor_align_fix,
                                   merged.C0_pipeline, rtol=1e-9)

    def test_aligned_reproduction_check(self):
        import pandas as pd
        check = pd.read_csv(RAW_DIR / "aligned_reproduction_check.csv")
        self.assertGreaterEqual(len(check), 900)
        self.assertLess(check.abs_diff.max(), 1e-5)

    def test_skeleton_csv_agrees_with_summary(self):
        import pandas as pd
        skel = pd.read_csv(RAW_DIR / "prop3_raw_skeleton_test.csv")
        main = skel[(skel.sigma_a >= 0.1) & (skel.emp_status == "observed")]
        self.assertEqual(len(main), 40)
        med = 10 ** main.log10_ratio.abs().median()
        self.assertAlmostEqual(med, 1.04387, places=4)

    def test_manifest_provenance(self):
        manifest = json.loads((RAW_DIR / "run_manifest.json").read_text())
        self.assertEqual(manifest["manifest_version"], 2)
        self.assertTrue(manifest["git_commit"])
        self.assertIn("runner_sha256", manifest)
        self.assertIn("output_dir", manifest["extra"] if "extra" in manifest
                      else manifest)
        extra = manifest.get("extra", manifest)
        self.assertEqual(extra.get("script"), "run_prop3_raw_metric_export.py")
        self.assertIn("raw_metric", extra)


if __name__ == "__main__":
    unittest.main()
