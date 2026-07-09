# Identifiability of gain–object separation — rigorous note v5 (mature capstone)

**Supersedes v4. Integrates GPT deep-dive R1 (#1) + R2 (#2) + R3 (#3), adversarially verified.**
After three rounds the identifiability **core is complete and paper-ready**; what remains is
implementation-specific constants, conditioning/algorithms, and information-theoretic limits — scope
items for the manuscript, not open theory. Full proofs in issues #1–#3. This note consolidates the
final results, resolves the ρ-convention ambiguity, and states the maturity audit.

---

## PART I — Identifiability (unchanged from v3/v4, now fully proven)

**Three notions** (v3): exact-algebraic (finite-sample) / statistical-asymptotic (stationarity
anchor) / estimation-conditioning. Thm A: square unconstrained is non-identifiable for *any*
invertible design (not Hadamard-specific). Thm B: random carriers give **statistical** relative-gain
identifiability up to global scale. (★) is the window-estimator consistency criterion, not a
universal iff.

**Tall-design thresholds (R2), now verified for the PHYSICAL low-pass gain space (R3 §8):**
generic M, log-gain `ℓ∈S`, `dim S=p`, S contains constants:
- local differential ID: `N ≥ K+p−1`
- generic exact finite-sample ID: `N ≥ K+p`
- uniform (every object): `N ≥ 2K+p−1`

R3 **closed the v4 open caveat**: for the Fourier low-pass drift space `S_LP=span{1, cos, sin (q≤m)}`,
`p=2m+1`, every nonconstant `s∈S_LP` has level-multiplicity `≤ p−1` (Lemma 1: degree-2m trig
polynomial), and `rank[M,−D_sM]=min(N,2K,K+N−m_max)` (Lemma 2). At `N≥K+p`, `m_max≤p−1≤N−K−1` ⇒
`K+N−m_max>2K` ⇒ rank `=min(N,2K)` ⇒ **the clean thresholds hold for low-pass S.** For other low-pass
conventions, check `L_S ≤ K` (if N<2K) or `≤ N−K` (if N≥2K); else use the stratum formula with
`ρ_α=min(N,2K,K+N−m_α)`.

**SRHT whitening (R2):** exact obstruction `Cov_D(Z_g,Z_h)=ŵ(g+h)` (Walsh transform of T²);
sign-only whitening ⟺ Walsh-flatness; permutation randomizes it, made likely by
`min(ε²K_4,εK_∞)≥C log(K/δ)`. Permutation-alone: `Var_P Z_g=(K S₂−S₁²)/(K−1)=S₂(K−K_eff)/(K−1)`
⇒ O(1/K_eff) upper variance but no uniform two-sided bound (flat object → zero excitation).

## PART II — Reconstruction bridge (NEW, R3) — the paper's performance layer

**Master finite-noise identity (R3 Thm 1, exact, no Gaussian approx).** Corrected bucket
`z_n=(1+δ_n)b_n+ξ_n`, `b=AT`, reconstruction `T̂=Lz`:
```
E‖T̂−T‖²/S₂ = ‖(LA−I)T + L diag(b)m_δ‖²/S₂        (bias)
            + tr(L diag(b) V_δ diag(b) Lᵀ)/S₂       (residual multiplicative gain)
            + tr(L Σ_ξ Lᵀ)/S₂                        (additive: read + Poisson)
```
Independent residual gain (Var δ_n=v): gain term `= v·B_L`, **leverage** `B_L=(1/S₂)Σ_n b_n²‖Le_n‖²`.
**Coherent/smooth residual gain needs the full matrix form** `(v/S₂)Σ r_δ(n−m)b_nb_m⟨Le_n,Le_m⟩`,
NOT the scalar v — this supersedes R1 Thm E's "orthogonal gives v" (true only for independent
coefficient-wise residuals + exact inversion).

Noise plug-ins: Gaussian read `Σ_ξ=diag(σ_read,n²/a_n²)`; **Poisson exact for all photon counts**
`Var(z_n)=b_n²/Φ_n` ⇒ `Σ_ξ=diag(τ_G,n²+b_n²/Φ_n)` (no log/Gaussian approx needed for reconstruction).

**Specializations:**
- **Orthogonal / full SRHT inversion:** `B_L=1` ⇒ `relMSE = v + (1/S₂)Σ(τ_G,n²+b_n²/Φ_n)`.
- **Pairwise Hadamard:** `R_pair,gain=(K_eff/4)·D_H(T)·Var(Δ)`, `D_H=(1/K)Σ(1−x_k²)²≈1` for
  non-DC coeffs; read `2σ_read²/S₂`; Poisson `K_eff/Φ_pair` (equal-pair budget).
- **Random/DGI:** `relMSE_DGI = C0/N + (1+C0)v/N + K τ_G²/(N σ²S₂) + (1+C0)/(N Φ_frame)`,
  with **exact one-sample constant** `C0=E‖Z‖²/S₂−1`; for iid patterns
  `C0=K+β₄−2+K_eff[K(μ/σ)²+2γ₃(μ/σ)]` (symmetric zero-mean: `C0=K+β₄−2`). **This replaces v4's
  heuristic `C1·v·K_eff` by the exact `(1+C0)v`** (C0 carries the K_eff/background dependence).

