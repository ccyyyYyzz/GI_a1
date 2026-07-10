# R12 — GPT primary-prover re-derivation of the repaired Appendix D (Theorem C chain)

> Captured 2026-07-10 from ChatGPT Pro (session "GitHub Review Round R12",
> https://chatgpt.com/c/6a50f91d-88a0-83eb-8c24-782866fe8324, worked 20m57s).
> Object: Appendix D @ 955d8f7 + `run_paper_fig7_lowphoton.py` + issue #7.
> **Overall verdict: REPLACE-WITH, not FATAL** — the chain is salvageable and, with the
> replacements below, cleaner and stronger than the committed version.

## Executive verdict table

| Item | Verdict |
|---|---|
| (a) Known-carrier finite-W identity | SOUND for averages of W DISTINCT frames; replicate-padded edge windows falsify the literal all-n 1/W claim |
| (b) Unknown-carrier Davydov chain | REPLACE-WITH (nonstationarity error; tight constant 16; additive o(W⁻¹)) |
| (c) Clamp probability/risk | REPLACE-WITH (residual-margin condition; edge windows change all-zero prob) |
| (d) β∈(0,1] restriction | REPLACE-WITH (real obstruction = carrier-weighted first moment; salvageable β>1 partial result) |
| (e) Log-domain minimax | REPLACE-WITH (I(θ)=λ false for d>0; finite-information truncation; direct Le Cam proof) |
| F.6 Q≤0 sign | SOUND (fixed wording correct; note ρ*=−log(1−Q) is an implicit fixed point unless v_blind frozen) |

## Four literal counterexamples that must not remain in archival text
1. Replicate-padded edge windows vs the claimed σ̄²/W: first width-65 window = 33 copies of frame 0 + frames 1..32 ⇒ Σw_j² = (33²+32)/65² ⇒ **W_eff = 65²/(33²+32) = 3.769**, variance up to **17.25×** larger than σ̄²/65.
2. Remark D.4.3 assumed stationarity of the soft-log sequence; with varying deterministic gain ℓ_k the sequence is NOT stationary even for i.i.d. carriers (no single γ_ψ(h) exists).
3. σ_LR²·W⁻¹·(1+o(1)) is invalid when σ_LR² = 0 (same differencing counterexample); must be written additively: Var = σ_LR²/W + o(W⁻¹).
4. I(θ) = λ for LOG-GAIN is false when dark counts d > 0 (correct: Σ E[s_k²/(s_k+d)]; equals Wλ̄ only at d=0).

## Key derivations (summary; full replacement LaTeX below)
- **Known-carrier identity**: Var(Z_n) = W⁻²Σ v_k(ℓ_k) = v̄_{n,α}/W EXACTLY (independent, non-identical); committed σ̄_α²/W is a valid inequality (uniform bound). Low-photon law via **window-average sensitivity**: M_n′(ℓ_n) = c_α λ̄_n[1+O_α(ε_n)] and Var(Z_n) = c_α²λ̄_n/W·[1+O_α(ε_n)] ⇒ Var/M′² = [1+O_α(ε_n)]/(Wλ̄_n) — NO carrier-comparability needed. The committed κ_min ≍ c_α λ̄ is false under unrestricted heteroscedasticity (example: λ₁=ε², λ₂=2ε−ε²) — κ_min-based display is only a conservative bound.
- **β>1**: with ℓ_k−ℓ_n = v_n u_k + r_{nk}, |r_{nk}| ≤ L|u_k|^β, the calibrated bias's first-order term is v_n Σ w_k q_k′(ℓ_n) u_k — centering kills Σw_k u_k but NOT the carrier-weighted moment. First-order counterexample: asymmetric carriers with q′=a₊ (u>0), a₋ (u<0) ⇒ bias O(h), killing every β>1 claim under the present assumptions. For constant carrier the first-order term cancels and the quadratic term O(h²) ≤ O(h^β) for 1<β≤2 ⇒ **salvageable second-order bound (D.11)** under homogeneous or "sensitivity-balanced" carriers (|Σw_k q_k′ u_k| ≲ h^β). Second-order expansion of M_n^{-1} does NOT remove an unbalanced first moment.
- **Minimax**: centered-log loss = exact quotient metric d²_quot = N⁻¹‖P_N(log ĝ − log g)‖² ✓ (code's mean-normalization is equivalent under P_N). Latent carriers: I_obs ≤ I_comp (score = conditional expectation of complete-data score) ⇒ 1/(Wλ̄) lower bound survives marginalization at d=0. Finite-information truncation: R_minimax ≳ min{δ₀², 1/(Wλ̄)} — pure 1/(Wλ̄) is the Wλ̄→∞ regime. Direct Poisson Le Cam proof (KL ≤ Cδ²Σλ_k v_k² conditional on carrier; marginalization only reduces KL). Hölder-bump choice W* ≍ (L_a²λ̄)^{−1/(2β+1)} gives the nonparametric rate L_a^{2/(2β+1)} λ̄^{−2β/(2β+1)} matching (D.9) exponents — replaces reliance on Theorem D's Gaussian bound (a Gaussian model is NOT a submodel of the mixed-Poisson experiment). Leading variance constant 1/(Wλ̄) matches marginal Fisher J(θ)=λ̄+O(λ̄²) in the rare-event regime; sharp constants remain open (as stated).
- **Clamp**: E_n^c ⊆ {|B_n+Z_n| ≥ r_n}, r_n = min{M_n(ℓ_n)−M_n(θ_min), M_n(θ_max)−M_n(ℓ_n)} ≥ κ̲_nΔ_n; P ≤ min{1,(B_n²+V_n)/r_n²}; sharper centered form when |B_n|<r_n: P ≤ V_n/(r_n−|B_n|)². Bernstein exponentiality REQUIRES residual margin r_n−|B_n| ≥ τ (bias can consume the margin). Edge windows: all-zero prob = e^{−33λ} not e^{−65λ} at the first window (2.6e−4 vs 8.8e−8 at λ=0.25). Clamp MSE term D_Θ²P(E^c) complete (bias-only contribution ≤ D_Θ²P²).

## Implementation findings (must be fixed or relabeled in code/experiment)
1. **Replicate padding at record edges** must be removed (truncated, renormalized distinct windows) or analyzed via the weighted theorem (aggregated weights). The "65 vs 64 = 1.6% slack" claim is interior-only.
2. **Fisher reference** should use the local information I_n = Σ_{k∈W_n} s_k²/(s_k+d) (=Σλ_k at d=0) with gauge projection, not the global nominal Wλ̄_record.
3. **Calibration interpolation not certified**: table exact at grid points, but log-λ linear interpolation + constant extension has no certified error bound; (D.8) should acquire a deterministic (ε_cal+ε_bis)²/κ̲_n² term and the clamp margin shrinks by ε_cal+ε_bis (matters most at low photons).
4. **Operating-range bracket**: code brackets g ∈ [λ_lo/b_max, λ_hi/b_min] (wider than the safe interval [λ_lo/b_min, λ_hi/b_max] ensuring ALL gb_k in-table); either use the safe interval or acknowledge the approximate M̃_n with controlled error.
5. **The Fig. 7 "known carrier" is an ORACLE quantity**: b_k ∝ (AT)_k from the simulated true object. The arm must be labeled oracle-known-carrier / flat-field-calibrated benchmark, NOT "programmed design intensities".
6. α→0 non-uniformity: expansions valid for fixed α; c_α = log(1+1/α) → ∞; distinguish fixed-theorem λ_->0 assumption from triangular low-intensity asymptotics.

## VERBATIM REPLACEMENT LATEX (integrate as-is, adapting only macro names/labels)

### R12-A: Exact weighted known-carrier statement (replaces the (D.8) display + proof core)
```latex
\paragraph{Exact finite-window identity with known carriers.}
For a fixed window $n$, let $\mathcal I_n$ be the set of distinct
frame indices used by the estimator and let $w_{nk}\ge0$,
$\sum_{k\in\mathcal I_n}w_{nk}=1$. If a padding convention repeats a
frame, all repeated occurrences are first aggregated into its single
weight $w_{nk}$. Put
\[
q_k(t)=m_\alpha(\Lambda_0e^t b_k+d),\qquad
v_k(t)=\operatorname{Var}\!\left[
\psi_\alpha(\operatorname{Pois}(\Lambda_0e^t b_k+d))\right],
\]
\[
M_n(t)=\sum_{k\in\mathcal I_n}w_{nk}q_k(t),
\qquad
y_n=\sum_{k\in\mathcal I_n}w_{nk}\psi_\alpha(C_k),
\]
and define
\[
B_n=\sum_{k\in\mathcal I_n}w_{nk}
\{q_k(\ell_k)-q_k(\ell_n)\},
\qquad
V_n=\sum_{k\in\mathcal I_n}w_{nk}^2v_k(\ell_k).
\]
Let
\[
\underline\kappa_n=\inf_{t\in\Theta}M_n'(t)>0,
\qquad
D_\Theta=\theta_{\max}-\theta_{\min},
\]
and let $\hat\theta_n$ be the generalized inverse of $M_n$, clipped to
$\Theta$. Then, conditionally on the gain path and known carriers,
\[
\operatorname{Var}\!\left[
\sum_{k\in\mathcal I_n}w_{nk}
\{\psi_\alpha(C_k)-q_k(\ell_k)\}\right]
=V_n
\]
exactly, and no mixing or stationarity assumption is required. If
$\mathcal E_n=\{y_n\in M_n(\Theta)\}$, then
\[
\mathbb E(\hat\theta_n-\ell_n)^2
\le
\frac{B_n^2+V_n}{\underline\kappa_n^2}
+D_\Theta^2\,\mathbb P(\mathcal E_n^c).
\tag{D.8}
\]
Moreover, with
$\overline\kappa_k=\sup_{t\in\Theta}q_k'(t)$, the pointwise modulus
$|\ell_k-\ell_n|\le L_a|k-n|^\beta$ gives
\[
|B_n|
\le
L_a\sum_{k\in\mathcal I_n}
w_{nk}\overline\kappa_k|k-n|^\beta.
\]
For an unpadded average of $W$ distinct frames, $w_{nk}=1/W$ and hence
\[
V_n=\frac{\bar v_{n,\alpha}}{W},
\qquad
\bar v_{n,\alpha}
=\frac1W\sum_{k\in W_n}v_k(\ell_k)
\le\bar\sigma_\alpha^2.
\]

\emph{Proof.}
Write
\[
y_n-M_n(\ell_n)=B_n+Z_n,\qquad
Z_n=\sum_{k\in\mathcal I_n}w_{nk}
\{\psi_\alpha(C_k)-q_k(\ell_k)\}.
\]
The variables in $Z_n$ are independent and centered conditionally on
the gain path and known carriers, so
$\mathbb EZ_n=0$ and
$\operatorname{Var}(Z_n)=V_n$ exactly. On $\mathcal E_n$, the mean
value theorem and $M_n'\ge\underline\kappa_n$ imply
\[
|\hat\theta_n-\ell_n|
\le\underline\kappa_n^{-1}|B_n+Z_n|.
\]
On $\mathcal E_n^c$, both $\hat\theta_n$ and $\ell_n$ belong to
$\Theta$, so the error is at most $D_\Theta$. Taking expectations and
using
$\mathbb E(B_n+Z_n)^2=B_n^2+V_n$
gives (D.8). The bound on $B_n$ follows by applying the mean value
theorem to each $q_k$ and then the pointwise modulus. \hfill$\blacksquare$
```
Plus the low-photon corollary (unpadded equal-weight window, d=0, fixed α, max_k λ_k(ℓ_n) ≤ ε):
```latex
M_n'(\ell_n)=c_\alpha\bar\lambda_n\{1+O_\alpha(\varepsilon)\},\qquad
V_n=\frac{c_\alpha^2\bar\lambda_n}{W}\{1+O_\alpha(\varepsilon)\},
\qquad
\frac{V_n}{M_n'(\ell_n)^2}
=\frac{1+O_\alpha(\varepsilon)}{W\bar\lambda_n},
```
with c_α = log(1+1/α), λ̄_n = W⁻¹Σλ_k(ℓ_n) — **no carrier-comparability assumption**.

### R12-B: Remark D.4.3 replacement (nonstationary covariance + Davydov constant 16)
```latex
\paragraph{Remark D.4.3 (unknown random carrier; nonstationary
finite-$W$ covariance bound).}
Let $\{B_k\}$ be an unobserved stationary random carrier with known
law, independent of the parameter, and let
\[
\bar m_{\alpha,k}(t)
=\mathbb E_B\,m_\alpha(\Lambda_0e^tB_k+d).
\]
Because the gain path $\ell_k$ may vary, stationarity of $\{B_k\}$
does not in general make the soft-log sequence stationary. Define
\[
z_k=\psi_\alpha(C_k)-\mathbb E\psi_\alpha(C_k),
\qquad
g_k(b)=m_\alpha(\Lambda_0e^{\ell_k}b+d).
\]
Conditional independence of the Poisson randomization gives, for
$i\ne j$,
\[
\operatorname{Cov}(z_i,z_j)
=\operatorname{Cov}(g_i(B_i),g_j(B_j)).
\]
Consequently the exact finite-window identity is
\[
\begin{aligned}
\operatorname{Var}\!\left(W^{-1}\sum_{i=1}^Wz_i\right)
={}&W^{-2}\sum_{i=1}^W\operatorname{Var}(z_i)\\
&+2W^{-2}\sum_{h=1}^{W-1}
\sum_{i=1}^{W-h}\operatorname{Cov}(z_i,z_{i+h}).
\end{aligned}
\tag{D.10}
\]
Let $p=2+\eta$, $r_\eta=\eta/(2+\eta)$, and assume
\[
v_*:=\sup_i\operatorname{Var}(z_i)<\infty,\qquad
G_p:=\sup_i\|g_i(B_i)-\mathbb Eg_i(B_i)\|_p<\infty.
\]
If the carrier is strongly mixing with coefficient $\alpha_B(h)$,
Davydov's inequality gives
\[
|\operatorname{Cov}(z_i,z_{i+h})|
\le8\,\alpha_B(h)^{r_\eta}G_p^2.
\]
Substitution into (D.10) yields the explicit finite-$W$ bound
\[
\operatorname{Var}\!\left(W^{-1}\sum_{i=1}^Wz_i\right)
\le
\frac1W\left[
v_*+16G_p^2\sum_{h=1}^{W-1}
\left(1-\frac hW\right)\alpha_B(h)^{r_\eta}
\right]
\le
\frac{v_*+16G_p^2\sum_{h\ge1}\alpha_B(h)^{r_\eta}}{W}.
\]
The factor $16$ is the constant obtained from Davydov's constant $8$
and the two covariance triangles. It is sharper to apply Davydov to
the conditional means $g_i(B_i)$ than to $z_i$ itself, because
independent Poisson shot noise contributes only to the diagonal
variance $v_*$.

If $\ell_k$ is constant and the resulting marked process is strictly
stationary, write $\gamma_\psi(h)=\operatorname{Cov}(z_0,z_h)$. Then
\[
\operatorname{Var}\!\left(W^{-1}\sum_{k=1}^Wz_k\right)
=
W^{-1}\sum_{|h|<W}\left(1-\frac{|h|}{W}\right)\gamma_\psi(h)
\le\frac{\sum_h|\gamma_\psi(h)|}{W},
\]
and when $\sum_h|\gamma_\psi(h)|<\infty$,
\[
\operatorname{Var}\!\left(W^{-1}\sum_{k=1}^Wz_k\right)
=\frac{\sigma_{\psi,\mathrm{LR}}^2}{W}+o(W^{-1}),
\qquad
\sigma_{\psi,\mathrm{LR}}^2=\sum_h\gamma_\psi(h).
\]
The multiplicative notation
$\sigma_{\psi,\mathrm{LR}}^2W^{-1}\{1+o(1)\}$ is valid only when
$\sigma_{\psi,\mathrm{LR}}^2>0$. For
$z_n=\epsilon_n-\epsilon_{n-1}$ the signed long-run variance is zero
while the finite-window variance is $2\sigma_\epsilon^2/W^2$.
```

### R12-C: Remark D.4.4 replacement (clamp)
```latex
\paragraph{Remark D.4.4 (clamp probability and its risk
contribution).}
Use the notation $B_n,V_n,\underline\kappa_n$ of the finite-window
proof and put
\[
r_n=
\min\{M_n(\ell_n)-M_n(\theta_{\min}),
M_n(\theta_{\max})-M_n(\ell_n)\}.
\]
If $\ell_n$ has margin $\Delta_n$ from $\partial\Theta$, then
$r_n\ge\underline\kappa_n\Delta_n$. Since
$y_n-M_n(\ell_n)=B_n+Z_n$, with
$\mathbb EZ_n=0$ and $\operatorname{Var}(Z_n)=V_n$,
\[
\mathcal E_n^c\subseteq\{|B_n+Z_n|\ge r_n\}.
\]
Therefore
\[
\mathbb P(\mathcal E_n^c)
\le\min\left\{1,\frac{B_n^2+V_n}{r_n^2}\right\}
\le\min\left\{1,\frac{B_n^2+V_n}{(\underline\kappa_n\Delta_n)^2}\right\}.
\]
If $|B_n|<r_n$, the sharper centered bound is
\[
\mathbb P(\mathcal E_n^c)
\le\min\left\{1,\frac{V_n}{(r_n-|B_n|)^2}\right\}.
\]
An exponential Bernstein bound requires a positive residual margin
$r_n-|B_n|$; it is not available merely from a positive parameter
margin when the deterministic smoothing bias can reach the boundary.

On $\mathcal E_n^c$, both the clamped estimate and the target lie in
$\Theta$, so
\[
\mathbb E\!\left[(\hat\theta_n-\ell_n)^2\mathbf1_{\mathcal E_n^c}\right]
\le D_\Theta^2\,\mathbb P(\mathcal E_n^c).
\]
This is the complete clamp-event contribution to the MSE. The
corresponding contribution to the squared bias alone is at most
$D_\Theta^2\mathbb P(\mathcal E_n^c)^2$.

For a window containing $W$ distinct, conditionally independent
Poisson counts,
\[
\mathbb P(C_k=0\ \hbox{for all }k\in W_n)
=\exp\!\left(-\sum_{k\in W_n}\lambda_k(\ell_k)\right)
\le e^{-W\lambda_-}.
\]
If a padding convention repeats observations, the sum and the
cardinality in this formula are over distinct frames after repeated
weights have been aggregated; in that case the exponent need not be
$W\lambda_-$.
```

### R12-D: Remark D.4.2 replacement (β≤1 theorem + precise obstruction above one)
```latex
\paragraph{Remark D.4.2 (the $\beta\le1$ theorem and the precise
obstruction above one).}
For $\beta\in(0,1]$, the pointwise modulus
$|\ell_k-\ell_n|\le L_a|k-n|^\beta$ and the mean value theorem give
\[
|q_k(\ell_k)-q_k(\ell_n)|\le\overline\kappa_kL_a|k-n|^\beta,
\]
so the triangle-inequality bias bound used in Theorem C is valid for
arbitrary known carriers.

For $\beta\in(1,2]$, standard smoothness has the local form
\[
\ell_k-\ell_n=v_nu_k+r_{nk},\qquad
u_k=(k-n)/N,\qquad
|r_{nk}|\le L|u_k|^\beta,
\]
rather than a pointwise modulus of order $\beta$ on the function
itself. Let $w_k$ be centered weights, $\sum_kw_ku_k=0$, and write
$q_k(t)=m_\alpha(\Lambda_0e^tb_k+d)$. Taylor's theorem gives
\[
\begin{aligned}
|B_n|\le{}&
|v_n|\left|\sum_kw_kq_k'(\ell_n)u_k\right|
+Q_1L\sum_kw_k|u_k|^\beta\\
&+Q_2\left\{v_n^2\sum_kw_ku_k^2+L^2\sum_kw_k|u_k|^{2\beta}\right\},
\end{aligned}
\tag{D.11}
\]
where $Q_1=\sup_{k,t\in\Theta}q_k'(t)$ and
$Q_2=\sup_{k,t\in\Theta}|q_k''(t)|$.

The first term in (D.11) is the load-bearing obstruction. Ordinary
centering cancels $\sum_kw_ku_k$, but it need not cancel the
carrier-weighted moment $\sum_kw_kq_k'(\ell_n)u_k$. With an
asymmetric heteroscedastic carrier this term is generally $O(W/N)$,
so an $O((W/N)^\beta)$ claim is false for $\beta>1$ under the present
assumptions.

For a constant carrier, or more generally under the
sensitivity-balance condition
\[
\left|\sum_kw_kq_k'(\ell_n)u_k\right|\lesssim (W/N)^\beta,
\]
the first term has the desired order. The remaining nonlinear term
is $O((W/N)^2)$ and is therefore no larger than $O((W/N)^\beta)$ for
$1<\beta\le2$, provided the local slope is bounded. Thus the existing
calibrated inverse does recover the $\beta$-order deterministic bias
under homogeneous or sensitivity-balanced carriers, with a constant
depending also on the slope bound and on $Q_2$.

A second-order Taylor expansion of $M_n^{-1}$ by itself does not
remove an unbalanced first moment. For arbitrary carriers, recovery
of the $\beta>1$ rate requires carrier-adapted moment conditions,
carrier-adapted local-linear weights, or a local-polynomial
likelihood fit. Theorem C therefore remains restricted to
$\beta\le1$, while the homogeneous-carrier and sensitivity-balanced
extensions above are valid weaker statements.
```

### R12-E: Gauge-invariant low-photon lower bound (replaces the minimax/Fisher paragraph)
```latex
\paragraph{Gauge-invariant low-photon lower bound.}
The loss corresponding to the unidentifiable global scale is
\[
d_{\mathrm{quot}}^2(\hat g,g)
=\inf_{a\in\mathbb R}\frac1N\|\log\hat g-\log g-a\mathbf1\|_2^2
=\frac1N\|P_N(\log\hat g-\log g)\|_2^2,
\qquad
P_N=I-\frac1N\mathbf1\mathbf1^\top.
\]
This is the centered-log-gain loss reported in Fig.~7. Multiplying
either gain profile by an arbitrary positive scalar leaves the loss
unchanged.

For the carrier-averaged model, let $B$ have a parameter-independent
known law and, conditionally on $B$, let
\[
C_k\sim\operatorname{Pois}(s_k(\theta,B_k)+d),\qquad
s_k(\theta,B_k)=\Lambda_0e^\theta B_k,
\]
independently across frames. The complete-data Fisher information
for a common log-gain parameter is
\[
I_{\mathrm{comp}}(\theta)
=\sum_{k=1}^W\mathbb E_B\frac{s_k(\theta,B_k)^2}{s_k(\theta,B_k)+d}.
\]
The observed mixed-Poisson score is the conditional expectation of
the complete-data score, so
$I_{\mathrm{obs}}(\theta)\le I_{\mathrm{comp}}(\theta)$.
For $d=0$ this becomes
\[
I_{\mathrm{comp}}(\theta)=\sum_{k=1}^W\mathbb E_Bs_k(\theta,B_k)
=W\bar\lambda.
\]

A lower bound valid for biased estimators follows directly from
Le Cam's method. Let $v\perp\mathbf1$ be a bounded contrast supported
on $O(W)$ frames and compare $\ell^{(0)}=\ell_0$ with
$\ell^{(1)}=\ell_0+\delta v$. Conditional on the carrier and with
$d=0$,
\[
\operatorname{KL}(P_0(\cdot\mid B),P_1(\cdot\mid B))
=\sum_k\lambda_{k,0}\{e^{\delta v_k}-1-\delta v_k\}
\le C\delta^2\sum_k\lambda_{k,0}v_k^2.
\]
Marginalization over the unobserved carrier cannot increase KL, hence
\[
\operatorname{KL}(P_0^C,P_1^C)\le C\delta^2W\bar\lambda.
\]
Choosing $\delta^2\asymp\min\{\delta_0^2,(W\bar\lambda)^{-1}\}$
and applying Le Cam's lemma gives the local quotient-risk bound
\[
R_{\mathrm{minimax}}\ge c\min\left\{\delta_0^2,\frac1{W\bar\lambda}\right\}.
\]
Thus the $1/(W\bar\lambda)$ law is a local-minimax statement in the
regime $W\bar\lambda\to\infty$; for bounded total information the
risk saturates at the squared diameter of the local parameter
neighborhood.

Taking a mean-zero $H_\beta(L_a)$ bump of width $W$ and amplitude
$\delta\asymp L_aW^\beta$, $0<\beta\le1$, gives
$\operatorname{KL}\lesssim L_a^2\bar\lambda W^{2\beta+1}$. The choice
$W_*\asymp(L_a^2\bar\lambda)^{-1/(2\beta+1)}$ therefore yields
\[
\inf_{\hat\ell}\sup_{\ell\in H_\beta(L_a)}
\mathbb E(\hat\ell_n^c-\ell_n^c)^2
\ge c_\beta L_a^{2/(2\beta+1)}\bar\lambda^{-2\beta/(2\beta+1)},
\]
with the usual boundary regimes when $W_*\notin[1,N]$. This is the
direct Poisson counterpart of the upper rate (D.9), and it remains
valid after averaging over an unobserved carrier because
marginalization only decreases KL.

For fixed $\alpha$, $d=0$, and uniformly small per-frame intensities,
\[
M_n'(\ell_n)=c_\alpha\bar\lambda_n\{1+o(1)\},\qquad
\operatorname{Var}(y_n)=\frac{c_\alpha^2\bar\lambda_n}{W}\{1+o(1)\},
\]
so the calibrated soft-log variance has leading constant
$1/(W\bar\lambda_n)$. Sharp minimax constants beyond this local
rare-event calculation are not claimed.

When $d>0$, every occurrence of $W\bar\lambda$ in the information
statement must instead be replaced by the effective log-gain
information $\sum_{k=1}^W\mathbb E_B\,s_k^2/(s_k+d)$; the identity
$I(\theta)=\lambda$ does not hold for log gain in the presence of
additive dark counts.
```

## Additional sound points recorded
- Centered-log projection can only DECREASE total squared error (‖P_N e‖ ≤ ‖e‖) ⇒ pointwise D.8 risks safely upper-bound the figure's integrated quotient loss; clamp × centering has no adverse interaction.
- Code's mean-normalization before log is equivalent under P_N (gauge alignment sound).
- Fisher line correctly appears only on the log-domain plot.
- F.6: Q≤0 ⇔ R_pair(0) ≥ R_rand(0) ⇒ ρ*=0 — committed wording correct; note ρ*=−log(1−Q) is an implicit fixed point unless v_blind is frozen.

## R12 closure conditions (all must land)
1. Weighted/window-average (D.8) replacement (R12-A) + either remove replicate padding in code (truncated renormalized windows) or analyze via aggregated weights.
2. R12-B replaces Remark D.4.3 (nonstationary; constant 16; additive o(W⁻¹)).
3. R12-C replaces Remark D.4.4 (residual margin; edge-window all-zero correction).
4. R12-D replaces Remark D.4.2 (carrier-weighted first-moment obstruction; salvageable partial β>1 result).
5. R12-E replaces the minimax/Fisher paragraph (d=0 scoping; finite-information truncation; direct Poisson lower bounds).
6. Fig. 7 carrier-aware arm relabeled oracle-known-carrier / flat-field; interpolation error acknowledged (certified bound or stated (ε_cal+ε_bis) term); operating-range bracket fixed or acknowledged; Fisher reference from local I_n.
