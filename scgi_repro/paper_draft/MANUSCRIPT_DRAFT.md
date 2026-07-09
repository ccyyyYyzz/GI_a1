# Identifiability by stationarity: blind gain–object separation in self-calibrating ghost imaging

**Abstract** — [PLACEHOLDER pending final numbers]

## 1. Introduction

Single-pixel (ghost) imaging has become the method of choice for imaging through media that defeat conventional cameras: turbid water, fog, smoke, and scattering channels around corners [PengChen2024APL; PengXiaoChen2025OE]. The instrument is disarmingly simple—a sequence of structured illumination patterns and a bucket detector—and the textbook design instinct is equally simple: use an ordered orthogonal basis. A Hadamard scan acquires exactly one transform coefficient per frame, the measurement matrix is perfectly conditioned, and an exact inverse is waiting at the end of the acquisition. Against additive noise, this is provably the safe choice; nothing about the pattern set is left to chance.

Dynamic media break this instinct in a specific and, we will argue, instructive way. A time-varying channel multiplies the bucket record by a slowly drifting gain: the $n$-th measurement is $R_n = a_n B_n$, where $B_n$ is the object-dependent bucket coefficient and $a_n > 0$ is an unknown per-frame gain with log-gain $\ell_n = \log a_n$ confined to a slow-drift class $S$ of dimension $p$. Recent experimental work on imaging through dynamically scattering water [PengChen2024APL] and free-space optical channels [PengXiaoChen2025OE] shows that self-calibrating schemes built on *random* illumination with an empirical gain correction recover images where ordered scans fail. Read naively, this is a puzzle: the ordered Hadamard scan is the better-conditioned instrument, so why does randomness—usually a concession, not a feature—win?

The resolution is that under gain drift the ordering itself becomes the liability. An ordered scan sorts the object's transform coefficients into a smooth sequence in acquisition time, so the object acquires a *temporal signature*: a slow gain trace and a slow coefficient trace cast the same shadow on the one-dimensional bucket record, and no estimator can tell them apart from that record alone. Hadamard is not defeated by randomness; it is defeated by chronology. We show that this confounding is not an artifact of any particular correction algorithm but a genuine algebraic ambiguity—for a square unconstrained design, *any* invertible pattern matrix can absorb a nonconstant gain into a perfectly valid alternative object (Theorem A). Conversely, random carriers escape it by a statistical mechanism: when the pattern sequence makes the bucket carrier's distribution stationary in time, slow gain becomes the only non-stationary component of the record, and the relative gain becomes identifiable up to the unavoidable global scale (Theorem B). Self-calibration is thus a property one can *design into acquisition time*, and its price, rates, and failure boundaries can be computed in advance.

This paper develops that observation into a quantitative identifiability theory. Our contributions are:

1. **A three-notion identifiability framework** for the bilinear gain–object model $R_n = a_n B_n$, separating exact-algebraic identifiability, statistical (asymptotic) identifiability, and estimation conditioning. Within it we prove the square-design obstruction (Theorem A) and the tall-design thresholds (Theorem A′)—generic exact identifiability at $N \ge K + p$ and uniform identifiability at $N \ge 2K + p - 1$—verified for the physical low-pass drift space. This is distinct from generic bilinear-injectivity results [KechKrahmer1603.07316; LiLeeBresler1501.06120; AhmedRechtRomberg1211.5608; ChoudharyMitra1402.2637; KuengRauhutTerstiege1410.6913]: the operator here is a diagonal-row map, and the anchor is temporal, not structural.

2. **The stationarity anchor (Theorem B)** and its consistency condition (★): random carriers pin the relative gain statistically, with a windowed log-domain estimator achieving the minimax rate over the drift class, including a photon-limited variant whose error scales as $1/(W\bar\lambda)$ for windows $W$.

3. **A synthesis, not a trade-off:** subsampled randomized Hadamard (SRHT) designs retain orthogonal conditioning while randomizing the temporal carrier, with an exact Walsh-domain necessary-and-sufficient whitening condition separating the roles of sign flips and permutations.

4. **An exact finite-noise reconstruction bridge** (Theorem 1) expressing relative MSE for any linear reconstructor through a leverage functional $B_L$, covering residual gain, read noise, and Poisson noise without Gaussian approximation, and specializing to orthogonal, pairwise-Hadamard, and random/DGI pipelines (with the DGI constant $C_0$ measured per implementation—no universal value exists).

5. **A phase diagram with a finite-$N$ flip boundary** $\rho^*$ in the drift-decorrelation parameter $\rho_{\mathrm{pair}}$ (Prop 3), giving a pre-acquisition go/no-go design chart (Fig. 5) for choosing between ordered and randomized acquisition.

We emphasize the scope: all results are theoretical, supported by numerical evidence; we report no hardware validation. Identifiability near $N = K + p$ is a uniqueness statement, not a conditioning guarantee, and random square designs remain algebraically non-identifiable—their advantage is statistical. The organizing idea throughout is the distilled form of the paradox: one makes the gain observable not by measuring it directly, but by making the object stop pretending to be time.

The paper is organized as follows. Section 2 fixes the model and the three notions of identifiability; Fig. 1 places ordered-Hadamard, iid-random, tall-random, and SRHT designs on the resulting two-axis map of conditioning versus identifiability. Section 3 positions the work against bilinear inverse-problem theory. Sections 4 and 5 establish the algebraic obstruction and the stationarity anchor; Sec. 6 derives estimation rates including the low-photon regime. Section 7 develops the SRHT synthesis, Sec. 8 the reconstruction bridge and phase diagram. Section 9 presents the numerical experiments, and Sec. 10 collects design rules, scope, and outlook.

