# Identifiability of gain–object separation in time-varying multiplicative single-pixel channels

**Rigorous note v2 — self-contained artifact for a GPT math deep-dive.**
Goal: this is the current best rigorous state of the theory behind "why randomized measurement
patterns beat deterministic orthogonal ones under a blind time-varying multiplicative channel."
We want it deepened and completed (see §10 open agenda). Proofs are given condensed so they can be
critiqued and extended.

---

## 0. Model and the unavoidable ambiguity

Known patterns `I_1,…,I_N ∈ ℝ^K`. Object `T ∈ ℝ^K`. Clean bucket `B_n = ⟨I_n, T⟩`. Unknown gain
`a_n > 0`. Data
```
    R_n = a_n · B_n,   n = 1,…,N.
```
**Global-scale ambiguity.** For any `λ>0`, `R_n = (λ a_n)(B_n/λ)`. So `(a,T)` is at best determined
up to `(a,T) ~ (λa, T/λ)`. "Identifiable" ≡ determined up to exactly this one scalar.

**Drift class.** Write `ℓ_n = log a_n` and assume `ℓ ∈ 𝒮`, a *linear* "slow" class (low-pass
subspace, or the linearization of a Lipschitz class), bandwidth `ρ = t_f/τ_c`, amplitude
`s = std(a)/⟨a⟩`. Effective pixel count `K_eff = (Σ_j T_j)² / Σ_j T_j²` (participation ratio).

---

## 1. Random-basis measurement statistics (Prop 1)

Let `I_n(j)` be i.i.d. across `n,j`, mean `μ_I`, variance `σ_I²`. Then `E[B_n]=μ_I S_1`
(`S_1=Σ_jT_j`), `Var(B_n)=σ_I² S_2` (`S_2=Σ_jT_j²`), and
```
    CV_B := σ_B/μ_B = (σ_I/μ_I)/√K_eff.
```
By the Lindeberg CLT (large `K_eff`), `B_n → 𝒩(μ_B,σ_B²)`, i.i.d. across `n` ⇒ **{B_n} is a white,
strictly stationary sequence**; the object enters only through the two scalars `(μ_B,σ_B)`.
(Numerically: `K_eff=187` ⇒ CV 0.0418 vs theory 0.0422; skew +0.02, excess kurt +0.05.)
Deterministic contrast: for Hadamard `B_n = c_{π(n)}` (Walsh coefficient), `CV ~ 68` vs `0.042`
(~1600×), heavy-tailed, object-dependent, non-stationary.

---

## 2. Theorem A — Deterministic bases are non-identifiable (exact, finite-dimensional)

**Assume** `N=K`, patterns are the rows of an invertible `H∈ℝ^{K×K}` (e.g. Hadamard); object
unconstrained (`c=HT` ranges over `ℝ^K`); `𝒮` a linear subspace with a non-constant element.
**Then** the gain is non-identifiable: each data record has a `dim 𝒮`-dimensional pre-image of
admissible `(a,T)`, strictly larger than the global-scale orbit.

*Proof.* `B_n=c_n`, `R_n=a_n c_n`. For any `s∈𝒮` set `a'_n=a_n e^{s_n}`, `c'_n=c_n e^{-s_n}`,
`T'=H^{-1}c'`. Then `a'_n c'_n = R_n ∀n`, `T'∈ℝ^K` valid, and `log a' = log a + s ∈ 𝒮` (linearity).
`s↦(a',T')` injective ⇒ `dim𝒮`-family. Constant `s` = global scale; a non-constant `s` exceeds it. ∎

**Cor A1 (slowness does not help).** Take `𝒮` = low-pass with bandwidth `≤ρ`. For any `ρ>0` a
non-constant low-pass `s` exists, so the gain stays non-identifiable no matter how slow the drift —
*as long as the object is unconstrained*. This is the precise sense of "blind Hadamard is ill-posed."

**Cor A2 (what a prior buys).** If `T∈𝒯` (nonneg/support/sparse), the family shrinks to
`{s : H^{-1}(c⊙e^{-s})∈𝒯}`. Identifiability can be restored in principle, but requires a strong
correct prior; conditioning (Thm D/E) stays poor. Ill-posedness is generic.

---

## 3. Theorem B — Random bases are identifiable (stationary-ergodic, asymptotic)

**Assume** the ensemble makes `{B_n}` strictly stationary and ergodic with `m_B:=E[log B_n]` finite,
`n`-independent (CLT/large-`K_eff` regime, `B_n>0` a.s. as `CV_B→0`); and `ℓ=log a` slow:
`sup_n |ℓ_n − (1/W)Σ_{k∈W_n} ℓ_k| → 0` as `W→∞, ρW→0`. **Then** `{a_n}` is identifiable up to global
scale and the windowed estimator `\hat ℓ_n = (1/W)Σ_{k∈W_n} log R_k − m_B` is consistent.