**Finite-N flip boundary (R3 §6)** — `ρ* = inf{ρ: R_pair(ρ) ≥ R_rand(ρ,N)}`; small-drift implicit form
```
r(ρ*) = 2[C0/N + (1+C0)v_blind/N + R_DGI,noise − R_pair,noise] / (K_eff D_H s²)
```
(OU: `r(ρ)=1−e^{−ρ}` ⇒ `ρ*=−log(1−Q)`, `Q=2Δ_R/(K_eff D_H s²)`). The **v3/v4 heuristic
`ρ*≈2C0/(N K_eff s²)` is the leading-order special case** (r(ρ)=ρ, D_H=1, negligible noise/v_blind,
ρ=adjacent-pair decorrelation).

**⚠ ρ-CONVENTION FIX (R3 §6.4/§9 — the one real inconsistency in v4).** Two distinct meanings:
- **ρ_pair** = adjacent-pair gain decorrelation (Var Δ ≈ 2s²·r(ρ_pair)) — used in the flip boundary.
- **ρ_bw** = normalized gain bandwidth, `p ≈ ρ_bw·N` — used in Part-I tall-design (`N≳K/(1−ρ_bw)`).
These are related (both increase with drift speed) but **not equal**; the explicit `1/N` in the flip
law is a ρ_pair statement. **The manuscript must define which ρ each figure/plot uses before
overlaying them.** (v4 §A's `N≳K/(1−ρ)` uses ρ_bw; the flip boundary uses ρ_pair.)

## PART III — Low-photon robustness (NEW, R3 §7) — log-domain does not break

Replace `log R_n` by a **calibrated soft-log** `ψ_α(c)=log(c+α)` with calibration curve
`m_α(θ)=E[ψ_α(C)]`, `C~Pois(Λ₀e^θB+d)`; estimator `θ̂_n=m_α⁻¹(mean_W ψ_α)`. Poisson derivative
identity `d/dλ Ef(C)=E[f(C+1)−f(C)]` ⇒ sensitivity `κ_α(λ)→1` (high λ), `→λ log(1+1/α)` (low λ);
variance `O(1/λ)` (high), `~λ` (low). **Rate (R3 (51)):**
`MSE* ≤ C κ_min⁻²[κ_max L_a]^{2/(2a+1)} σ_{α,LR}^{4a/(2a+1)}`; photon-starved limit **`~1/(W λ̄)`**,
minimax-sharp (Poisson Fisher info for log-intensity = λ). Zeros only *reduce* Fisher information;
they do not blow the estimator up. Variants: offset design, Anscombe `2√(C+3/8)`, full Poisson-mixture
MLE (`1/(W J)`, `J~Eλ` at low photons).

## PART IV — Maturity audit (R3 §10) — my judgment: MATURE

**Complete / paper-ready (proven & verified):** algebraic taxonomy (Thm A + tall thresholds);
low-pass verification (R3 §8); statistical stationarity anchor (Thm B) with gauge isolated;
gain-estimation rate + minimax-optimality (R1 B1) incl. robust Poisson version; SRHT N&S Walsh
whitening (R2); reconstruction bridge master formula (R3 Thm 1) covering all bases + read + Poisson +
residual gain; finite-N flip boundary with the heuristic as leading order; verified/corrected
citations (R2 §0.4).

**Scope items — NOT theory gaps (state as assumptions/future-work):** implementation constants
(C0, D_H, photon allocation, χ_δ) must be measured from the actual pipeline; algorithmic
**conditioning** near `N=K+p` (uniqueness ≠ stability) — a random-matrix/numerical question;
global prior-restored identifiability for deterministic sparse supports (R1 gave local rank criteria);
extreme-low-photon with no offset/reference (Fisher→0 as Φ→0 — an *information* limit); model
mismatch (calibration errors, motion, gain jumps, dead pixels).

**Honest final verdict (mine, concurring with GPT R3 §10.3):** the theory correctly separates
algebraic uniqueness, statistical gain anchoring, and estimation conditioning, and the R3 bridge makes
the performance claims precise enough to support the phase diagram. The irreducible limits are
information/modeling limits (zero photons = no information; p≈N = blind algebraic separation
impossible; unspecified DGI = no universal C0; uniqueness ≠ conditioning), which the manuscript should
state explicitly rather than bury in heuristics. **No further math round is expected to close a core
gap; the remaining work is numerical (measure C0/D_H from the code, feed the phase diagram) and
editorial (write it up with the ρ-convention and scope statements explicit).**

## Corrections applied to R1/R2/v4 in this capstone
R1 Thm E → leverage formula (coherent gain needs the matrix form) · v4 heuristic `C1 v K_eff` →
exact `(1+C0)v` · v4 `ρ` split into ρ_pair vs ρ_bw · v4 "fast drift kills every basis" qualified
(blind-algebraic only; known-gain/external-calibration can still work) · v4 §E low-pass caveat →
PROVEN (Part I) · "no universal C0" (implementation-dependent) · pairwise assumes stable S₁
normalization (needs offset/clipping at low photons).

---
*Novelty (unchanged, now on firm ground): the contribution is the **temporal-statistical
identifiability mechanism** (stationarity anchor) + the nonparametric slow-gain calibration rate +
the ordered-orthogonal confounding failure mode + the SRHT synthesis + the finite-noise reconstruction
bridge — NOT generic bilinear injectivity (known: Kech–Krahmer et al.). Positioned & citation-verified
in R2 §0.4 / v4 §D.*