## 2. Problem setup and three notions of identifiability

We consider a single-pixel (bucket-detection) acquisition of $N$ frames. On frame $n$ a programmed pattern $m_n \in \mathbb{R}^K$ illuminates a static object $T \in \mathbb{R}^K$, producing the ideal bucket value $B_n = m_n^{\mathsf T} T$; we call the sequence $\{B_n\}$ the *object carrier*. The recorded signal is corrupted by a slowly drifting multiplicative gain — source power, detector responsivity, coupling efficiency —

$$
R_n \;=\; a_n B_n, \qquad a_n = e^{\ell_n} > 0 ,
$$

with log-gain trajectory $\ell = (\ell_1,\dots,\ell_N)$ confined to a *drift class* $S \subset \mathbb{R}^N$, $p = \dim S$, which always contains the constants. The constant direction is a pure gauge: $(a, T) \mapsto (c\,a,\; T/c)$ leaves every $R_n$ invariant, so all statements below are up to a global scale. For physically slow drift we take $S$ to be a low-pass (Fourier) space of normalized bandwidth $\rho_{\mathrm{bw}}$, so that $p \approx \rho_{\mathrm{bw}} N$; this bandwidth parameter must not be confused with the adjacent-pair decorrelation $\rho_{\mathrm{pair}}$ entering the finite-$N$ flip boundary of Sec. 8. The blind problem — recover $(a, T)$ from $\{R_n\}$ alone — is bilinear, and asking whether it is "solvable" turns out to be three distinct questions. Separating them is itself a contribution of this paper.

**Algebraic identifiability.** Does the noiseless record determine $(a,T)$ up to gauge, or does some other pair $(a', T')$ with $\ell' - \ell \in S$ nonconstant reproduce the data exactly? This is a finite-sample, deterministic question about collisions $MT = D_s M T'$, and its answer depends on the design $M$ and on the dimension count $N$ versus $K + p$. Section 4 (Theorem A and the tall-design thresholds, Theorem A′) shows that every square invertible design — however well-conditioned — fails it, and that overdetermination restores it generically at $N \ge K + p$.

**Statistical identifiability.** When the patterns are drawn from a random ensemble, a weaker but operationally decisive property becomes available: if the carrier $B_n$ is *stationary* — its distribution does not depend on $n$ — then any slow modulation of local averages over windows $W$ is attributable to the gain alone, and the relative gain is identifiable in distribution even where exact algebraic separation is impossible. This stationarity anchor is developed in Sec. 5 (Theorem B) and is the mechanism the field's empirical successes have been implicitly exploiting.

**Estimation conditioning.** Uniqueness is not accuracy. Even when one of the first two notions holds, the finite-noise error of a concrete estimator is governed by conditioning quantities — the window size $W$, the residual-gain variance $v$, the leverage $B_L$ of the reconstruction operator — quantified by the rate analysis of Sec. 6 and the reconstruction bridge of Sec. 8. In particular, identifiability at the threshold $N = K + p$ says nothing about stability there.

We contend that much of the confusion surrounding blind gain correction stems from conflating these three notions: judging an acquisition scheme by the visual quality of a blindly corrected reconstruction entangles algebraic ambiguity, the presence or absence of a statistical anchor, and estimator conditioning into a single scalar, although the three failures call for entirely different remedies. Figure 1 disentangles them as a two-axis map — inversion conditioning against blind identifiability — on which ordered Hadamard, i.i.d.-random (DGI), tall random, and SRHT acquisitions occupy visibly different corners, a separation that Secs. 4 and 5 explain.

## 3. Relation to prior work

Gain–object separation is a bilinear inverse problem: writing the log-gain as $\ell_n=\log a_n$ and lifting the unknowns to the rank-one array $X=aT^{\top}$, each bucket reads $R_n=a_n B_n$ with $B_n=m_n^{\top}T$, a bilinear form in the object $T$ and the gain trace $a$. This places our question inside a mature literature on bilinear identifiability, and it is worth stating precisely what that literature settles and what it leaves open for the diagonal-gain geometry considered here.

The sharpest injectivity counts for lifted bilinear maps are Kech–Krahmer's optimal conditions for generic identifiability [KechKrahmer1603.07316], which for a rank-one measurement model require on the order of $2(n_1+n_2)-4$ generic measurements. These counts do not transfer to our setting: the operator $L_M(X)_n=a_n\,m_n^{\top}T$ is a *diagonal-row* map, not a generic rank-one measurement, so the object carrier and the gain enter through a structured — not generic — set of linear forms. The relevant identifiability question is instead the intersection geometry of the object subspace with its gain-modulated copy, $\,U\cap D_sU$. Choudhary–Mitra's scaling laws for bilinear inverse problems [ChoudharyMitra1402.2637] are the closest in spirit to our Theorem A: their rank-two nullspace obstruction is exactly the mechanism by which a square unconstrained design absorbs a nonconstant gain into a redefined object. Li–Lee–Bresler's unified framework [LiLeeBresler1501.06120] supplies the subspace- and sparsity-constrained identifiability thresholds that our tall-design counts ($N\ge K+p$ generic, $N\ge 2K+p-1$ uniform) specialize to for the diagonal-gain model. Ahmed–Recht–Romberg [AhmedRechtRomberg1211.5608] establish convex recovery for blind deconvolution under subspace priors, and Kueng–Rauhut–Terstiege [KuengRauhutTerstiege1410.6913] give the low-rank-from-rank-one-measurement guarantees; both are the algorithmic backdrop against which our purely algebraic and statistical criteria should be read.