*Proof.* `log R_k = ℓ_k + m_B + z_k`, `z_k:=log B_k − m_B` zero-mean stationary ergodic.
`\hat ℓ_n − ℓ_n = [(1/W)Σℓ_k − ℓ_n] + [(1/W)Σ z_k]`. First bracket → 0 by slowness (`ρW→0`); second
→ 0 by the ergodic theorem. Only `ℓ_n + m_B` recovered ⇒ up to global scale. Then `\hat B=R/\hat a`,
invert (correlation/DGI or least squares). ∎

---

## 4. Proposition C — The dividing line

Identifiability ⇔
```
   (★)  (1/W) Σ_{k∈W_n} log B_k  →  a limit independent of n (and of the object beyond a global const).
```
Random: (★) holds (stationary+ergodic, limit `m_B`). Hadamard: `(1/W)Σ log|c_{π(k)}| = μ_n` is
**n-dependent and object-dependent** (sequency ordering ⇒ decreasing envelope), so
`\hat ℓ_n = ℓ_n + μ_n` — `μ_n` confounded with the gain. (★) is a property of the *pattern ensemble*.

---

## 5. Theorem D — Estimation error, object-independence, CRB, Fisher singularity

Under Thm B with `z_k` weakly dependent (summable autocovariance) and `ℓ` twice-differentiable
(curvature scale `ρ`):
```
   MSE(W) ≈ σ_z²/W + c(sρ)²W²,   min at  W* ~ (σ_z²/(s²ρ²))^{1/3},   MSE* ~ σ_z^{4/3}(sρ)^{2/3},
   σ_z² = Var(log B) ≈ CV_B² = (σ_I/μ_I)²/K_eff.
```
Key: `σ_z²` depends on the object **only through `K_eff`**, small (`~1/K_eff`), essentially
object-independent. Hadamard has no such bound (carrier "CV" `O(1)`+, and the bias term does not
vanish, Prop C). **CRB:** for `log R_n=ℓ_n+z_n`, `z_n~𝒩(0,σ_z²)` i.i.d., `ℓ` in a `W`-dim smooth
class, `CRB ≥ σ_z²/W_eff`; the windowed estimator attains this order. For Hadamard the Fisher
information is **singular along the ambiguity direction** `s` of Thm A ⇒ `CRB=+∞`: the
estimation-theoretic face of non-identifiability.

---

## 6. Proposition 3 — Pairwise (differential) normalization: exact failure law

