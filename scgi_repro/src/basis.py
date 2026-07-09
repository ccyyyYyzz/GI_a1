"""Measurement bases for compact ghost-imaging mechanism studies.

The module keeps the public surface small: build a basis, simulate bucket
measurements with ``basis.measure()``, and reconstruct with ``basis.reconstruct()``.
Paired Hadamard-style bases expose complementary amplitude frames while retaining
the signed transform rows needed for exact inverse reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Optional, Tuple

import torch


def is_power_of_two(value: int) -> bool:
    """Return True when ``value`` is a positive power of two."""

    return value > 0 and (value & (value - 1)) == 0


def _cpu_generator(seed: int) -> torch.Generator:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(int(seed))
    return generator


def hadamard_matrix(size: int, device: str = "cpu", dtype: torch.dtype = torch.float32) -> torch.Tensor:
    """Create a Sylvester Hadamard matrix with entries in ``{-1, +1}``.

    ``size`` must be a power of two. The returned matrix satisfies
    ``H @ H.T == size * I``.
    """

    if not is_power_of_two(size):
        raise ValueError(f"Hadamard size must be a power of two, got {size}.")

    matrix = torch.ones((1, 1), dtype=dtype, device=device)
    while matrix.shape[0] < size:
        top = torch.cat((matrix, matrix), dim=1)
        bottom = torch.cat((matrix, -matrix), dim=1)
        matrix = torch.cat((top, bottom), dim=0)
    return matrix


def interleave_paired_frames(signed_rows: torch.Tensor) -> torch.Tensor:
    """Convert signed +/-1 rows into complementary 0/1 physical frames."""

    plus = 0.5 * (1.0 + signed_rows)
    minus = 0.5 * (1.0 - signed_rows)
    frames = torch.empty(
        (2 * signed_rows.shape[0], signed_rows.shape[1]),
        dtype=signed_rows.dtype,
        device=signed_rows.device,
    )
    frames[0::2] = plus
    frames[1::2] = minus
    return frames


def _row_sign_changes(rows: torch.Tensor) -> torch.Tensor:
    """Count one-dimensional sign changes for each Hadamard row."""

    signs = torch.sign(rows)
    return (signs[:, 1:] != signs[:, :-1]).sum(dim=1)


def hadamard_row_order(size: int, order: str = "natural", seed: int = 0) -> torch.Tensor:
    """Return row indices for common Hadamard sampling orders.

    ``sequency`` sorts rows by one-dimensional zero crossings. ``cake`` is a
    compact cake-cutting proxy: rows are sorted by two-dimensional total
    variation after reshaping square images, with sequency and natural index as
    deterministic tie-breakers.
    """

    key = order.lower().replace("-", "_")
    if key in {"natural", "ordered", "hadamard", "hadamard_paired"}:
        return torch.arange(int(size), dtype=torch.long)
    if key in {"random", "random_order", "random_permutation", "permuted"}:
        return torch.randperm(int(size), generator=_cpu_generator(seed))

    h = hadamard_matrix(int(size))
    sign_changes = _row_sign_changes(h)
    if key in {"sequency", "walsh", "walsh_sequency"}:
        return torch.tensor(
            sorted(range(int(size)), key=lambda idx: (int(sign_changes[idx]), idx)),
            dtype=torch.long,
        )
    if key in {"cake", "cake_cutting", "cakecutting", "cc"}:
        side = int(math.isqrt(int(size)))
        if side * side == int(size):
            patterns = h.reshape(int(size), side, side)
            tv = (
                patterns[:, 1:, :].sub(patterns[:, :-1, :]).abs().sum(dim=(1, 2))
                + patterns[:, :, 1:].sub(patterns[:, :, :-1]).abs().sum(dim=(1, 2))
            )
        else:
            tv = sign_changes.to(dtype=torch.float32)
        return torch.tensor(
            sorted(range(int(size)), key=lambda idx: (float(tv[idx]), int(sign_changes[idx]), idx)),
            dtype=torch.long,
        )
    raise ValueError(f"Unsupported Hadamard row order: {order}")


def _canonical_hadamard_order(order: str) -> str:
    key = order.lower().replace("-", "_")
    if key in {"natural", "ordered", "hadamard", "hadamard_paired"}:
        return "natural"
    if key in {"random", "random_order", "random_permutation", "permuted"}:
        return "random"
    if key in {"sequency", "walsh", "walsh_sequency"}:
        return "sequency"
    if key in {"cake", "cake_cutting", "cakecutting", "cc"}:
        return "cake"
    raise ValueError(f"Unsupported Hadamard row order: {order}")


@dataclass
class MeasurementBasis:
    """Container for a physical measurement basis and its inverse map."""

    name: str
    patterns: torch.Tensor
    paired: bool
    signed_rows: Optional[torch.Tensor] = None
    row_indices: Optional[torch.Tensor] = None
    srht_signs: Optional[torch.Tensor] = None
    reconstruction: str = "least_squares"
    ridge: float = 1.0e-5
    reconstruction_matrix: Optional[torch.Tensor] = None
    inverse_scale: Optional[float] = None
    coefficient_weights: Optional[torch.Tensor] = None
    four_step: bool = False
    fourier_indices: Optional[torch.Tensor] = None
    metadata: Optional[Dict[str, object]] = None

    @property
    def num_frames(self) -> int:
        return int(self.patterns.shape[0])

    @property
    def num_pixels(self) -> int:
        return int(self.patterns.shape[1])

    @property
    def num_coefficients(self) -> int:
        if self.four_step and self.fourier_indices is not None:
            return int(self.fourier_indices.numel())
        if self.paired and self.signed_rows is not None:
            return int(self.signed_rows.shape[0])
        return int(self.patterns.shape[0])

    @property
    def is_complete_orthogonal(self) -> bool:
        if self.four_step:
            return bool(self.fourier_indices is not None and self.fourier_indices.numel() == self.num_pixels)
        return bool(self.paired and self.signed_rows is not None and self.num_coefficients == self.num_pixels)

    def measure(self, object_flat: torch.Tensor) -> torch.Tensor:
        """Return noiseless bucket measurements for a flattened object."""

        vector = object_flat.to(device=self.patterns.device, dtype=self.patterns.dtype).reshape(-1)
        if vector.numel() != self.num_pixels:
            raise ValueError(f"Expected {self.num_pixels} pixels, got {vector.numel()}.")
        return self.patterns @ vector

    def coefficients_from_frames(self, frame_values: torch.Tensor) -> torch.Tensor:
        """Convert paired frame measurements into signed transform coefficients."""

        if not self.paired:
            raise ValueError("coefficients_from_frames is only valid for paired bases.")
        values = frame_values.reshape(-1).to(device=self.patterns.device, dtype=self.patterns.dtype)
        if values.numel() != self.num_frames:
            raise ValueError(f"Expected {self.num_frames} frame values, got {values.numel()}.")
        return values[0::2] - values[1::2]

    def reconstruct(self, values: torch.Tensor, values_are_coefficients: bool = False) -> torch.Tensor:
        """Reconstruct a flattened image from corrected measurements or coefficients."""

        if self.four_step:
            corrected = values.reshape(-1).to(device=self.patterns.device)
            return self._reconstruct_four_step(corrected, values_are_coefficients=values_are_coefficients)
        corrected = values.reshape(-1).to(device=self.patterns.device, dtype=self.patterns.dtype)
        if self.paired:
            coeffs = corrected if values_are_coefficients else self.coefficients_from_frames(corrected)
            return self._reconstruct_paired(coeffs)
        return self._reconstruct_random(corrected)

    def _reconstruct_paired(self, coefficients: torch.Tensor) -> torch.Tensor:
        if self.signed_rows is None:
            raise ValueError("Paired reconstruction requires signed_rows.")
        coeffs = coefficients.reshape(-1).to(device=self.signed_rows.device, dtype=self.signed_rows.dtype)
        if coeffs.numel() != self.num_coefficients:
            raise ValueError(f"Expected {self.num_coefficients} coefficients, got {coeffs.numel()}.")

        if self.coefficient_weights is not None:
            weights = self.coefficient_weights.reshape(-1).to(device=self.signed_rows.device, dtype=self.signed_rows.dtype)
            if weights.numel() != coeffs.numel():
                raise ValueError(f"Expected {coeffs.numel()} coefficient weights, got {weights.numel()}.")
            return self.signed_rows.transpose(0, 1) @ (coeffs * weights)

        backprojection = self.signed_rows.transpose(0, 1) @ coeffs
        scale = float(
            self.inverse_scale
            if self.inverse_scale is not None
            else (self.num_pixels if self.is_complete_orthogonal else self.num_coefficients)
        )
        return backprojection / max(scale, 1.0)

    def _fourier_coefficients_from_frames(self, frame_values: torch.Tensor) -> torch.Tensor:
        values = frame_values.reshape(-1).to(device=self.patterns.device, dtype=self.patterns.dtype)
        expected = 4 * self.num_coefficients
        if values.numel() != expected:
            raise ValueError(f"Expected {expected} four-step frame values, got {values.numel()}.")
        real = values[0::4] - values[2::4]
        imag = values[1::4] - values[3::4]
        complex_dtype = torch.complex128 if real.dtype == torch.float64 else torch.complex64
        return torch.complex(real.to(dtype=real.dtype), imag.to(dtype=imag.dtype)).to(dtype=complex_dtype)

    def _reconstruct_four_step(self, values: torch.Tensor, values_are_coefficients: bool = False) -> torch.Tensor:
        if self.fourier_indices is None:
            raise ValueError("Four-step Fourier reconstruction requires fourier_indices.")
        coeffs = values if values_are_coefficients else self._fourier_coefficients_from_frames(values)
        coeffs = coeffs.reshape(-1)
        if not torch.is_complex(coeffs):
            if coeffs.numel() != 2 * self.num_coefficients:
                raise ValueError(
                    f"Expected complex Fourier coefficients or {2 * self.num_coefficients} stacked real/imag values, "
                    f"got {coeffs.numel()}."
                )
            complex_dtype = torch.complex128 if coeffs.dtype == torch.float64 else torch.complex64
            coeffs = torch.complex(coeffs[0::2], coeffs[1::2]).to(dtype=complex_dtype)
        if coeffs.numel() != self.num_coefficients:
            raise ValueError(f"Expected {self.num_coefficients} Fourier coefficients, got {coeffs.numel()}.")

        complex_dtype = torch.complex128 if self.patterns.dtype == torch.float64 else torch.complex64
        spectrum = torch.zeros((self.num_pixels,), dtype=complex_dtype, device=self.patterns.device)
        spectrum[self.fourier_indices.to(device=self.patterns.device)] = coeffs.to(device=self.patterns.device)
        return torch.fft.ifft(spectrum).real.to(dtype=self.patterns.dtype)

    def _reconstruct_random(self, measurements: torch.Tensor) -> torch.Tensor:
        if measurements.numel() != self.num_frames:
            raise ValueError(f"Expected {self.num_frames} measurements, got {measurements.numel()}.")

        if self.reconstruction == "correlation":
            design = self.patterns
            centered_design = design - design.mean(dim=0, keepdim=True)
            centered_y = measurements - measurements.mean()
            variance = centered_design.pow(2).mean(dim=0).clamp_min(1.0e-8)
            return (centered_design.transpose(0, 1) @ centered_y) / (float(self.num_frames) * variance)

        if self.reconstruction_matrix is None:
            self.reconstruction_matrix = _least_squares_reconstruction_matrix(self.patterns, ridge=self.ridge)
        return self.reconstruction_matrix @ measurements


def _least_squares_reconstruction_matrix(patterns: torch.Tensor, ridge: float) -> torch.Tensor:
    """Build ``(A.T A + ridge I)^-1 A.T`` for repeated compact reconstructions."""

    design = patterns
    gram = design.transpose(0, 1) @ design
    diag_scale = gram.diag().mean().clamp_min(1.0)
    eye = torch.eye(gram.shape[0], dtype=gram.dtype, device=gram.device)
    return torch.linalg.solve(gram + float(ridge) * diag_scale * eye, design.transpose(0, 1))


def make_random_basis(
    distribution: str,
    num_pixels: int,
    num_frames: Optional[int] = None,
    seed: int = 0,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    reconstruction: str = "least_squares",
    ridge: float = 1.0e-5,
    precompute_inverse: bool = True,
) -> MeasurementBasis:
    """Create an i.i.d. random measurement basis.

    Supported distributions are ``uniform`` on [0, 1], ``binary`` Bernoulli(0.5),
    and signed ``gaussian`` N(0, 1).
    """

    frames = int(num_frames if num_frames is not None else 2 * num_pixels)
    if frames <= 0:
        raise ValueError("num_frames must be positive.")

    generator = _cpu_generator(seed)
    dist = distribution.lower()
    shape = (frames, int(num_pixels))
    if dist == "uniform":
        patterns = torch.rand(shape, generator=generator, dtype=dtype)
    elif dist == "binary":
        patterns = torch.randint(0, 2, shape, generator=generator, dtype=torch.int64).to(dtype=dtype)
    elif dist == "gaussian":
        patterns = torch.randn(shape, generator=generator, dtype=dtype)
    else:
        raise ValueError(f"Unsupported random basis distribution: {distribution}")

    patterns = patterns.to(device=device)
    basis = MeasurementBasis(
        name=f"random_{dist}",
        patterns=patterns,
        paired=False,
        reconstruction=reconstruction,
        ridge=ridge,
        metadata={"distribution": dist, "seed": int(seed)},
    )
    if precompute_inverse and reconstruction == "least_squares":
        basis.reconstruction_matrix = _least_squares_reconstruction_matrix(patterns, ridge=ridge)
    return basis


def make_hadamard_paired_basis(
    num_pixels: int,
    num_coefficients: Optional[int] = None,
    order: str = "natural",
    seed: int = 0,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> MeasurementBasis:
    """Create complementary paired Hadamard measurements."""

    size = int(num_pixels)
    coeffs = int(num_coefficients if num_coefficients is not None else size)
    if coeffs <= 0 or coeffs > size:
        raise ValueError(f"num_coefficients must be in [1, {size}], got {coeffs}.")

    order_key = _canonical_hadamard_order(order)
    row_order = hadamard_row_order(size, order=order_key, seed=seed)[:coeffs].to(device=device)
    signed_rows = hadamard_matrix(size, device=device, dtype=dtype).index_select(0, row_order)
    name = "hadamard_paired" if order_key == "natural" else f"hadamard_{order_key}_paired"
    return MeasurementBasis(
        name=name,
        patterns=interleave_paired_frames(signed_rows),
        paired=True,
        signed_rows=signed_rows,
        row_indices=row_order,
        metadata={"transform": "hadamard", "row_order": order_key, "ordered": order_key in {"natural", "ordered"}},
    )


def make_srht_paired_basis(
    num_pixels: int,
    num_coefficients: Optional[int] = None,
    seed: int = 0,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    permute_rows: bool = True,
) -> MeasurementBasis:
    """Create complementary paired SRHT measurements.

    Rows are ``H[row] * D`` where ``D`` is a fixed random sign diagonal. When
    ``num_coefficients == num_pixels`` this is an orthogonal basis with exact
    inverse reconstruction; otherwise reconstruction is a normalized
    backprojection from the sampled rows.
    """

    size = int(num_pixels)
    coeffs = int(num_coefficients if num_coefficients is not None else size)
    if coeffs <= 0 or coeffs > size:
        raise ValueError(f"num_coefficients must be in [1, {size}], got {coeffs}.")

    generator = _cpu_generator(seed)
    hadamard = hadamard_matrix(size, device=device, dtype=dtype)
    signs = torch.randint(0, 2, (size,), generator=generator, dtype=torch.int64)
    signs = signs.mul(2).sub(1).to(device=device, dtype=dtype)

    if permute_rows:
        row_indices = torch.randperm(size, generator=generator)[:coeffs].to(device=device)
    else:
        row_indices = torch.arange(coeffs, device=device)

    signed_rows = hadamard.index_select(0, row_indices) * signs.reshape(1, -1)
    return MeasurementBasis(
        name="srht_paired",
        patterns=interleave_paired_frames(signed_rows),
        paired=True,
        signed_rows=signed_rows,
        row_indices=row_indices,
        srht_signs=signs,
        metadata={"transform": "srht", "seed": int(seed), "permute_rows": bool(permute_rows)},
    )


def dct_matrix(size: int, device: str = "cpu", dtype: torch.dtype = torch.float32) -> torch.Tensor:
    """Create full-contrast DCT-II cosine rows in ``[-1, +1]``."""

    n = int(size)
    if n <= 0:
        raise ValueError("DCT size must be positive.")
    rows = torch.arange(n, dtype=dtype, device=device).reshape(-1, 1)
    cols = torch.arange(n, dtype=dtype, device=device).reshape(1, -1)
    return torch.cos(math.pi / float(n) * (cols + 0.5) * rows)


def make_dct_paired_basis(
    num_pixels: int,
    num_coefficients: Optional[int] = None,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> MeasurementBasis:
    """Create complementary paired DCT-II measurements.

    The physical rows use full cosine contrast. Reconstruction weights each
    coefficient by the inverse row energy, which gives the exact inverse for
    the complete DCT-II row set.
    """

    size = int(num_pixels)
    coeffs = int(num_coefficients if num_coefficients is not None else size)
    if coeffs <= 0 or coeffs > size:
        raise ValueError(f"num_coefficients must be in [1, {size}], got {coeffs}.")

    signed_rows = dct_matrix(size, device=device, dtype=dtype)[:coeffs]
    return MeasurementBasis(
        name="dct_paired",
        patterns=interleave_paired_frames(signed_rows),
        paired=True,
        signed_rows=signed_rows,
        row_indices=torch.arange(coeffs, device=device),
        coefficient_weights=1.0 / signed_rows.pow(2).sum(dim=1).clamp_min(1.0e-8),
        metadata={"transform": "dct_ii", "ordered": True, "full_contrast": True},
    )


def make_fourier_fourstep_basis(
    num_pixels: int,
    num_coefficients: Optional[int] = None,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
) -> MeasurementBasis:
    """Create a four-step phase-shift Fourier measurement basis.

    Each frequency uses four non-negative frames with phases
    ``0, pi/2, pi, 3pi/2``. The differences recover the real and imaginary DFT
    coefficients, which are inverted by ``torch.fft.ifft``.
    """

    size = int(num_pixels)
    coeffs = int(num_coefficients if num_coefficients is not None else size)
    if coeffs <= 0 or coeffs > size:
        raise ValueError(f"num_coefficients must be in [1, {size}], got {coeffs}.")

    freqs = torch.arange(coeffs, dtype=dtype, device=device).reshape(-1, 1)
    pixels = torch.arange(size, dtype=dtype, device=device).reshape(1, -1)
    theta = 2.0 * math.pi * freqs * pixels / float(size)
    phases = torch.tensor([0.0, 0.5 * math.pi, math.pi, 1.5 * math.pi], dtype=dtype, device=device)
    frames = 0.5 * (1.0 + torch.cos(theta[:, None, :] + phases.reshape(1, 4, 1)))
    patterns = frames.reshape(4 * coeffs, size)
    return MeasurementBasis(
        name="fourier_fourstep",
        patterns=patterns,
        paired=False,
        four_step=True,
        fourier_indices=torch.arange(coeffs, device=device),
        metadata={"transform": "dft", "phase_steps": 4, "ordered": True},
    )


def make_basis(
    name: str,
    num_pixels: int,
    num_frames: Optional[int] = None,
    seed: int = 0,
    device: str = "cpu",
    dtype: torch.dtype = torch.float32,
    reconstruction: str = "least_squares",
) -> MeasurementBasis:
    """Factory for all measurement bases used by the M1 runner."""

    key = name.lower().replace("-", "_")
    if key.startswith("random_"):
        return make_random_basis(
            key.replace("random_", "", 1),
            num_pixels=num_pixels,
            num_frames=num_frames,
            seed=seed,
            device=device,
            dtype=dtype,
            reconstruction=reconstruction,
        )
    if key in {"uniform", "binary", "gaussian"}:
        return make_random_basis(
            key,
            num_pixels=num_pixels,
            num_frames=num_frames,
            seed=seed,
            device=device,
            dtype=dtype,
            reconstruction=reconstruction,
        )
    if key in {"hadamard", "hadamard_paired", "hadamard_natural", "hadamard_natural_paired"}:
        coeffs = None if num_frames is None else max(1, int(num_frames) // 2)
        return make_hadamard_paired_basis(
            num_pixels=num_pixels,
            num_coefficients=coeffs,
            order="natural",
            seed=seed,
            device=device,
            dtype=dtype,
        )
    if key in {"hadamard_sequency", "hadamard_sequency_paired", "walsh_sequency", "walsh_sequency_paired"}:
        coeffs = None if num_frames is None else max(1, int(num_frames) // 2)
        return make_hadamard_paired_basis(
            num_pixels=num_pixels,
            num_coefficients=coeffs,
            order="sequency",
            seed=seed,
            device=device,
            dtype=dtype,
        )
    if key in {"hadamard_cake", "hadamard_cake_paired", "hadamard_cake_cutting", "hadamard_cake_cutting_paired"}:
        coeffs = None if num_frames is None else max(1, int(num_frames) // 2)
        return make_hadamard_paired_basis(
            num_pixels=num_pixels,
            num_coefficients=coeffs,
            order="cake",
            seed=seed,
            device=device,
            dtype=dtype,
        )
    if key in {"hadamard_random", "hadamard_random_paired", "hadamard_random_order", "hadamard_random_order_paired"}:
        coeffs = None if num_frames is None else max(1, int(num_frames) // 2)
        return make_hadamard_paired_basis(
            num_pixels=num_pixels,
            num_coefficients=coeffs,
            order="random",
            seed=seed,
            device=device,
            dtype=dtype,
        )
    if key in {"srht", "srht_paired"}:
        coeffs = None if num_frames is None else max(1, int(num_frames) // 2)
        return make_srht_paired_basis(
            num_pixels=num_pixels,
            num_coefficients=coeffs,
            seed=seed,
            device=device,
            dtype=dtype,
        )
    if key in {"dct", "dct_paired"}:
        coeffs = None if num_frames is None else max(1, int(num_frames) // 2)
        return make_dct_paired_basis(num_pixels=num_pixels, num_coefficients=coeffs, device=device, dtype=dtype)
    if key in {"fourier", "fourier_fourstep", "fourier_4step"}:
        coeffs = None if num_frames is None else max(1, int(num_frames) // 4)
        return make_fourier_fourstep_basis(num_pixels=num_pixels, num_coefficients=coeffs, device=device, dtype=dtype)
    raise ValueError(f"Unsupported basis name: {name}")


def basis_frame_budget(num_pixels: int, paired_coefficients: Optional[int] = None) -> Tuple[int, int]:
    """Return a fair compact frame budget for random and paired bases."""

    coeffs = int(paired_coefficients if paired_coefficients is not None else num_pixels)
    return 2 * coeffs, coeffs