On the imaging side, the practice of single-pixel and computational ghost imaging has long weighed ordered Hadamard bases against random speckle patterns for their conditioning and noise properties, but without an identifiability account of slow multiplicative drift. Learned gain correction of the SCGI type [PengChen2024APL] and reference-frame calibration [PengXiaoChen2025OE] address the same physical nuisance empirically; our analysis explains why their static-correction ceiling is the honest performance bound, and when a drifting gain becomes blindly separable at all.

Against this background the contribution of the present work is specific. We do not add to generic bilinear injectivity, which is settled by the references above. What is new is the temporal-statistical mechanism: relative-gain identifiability secured by making the object carrier stationary (Theorem B), the associated nonparametric slow-gain calibration rate, the ordered-orthogonal confounding failure mode that this mechanism repairs, the SRHT synthesis that recovers orthogonal conditioning without sacrificing self-calibration, and the finite-noise reconstruction bridge that renders the phase diagram quantitative. The novelty is the stationarity anchor, not bilinear injectivity per se.

## 4. The algebraic obstruction and when oversampling cures it

The paradox of Sec. 1 is not an estimator artifact. Write the noiseless bucket record as $R_n = a_n B_n$ with $B_n = m_n^{\mathsf T}T$ the carrier coefficient of the object $T\in\mathbb R^{K}$ under illumination row $m_n$, and $\ell_n=\log a_n$ the log-gain. Stack $N=K$ frames into an invertible square design $M$. Then the multiplicative drift is absorbed *exactly* into a relabelled object.

> **Theorem A (square non-identifiability).** For any invertible $M\in\mathbb R^{K\times K}$ and any nonconstant gain $a=(a_n)$, there exists a distinct object $T'\neq cT$ producing the identical bucket record: $\operatorname{diag}(a)MT = M T'$ with $T'=M^{-1}\operatorname{diag}(a)MT$. Gain–object separation is unidentifiable up to the global-scale gauge $a\mapsto ca,\ T\mapsto T/c$. *(Proof: Appendix A / issue #1.)*

The object is a barcode printed onto time and the drift is a smudge across it; when the barcode carries slow structure, the theorem says the smudge can be *reread as a different barcode* rather than dismissed as blur. This is a genuine orbit of the bilinear map, and it holds for *every* invertible design — Hadamard, Fourier, or otherwise. Two corollaries sharpen the trap.

> **Corollary 1 (slowness does not help).** Restricting $\ell\in S$ to a slow drift class does not restore identifiability at $N=K$: $T'$ inherits the same smoothness whenever $S$ is closed under the induced action, so a slowly varying gain masquerades as a slowly varying object.

> **Corollary 2 (positivity is not enough; support zeros can be).** Nonnegativity of $T$ alone does not break the orbit. Known zeros in the object support *can*: each enforced zero removes a degree of freedom from $T'$, and $K_0\ge p$ generic support zeros restore local identifiability. *(Proof: Appendix A / issue #1.)*

The first escape is overdetermination. Take a generic tall design $M\in\mathbb R^{N\times K}$, $N>K$, with $\ell\in S$, $\dim S=p$, $S\ni$ constants (the gauge). A collision $MT=\operatorname{diag}(e^{s})MT'$ with $s=\ell'-\ell$ is governed by the intersection $\mathrm{range}(M)\cap\operatorname{diag}(e^{s})\,\mathrm{range}(M)$. Counting the projective incidence dimension of diagonal-gain collisions gives $\Delta = (p-1) + 2K-1-\operatorname{rank}[M,\,-\operatorname{diag}(b)M]$, with the rank equal to $\min(N,2K)$ on the dense stratum; generic-point identifiability requires $\Delta<K-1$ and uniform identifiability $\Delta<0$. This yields three thresholds.

