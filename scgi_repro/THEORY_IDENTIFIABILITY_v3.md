# Identifiability of gain–object separation — rigorous note v3

**Supersedes v2. Incorporates the GPT deep-dive R1 (GitHub issue #1, nonce MATHDIVE-1c8e8a1764) after adversarial verification.** Full extended proofs live in issue #1; this note states the corrected results and flags what still needs checking.

## Front matter — three distinct notions of identifiability (the key reframing)

The v2 note conflated two things. Separate them:

1. **Exact algebraic identifiability** (finite-sample, noiseless). In the square N=K unconstrained-object case this **fails for ANY invertible design — including a random one** — not just Hadamard (Thm A generalized). Randomness gives no exact-algebraic advantage here.
2. **Statistical / asymptotic identifiability** of the *relative* gain trajectory, via a temporal stationarity anchor (Thm B). This is where randomization wins — and it is asymptotic (large K_eff, mixing, slow gain), not exact.
3. **Estimation conditioning** (how small the residual gain error / reconstruction MSE can be made) — Thms D/E.

⇒ **Thm B must be advertised as "statistical/asymptotic relative-gain identifiability," never as exact identifiability of (a,T) in Thm A's unconstrained class.**

## §1 Prop 1 (carrier stats) — corrected
Mean/var unchanged: E B_n=μ_I S₁, Var B_n=σ_I² S₂, CV_B=(σ_I/μ_I)/√K_eff. **But the CLT/log-transform need more than K_eff:**
- **Lindeberg spikiness** `K_∞ := S₂/‖T‖_∞² → ∞` (Berry–Esseen small parameter `≤ Σ|T_j|³/S₂^{3/2} ≤ K_∞^{-1/2}`). K_eff large does NOT imply K_∞ large (a single spike breaks the CLT while K_eff stays large).
- `B_n>0` w.h.p. (nonneg patterns/object), μ_I>0, finite 2+η moment.
- "object enters only via (μ_B,σ_B)" is true **only at the Gaussian-approximation level**; exact law depends on all weighted cumulants. For gain recovery this only enters as a *time-constant* `m_T=E[log B_n]`, absorbed into global scale.

## §2 Thm A (deterministic non-identifiability) — generalized
For **any** invertible M∈ℝ^{K×K} (Hadamard OR random square), unconstrained object, linear log-gain class S: for s∈S, ℓ'=ℓ+s, c'=c⊙e^{-s}, T'=M⁻¹c' give identical data. **Non-gauge ambiguity dim = dim S − dim(S∩span{1}) ≥ 1** whenever S has a nonconstant element. Caveats: (i) N>K breaks the trivial construction — B' must lie in the column space (→ bilinear inverse problem); (ii) if S excludes constants, impose a gauge Σℓ_n=0; (iii) zero buckets c_n=0 break logs — separate that pathology.

## §2b Cor A2 (priors) — nonnegativity alone is NOT enough
Let M_s=H⁻¹diag(e^{-s})H, ambiguity set V_𝒯(T)={s∈S: M_sT∈𝒯}. **Full-support strictly-positive T: nonnegativity does NOT restore identifiability** (M_sT stays positive for small s → nonconstant ambiguity survives). **Support zeros do:** with known support Ω, local criterion `ker(P_{Ω^c} H⁻¹ diag(HT) | S) = S∩span{1}`; generic thresholds `K−q ≥ dim(S/span1)` (known support), `K ≥ 2q + dim(S/span1)` (unknown, dimension-counting heuristic — cf. Kech–Krahmer sparsity threshold). Finite-amplitude sufficient version via singular-value margin in issue #1.

## §3 Thm B (random identifiability) — rescoped to statistical/asymptotic
Y_n=log R_n=ℓ_n+m_T+z_n, m_T time-constant, {z_n} centered stationary mixing. Windowed average estimates ℓ_n+m_T ⇒ **ℓ_n−mean(ℓ) (relative gain) is consistently estimable up to global scale.** NOT exact finite-sample identifiability of (a,T). Reconstruction after gain correction needs a **separate** conditioning assumption (enough random patterns for DGI, or full orthogonal set for SRHT/Hadamard).

## §4 Prop C — estimator-specific
(★) `W⁻¹Σ_{k∈W_n} log B_k` ≈ n-independent (up to global-scale const) is **necessary & sufficient for consistency of the blind stationarity-anchor/windowed estimator** (under slow-gain + mixing) — NOT a universal iff for identifiability (bilinear/sparsity/overdetermined methods can identify when (★) fails; a random permutation of Hadamard coeffs can make (★) hold in a finite-population sense).

## §5 Thm D → B1 (rate + minimax) — generalized & lower-bounded
Hölder-α drift, seminorm L_α, order-matched window: `MSE(W) ≤ C₁σ_eff²/W + C₂ L_α² W^{2α}`, `W*≍(σ_eff²/L_α²)^{1/(2α+1)}`, `MSE*≍L_α^{2/(2α+1)} σ_eff^{4α/(2α+1)}`. **Recovers v2's (sρ)^{2/3} at α=1, L₁≍sρ.** Non-asymptotic: β-mixing (β(k)≤β₀e^{-(k/b)^κ}) + sub-exponential z ⇒ blocking-Bernstein high-probability bound (issue #1). **Minimax lower bound** (Assouad/two-point for Hölder; van Trees/Pinsker for Sobolev): `≥ c_α L^{2/(2α+1)}(σ²/N)^{2α/(2α+1)}` ⇒ **the stationarity-anchor estimator is rate-optimal** with σ_eff²≈(σ_I/μ_I)²/K_eff (under spikiness).

## §6 D1 (CRB, Fisher singularity) — made precise
Quotient Fisher: ℓ=Uθ, Y=Uθ+m𝟙+z, z~N(0,Σ). Eliminating the nuisance m (indistinguishable from global scale): `I_θ = Uᵀ Σ^{-1/2} P_⊥ Σ^{-1/2} U`. Estimable functional Lθ: `Cov ≥ L I_θ⁺ Lᵀ`; component along ker I_θ ⇒ CRB=∞. **Fisher-singular ⇔ non-identifiable, precise version:** I_θ = S_θ*S_θ (pullback metric of the quotient score); I_θ PD on T(Θ/G) ⇔ local *differential* identifiability (immersion). An ambiguity curve ⇒ Fisher null direction; conversely singularity ⇒ failure of local differential identifiability (⇒ genuine local non-identifiability under constant-rank/analyticity; does NOT rule out isolated global aliases). For Thm A the ambiguity curve is explicit ⇒ exact implication.

## §7 Prop 3 (pairwise) — exact law
x_k=c_k/S₁, a⁻=a⁺(1+δ_k): `ĉ_k − c_k = −S₁ δ_k(1−x_k²)/[2+δ_k(1−x_k)]` (v2's first-order = denominator→2). `relMSE_pair=(S₁²/(K S₂))Σ E[δ²(1−x²)²/(2+δ(1−x))²] ≈ (Var δ/4)K_eff` when |δ| small & most |x_k| small; OU: Var δ≈2s²·(Δt/τ_c). Assumes S₁ known/calibrated (else global-scale ambiguity remains).

## §8 Thm E — status
(a) orthonormal exact inversion `relMSE=v` — exact, given E(ε−1)=0, Var=v, ε⊥coeffs, H normalized. (b) random DGI `relMSE≈(C₀+C₁ v K_eff)/N` — **label as a moment heuristic** until C₀,C₁ derived from 4th moments+conditioning. Logical point stands: random wins because **v can be made small blindly**, not because it's better at equal v.

## §9 Thm F (SRHT) — the important correction
x=UDPT (U orthonormal Hadamard, D random signs, P optional random permutation). **Sign randomization alone gives identical MARGINALS only** (mean 0, var S₂ per row); it does **NOT** decorrelate rows for a fixed object: `Cov_D(√K x_k,√K x_l)=Σ_j χ_{kl}(j)T_j²` = a **Walsh coefficient of T²**, which can be as large as S₂ (counterexample: T² aligned with χ_{kl}'s positive support). Correct whitening needs **either** small Walsh spectrum of T² (`max_{k≠l}|Σχ_{kl}(j)T_j²|≤εS₂`) **or random pixel permutation P**, with the right parameters `K_4=S₂²/ΣT_j⁴` and K_∞:
- pairwise (permutation, Serfling/Bernstein): `min(K_4,K_∞) ≳ ε^{-2}log(K/δ)`.
- window energy (Hanson–Wright): `Q_A=‖P_A UDPT‖²`, `W K_∞/K ≳ log(M/δ)` for M windows.
Dense bounded-dynamic-range T ⇒ K_∞≍K_4≍K_eff≍K (condition reduces to W≳log M); sparse T ⇒ much stronger. **Permutation-alone gives (★) (exchangeability) but NOT the small σ_z²≈1/K_eff variance advantage** — that needs random nonnegative patterns or offset SRHT with adequate spikiness.

## §10 Literature positioning & what is genuinely NEW
Lift X=aTᵀ (rank-one): R_n=⟨e_n I_nᵀ, X⟩, linear in X. Related work:
- **Ahmed–Recht–Romberg 2014** (blind deconv via lifting/nuclear norm) — recovery under known subspace+randomness.
- **Choudhary–Mitra 2014** (BIP identifiability scaling / fundamental limits) — conic-prior identifiability via rank-2 nullspaces; **closest to Thm A/A2**.
- **Li–Lee–Bresler** (algebraic BIP identifiability; gain/phase calibration) — what priors buy.
- **Kech–Krahmer 2017** (optimal injectivity: m≥2(n₁+n₂)−4 subspace, m>2(s₁+s₂)−2 sparsity) — the finite-dim comparison threshold.
- **Kliesch–Kueng–Eisert–Gross** — low-rank/structured-random recovery; methodologically related but **do NOT state the stationarity-anchor mechanism**.
⚠️ **All arXiv IDs in issue #1 must be verified before citing** (LLM-supplied; the Kliesch et al. pairing is a hedged best-guess and likely needs correction).

**What the literature already covers:** Thm A as a rank-2 nullspace non-injectivity; A2 as prior-constrained injectivity on cones/supports; finite-dim sample complexity for overdetermined subspace-gain variants.

**What is genuinely NEW (state carefully — NOT "random bilinear maps are identifiable", which is known):**
1. **Temporal stationarity anchor** — randomized patterns make log B_n stationary with time-independent mean ⇒ relative gain recoverable from ONE acquisition sequence by local averaging.
2. **Slow-gain nonparametric calibration rate** — variance/W + drift-bias tradeoff, carrier variance ≈1/K_eff (under spikiness), minimax-optimal.
3. **Ordered-orthogonal failure mode** — deterministic inversion is well-conditioned given the gain, yet blind correction fails because ordered coefficients form an object-dependent low-frequency envelope confounded with gain.
4. **SRHT synthesis** — exact orthogonal reconstruction + randomized/stationary carrier (with the right offset/signs/permutation/spikiness).
⇒ **A temporal-statistical identifiability story, not a finite-dimensional generic-injectivity story.**

## §11 Open problems (post-R1)
Finite-sample algebraic identifiability for tall N>K log-slow-gain designs (sharp (N,K,p) thresholds); sharp minimax constants; joint estimation of m_T/K_eff with T; robust log-transform for zero/low-photon buckets; SRHT optimal-spikiness necessary+sufficient (Walsh-flatness); exact permutation-vs-signs separation theorem; prior-restored *global* identifiability via verifiable rank/transversality; unified relMSE(v,N,basis,noise); finite-N phase transition in (N,K_eff,s,ρ) vs the analytic flip boundary; model-mismatch (nonstationary objects, calibration errors, jump gains).

## Editing checklist applied vs v2
Thm B rescoped (statistical, relative gain) · K_eff→{K_∞ Lindeberg, K_4 whitening, K_eff CV} · Prop C→window-estimator iff · exact Prop 3 · D→quotient-Fisher/CRB · Thm F sign-vs-permutation split · Thm A generalized to any invertible design · A2 support-zeros criterion · lit positioning + novelty.