Paired frames `(1±h_k)/2`, adjacent-frame drift `a⁻ = a⁺(1+δ)`. Estimator
`\hat c = S_1 (R⁺−R⁻)/(R⁺+R⁻)`. First order:
```
   Δc_k = −(δ_k/2) S_1 (1 − (c_k/S_1)²) ≈ −(δ_k/2) S_1.
```
Error ∝ **total flux `S_1`**, independent of the coefficient magnitude ⇒ small (high-freq)
coefficients have relative error ∝ `S_1/c_k` → blow up. (Numerically: pointwise corr 1.00000.)
By Parseval, `relMSE_pair = (Var(δ)/4) K_eff`; for OU drift `Var(δ) ≈ 2 s² ρ`, giving the
**pairwise failure threshold** `ρ_fail ≈ 2/(K_eff s²)`. (Explains "slow drift → Hadamard fine;
fast drift → sudden collapse.")

---

## 7. Theorem E — Error propagation (reconstruction side)

Corrected buckets `Y_n=ε_n B_n`, `E[ε]=1`, `Var(ε)=v`, `ε⊥B`.
**(a) Orthonormal exact inversion:** `T̂−T = H^{-1}((ε−1)⊙c)`, `relMSE = v` (one-to-one; error
weighted by `c_k²` ⇒ structured artifacts on energetic coefficients).
**(b) Random correlation/DGI:** `relMSE ≈ (C_0 + C_1 v K_eff)/N` (gain error incoherently averaged
`∝1/N`; `C_0` = intrinsic sampling floor).
**Honest corollary:** at equal `v`, orthogonal is *better* (`v` vs `~(C_0+…)/N`). Random's advantage
is that **`v` itself is driven small blindly** (Thm B/D: `v=MSE*→0`), whereas blind Hadamard has
`v=O(1)` (Thm A) unless slow-drift pairwise cancellation (Prop 3) applies.

---

## 8. Theorem F — SRHT attains both

SRHT patterns = rows of `HD`, `D=diag(η)`, `η_j∈{±1}` i.i.d. fair, fixed once. `c̃_k=Σ_j H_{kj}η_jT_j`.
Over `D`: `E_D[c̃_k]=0` (exact, all `k`); `Var_D(c̃_k)=Σ_j H_{kj}²T_j²=S_2` (exact, `k`-independent);
`Cov_D(c̃_k,c̃_{k'})=Σ_j H_{kj}H_{k'j}T_j²` = off-diagonal of `H diag(T²) Hᵀ`, magnitude `O(S_2/√K)`
(concentration). ⇒ `{c̃_k}` zero-mean, equal-variance `S_2`, asymptotically uncorrelated, and by a
Lindeberg CLT over `j`, marginally `𝒩(0,S_2)` and **identically distributed across `k`** ⇒ satisfies
(★) ⇒ Thm B applies (identifiable, small `v`). Meanwhile `HD` orthogonal (×const) ⇒ exact inversion
⇒ Thm E(a): `relMSE=v`, **no `1/N` sampling floor**. Hence SRHT = identifiability (Thm B) + exact
inversion (Thm E(a)) simultaneously. Ablation shows sign-only OR permutation-only each suffices:
what matters is decorrelating the object↔gain (coefficient↔time) entanglement.

**Note F1.** The Gaussian *marginal* of `c̃_k` is incidental (CLT byproduct). What (★)/Thm B need is
*stationarity+equal-variance of the carrier*, produced directly by the sign randomization. Hence the
operative variable is **randomization of the sign/phase structure, not the marginal distribution.**

---

## 9. Synthesis — analytic phase diagram

| scheme | relMSE (analytic) | valid region |
|---|---|---|
| Hadamard + pairwise | `s²ρ K_eff/2` | slow: `ρ ≪ 2/(K_eff s²)` |
| random + blind + DGI | `(C_0 + C_1 v* K_eff)/N`, `v*~(CV²)^{2/3}(sρ)^{2/3}` | wide, `N`-limited |
| Hadamard + blind | `O(1)` | none |
| SRHT + blind | random's identifiability + orthogonal's `v` | wide |

Flip boundary (pairwise-Hadamard vs random-blind): `ρ* ≈ 2 C_0 / (N K_eff s²)` — predicts `ρ*` shifts
left with larger `N`, brighter object (`K_eff↑`), stronger drift (`s↑`).

---

## 10. OPEN AGENDA — what we want deepened/completed (attack these)

- **B1 (mixing + rate).** Replace "ergodic + slow" with explicit `α`/`β`-mixing conditions + a
  modulus of continuity on `ℓ`; give a *non-asymptotic* rate for `\hat ℓ` and state whether the
  windowed estimator is minimax over the drift class `𝒮`.
- **D1 (CRB / van Trees).** A proper Cramér–Rao / Bayesian van Trees lower bound for estimating the
  smooth sequence `ℓ` from `{R_n}` under the random model; minimax rate over `𝒮`; matching upper
  bound. Make "Fisher singular ⟺ non-identifiable" a precise statement.
- **F1 (SRHT whiteness, rigorous).** Bound the `O(S_2/√K)` cross-covariances via Hanson–Wright;
  state the exact spikiness condition on `T` (`K_eff` large) for (★); prove whether a random
  permutation *alone* (no signs) is provably sufficient, and characterize the failure set.
- **A2′ (prior-restored identifiability).** With `T∈𝒯` (nonneg + support/sparsity), characterize the
  ambiguity variety `{s : H^{-1}(c⊙e^{-s})∈𝒯}` and give conditions for it to collapse to the
  global-scale orbit.
- **LIT (positioning).** Map `R_n=a_n⟨I_n,T⟩` onto the **bilinear inverse problem / blind
  deconvolution identifiability** literature (Ahmed–Recht–Romberg 2014; Choudhary–Mitra 2014;
  Li–Lee–Bresler 2016; Kech–Krahmer 2017; Kliesch–Kueng–Eisert–Gross). Does the subspace/lifting
  identifiability theory recover Thms A/B? Does our "stationarity anchor" correspond to a known
  deterministic identifiability condition (e.g. a subspace/genericity condition)? What sample
  complexity `N` do those results give vs our windowed estimator? Clarify what is genuinely new here
  (time-varying multiplicative + stationarity-based blind identifiability) vs prior art.
- **E1 (unified + noise).** Unify E(a)/E(b) into one `relMSE(v,N,basis)` and rederive `ρ*`
  rigorously; add additive detector noise (low-photon: ratio amplification in pairwise, Prop 3).
- **INFO (phase transition).** Sample-complexity / phase-transition statement for blind gain
  recovery as a function of `(N, K_eff, s, ρ)`.

All numerical spot-checks to date are consistent with §1–§9 (script `verify_theory.py`). Please:
(i) find and fix any weak assumption or gap in §2–§8; (ii) supply the missing rigor in §10; (iii)
position against the literature; (iv) flag anything you believe is wrong.