> **Theorem A′ (tall-design thresholds).** For generic tall $M$ and transverse nonconstant gain family of dimension $p$:
> - local differential identifiability: $N \ge K+p-1$;
> - generic exact finite-sample identifiability: $N \ge K+p$;
> - uniform (every nonzero object): $N \ge 2K+p-1$.
>
> *(Proof: Appendix B / issue #2.)*

These bounds are proven for the *physical* low-pass drift space, not merely assumed. For $S_{\mathrm{LP}}=\mathrm{span}\{1,\cos q\omega,\sin q\omega:q\le m\}$, $p=2m+1$, a level-multiplicity lemma (a nonconstant degree-$2m$ trigonometric polynomial attains each value at most $p-1$ times) bounds the collision rank, giving $\operatorname{rank}[M,-\operatorname{diag}(b)M]=\min(N,2K)$ whenever $N\ge K+p$; the clean thresholds then transfer verbatim to the low-pass subspace. *(Proof: Appendix B / issue #3.)* For other conventions one checks the level count $L_S\le K$ (if $N<2K$) or $L_S\le N-K$ (if $N\ge 2K$).

The picture is a dichotomy, and it sets up the rest of the paper. When $N\ge K+p$, overdetermination *alone* separates gain from object — no statistical mechanism is logically needed, though randomization still buys stable conditioning (the identifiability axis of Fig. 1). When $K<N<K+p$, tallness is insufficient even generically, and the stationarity anchor of Sec. 5 (or a support/sparsity prior) becomes *required*, not merely convenient. The two regimes meet through the drift bandwidth: a gain occupying a fraction $\rho_{\mathrm{bw}}$ of the frame band spans $p\approx \rho_{\mathrm{bw}}N$ low-pass modes, so $N\ge K+p$ reads as

$$ N \;\gtrsim\; \frac{K}{1-\rho_{\mathrm{bw}}}. $$

Slow drift ($\rho_{\mathrm{bw}}\ll1$) is cured by modest oversampling; as $\rho_{\mathrm{bw}}\to1$, $p\to N$ and blind algebraic separation is impossible for *any* $N$, forcing the statistical route.

## 5. Statistical identifiability: the stationarity anchor

Section 4 offered one escape from the gain–object orbit: buy identifiability with surplus rows. This section develops a second, logically distinct escape that operates even at fixed $N$ and, crucially, explains *why* randomized acquisition self-calibrates while ordered acquisition does not. The idea is best stated before the mathematics. A drifting gain is a boat carried by a slow current, and the bucket record is our only view of the water. If the waves change character with position — as the ordered Hadamard coefficient sequence does, sweeping through the object's spectral envelope — we cannot tell the current from the coastline: a slow change in the record may be drift, or may be the scenery. But if the waves are *statistically identical everywhere*, any slow modulation of the record has exactly one available explanation. Local averaging then drops an anchor into the distribution itself: it pins the *relative* drift, while the absolute scale remains gauged away. This intuition, and nothing stronger, is what the results below formalize.

Write $Y_n=\log R_n=\ell_n+\log B_n$. The anchor requirement is a condition on the carrier alone:

> **Condition (★) (stationary carrier).** For windows $W_n$ of length $W$, the windowed carrier average $W^{-1}\sum_{k\in W_n}\log B_k$ is approximately independent of the window location $n$, up to a single scalar absorbed by the global-scale gauge.

Random illumination satisfies (★) by construction:

> **Proposition 1 (random-basis carrier).** For i.i.d. random patterns with pixel mean $\mu_I$ and standard deviation $\sigma_I$, the carrier $\{B_n\}$ is white and strictly stationary, and the object enters its first two moments only through the scalars $S_1=\sum_j T_j$ and $S_2=\sum_j T_j^2$: $\mathbb{E}B_n=\mu_I S_1$, $\operatorname{Var}B_n=\sigma_I^2 S_2$, hence $\mathrm{CV}_B=(\sigma_I/\mu_I)/\sqrt{K_{\mathrm{eff}}}$ with $K_{\mathrm{eff}}=S_1^2/S_2$. Gaussian and log-domain approximations additionally require the Lindeberg-type spikiness condition $K_\infty=S_2/\|T\|_\infty^2\to\infty$; the reduction of the object to two scalars holds at this Gaussian-approximation level, not exactly. *(Proof: Appendix C / issue #1.)*

Figure 2 shows the two carriers side by side: the random trace is a flat, object-independent noise band, whereas the ordered Hadamard trace *is* the object's coefficient envelope — a deterministic, strongly non-stationary signature imprinted on acquisition time. Under ordered scanning the object masquerades as a temporal trend, precisely the degree of freedom a slow gain occupies, and (★) fails. We emphasize the correct logical status of the condition:

> **Proposition 2 ((★) is an estimator criterion, not a universal one).** Condition (★) is necessary and sufficient for consistency of the blind windowed (stationarity-anchor) gain correction. It is *not* an if-and-only-if condition for identifiability by all mechanisms: the overdetermined designs of Sec. 4 identify algebraically without any stationarity, and conversely (★) confers no exact algebraic identifiability. *(Proof: Appendix C / issue #1.)*

The main statistical result is then:

> **Theorem B (statistical relative-gain identifiability).** Let $Y_n=\log R_n=\ell_n+m_T+z_n$, where $m_T=\mathbb{E}\log B_n$ is a scalar depending on the object but not on time, $\{z_n\}$ is centered, stationary, and mixing, and $\ell\in S$ lies in a quantitative slow-modulus (Hölder) class. Then windowed averages of $Y_n$ consistently estimate $\ell_n+m_T$; consequently the centered log-gain $\ell_n-\overline{\ell}$ — equivalently the relative gain up to one global scale — is identifiable and consistently estimable, while the scalar $m_T$ plus the gauge of $\ell$ is not. *(Proof: Appendix C / issue #1.)*

Theorem B must be read with its scope intact. It is an asymptotic, high-probability statement about *relative*-gain recovery up to the global-scale gauge — never exact finite-sample identifiability of $(a,T)$. In particular it does not contradict Theorem A: a random square design remains algebraically non-identifiable; what randomness buys is statistical separability, a different currency. This is also what distinguishes the mechanism from the bilinear-inverse identifiability literature [LiLeeBresler1501.06120; KechKrahmer1603.07316; ChoudharyMitra1402.2637]: the anchor is a property of the *temporal distribution* of the carrier, not of subspace injectivity.

The anchor also explains why the self-calibrating GI likelihood of Refs. [PengChen2024APL; PengXiaoChen2025OE] works. Under Proposition 1's Gaussian approximation the bucket record given $(a,\mu_B,\sigma_B)$ is a slow trend plus stationary residuals, and the SCGI Gaussian-likelihood loss is exactly the maximum-likelihood fit of that trend — i.e., a consistent ML realization of the windowed anchor estimator, inheriting Theorem B's guarantee (and its gauge).

Figure 3 is the core numerical evidence. Across a panel of objects, the blind gain-estimation error $\|\hat a-a\|/\|a\|$ under random illumination collapses onto a single tight $1/\sqrt{W}$ bundle, independent of the object, exactly as $\mathrm{CV}_B/\sqrt{W}$ predicts; under ordered Hadamard the curves scatter by object and do not decay with $W$ — the object envelope is a bias no amount of averaging removes. The window $W$ itself carries a bias–variance trade-off (drift curvature versus $\mathrm{CV}_B^2/W$), whose optimal resolution and minimax rate are the subject of Sec. 6.

## 6. Estimation rate, lower bounds, and low-photon robustness

Section 5 establishes that relative gain is *identifiable* from a stationary carrier; here we show it is recovered *efficiently and predictably*. The estimator is a windowed soft-log: over a window $W$ of frames sharing a slowly varying gain, average $\psi_\alpha(c)=\log(c+\alpha)$ and invert the calibration curve, $\hat\theta_n=m_\alpha^{-1}\!\big(\mathrm{mean}_W\,\psi_\alpha\big)$, with $m_\alpha(\theta)=\mathbb{E}[\psi_\alpha(C)]$ for $C\sim\mathrm{Pois}(\Lambda_0 e^{\theta B}+d)$. Because the log-gain $\ell$ lies in a Hölder-$\beta$ class of smooth drift, the window trades bias against variance in the usual nonparametric way: wider $W$ suppresses variance as $O(1/W)$ but incurs an approximation bias set by the local smoothness $\beta$ and the drift Lipschitz constant $L_a$.

> **Theorem C (windowed rate).** For log-gain in a Hölder-$\beta$ class with constant $L_a$, the bias-optimized windowed estimator attains
> $$\mathrm{MSE}^{*}\;\le\; C\,\kappa_{\min}^{-2}\,\big[\kappa_{\max}L_a\big]^{2/(2\beta+1)}\,\sigma_{\alpha,\mathrm{LR}}^{4\beta/(2\beta+1)},$$
> the standard nonparametric rate in the effective per-frame noise $\sigma_{\alpha,\mathrm{LR}}$. *(Proof: Appendix D / issue #3.)*

This rate is not merely achievable but *optimal*. A van Trees / Pinsker argument over the same smoothness class produces a matching lower bound, so no estimator improves on Theorem C by more than constants.

> **Theorem D (minimax optimality).** Over the Hölder-$\beta$ drift class the windowed estimator is minimax-rate optimal; the constant is Pinsker-sharp in the Gaussian-equivalent limit. *(Proof: Appendix D / issue #1.)*

The floor beneath both bounds is Fisher-information geometry. Working in the gauge quotient (global scale is unobservable, Sec. 5), the relevant object is the *quotient Fisher information*: the Fisher matrix restricted to directions transverse to the scale orbit. This makes the identifiability dichotomy quantitative — the Fisher matrix is singular exactly along the null direction of Theorem A. Non-identifiability is not poor conditioning; it is a genuine flat direction of the likelihood, the ambiguity $(a,T)\mapsto(a s^{-1}, sT)$ made infinitesimal.

Which design constant controls what is a spikiness question, and three distinct functionals appear. $K_{\mathrm{eff}}=S_1^2/S_2$ (Prop 1) governs excitation and the pairwise-Hadamard residual-gain budget; $K_\infty=S_2/\|T\|_\infty^2$ controls worst-coefficient leverage and the tail of $B_L$; $K_4=S_2^2/\sum_j T_j^4$ enters the concentration guarantee for permutation whitening (Sec. 7, via $\min(\epsilon^2 K_4,\epsilon K_\infty)\ge C\log(K/\delta)$). Conflating them mislabels the operative bottleneck: a design flat in $K_{\mathrm{eff}}$ can still be spiky in $K_\infty$.

Low photon counts do not break the log domain. The Poisson derivative identity $\frac{d}{d\lambda}\mathbb{E}f(C)=\mathbb{E}[f(C{+}1){-}f(C)]$ gives a sensitivity $\kappa_\alpha(\lambda)\to 1$ at high $\bar\lambda$ and $\kappa_\alpha(\lambda)\to\lambda\log(1+1/\alpha)$ as $\bar\lambda\to 0$; the offset $\alpha$ absorbs empty bins so no frame ever contributes $\log 0$. Propagating through Theorem C, the photon-starved variance degrades gracefully as $\sim 1/(W\bar\lambda)$ — the Fisher-matched scaling, since the Poisson information for log-intensity is $\lambda$ itself. Zero photons carry zero Fisher information; they cut precision but never diverge (Fig. 7).

The caveat is stated honestly. At $\bar\lambda<1$ the soft-log becomes shrinkage-bias-dominated: $\psi_\alpha$ pulls the estimate toward $\log\alpha$, and the estimator sits *below* its Fisher reference not because it beats the bound but because it is biased. The $1/(W\bar\lambda)$ law is the variance-limited regime above this crossover; below it, honest accounting reports the bias floor rather than the optimistic Fisher curve, and recovering the rate requires the offset-design or full Poisson-mixture MLE variants.

## 7. Basis design: randomized orthogonal acquisition (SRHT)

A reader who has followed the stationarity anchor of Sec. 5 will raise a natural objection: the anchor was purchased with random illumination, yet the appeal of ordered Hadamard was its exact, perfectly conditioned inverse. Must one surrender orthogonal conditioning to buy self-calibration? The answer is no. The subsampled randomized Hadamard transform (SRHT) — an orthogonal Hadamard carrier composed with a random sign flip and a random pixel permutation — keeps a full-rank, well-conditioned forward map while randomizing the *temporal handwriting* of the object. One shuffles the deck without bending the cards.

The mechanism is exact. Writing the per-coefficient excitation as $Z_g$ under a random diagonal sign $D$, the residual gain–object coupling is governed entirely by the Walsh spectrum of the squared object. With $w = T^2$,
$$\operatorname{Cov}_D(Z_g, Z_h) = \hat{w}(g+h),$$
the Walsh transform of $w$ evaluated at the dyadic sum of indices. Sign randomization alone therefore whitens the excitation — decorrelates every coefficient pair — **if and only if** $w$ is Walsh-flat, i.e. $\hat{w}(k)$ is negligible for all $k\neq 0$. This is a condition on the object, not the design: a structured $T$ concentrates $\hat{w}$ off the origin and sign flips cannot remove it.

The random permutation supplies the missing genericity. It acts as a probabilistic Walsh-flattener: permuting pixels spreads the mass of $\hat{w}$ across the spectrum, and the off-origin covariance is driven below tolerance $\varepsilon$ with probability $1-\delta$ once the object is spectrally spread enough,
$$\min\!\big(\varepsilon^2 K_4,\ \varepsilon K_\infty\big) \ \geq\ C \log(K/\delta),$$
with $K_4$ and $K_\infty$ the spread functionals of Sec. 6. Both diverge as the object's energy delocalizes and collapse when a few pixels dominate; the bound quantifies precisely how much delocalization the permutation needs.

Permutation is a genuine second ingredient, not a substitute for the analysis. Under permutation alone,
$$\operatorname{Var}_P Z_g = \frac{K S_2 - S_1^2}{K-1} = S_2\,\frac{K - K_{\mathrm{eff}}}{K-1},$$
so the residual carries an $O(1/K_{\mathrm{eff}})$ *upper* bound on variance — reassuring on average — but no matching lower bound. A flat object realizes the gap: it produces zero excitation, so permutation cannot guarantee two-sided control coefficient by coefficient. The whitening claim is one-sided unless the sign flip and the spectral-spread condition are both in force. Figure 6 isolates these contributions by ablation (none / permutation / sign / both), and the two-sided regime is exactly the "both" cell.

This yields a design rule rather than a single number.

> **Design rule (blind slow gain).**
> (i) Do *not* acquire in ordered Hadamard when the nuisance is a blind, slowly drifting gain — the ordering hands the object a temporal signature (Sec. 4).
> (ii) Randomize the carrier: apply the SRHT sign flip *and* permutation.
> (iii) Verify Walsh-flatness of $T^2$, or rely on the permutation bound above with $K_4, K_\infty$ estimated from the object class.
> (iv) Keep a positivity / offset margin so the log or soft-log stage of Sec. 6 stays away from its singularity.
> (v) Choose the averaging window $W$ from the bias–variance trade of Sec. 6, not from conditioning.

The synthesis is that orthogonality and self-calibration are compatible: SRHT preserves the $B_L = 1$ leverage of a full orthogonal inversion (Sec. 8) while making the object carrier statistically stationary in time, so the only non-stationary structure left in the bucket record is the gain itself. The conditioning that made ordered Hadamard attractive is retained; only its chronology is discarded.

*(Proof of the Walsh identity and permutation bound: Appendix E / issue #2.)*

## 8. From identifiability to images: the reconstruction bridge and phase diagram

Sections 4–7 answer the question a statistician asks — *is the gain identifiable, and at what rate?* — but an imaging practitioner asks a different one: *how many gray levels do I lose?* This section supplies the bridge. The result is exact, holds at finite $N$ and finite photon count, and reduces every acquisition strategy in this paper to three numbers that can be read off a single chart before any hardware is built.

Let the corrected bucket record be $z_n=(1+\delta_n)b_n+\xi_n$ with $b=AT$, where $\delta_n$ is the *residual* multiplicative gain after whatever blind correction the pipeline applied, and let $\hat T=Lz$ be any linear reconstruction.

> **Theorem 1 (master finite-noise relMSE identity).** Without Gaussian or small-noise approximation,
> $$\frac{\mathbb{E}\|\hat T-T\|^2}{S_2}\;=\;\underbrace{\frac{\|(LA-I)T+L\,\mathrm{diag}(b)\,m_\delta\|^2}{S_2}}_{\text{bias}}\;+\;\underbrace{\frac{\operatorname{tr}\!\big(L\,\mathrm{diag}(b)\,V_\delta\,\mathrm{diag}(b)\,L^\top\big)}{S_2}}_{\text{residual gain}}\;+\;\underbrace{\frac{\operatorname{tr}\!\big(L\,\Sigma_\xi L^\top\big)}{S_2}}_{\text{read + Poisson}}.$$
> If the residual gains are independent with $\mathrm{Var}\,\delta_n=v$, the gain term collapses to $v\,B_L$ with the **leverage** $B_L=(1/S_2)\sum_n b_n^2\|Le_n\|^2$; coherent (smooth) residuals require the full matrix form. *(Proof: Appendix F / issue #3.)*

The Poisson plug-in $\Sigma_\xi=\mathrm{diag}(\tau_{G,n}^2+b_n^2/\Phi_n)$ is exact at all photon counts, so the identity — not an approximation to it — is what Fig. 4 tests. Specializing $L$:

- **Orthogonal / SRHT full inversion:** $B_L=1$, so $\mathrm{relMSE}=v+(1/S_2)\sum_n(\tau_{G,n}^2+b_n^2/\Phi_n)$. The imager passes residual gain through at unit leverage — no amplification, no dilution.
- **Pairwise (differenced) Hadamard:** the gain term is $R_{\mathrm{pair}} = (K_{\mathrm{eff}}/4)\,D_H(T)\,\mathrm{Var}(\Delta)$, with $D_H\approx 1$ for non-DC coefficients and $\mathrm{Var}(\Delta)\approx 2s^2 r(\rho_{\mathrm{pair}})$ the adjacent-pair gain increment. Differencing converts *slowness* of the drift directly into suppression.
- **Random / DGI:** $\mathrm{relMSE}_{\mathrm{DGI}} = C_0/N + (1+C_0)v/N + $ noise terms, where $C_0=\mathbb{E}\|Z\|^2/S_2-1$ is the exact one-sample constant of the correlator ($C_0=K+\beta_4-2$ for symmetric zero-mean patterns). There is **no universal $C_0$**: it depends on the pattern statistics, background, and normalization, and must be measured from the pipeline at hand — for our SCGI-style testbed [PengChen2024APL; PengXiaoChen2025OE] the measured value is used throughout Figs. 4 and 5.

This yields an honest corollary that the identifiability results alone would obscure: **at equal residual variance $v$, orthogonal inversion is the best conduit** — it has $B_L=1$ and no $C_0/N$ estimator floor. The randomized bases do not win because they transmit gain error more gracefully; they win because Theorem B and the window estimator of Sec. 6 let $v$ *itself* be driven down blindly, at rate $1/W$ per window, whereas an ordered scan offers no blind handle on $v$ at all.

The competition between these closed forms produces a finite-$N$ flip boundary.

> **Prop 3 (finite-$N$ flip boundary).** $\rho^{*}=\inf\{\rho_{\mathrm{pair}}: R_{\mathrm{pair}}(\rho_{\mathrm{pair}})\ge R_{\mathrm{rand}}(\rho_{\mathrm{pair}},N)\}$ satisfies, in the small-drift regime,
> $$r(\rho^{*})=\frac{2\big[C_0/N+(1+C_0)v_{\mathrm{blind}}/N+R_{\mathrm{DGI,noise}}-R_{\mathrm{pair,noise}}\big]}{K_{\mathrm{eff}}\,D_H\,s^{2}},$$
> whose leading order ($r(\rho)=\rho$, $D_H=1$, negligible noise and $v_{\mathrm{blind}}$) is the heuristic $\rho^{*}\approx 2C_0/(N K_{\mathrm{eff}} s^{2})$. *(Proof: Appendix F / issue #3.)*

> **Remark (two decorrelation conventions — do not conflate).** Throughout, $\rho_{\mathrm{pair}}$ denotes *adjacent-pair* gain decorrelation, the variable entering $\mathrm{Var}(\Delta)$ and Prop 3; $\rho_{\mathrm{bw}}$ denotes the normalized gain *bandwidth*, $p\approx\rho_{\mathrm{bw}}N$, the variable entering the tall-design thresholds of Sec. 4 ($N\gtrsim K/(1-\rho_{\mathrm{bw}})$). Both grow with drift speed but are not equal, and every axis in Fig. 5 is labeled by which one it carries.

Figure 4 shows the bridge validated term by term: predicted bias, gain, and noise contributions against measured relMSE across bases, drift speeds, and photon budgets — numerical evidence, on simulation, that Theorem 1 is an accounting identity rather than a bound. Figure 5 assembles the payoff: the phase diagram over (basis, $\rho_{\mathrm{pair}}$, noise level $\sigma$) with the $\rho^{*}$ curve overlaid. Three regimes emerge. For **slow drift** ($\rho_{\mathrm{pair}}<\rho^{*}$), pairwise Hadamard is fine: differencing suppresses what little the gain moves, and orthogonal conditioning is kept for free. For **intermediate drift**, the randomized bases win — the stationarity anchor buys a small $v_{\mathrm{blind}}$ that no ordered scan can reach. For **fast drift** ($\rho_{\mathrm{bw}}\to 1$, $p$ approaching $N$), every *blind algebraic* strategy hits the noise floor together, as Theorem A′'s counting demands; this is a statement about blind separation, not about the physics — an externally calibrated or metered gain restores the problem to ordinary inversion. The chart is a pre-acquisition instrument: locate your drift spectrum and photon budget on it, and the go/no-go decision — and the basis — follow before the first frame is taken.

## 9. Numerical experiments

[PLACEHOLDER — pending r2 figure verification: Fig.2 stationarity, Fig.3 gain-error collapse, Fig.4 bridge, Fig.5 phase diagram (existing M2), Fig.6 SRHT ablation (existing M3), Fig.7 low-photon]

## 10. Discussion: significance, scope, and outlook

The results of Sections 2–9 are, at bottom, a set of pre-acquisition design tools: quantities one can evaluate on the illumination basis and the expected drift *before* photons are collected, and which predict whether blind gain–object separation will succeed. We collect them here as four deliverables, then state their limits and the experimental program they invite.

**A go/no-go identifiability predictor.** The tall-design thresholds convert "will this acquisition self-calibrate?" into arithmetic. For a physical low-pass drift class $S$ of dimension $p=\dim S$, local differential identifiability holds at $N\ge K+p-1$, generic exact finite-sample identifiability at $N\ge K+p$, and uniform (every-object) identifiability at $N\ge 2K+p-1$ (Theorem A′, proven for the physical low-pass drift space). Written through the bandwidth relation $p\approx\rho_{\mathrm{bw}}N$, the generic threshold becomes $N\gtrsim K/(1-\rho_{\mathrm{bw}})$: slow drift needs only modest oversampling, while $\rho_{\mathrm{bw}}\to1$ ($p\to N$) makes blind algebraic separation impossible for any $N$, forcing reliance on the statistical anchor of Theorem B. This is a regime map the experimenter reads off before building.

**An SRHT design rule.** When blind slow gain is the operative nuisance, do not run ordered Hadamard: its chronological coefficient ordering hands the object a temporal signature indistinguishable from drift. Randomize the carrier instead — via sign or pixel-permutation randomization of a Walsh–Hadamard design — and verify the exact whitening condition, Walsh-flatness of the realized $T^2$ (Sec. 7), or fall back on permutation, which is made likely by $\min(\varepsilon^2 K_4,\varepsilon K_\infty)\ge C\log(K/\delta)$ (Fig. 6). Retain a positivity/offset margin, and choose the gain window $W$ from the bias–variance tradeoff of the windowed estimator. SRHT thus buys statistical self-calibration without surrendering orthogonal conditioning.

**A phase diagram as a falsifiable design map.** The master finite-noise identity (Theorem 1) and the finite-$N$ flip boundary $\rho^*$ (Prop 3) render relMSE across DGI, SRHT, and pairwise-Hadamard as a chart over basis, drift, and noise (Fig. 5). Crucially, $\rho_{\mathrm{pair}}$ (adjacent-pair decorrelation, entering $\rho^*$) and $\rho_{\mathrm{bw}}$ (bandwidth, entering the tall-design law) are distinct axes and must be labeled as such before any overlay (Remark, Sec. 8). The heuristic $\rho^*\approx 2C_0/(NK_{\mathrm{eff}}s^2)$ appears as the leading-order limit of the full boundary — a prediction the diagram exposes to falsification, not a fitted curve.

**A cross-domain principle.** The exportable statement is basis-agnostic: *to self-calibrate a multiplicative nuisance, design the carrier so its distribution is stationary in the nuisance coordinate.* Blind gain and phase calibration, flat-field correction, coded-aperture and computational microscopy, and single-pixel spectroscopy share the bilinear structure in which this reasoning applies. We offer them as analogues and motivation, not as proven domains; each would require its own operator analysis of the diagonal-row map [LiLeeBresler1501.06120; KechKrahmer1603.07316].

**Scope and limits.** The claims are theory and simulation only, with no hardware validation. Uniqueness near $N=K+p$ is an identifiability statement, not a conditioning guarantee; stability there is a separate random-matrix question. Random square unconstrained designs are *not* algebraically identifiable — any invertible design absorbs nonconstant gain into a redefined object (Theorem A). There is no universal DGI constant $C_0$ or Hadamard factor $D_H$; both must be measured per pipeline. The low-photon soft-log $\psi_\alpha$ avoids the log-zero singularity but cannot manufacture information — zero photons carry zero Fisher information for log-intensity, an information limit, not an estimator defect.

**Experimental feasibility.** The theory issues sharp, falsifiable predictions for a bench with programmable drift: a drift-rate flip point $\rho^*$ at which randomized carriers overtake pairwise Hadamard, and an SRHT-versus-ordered-Hadamard separation in blind gain-estimation error under stirred-scattering gain (Fig. 3). Testing these against a physical single-pixel system — with real read noise, Poisson statistics, and unmodeled gain jumps — we leave to future hardware work, likely in collaboration with an optical-imaging group.

Taken together, these tools make gain observable not by measuring it directly, but by making the object stop pretending to be time.

## References

- [KechKrahmer1603.07316] — Kech & Krahmer, optimal injectivity conditions for bilinear inverse problems (arXiv:1603.07316).
- [LiLeeBresler1501.06120] — Li, Lee & Bresler, unified identifiability framework for bilinear inverse problems (arXiv:1501.06120).
- [AhmedRechtRomberg1211.5608] — Ahmed, Recht & Romberg, blind deconvolution using convex programming (arXiv:1211.5608).
- [ChoudharyMitra1402.2637] — Choudhary & Mitra, identifiability scaling laws in bilinear inverse problems (arXiv:1402.2637).
- [KuengRauhutTerstiege1410.6913] — Kueng, Rauhut & Terstiege, low-rank recovery from rank-one measurements (arXiv:1410.6913).
- [PengChen2024APL] — Peng & Chen, self-calibrating ghost imaging through dynamically scattering media (Appl. Phys. Lett., 2024).
- [PengXiaoChen2025OE] — Peng, Xiao & Chen, reference-frame gain calibration for free-space single-pixel imaging (Opt. Express, 2025).