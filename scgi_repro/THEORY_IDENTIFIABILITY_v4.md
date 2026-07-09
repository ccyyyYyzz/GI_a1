# Identifiability of gain–object separation — rigorous note v4

**Supersedes v3. Integrates GPT deep-dive R1 (issue #1) + R2 (issue #2), after adversarial verification.** v3's three-notion framing (exact-algebraic / statistical-asymptotic / estimation-conditioning) stands. This note adds the two results R2 closed, corrects two v3 overstatements, and records the verified citations. Full proofs in issues #1–#2.

---

## A. Tall-design finite-sample identifiability thresholds (NEW — R2 §1)

Model `y = diag(e^ℓ) M T`, `M∈ℝ^{N×K}` generic tall (N>K), log-gain `ℓ∈S`, `dim S=p`, S contains constants (the global-scale gauge). Lift `X=aTᵀ`; the operator is the **diagonal-row** map `L_M(X)_n = a_n m_nᵀT` — **NOT** a generic rank-one measurement, so Kech–Krahmer's `m≥2(n₁+n₂)−4` does **not** transfer. Collision `MT = D_s MT'`, `s=ℓ'−ℓ`; ambiguity controlled by `U ∩ D_s U`.

**Thresholds (generic M, generic/transverse nonconstant gain family):**
- **local differential identifiability:** `N ≥ K + p − 1`
- **generic exact finite-sample identifiability:** `N ≥ K + p`  (i.e. surplus rows `N−K ≥ p`)
- **uniform (every nonzero object):** `N ≥ 2K + p − 1`

Proof = projective incidence dimension `Δ = r + 2K − 1 − ρ`, `r=p−1` nonconstant gain dims, `ρ=rank[M,−D_bM]=min(N,2K)` on the dense stratum; generic-point ID ⟺ `Δ<K−1`, uniform ⟺ `Δ<0`. For **non-generic structured S**, use the stratum formula `max_α (r_α + 2K − 1 − ρ_α) < K−1` (generic) / `< 0` (uniform).

**Overdetermination-vs-statistics dichotomy (the payoff):**
- `N ≥ K+p`: overdetermination alone gives identifiability — **no stationarity mechanism logically needed** (still useful for stable estimation).
- `K < N < K+p`: tallness insufficient even generically ⇒ **the v3 statistical stationarity mechanism (or a sparsity/support prior) is required.**
- `N ≤ K`: even known-gain recovery not injective without priors.

**★ Synthesis (my addition — connects to the drift rate & flip boundary):** for a gain with bandwidth ρ over N frames, the log-gain subspace dimension scales as `p ≈ ρN` (number of low-pass modes). Then the algebraic threshold `N ≥ K+p` becomes `N(1−ρ) ≳ K`, i.e. **`N ≳ K/(1−ρ)`**. Slow drift (ρ≪1): modest oversampling identifies algebraically. Fast drift (ρ→1): `p→N`, algebraic identifiability is impossible for ANY N ⇒ one **must** fall back on the statistical mechanism (and even that fails once the gain de-correlates within the averaging window — the v3/§7 pairwise-collapse regime). This is the rigorous origin of the "fast drift kills every basis" wall and links §A to the empirical flip boundary `ρ*`.

## B. SRHT sign/permutation whitening — exact Walsh condition (NEW — R2 §2)

`Z_g = √K(UDT)_g = Σ_j χ_g(j)ε_j T_j`, `w=T²`, `ŵ(h)=Σ_j χ_h(j)T_j²` (Walsh transform, `ŵ(0)=S₂`). Exact covariance obstruction:
```
   Cov_D(Z_g, Z_h) = ŵ(g+h).
```
**Necessary-and-sufficient conditions (sign-only, realized order):**
- exact pairwise whitening ⟺ `ŵ(q)=0 ∀q≠0` ⟺ **T² flat** (`T_j²=S₂/K ∀j`);
- ε-pairwise ⟺ `max_{q≠0}|ŵ(q)| ≤ εS₂`;
- ε-spectral over window class 𝒜 ⟺ `sup_A ‖R_A‖_op ≤ ε`, `R_A(g,h)=ŵ(g+h)/S₂`;
- window-average ⟺ `sup_A |Σ_{q≠0} m_A(q)ŵ(q)| ≤ ε|A|S₂`, `m_A(q)=#{(g,h)∈A²: g≠h, g+h=q}`.

**Random pixel permutation** replaces T² by (PT)² (exact same conditions), and makes flatness *likely*: `Pr(|ŵ^P(q)|≥εS₂) ≤ 2exp(−c·min(ε²K_4, εK_∞))` (Bernstein–Serfling on the half-population sum), union over K−1 frequencies ⇒ pairwise ε-flatness w.p. ≥1−δ when
```
   min(ε² K_4, ε K_∞) ≥ C log(K/δ),   K_4 = S₂²/Σ_j T_j⁴,  K_∞ = S₂/max_j T_j².
```
⇒ **K_4, K_∞ are sufficient PROBABILISTIC parameters; the exact deterministic condition is Walsh-flatness of the realized (P)T².** (v3's spikiness conditions were sufficient, not N&S — corrected.)

**Sharp obstruction:** if T² aligns with a nonzero Walsh character χ_q, one non-DC coefficient equals S₂ ⇒ a row pair is perfectly correlated; **signs cannot fix it, permutation usually can** (unless energy is on too few pixels).

## C. Permutation-alone carrier variance — v3 §9 CORRECTED (R2 §3)

For a non-DC row under permutation-only (no signs), `Z_g(P)=Σ_j χ_g(j)T_{Pj}`: E_P Z_g=0 and
```
   Var_P Z_g = (K·S₂ − S₁²)/(K−1) = S₂ (K − K_eff)/(K−1).    [re-derived & verified]
```
With offset patterns `B_g=μS₁+σZ_g`, relative carrier variance `= (σ/μ)²(K−K_eff)/((K−1)K_eff) ≤ (σ/μ)²/K_eff`.
⇒ **permutation-alone DOES attain the O(1/K_eff) UPPER variance scale** (v3 §9's "permutation-alone cannot get small variance" was WRONG). BUT it **cannot guarantee a two-sided Θ(1/K_eff) LOWER bound**: a flat object has K_eff=K yet ŵ(q)=0 ∀q ⇒ zero excitation. Correct statement:
- permutation ⇒ finite-population stationarity/exchangeability + O(1/K_eff) upper variance;
- it does NOT generate independent Rademacher carrier noise, and has zero excitation for flat objects;
- **signs / iid nonnegative random patterns** are needed only if the model requires independent carrier fluctuations ~S₂ for *every* object (including flat).

## D. Verified citations (R2 §0.4 — opened before citing; re-verify once more at submission)
- Ahmed–Recht–Romberg, *Blind Deconvolution using Convex Programming*, arXiv:1211.5608 (posted 2012).
- Choudhary–Mitra, *Identifiability Scaling Laws in Bilinear Inverse Problems*, arXiv:1402.2637.
- Li–Lee–Bresler, *A Unified Framework for Identifiability Analysis in BIP…*, arXiv:1501.06120 (**primary BIP/BGPC identifiability cite**); also 1505.03399, and 1507.01308 (*Minimal Assumptions* — clean almost-all vs all-pairs thresholds); 1712.00111 (BGPC algorithmic, not the identifiability cite).
- Kech–Krahmer, *Optimal Injectivity Conditions for Bilinear Inverse Problems…*, arXiv:1603.07316.
- Kliesch–Kueng–Eisert–Gross, arXiv:1701.03135 = **low-Kraus-rank quantum process tomography** (real, but NOT a stationarity-anchor source — do not cite as the rank-one-measurement entry).
- For "low-rank recovery from rank-one measurements": **Kueng–Rauhut–Terstiege, arXiv:1410.6913** (correct entry).

## E. Remaining open after R2 (mostly second-order / bridge-to-practice)
Numerical conditioning + algorithms at the tall-design threshold; **minimax CONSTANTS** for the stationarity-anchor estimator (rate is done, §v3-B1); **robust log-transform for zero / low-photon (Poisson) buckets**; global prior-restored identifiability for non-generic deterministic supports; **unified finite-noise `relMSE(v,N,basis,noise)`** across DGI / SRHT / Hadamard (the bridge to the paper's phase diagram / flip boundary); verify the physical low-pass gain subspace S satisfies the dense-stratum genericity used in §A.

---
*Maturity note: the identifiability CORE (exact + statistical characterization, sharp finite-sample thresholds, estimation rate + minimax-optimality, SRHT N&S whitening, error propagation, positioned novelty with verified citations) is now essentially complete and rigorous. §E items are refinements / the bridge to reconstruction performance — targeted next in R3.*
