# Appendices

Appendix A supports Sec. 4 (Theorem A and Corollaries 1-2); Appendix B supports Sec. 4 (Theorem A′, low-pass lemmas); Appendix C supports Sec. 5 (Propositions 1–2, condition (★), Theorem B); Appendix D supports Sec. 6 (Theorems C-D, Fisher geometry, low-photon); Appendix E supports Sec. 7 (SRHT Walsh condition, permutation bounds); Appendix F supports Sec. 8 (Theorem 1, specializations, Prop 3).
Heuristic or genericity steps are labeled as such inside each proof; every appendix ends its theorems with a 'What this does not claim' paragraph.

## Appendix A — Square-design non-identifiability

This appendix proves Theorem A of Sec. 4 together with its two corollaries, in the notation of the main text: noiseless bucket record $R_n = a_n B_n$, carrier $B_n = (MT)_n$, log-gain $\ell = \log a$ (entrywise), drift class $S$ a linear subspace of $\mathbb{R}^N$ with $\operatorname{span}\{\mathbf 1\}\subseteq S$ and $\dim S = p$. Full derivations first appeared in review issue #1 (where they carried the working labels Thm A and Cors. A2/A2′); this appendix is the archival form under the manuscript labels Theorem A, Corollary 1, Corollary 2.

### A.0 Standing assumptions

- **(A1) Model.** Noiseless record $R_n = a_n(MT)_n$, $n = 1,\dots,N$, with $N = K$ and $M \in \mathbb{R}^{K\times K}$ **invertible** — Hadamard, Fourier, random square, or otherwise. Write $c = MT$ for the carrier coefficient vector, so $R = e^{\ell}\odot c$ ($\odot$ = entrywise product).
- **(A2) Gain class.** $a_n > 0$ for all $n$; the admissible log-gains form (or contain a neighborhood inside) the linear subspace $S \ni \mathbf 1$, $\dim S = p \ge 2$; write $p - 1 = \dim(S/\operatorname{span}\{\mathbf 1\})$ for the nonconstant drift dimension.
- **(A3) Object class.** $T \in \mathbb{R}^K$ unconstrained (Theorem A, Corollary 1); constrained classes are treated in Corollary 2.
- **(A4) Carrier support.** For the clean dimension statements we assume full carrier support, $c_n = (MT)_n \neq 0$ for all $n$; this holds for generic $T$ (each $\{c_n = 0\}$ is a hyperplane). Zero buckets are discussed in Remark A.2.
- **(A5) Gauge.** The global-scale gauge orbit of a pair $(\ell, T)$ is $\mathcal G(\ell,T) = \{(\ell + t\mathbf 1,\, e^{-t}T) : t \in \mathbb{R}\}$; identifiability is always meant modulo $\mathcal G$.

### A.1 Theorem A (square non-identifiability, any invertible design)

**Theorem A.** *Assume (A1)–(A5). For every $s \in S$ the pair*

$$\ell' = \ell + s, \qquad c' = e^{-s}\odot c, \qquad T'(s) = M^{-1}\!\left(e^{-s}\odot MT\right)$$

*reproduces the bucket record exactly: $e^{\ell'_n} c'_n = R_n$ for all $n$. If $s$ is nonconstant on $\operatorname{supp}(MT)$ — under (A4), simply nonconstant — then $(\ell', T'(s)) \notin \mathcal G(\ell, T)$ and $T'(s) \neq \gamma T$ for every $\gamma \in \mathbb{R}$. The set of admissible pairs consistent with the record therefore contains a real-analytic family of dimension $\dim S = p$, of which the gauge orbit accounts for only $\dim(S \cap \operatorname{span}\{\mathbf 1\}) = 1$; the non-gauge ambiguity dimension is at least $p - 1 \ge 1$. In particular, gain–object separation from a square design is not identifiable modulo gauge whenever $S$ contains a nonconstant element.*

*Proof.* **(Data equality.)** $e^{\ell'_n}c'_n = e^{\ell_n + s_n}\, e^{-s_n} c_n = e^{\ell_n} c_n = R_n$, and $T'(s) = M^{-1}c'$ is well defined because $M$ is invertible. Both steps are exact; no smallness of $s$ is used.

**(Distinctness of the object.)** $T'(s) = \gamma T$ for some $\gamma$ iff $MT'(s) = \gamma MT$, i.e. $e^{-s_n} c_n = \gamma c_n$ for every $n$, i.e. $e^{-s_n} = \gamma$ for every $n \in \operatorname{supp}(c)$. Since $x \mapsto e^{-x}$ is injective, this forces $s$ constant on $\operatorname{supp}(c)$. Contrapositively, $s$ nonconstant on $\operatorname{supp}(MT)$ implies $T'(s)$ is not proportional to $T$.

**(Distinctness modulo gauge.)** $(\ell + s, T'(s)) \in \mathcal G(\ell,T)$ requires $\ell + s = \ell + t\mathbf 1$ in the gain coordinate, i.e. $s = t\mathbf 1$ (log is injective on positive gains). A nonconstant $s$ therefore leaves the orbit; note that when $s = t\mathbf 1$ the construction reduces exactly to the gauge, $T'(t\mathbf 1) = e^{-t}T$, so the family contains the orbit and nothing of the orbit is double-counted.

**(Dimension.)** The map $s \mapsto (\ell + s, T'(s))$ is injective (read off the first coordinate) and real-analytic in $s$, hence its image is a $p$-dimensional analytically parametrized family of exact solutions. Intersecting with the gauge orbit uses up $\dim(S \cap \operatorname{span}\{\mathbf 1\}) = 1$ dimension, leaving non-gauge ambiguity dimension $\ge p - 1$. $\blacksquare$

The display in the main text (Sec. 4) is the instance $s = \bar\ell\,\mathbf 1 - \ell$: the drift is absorbed *in one step* into the relabelled object $T' = M^{-1}\operatorname{diag}(a)MT$ (up to the gauge constant), leaving a constant gain. The hypothesis "$a$ nonconstant on the support of $MT$" in the main-text statement is exactly the distinctness condition established above.

**What this does not claim.** Theorem A is a statement about the square case $N = K$ and an unconstrained object; for $N > K$ the construction fails unless $e^{-s}\odot MT$ remains in $\operatorname{range}(M)$, and the correct analysis is the tall-design collision count of Theorem A′ (see Appendix B). It does not say the record is uninformative about the gain in a statistical model: under random illumination, the *relative* gain is consistently estimable (Theorem B; see Appendix C), a different — statistical, asymptotic — notion of identifiability which Theorem A neither contradicts nor implies. Finally, Theorem A is about uniqueness, not conditioning: it makes no claim about how well- or ill-posed any estimator is.

### A.2 Corollary 1 (slowness does not help)

**Corollary 1.** *Assume (A1)–(A5).*

*(i) If the admissible log-gain class is the linear space $S$ itself, the entire ambiguity family of Theorem A lies inside the class: $\ell \in S,\ s \in S \Rightarrow \ell + s \in S$. In particular, choosing $s = \bar\ell\,\mathbf 1 - \ell \in S$ produces a **constant-gain** exact explanation of the record with the static object $T' = M^{-1}(e^{\ell - \bar\ell}\odot MT)$: a slowly drifting gain over the true object is indistinguishable from no drift at all over a relabelled object.*

*(ii) If the admissible class is a slowness ball $\mathcal B_L = \{\ell \in S : \lVert \ell \rVert_* \le L\}$ for any seminorm $\lVert\cdot\rVert_*$ vanishing on constants (e.g. a Hölder or low-pass-energy seminorm), and $\ell$ is interior ($\lVert\ell\rVert_* < L$), then every nonconstant $s \in S$ with $\lVert s\rVert_*$ small enough keeps $\ell + s \in \mathcal B_L$. The local non-gauge ambiguity dimension remains $p - 1$: slowness bounds the **size** of the ambiguity, never its **dimension**.*

*Proof.* (i) is linearity of $S$ plus Theorem A applied with the stated $s$; nonconstancy of $\ell$ on $\operatorname{supp}(c)$ makes the constant-gain alternative distinct modulo gauge. (ii) Subadditivity of the seminorm gives $\lVert \ell + s\rVert_* \le \lVert\ell\rVert_* + \lVert s\rVert_* \le L$ once $\lVert s\rVert_* \le L - \lVert\ell\rVert_*$; the set of such $s$ is a neighborhood of $0$ in $S$ and Theorem A applies to each nonconstant member. $\blacksquare$

**What this does not claim.** Slowness is not useless in general — in the tall-design regime the whole point is that slow drift means small $p$, making the threshold $N \ge K + p$ cheap to satisfy (Sec. 4). The corollary only asserts that at $N = K$ a slowness prior *by itself* removes nothing from the ambiguity, because the ambiguity directions live in the slow class itself.

### A.3 Corollary 2 (nonnegativity is insufficient; known support zeros can restore local identifiability)

Throughout this corollary write $H$ for the square invertible design ($H = M$; the letter matches the fixed-basis usage, e.g. Hadamard), and define the gain-absorption operator

$$M_s := H^{-1}\operatorname{diag}(e^{-s})H, \qquad T'(s) = M_s T,$$

so that the ambiguity set at $T$ under an object prior class $\mathcal T$ is $V_{\mathcal T}(T) = \{s \in S : M_sT \in \mathcal T\}$, and identifiability modulo gauge is the assertion $V_{\mathcal T}(T) = S \cap \operatorname{span}\{\mathbf 1\}$.

**Corollary 2.** *Assume (A1)–(A5).*

*(i) (Positivity insufficient.) Let $\mathcal T_+ = \{T : T_j \ge 0\ \forall j\}$ and let $T$ have full support, $T_j > 0$ for all $j$. Then there is $r > 0$ such that every $s \in S$ with $\lVert s\rVert_\infty < r$ satisfies $M_sT > 0$; explicitly, it suffices that*

$$\lVert H^{-1}\rVert_{2}\,\lVert HT\rVert_2\,(e^{r} - 1) < \min_j T_j .$$

*Hence $V_{\mathcal T_+}(T)$ contains a full neighborhood of $0$ in $S$ and the local non-gauge ambiguity dimension is still $p - 1$.*

*(ii) (Known support zeros; local criterion.) Let $\Omega \subset \{1,\dots,K\}$, $|\Omega| = q$, and $\mathcal T_\Omega = \{T : T_{\Omega^c} = 0,\ T \ge 0\}$, with the true $T \in \mathcal T_\Omega$, $T_\Omega > 0$. Then local identifiability modulo gauge holds at $T$ if and only if (at the first-order level)*

$$\ker\!\big(P_{\Omega^c} H^{-1}\operatorname{diag}(HT)\,\big|_S\big) \;=\; S \cap \operatorname{span}\{\mathbf 1\},$$

*where $P_{\Omega^c}$ is coordinate projection onto $\Omega^c$. The gauge direction always lies in the kernel; when the kernel is exactly the gauge, no ambiguity exists in a quantifiable ball: with $\gamma$ the smallest singular value of the linearized map on a complement $S_\perp$ of $\operatorname{span}\{\mathbf 1\}$ in $S$ and $C_H$ a second-order remainder constant (below), every $s$ with $0 < \lVert s_\perp\rVert_2 < \gamma / C_H$ violates the support constraint.*

*(iii) (Generic counts — dimension-counting arguments, labeled as such.) The linearized map in (ii) sends the $(p-1)$-dimensional space $S/\operatorname{span}\{\mathbf 1\}$ into $\mathbb{R}^{K-q}$; injectivity is possible only if $K_0 := K - q \ge p - 1$, i.e. **at least one known zero per nonconstant drift dimension**. For generic $(H, T_\Omega)$ this necessary count is expected to be sufficient. For unknown support of size $\le q$, dimension counting predicts the threshold $K \ge 2q + (p-1)$, up to endpoint conventions.*

*Proof.* **(i)** $M_0T = T$ and $\lVert M_sT - T\rVert_2 = \lVert H^{-1}\big((e^{-s} - \mathbf 1)\odot HT\big)\rVert_2 \le \lVert H^{-1}\rVert_2\,\lVert HT\rVert_2\,\max_n|e^{-s_n} - 1| \le \lVert H^{-1}\rVert_2\,\lVert HT\rVert_2\,(e^{\lVert s\rVert_\infty} - 1)$. If this is below $\min_j T_j$ then $M_sT > 0$ entrywise. Since the positive orthant is open and $s \mapsto M_sT$ is continuous, positivity excludes nothing locally; Theorem A supplies the distinctness. $\blacksquare$ (i)

**(ii)** Define the support-constraint map $F : S \to \mathbb{R}^{K-q}$, $F(s) = P_{\Omega^c} M_s T$. It is real-analytic, $F(0) = P_{\Omega^c}T = 0$, and its differential at $0$ is

$$DF_0\,u = -\,P_{\Omega^c} H^{-1}\operatorname{diag}(HT)\,u,$$

by differentiating $e^{-tu} = \mathbf 1 - tu + O(t^2)$ inside $M_{tu}$. The gauge is always in the kernel: $H^{-1}\operatorname{diag}(HT)\mathbf 1 = H^{-1}(HT) = T$ and $P_{\Omega^c}T = 0$; consistently, $F(t\mathbf 1) = e^{-t}F(0) = 0$ exactly, for all $t$.

*Necessity of the criterion (first-order sense).* If the kernel strictly exceeds the gauge, some nonconstant $u \in S$ satisfies the linearized support constraint. This is a first-order ambiguity direction: it makes $T$ a critical point of the constrained model map and hence a Fisher-information null direction for the corresponding functional (cf. Remark A.1), so local *differential* identifiability fails. Whether the direction integrates to an exact ambiguity curve requires a further constant-rank or analyticity argument and can fail at second order; we claim only the first-order (differential) statement, which is what the criterion tests.

*Sufficiency in a ball.* Suppose the kernel equals the gauge and let $\gamma = \sigma_{\min}(DF_0|_{S_\perp}) > 0$. Entrywise Taylor with remainder, $|e^{-x} - 1 + x| \le \tfrac{x^2}{2}e^{|x|}$, gives for $\lVert s\rVert_\infty \le 1$

$$\lVert F(s) - DF_0\,s\rVert_2 \;\le\; C_H\,\lVert s\rVert_2^2, \qquad C_H := \tfrac{e}{2}\,\lVert H^{-1}\rVert_2\,\lVert HT\rVert_2 .$$

For gauge-fixed $s = s_\perp \in S_\perp$ (any $s$ may be reduced to this form using $F(s + t\mathbf 1) = e^{-t}F(s)$, which rescales but never annihilates $F$),

$$\lVert F(s_\perp)\rVert_2 \;\ge\; \gamma\,\lVert s_\perp\rVert_2 - C_H\,\lVert s_\perp\rVert_2^2 \;>\; 0 \quad\text{for } 0 < \lVert s_\perp\rVert_2 < \gamma / C_H .$$

A nonzero $F(s)$ means $M_sT \notin \mathcal T_\Omega$ (support constraint violated), so no non-gauge ambiguity exists in that ball. This is the quantitative inverse-function-theorem argument of issue #1 in explicit constants. $\blacksquare$ (ii)

**(iii)** *These are genericity/dimension-count arguments, not proofs, and we state them as such.* The necessity direction is rigorous: a linear map from a $(p-1)$-dimensional space cannot be injective into $\mathbb{R}^{K-q}$ if $K - q < p - 1$, so at least $p - 1$ known zeros are required. The sufficiency direction is generic: the entries of $P_{\Omega^c}H^{-1}\operatorname{diag}(HT)|_{S_\perp}$ are polynomial in $(H, T)$, so full column rank holds off a proper algebraic subvariety *provided a single witness exists*; the dimension count $K - q \ge p - 1$ makes a witness expected but, for a *fixed* named basis (e.g. Hadamard with a specific low-pass $S$), the rank must be verified directly — the correct fixed-basis statement is rank-based, not dimensional. The unknown-support count $K \ge 2q + (p-1)$ arises from demanding that the $q$-sparse model avoid all of its gain-transformed copies $M_s\Sigma_q$, in analogy with the generic sparsity thresholds of Kech–Krahmer for generic bilinear maps; it is a heuristic prediction of the generic threshold, unverified for structured designs, and the uniform no-support-switching condition it summarizes is strictly stronger than (ii). $\blacksquare$ (heuristic scope)

**What this does not claim.** Part (i) says nonnegativity fails to restore *identifiability*; it may still improve estimator conditioning and is routinely useful as regularization — no claim is made either way. Part (ii) is local: it excludes ambiguities in a ball around $T$ and is silent about isolated global aliases, which can exist even with a nonsingular linearization; global uniqueness needs a separate compactness/non-vanishing argument outside the ball. The criterion is also stated at fixed, *known* support; for unknown support only the heuristic count of part (iii) is offered, and part (iii) makes no claim for any specific fixed basis without an explicit rank check.

### A.4 Remarks

**Remark A.1 (Fisher-theoretic reading).** Because the ambiguity of Theorem A is an explicit real-analytic curve $t \mapsto (\ell + ts, T'(ts))$ along which the noiseless data are constant, every nonconstant $s \in S/\operatorname{span}\{\mathbf 1\}$ yields an exact null direction of the (gauge-quotient) Fisher information in any regular dominated noise model built on this record: the Cramér–Rao bound is infinite for any functional that varies along the curve. Here the implication "explicit ambiguity curve $\Rightarrow$ Fisher null direction" is exact, not merely first-order.

**Remark A.2 (zero buckets).** If some $c_n = (MT)_n = 0$, two separate pathologies arise, which the statements above deliberately quarantine via (A4): the gain values $a_n$ at zero-carrier frames are entirely unobservable (a trivial extra ambiguity, of dimension $\dim(S \cap \{s : s = 0 \text{ on } \operatorname{supp}(c)\})$ beyond the count of Theorem A), and log-domain processing of $R_n = 0$ is undefined, an estimation-side issue treated by the calibrated soft-log machinery of the low-photon analysis (Sec. 6; see Appendix D), not an identifiability issue.

## Appendix B — Tall-Design Thresholds and the Low-Pass Drift Space

This appendix proves the tall-design identifiability thresholds quoted as **Theorem A′** in Sec. 4 (local differential identifiability at $N\ge K+p-1$; generic exact finite-sample identifiability at $N\ge K+p$; uniform identifiability at $N\ge 2K+p-1$), restated below as Theorem A′(i)–(iii), and the two lemmas that transfer these thresholds from *generic* drift subspaces to the *physical* Fourier low-pass drift space $S_{\mathrm{LP}}$. The material consolidates issue #2 §1 and issue #3 §8 of the working record. Throughout we distinguish carefully between fully rigorous steps and steps that are standard algebraic-geometry *genericity / dimension-count* arguments; the latter are flagged where they occur.

### B.0 Setting, notation, and the meaning of "generic"

The bucket record is $R_n=a_nB_n$ with $B=MT$, i.e. in vector form

$$
y=\operatorname{diag}(e^{\ell})\,M\,T,\qquad M\in\mathbb R^{N\times K},\ N>K,\qquad \ell\in S,\ T\in\mathbb R^{K}\setminus\{0\},
\tag{B.1}
$$

where $\ell=\log a$ is the log-gain trajectory, confined to the drift class $S\subset\mathbb R^{N}$ with $p=\dim S$. Set

$$
C=S\cap\operatorname{span}\{\mathbf 1\},\qquad c=\dim C\in\{0,1\},\qquad r=p-c .
$$

The integer $r$ counts the *nonconstant* gain degrees of freedom. In the convention used throughout the paper, $\mathbf 1\in S$ (the constant direction is the unavoidable global-scale gauge $(a,T)\mapsto(ca,\,T/c)$), so $c=1$ and $r=p-1$. All identifiability statements are modulo this gauge. Via the bandwidth relation $p\approx\rho_{\mathrm{bw}}N$ of Sec. 2, every threshold below can be re-read as a condition on $\rho_{\mathrm{bw}}$; the pair-decorrelation parameter $\rho_{\mathrm{pair}}$ of Sec. 8 plays no role in this appendix.

**Genericity convention.** "Generic $M$" (and, where stated, "generic drift subspace") means: outside a proper real semialgebraic subset of the relevant parameter space. Equivalently, the stated property holds almost surely when the excluded parameters are drawn from any distribution absolutely continuous with respect to Lebesgue measure. The standard proof route is to verify the property over $\mathbb C$ on a Zariski-open set and restrict to the real points; we use this convention silently below. Note at the outset that a *deterministic structured* design — e.g. an ordered Hadamard matrix — is **not** covered by any genericity statement here and must be checked separately.

### B.1 The collision equation

**Lemma B.1 (lifted collision equation).** *Two parameter pairs $(\ell,T)$ and $(\ell',T')$, with $\ell,\ell'\in S$ and $T,T'\neq0$, produce identical noiseless records $(B.1)$ if and only if*

$$
MT = D_s\,M\,T',\qquad s=\ell'-\ell\in S,\qquad D_s=\operatorname{diag}(e^{s}) .
\tag{B.2}
$$

*The constant part of $s$ is exactly the gauge (a relative rescaling of $T$ vs. $T'$); consequently all non-gauge aliases are described by the incidence relation*

$$
[\,M,\ -D_s M\,]\begin{bmatrix}T\\ T'\end{bmatrix}=0
\tag{B.3}
$$

*with $s$ nonconstant modulo $C$. Equivalently, writing $U=\operatorname{range}(M)$, an alias exists iff $MT\in U\cap D_sU$.*

**Proof.** $\operatorname{diag}(e^{\ell})$ is invertible, so equality of the two records is equivalent to (B.2). If $s$ is constant, $s=\sigma\mathbf 1$, then (B.2) reads $MT=e^{\sigma}MT'$; since $N>K$ and generic $M$ has full column rank, $T=e^{\sigma}T'$, which is the gauge orbit. Conversely a nonconstant $s\bmod C$ gives a genuinely distinct pair. Rewriting (B.2) as a nullspace condition gives (B.3). Finally, note that a kernel vector of $[M,-D_sM]$ with $T=0$ forces $D_sMT'=0$, hence $T'=0$ (both $M$ and $D_sM$ are injective for full-column-rank $M$); so every nonzero kernel element has both blocks nonzero. $\blacksquare$

This diagonal structure is why the generic bilinear counts of Kech–Krahmer (arXiv:1603.07316) do not apply verbatim: $y_n=a_n m_n^{\top}T$ is a *diagonal-row* measurement, not a generic rank-one measurement, and the ambiguity is governed by the intersection of the fixed $K$-plane $U$ with its diagonally modulated copy $D_sU$.

### B.2 The stratum-counting lemma

Let $B=\exp(S)/\mathbb R_{+}$ be the nonconstant gain-ratio manifold (dimension $r=p-1$), parametrizing the classes $b=e^{s}$ modulo positive scalars, $s$ nonconstant. For a **fixed** design $M$, stratify $B$ by the level sets of the rank function:

$$
B=\bigsqcup_{\alpha}B_{\alpha},\qquad \rho_\alpha := \operatorname{rank}[\,M,-D_bM\,]\ \text{constant for }b\in B_\alpha,\qquad r_\alpha:=\dim B_\alpha .
$$

Such a finite stratification into locally closed strata exists for every $M$: after the substitution $u=e^{s}$ the rank function is semialgebraic in $u$, its finitely many level sets are semialgebraic, and finite semialgebraic stratification is standard (Bochnak–Coste–Roy, *Real Algebraic Geometry*, Ch. 9). Define the **projective collision dimension**

$$
\Delta_\alpha := r_\alpha + 2K-1-\rho_\alpha .
\tag{B.4}
$$

**Lemma B.2 (stratum counting).** *Fix $M\in\mathbb R^{N\times K}$ of full column rank and stratify $B$ as above. Consider the collision incidence variety*

$$
Z_\alpha=\bigl\{(b,[T:T'])\in B_\alpha\times\mathbb P^{2K-1}\ :\ [M,-D_bM]\begin{bmatrix}T\\T'\end{bmatrix}=0\bigr\}.
$$

*Then:*

1. *$Z_\alpha=\varnothing$ if and only if $\rho_\alpha=2K$; otherwise $\dim Z_\alpha=\Delta_\alpha$ (and then automatically $\Delta_\alpha\ge r_\alpha\ge0$).*
2. *The "bad first-object" set contributed by stratum $\alpha$ — the projection of $Z_\alpha$ to $[T]\in\mathbb P^{K-1}$ — has dimension at most $\Delta_\alpha$.*
3. *(Sufficiency, rigorous.) If $\max_\alpha\Delta_\alpha<K-1$, where the maximum runs over strata with $\rho_\alpha<2K$, then a generic object $T$ has no non-gauge alias. (Necessity, genericity-flagged.) Conversely, if some stratum has $\Delta_\alpha\ge K-1$ **and** the projection $Z_\alpha\to\mathbb P^{K-1}$ is dominant, a generic object has an alias.*
4. *Uniform identifiability (every nonzero object alias-free) holds if and only if $\rho_\alpha=2K$ for every stratum — equivalently, with the convention that the maximum in (3) runs over kernel-supporting strata (empty maximum $=-\infty$), iff $\max_\alpha\Delta_\alpha<0$.*

**Proof.** (1) For fixed $b\in B_\alpha$ the fiber of $Z_\alpha$ is the projectivized nullspace of $[M,-D_bM]$, of projective dimension $(2K-\rho_\alpha)-1=2K-1-\rho_\alpha$; it is empty iff the nullspace is $\{0\}$, i.e. iff $\rho_\alpha=2K$ (possible only when $N\ge2K$, since $\rho_\alpha\le\min(N,2K)$). On a constant-rank stratum the nullspaces form a vector bundle over $B_\alpha$ (constant-rank kernels vary continuously; locally trivial by choosing complementary minors), so the fiber dimension is constant and

$$
\dim Z_\alpha=\dim B_\alpha+(2K-1-\rho_\alpha)=\Delta_\alpha .
$$

When $\rho_\alpha\le 2K-1$ we get $\Delta_\alpha\ge r_\alpha\ge0$.

(2) The image of a semialgebraic set under the projection $Z_\alpha\to\mathbb P^{K-1}$ has dimension at most $\dim Z_\alpha$ (semialgebraic dimension is non-increasing under maps; Bochnak–Coste–Roy, Prop. 2.8.6).

(3) *Sufficiency:* the union over the finitely many strata of the bad projections is semialgebraic of dimension $\le\max_\alpha\Delta_\alpha<K-1=\dim\mathbb P^{K-1}$, hence its complement is dense and full-measure. Every $T$ in the complement has no alias with any nonconstant ratio. This direction is fully rigorous. *Necessity:* if $\Delta_\alpha\ge K-1$ and the projection is dominant, the image fills $\mathbb P^{K-1}$ up to lower-dimensional sets, so a generic $T$ has an alias. **Status:** the dominance of the projection for generic $M$ is a *standard algebraic-geometry genericity assertion* — failure of dominance is the vanishing of a Jacobian minor of the projection, hence a proper algebraic condition on $M$ once a single example with full projection rank exists; the source (issue #2 §1.3) asserts this by the usual dimension/transversality count and does not exhibit the witness per stratum. We record the necessity direction as resting on this dominant-projection argument, in the same way as the generic bilinear identifiability literature (Kech–Krahmer; Li–Lee–Bresler, arXiv:1501.06120).

(4) Uniform injectivity means (B.3) has no solution with nonconstant $s$ and $T,T'\neq0$, i.e. every fiber over every $b\in B$ is empty. By (1) this happens iff $\rho_\alpha=2K$ on every stratum. Since strata with $\rho_\alpha\le2K-1$ have $\Delta_\alpha\ge0$, the stated $\max\Delta_\alpha<0$ criterion is equivalent under the empty-maximum convention. This direction is deterministic and rigorous given the stratification. $\blacksquare$

**Remark (archival precision).** The source states claim 1 as "$Z_\alpha$ has dimension $\Delta_\alpha$ if $\Delta_\alpha\ge0$, empty if $\Delta_\alpha<0$". As written that phrasing misses the case $\rho_\alpha=2K$, $r_\alpha\ge1$ (where $\Delta_\alpha=r_\alpha-1\ge0$ but $Z_\alpha=\varnothing$). The corrected bookkeeping above — emptiness governed by $\rho_\alpha=2K$, not by the sign of $\Delta_\alpha$ — is what claims 3–4 actually use, and is how the uniform threshold at $N\ge 2K+p-1$ (which lives in the regime $N>2K$) is consistent with $\rho_\alpha\le\min(N,2K)$.

**What this does not claim.** Lemma B.2 is a statement about *exact noiseless collisions* only: it says nothing about conditioning, noise robustness, or the behavior of any estimator. It does not evaluate the ranks $\rho_\alpha$ — that is where genericity of $M$ (Sec. B.3) or the low-pass lemmas (Sec. B.4) enter. It does not cover deterministic structured designs unless their stratum ranks are computed explicitly. The necessity half of claim 3 has genericity status as flagged.

### B.3 Clean thresholds for generic drift families

On a *generic* $p$-dimensional log-gain subspace, the ratio manifold has a dense open stratum on which $D_b$ has no forced coordinate equalities, and for generic $M$ the rank on that stratum is maximal:

$$
\operatorname{rank}[\,M,-D_bM\,]=\min(N,2K).
\tag{B.5}
$$

**Status of (B.5):** this is the *dominant-stratum hypothesis* of issue #2 §1.4 — a genericity/dimension-count assertion (a single $(M,b)$ witness with full rank makes the relevant minor a not-identically-zero polynomial, hence nonzero generically). For the physical low-pass space it is *proved*, for every nonconstant $b$, in Sec. B.4–B.5 below; that is precisely why the low-pass lemmas matter.

Under (B.5) the collision count takes a single unified form. If $N<2K$, the dense stratum has $\rho=N$ and, by Lemma B.2(1),

$$
\Delta = r+2K-1-N .
\tag{B.6}
$$

If $N\ge2K$, the dense stratum has $\rho=2K$ and empty fibers; collisions can then live only on the *rank-drop locus* $\{b: \operatorname{rank}[M,-D_bM]\le 2K-1\}$. The corank-one determinantal variety in $\mathbb R^{N\times2K}$ has codimension $(N-2K+1)\cdot 1$ (classical; Eagon–Northcott / Bruns–Vetter, *Determinantal Rings*), so a *transversally embedded* $r$-parameter family meets it in a set of dimension $r-(N-2K+1)$, over which the kernel fiber is $0$-dimensional; the incidence dimension is again $r-(N-2K+1)+0=r+2K-1-N=\Delta$. Thus (B.6) controls both regimes. **Status:** the transversality of the structured family $b\mapsto[M,-D_bM]$ to the determinantal variety is again a genericity assertion of the same standard type, asserted (not instance-verified) in the source.

**Theorem A′(i) (local differential threshold: $N\ge K+p-1$).** *Let $M$ be generic, $S$ a generic $p$-dimensional log-gain space with $\mathbf 1\in S$ ($r=p-1$), and $T$ generic. After quotienting the global-scale gauge, the parameter manifold of pairs $(\ell\bmod C,\,[T])$ has dimension $(K-1)+r=K+p-2$, and the projectivized data space has dimension $N-1$. Local differential identifiability (injectivity of the differential of $(\ell,T)\mapsto[\operatorname{diag}(e^{\ell})MT]$ at generic points) holds iff $N-1\ge K+p-2$, i.e. $N\ge K+p-1$.*

**Proof.** Necessity is the dimension inequality: an injective linear map from a $(K+p-2)$-dimensional tangent space into an $(N-1)$-dimensional one requires $N-1\ge K+p-2$. For sufficiency, the differential has columns $M\,\delta T$ (object directions) and $\operatorname{diag}(MT)\,\delta\ell$, $\delta\ell\in S/C$ (gain directions), with the joint scale direction quotiented out. Full rank $K+p-2$ of this $N\times(K+p-1)$-block-minus-gauge system is the nonvanishing of some minor — a polynomial condition in $(M,S,T)$. **Status:** the source (issue #2 §1.5) asserts the existence of a full-rank witness by "a generic rank calculation," i.e. the standard specialization argument; the witness is not exhibited. We therefore record sufficiency as a *standard dimension-count genericity argument*, consistent with its use throughout this literature. $\blacksquare$

**What this does not claim.** Local injectivity of the differential does not imply global uniqueness; at the boundary $N=K+p-1$ the map is generically locally finite-to-one but **not** generically one-to-one (see Theorem A′(ii): there $\Delta=K-1$, so aliases generically exist). No statement is made about the singular values of the Jacobian, i.e. about conditioning.

**Theorem A′(ii) (sharp generic-point threshold: $N\ge K+p$).** *For generic tall $M$ and a generic (transverse) nonconstant gain-ratio family of dimension $r=p-1\ge1$, almost every pair $(\ell,T)$ is identifiable modulo global scale iff $N>K+r$, i.e. iff*

$$
N\ \ge\ K+p .
\tag{B.7}
$$

*For $K<N\le K+p-1$, a generic object has a non-gauge algebraic alias: overdetermination alone is insufficient.*

**Proof.** By (B.6), the bad-object projection has dimension at most $\Delta=r+2K-1-N$ (Lemma B.2(2)). Generic-point identifiability holds when $\Delta<K-1$, i.e. $r+2K-1-N<K-1$, i.e. $N>K+r=K+p-1$; integrality gives (B.7). This direction inherits only the rank hypothesis (B.5) — rigorous once (B.5) is established (for low-pass $S$, unconditionally by Sec. B.5). For the converse, $N\le K+r$ gives $\Delta\ge K-1$, and under the dominant-projection assertion (Lemma B.2(3), genericity-flagged) the bad set fills $\mathbb P^{K-1}$, so a generic object has an alias. $\blacksquare$

**What this does not claim.** "Generic" excludes an unquantified measure-zero exceptional set of objects; below the uniform threshold, exceptional objects with exact aliases *do* exist (the gap $K+p\le N<2K+p-1$ is real). The theorem says nothing about the conditioning of the inversion near $N=K+p$ — uniqueness at the threshold is compatible with arbitrarily bad stability, which is a separate random-matrix question (Sec. 10). It does not apply to deterministic designs, and it does not say statistical mechanisms are useless above threshold — only that they are not *logically required* for identifiability.

**Theorem A′(iii) (sharp uniform threshold: $N\ge 2K+p-1$).** *In the setting of Theorem A′(ii), every nonzero object is identifiable modulo global scale iff $N\ge 2K+r=2K+p-1$.*

**Proof.** Uniform identifiability is emptiness of the whole collision incidence, i.e. $\Delta<0$ in the unified count: $r+2K-1-N<0 \iff N\ge 2K+r$. Concretely, for $N\ge 2K+r$ the rank-drop locus has expected dimension $r-(N-2K+1)\le r-(r+1)<0$ in the $r$-dimensional family, so (under the determinantal-transversality assertion flagged above) the family misses it entirely and every $b$ has trivial kernel, $\rho=2K$; Lemma B.2(4) concludes. Conversely for $2K\le N<2K+r$ the drop locus has nonnegative expected dimension and (generically, same flag) is nonempty, producing an exact alias for some object; for $N<2K$ the kernel is nontrivial for *every* $b$, so uniform identifiability fails outright. $\blacksquare$

**What this does not claim.** Uniformity is over *objects*, not over designs: $M$ and the drift family are still generic, and an adversarially chosen $M$ can defeat the bound. No claim is made about recovery algorithms or noise.

### B.4 The two low-pass lemmas

The clean thresholds above rest on the rank identity (B.5), asserted generically. The physical drift space is not generic — it is the Fourier low-pass space

$$
S_{\mathrm{LP}}=\operatorname{span}\Bigl\{\mathbf 1,\ \cos\tfrac{2\pi qn}{N},\ \sin\tfrac{2\pi qn}{N}\ :\ q=1,\dots,m\Bigr\},\qquad p=\dim S_{\mathrm{LP}}=2m+1,
\tag{B.8}
$$

with $r=p-1=2m$ and the below-Nyquist condition $p\le N$. The next two lemmas verify (B.5) for this space *without* any genericity assumption on $S$.

**Lemma B.5 (level-multiplicity bound; fully rigorous).** *Let $s\in S_{\mathrm{LP}}$ be nonconstant, $p<N$. Then no value is attained by $(s_n)_{n=0}^{N-1}$ more than $2m=p-1$ times. Consequently the largest eigenvalue multiplicity of $D_s=\operatorname{diag}(e^{s_n})$ satisfies*

$$
m_{\max}(s)\ \le\ p-1 .
\tag{B.9}
$$

**Proof.** Write $z_n=e^{2\pi i n/N}$; the $N$ points $z_0,\dots,z_{N-1}$ are distinct. Every $s\in S_{\mathrm{LP}}$ has the Laurent representation $s_n=\sum_{q=-m}^{m}c_qz_n^{q}$ with conjugate symmetry $c_{-q}=\overline{c_q}$ (real $s$). Suppose $s_n=c$ at more than $2m$ distinct indices. Then the ordinary polynomial

$$
P(z)=z^{m}\bigl(\textstyle\sum_{q=-m}^{m}c_qz^{q}-c\bigr),\qquad \deg P\le 2m,
$$

has more than $2m$ distinct roots on the unit circle, hence $P\equiv0$ (fundamental theorem of algebra). Then $s(z)\equiv c$ on the whole circle, so $s$ is the constant sequence — contradiction. Since $x\mapsto e^{x}$ is injective, the eigenvalue multiplicities of $D_s$ equal the level multiplicities of $s$, giving (B.9). $\blacksquare$

**Lemma B.6 (generic rank of $[M,-DM]$ with repeated diagonal values).** *Let $D\in\mathbb R^{N\times N}$ be a non-scalar diagonal matrix whose most-repeated diagonal value has multiplicity $m_{\max}$. Then for generic $M\in\mathbb R^{N\times K}$,*

$$
\operatorname{rank}[\,M,-DM\,]=\min\bigl(N,\ 2K,\ K+N-m_{\max}\bigr).
\tag{B.10}
$$

**Proof.** *Upper bound (deterministic — holds for every $M$).* The column space of $[M,-DM]$ is $U+DU$ with $U=\operatorname{range}(M)$. Let $\lambda$ be a most-repeated diagonal value and write $D=\lambda I+Q$, so $Q$ is diagonal with exactly $N-m_{\max}$ nonzero entries, $\operatorname{rank}Q=N-m_{\max}$. Then $U+DU=U+QU$, hence

$$
\dim(U+DU)\ \le\ \dim U+\dim QU\ \le\ K+\min(K,\,N-m_{\max}),
$$

together with the trivial bounds $\le N$ and $\le 2K$. This is the right-hand side of (B.10).

*Lower bound (genericity via witness; status flagged).* It suffices to exhibit a single $M_0$ attaining the bound: then the corresponding maximal minor of $[M,-DM]$ is a polynomial in the entries of $M$ that is not identically zero, so it is nonzero off a proper algebraic set — the standard specialization argument. The source (issue #3 §8.3) constructs $M_0$ in coordinates adapted to $Q$: order the coordinates so that the $Q$-active indices (those with $d_i\neq\lambda$) come first, and build the $K$ columns of $M_0$ by pairing active coordinates with inactive ones (each pair $u=e_{\text{act}}+e_{\text{inact}}$ contributes two independent directions to $U+QU$, since $Qu=q\,e_{\text{act}}$) and, when inactive coordinates are exhausted, pairing active coordinates carrying *distinct* diagonal values (possible because no value has multiplicity exceeding $m_{\max}$), until the count saturates at $N$, $2K$, or $K+(N-m_{\max})$. **Status:** the source gives this as a construction sketch; the saturation bookkeeping across the finitely many cases is elementary but is not carried out line-by-line there. We record the lower bound as a *standard witness-plus-specialization genericity argument*, not as an instance-checked computation. $\blacksquare$

**What these lemmas do not claim.** Lemma B.5 is specific to the exact Fourier grid (B.8) below Nyquist; a different "low-pass" convention (e.g. a wavelet or spline drift class, or an off-grid Fourier family) can have larger level multiplicity and must be re-checked via (B.12) below. Lemma B.6 is a statement about *generic* $M$ given $D$; a deterministic design may realize strictly smaller rank (only the upper bound is universal).

### B.5 Transfer to the physical low-pass space

**Proposition B.7 (low-pass transfer).** *Let $S=S_{\mathrm{LP}}$ as in (B.8), $p=2m+1<N$, and suppose the generic-point threshold $N\ge K+p$ holds. Then for generic $M$, every nonconstant $s\in S_{\mathrm{LP}}$ satisfies*

$$
\operatorname{rank}[\,M,-D_sM\,]=\min(N,2K),
\tag{B.11}
$$

*i.e. the whole nonconstant ratio manifold behaves as the dense stratum of Sec. B.3. Consequently the clean thresholds of Theorem A′(i)–(iii) hold verbatim for the physical low-pass drift space:*

$$
\text{local: } N\ge K+p-1,\qquad \text{generic: } N\ge K+p,\qquad \text{uniform: } N\ge 2K+p-1 .
$$

**Proof.** Fix a nonconstant $s\in S_{\mathrm{LP}}$. By Lemma B.5, $m_{\max}(s)\le p-1$. Apply Lemma B.6:

- If $N<2K$: the threshold gives $p-1\le N-K-1<2K-K-1<K$, so $K+N-m_{\max}\ge K+N-(p-1)>N$, and (B.10) yields $\operatorname{rank}=N=\min(N,2K)$.
- If $N\ge2K$: the threshold gives $p-1\le N-K-1\le N-K$, so $K+N-m_{\max}\ge 2K$, and (B.10) yields $\operatorname{rank}=2K=\min(N,2K)$.

This arithmetic is exact and rigorous. Two statuses must be recorded. *(i) Simultaneity of genericity.* Lemma B.6's exceptional set of designs depends on $D_s$; asserting (B.11) for **all** nonconstant $s$ with **one** generic $M$ requires a uniformization step: the bad set $X=\{(M,s):\operatorname{rank}<\min(N,2K)\}$ is semialgebraic in $(M,e^{s})$ with proper algebraic $s$-slices, so by the semialgebraic fiber-dimension theorem $\dim X\le\dim B+NK-1$, whence for almost every $M$ the bad-$s$ set has positive codimension in $B$; that any such residual exceptional strata do not enlarge $\max_\alpha\Delta_\alpha$ is the same determinantal-transversality dimension count flagged in Sec. B.3. We state this as a *standard genericity argument*, matching the source's level of justification. *(ii)* Given (B.11), the sufficiency directions of Theorem A′(ii)–(iii) are rigorous for $S_{\mathrm{LP}}$; the necessity directions retain the dominant-projection flag of Lemma B.2(3). $\blacksquare$

**Other low-pass conventions.** If the implemented drift class is not exactly (B.8), define its maximal nonconstant level multiplicity

$$
L_S=\sup_{\substack{s\in S\\ s\ \text{nonconstant}}}\ \max_{c}\ \#\{n: s_n=c\}.
\tag{B.12}
$$

By the same arithmetic, the clean thresholds are guaranteed whenever

$$
L_S\le K\ \ (\text{if }N<2K)\qquad\text{or}\qquad L_S\le N-K\ \ (\text{if }N\ge2K).
\tag{B.13}
$$

If (B.13) fails, the clean $N\ge K+p$ statement must **not** be used; instead apply the stratum formula of Lemma B.2 with $\rho_\alpha=\min(N,2K,K+N-m_\alpha)$, where $m_\alpha$ is the diagonal multiplicity on stratum $\alpha$: generic-point identifiability iff $\max_\alpha(r_\alpha+2K-1-\rho_\alpha)<K-1$, uniform iff $<0$ (kernel-supporting-strata convention). For the standard Fourier space (B.8), (B.13) holds automatically at $N\ge K+p$ and no correction is needed.

**What this does not claim.** The transfer says nothing about the regime $K<N<K+p$, where tallness is insufficient *even generically* and the statistical stationarity anchor of Sec. 5 (Theorem B) or a support/sparsity prior is required — the low-pass structure does not rescue algebraic identifiability below threshold, and at $p\approx N$ ($\rho_{\mathrm{bw}}\to1$) blind algebraic separation is impossible for any $N$. It does not claim well-conditioned inversion at or near $N=K+p$. It does not cover deterministic designs (the ordered-Hadamard obstruction of Theorem A is unaffected). And it certifies only the exact grid-Fourier below-Nyquist model; any other drift-class implementation must pass the $L_S$ check (B.12)–(B.13) before the clean thresholds are quoted.

## Appendix C — Carrier statistics and the stationarity anchor

This appendix proves Proposition 1, formalizes condition (★) quantitatively, proves Proposition 2 (with counterexamples in both directions), and proves Theorem B. Throughout, $R_n = a_n B_n$ is the bucket record, $B_n = \langle I_n, T\rangle = \sum_{j=1}^K I_{n,j} T_j$ the carrier, $\ell_n = \log a_n$ the log-gain, $S$ the drift class with $p=\dim S$, $S_1=\sum_j T_j$, $S_2=\|T\|_2^2$, $K_{\mathrm{eff}}=S_1^2/S_2$, $K_\infty=S_2/\|T\|_\infty^2$, $K_4=S_2^2/\sum_j T_j^4$, and $W$ denotes the window length of the blind estimator $\hat g_n = W^{-1}\sum_{k\in W_n} Y_k$ applied to $Y_n=\log R_n$. Asymptotic statements are for a triangular array indexed by $(K,N)$: the object $T=T^{(K)}$ and pattern law may vary with $K$, and limits are taken along $K,N\to\infty$. Full derivations first appeared in review issue #1 of the theory repository; the soft-log low-photon variant is in issue #3, Sec. 7.

### C.1 Proposition 1 — random-basis carrier statistics

**Proposition 1 (carrier moments, stationarity, CLT, Berry–Esseen).** Assume:

- **(P1)** $T_j\ge 0$ for all $j$, $S_1>0$, $S_2>0$.
- **(P2)** The pattern entries $\{I_{n,j}\}$ are i.i.d. across $n$ and $j$ with mean $\mu_I>0$ and variance $\sigma_I^2>0$; the entries are nonnegative (so $B_n\ge 0$ a.s., and $B_n>0$ a.s. whenever $P(I=0)^{|\mathrm{supp}\,T|}=0$).
- **(P3)** (for the CLT) Spikiness $K_\infty\to\infty$ along the array, with the family $\{(I-\mu_I)^2\}$ uniformly integrable (automatic for a fixed pattern law).
- **(P4)** (for Berry–Esseen) $\nu_3 := \mathbb{E}|I-\mu_I|^3/\sigma_I^3<\infty$.

Then:

**(i) Exact moments and stationarity.** $\mathbb{E}B_n=\mu_I S_1$, $\operatorname{Var}B_n=\sigma_I^2 S_2$, hence $\mathrm{CV}_B=(\sigma_I/\mu_I)/\sqrt{K_{\mathrm{eff}}}$. The sequence $\{B_n\}_{n\ge1}$ is i.i.d., hence strictly stationary and white.

**(ii) CLT.** Under (P1)–(P3), $(B_n-\mu_I S_1)/(\sigma_I\sqrt{S_2}) \Rightarrow \mathcal N(0,1)$.

**(iii) Berry–Esseen.** Under (P4), for a universal constant $C$,
$$\sup_x\Big|\,P\Big(\tfrac{B_n-\mu_I S_1}{\sigma_I\sqrt{S_2}}\le x\Big)-\Phi(x)\Big| \;\le\; C\,\nu_3\,\frac{\sum_j |T_j|^3}{S_2^{3/2}} \;\le\; C\,\nu_3\,K_\infty^{-1/2}.$$
The correct CLT small parameter is $K_\infty^{-1/2}$, **not** $K_{\mathrm{eff}}^{-1}$.

**(iv) Higher cumulants and the log carrier.** For $r\ge 2$ the cumulants are $\kappa_r(B_n)=\kappa_r(I)\sum_j T_j^r$, so the standardized law of $B_n$ depends on $T$ through *all* ratios $\sum_j T_j^r/S_2^{r/2}$, $r\ge3$; these vanish as $K_\infty\to\infty$ but are not controlled by $K_{\mathrm{eff}}$ alone. Writing $B_n=\mu_I S_1(1+u_n)$ with $\mathbb{E}u_n=0$, $\operatorname{Var}u_n=(\sigma_I/\mu_I)^2/K_{\mathrm{eff}}$, a third-order Taylor expansion gives
$$\mathbb{E}\log B_n=\log(\mu_I S_1)-\tfrac12\operatorname{Var}(u_n)+O(\mathbb{E}|u_n|^3),\qquad \operatorname{Var}(\log B_n)=\frac{(\sigma_I/\mu_I)^2}{K_{\mathrm{eff}}}+O(\mathbb{E}|u_n|^3).$$

*Proof.* (i) Linearity of expectation and independence across $j$ give the mean and (Bienaymé) the variance; independence across $n$ gives the i.i.d. claim. (ii) Apply the Lindeberg–Feller CLT [Billingsley, *Probability and Measure*, Thm. 27.2] to the triangular array $X_j=T_j(I_{n,j}-\mu_I)$ with $s^2=\sigma_I^2 S_2$. Since $|X_j|\le \|T\|_\infty|I-\mu_I|$, the event $\{|X_j|>\varepsilon s\}$ is contained in $\{|I-\mu_I|>\varepsilon\sigma_I\sqrt{K_\infty}\}$, so the Lindeberg fraction is
$$\frac{1}{\sigma_I^2 S_2}\sum_j T_j^2\,\mathbb{E}\big[(I-\mu_I)^2\mathbf 1\{|X_j|>\varepsilon s\}\big]\;\le\;\frac{1}{\sigma_I^2}\,\mathbb{E}\big[(I-\mu_I)^2\mathbf 1\{|I-\mu_I|>\varepsilon\sigma_I\sqrt{K_\infty}\}\big]\;\longrightarrow\;0$$
by uniform integrability as $K_\infty\to\infty$. (iii) Esseen's inequality for sums of independent, non-identically distributed variables [Petrov, *Sums of Independent Random Variables*, Ch. V] gives the bound with third-moment ratio $\nu_3\sum_j|T_j|^3/S_2^{3/2}$, and $\sum_j|T_j|^3\le\|T\|_\infty S_2$ yields the $K_\infty^{-1/2}$ form. (iv) Cumulant homogeneity ($\kappa_r(cX)=c^r\kappa_r(X)$) and additivity over independent summands give the cumulant formula. The log expansion is Taylor's theorem with Lagrange remainder applied to $\log(1+u)$ on the event $\{|u_n|\le\tfrac12\}$. ∎

**Status of the log expansion (flagged).** Step (iv) is a **controlled moment expansion, not a distribution-free theorem**: making the $O(\mathbb{E}|u_n|^3)$ remainder rigorous, and ensuring integrability of $\log B_n$ near $B_n=0$, requires a high-probability bound $P(|u_n|>\tfrac12)$ decaying fast enough — e.g. sub-exponential pattern entries plus $K_\infty$-driven concentration, or a strictly positive pattern floor $I\ge I_{\min}>0$. In the source derivation this step is a moment calculation; we use it only through the variance scale $\sigma_{\mathrm{LR}}^2\asymp 1/K_{\mathrm{eff}}$ (per-frame and long-run variances coincide for the i.i.d. carrier) entering rate constants, never in identifiability statements. Zero and near-zero buckets are excluded here; the calibrated soft-log $\psi_\alpha(c)=\log(c+\alpha)$ of Appendix D (issue #3, Sec. 7) removes this restriction with a photon-dependent sensitivity factor.

**What this does not claim.** The proposition does not say the carrier law is determined by $(\mu_B,\sigma_B)$ — that reduction holds only at the Gaussian-approximation level; the exact law feels every weighted cumulant of $T$. For gain recovery this residual object dependence enters $m_T=\mathbb{E}\log B_n$ only as a *time-constant* scalar, absorbed by the global-scale gauge. It also does not assert cross-row decorrelation or window-energy whitening for structured (SRHT) carriers — those require the Walsh-spectrum/$K_4$ conditions of Appendix E, where $K_{\mathrm{eff}}$ alone is again insufficient.

### C.2 The quantitative stationarity condition (★)

**Definition (★)$(W,\epsilon,\delta)$.** Let $\{B_n\}_{n\le N}$ be the carrier and $W_n$ length-$W$ windows covering $\{1,\dots,N\}$. The carrier satisfies the *quantitative stationarity anchor* with tolerance $\epsilon$ and confidence $1-\delta$ if there exists a scalar $m_T\in\mathbb R$ (allowed to depend on $T$, not on $n$) such that
$$P\Big(\max_{1\le n\le N}\Big|\,W^{-1}\!\!\sum_{k\in W_n}\log B_k-m_T\Big|\le \epsilon\Big)\ \ge\ 1-\delta .$$
We say **(★) holds asymptotically** if for every $\delta>0$ there are windows $W=W_N\to\infty$, $W/N\to0$, with $\epsilon=\epsilon_{W,N,\delta}\to0$. The scalar $m_T$ is exactly the quantity absorbed by the global-scale gauge $a\mapsto ca$, $T\mapsto T/c$ (which shifts $m_T\mapsto m_T-\log c$, $\ell\mapsto\ell+\log c$, leaving $Y$ invariant).

### C.3 Proposition 2 — (★) is a window-estimator criterion, not a universal one

**Proposition 2.** Assume the drift is slow in the sense of hypothesis (B3) below, with $C_\beta L_a W^\beta\to0$. Then:

**(a) Equivalence for the windowed corrector.** The blind windowed estimator $\hat g_n=W^{-1}\sum_{k\in W_n}Y_k$ is uniformly consistent for $\ell_n+m_T$ (in probability, uniformly over $n$) **if and only if** (★) holds asymptotically.

**(b) (★) is not necessary for identifiability.** There are designs violating (★) that are nonetheless identifiable: a tall generic design with $N\ge K+p$ is exactly algebraically identifiable modulo scale (Theorem A′; see Appendix B) with *no* stationarity whatsoever — including deterministic ordered designs; likewise, $K_0\ge p-1$ known support zeros restore local identifiability under ordered Hadamard (see Appendix A).

**(c) (★) is not sufficient for algebraic identifiability.** There are settings where (★) holds yet exact separation of $(a,T)$ is impossible: (c1) any *square* random design $N=K$ — Proposition 1 gives (★), yet Theorem A applies to every invertible realization, so a nonconstant $s\in S$ still maps $(\ell,T)$ to an exact alias; (c2) a uniform random re-ordering $\pi$ of the *deterministic* ordered Hadamard record makes (★) hold without changing the coefficient multiset — hence without adding any algebraic information. Quantitatively, Serfling's inequality for sampling without replacement [Serfling, *Ann. Statist.* 2 (1974) 39] gives, for the finite population $g_k=\log B_k$ with variance $\tau_g^2$ and range $R_g$,
$$P\Big(\Big|W^{-1}\!\!\sum_{i=n}^{n+W-1} g_{\pi(i)}-\overline g\Big|\ge t\Big)\ \le\ 2\exp\!\Big[-\frac{W t^2}{2\tau_g^2+\tfrac23 R_g t}\Big],$$
so a union bound over the $\le N$ windows yields (★)$(W,\epsilon,\delta)$ whenever $\log N\ll W$ (and $W$ remains below the drift coherence time). This device fails when some $g_k$ are undefined (zero buckets) or the population log-variance/range is uncontrolled, and it does **not** deliver the small carrier variance $\sigma_{\mathrm{LR}}^2\asymp1/K_{\mathrm{eff}}$ of genuinely random nonnegative patterns.

*Proof.* (a) Decompose exactly
$$\hat g_n-(\ell_n+m_T)\;=\;\underbrace{\Big(W^{-1}\!\!\sum_{k\in W_n}\ell_k-\ell_n\Big)}_{\text{drift bias}}\;+\;\underbrace{\Big(W^{-1}\!\!\sum_{k\in W_n}\log B_k-m_T\Big)}_{\text{carrier deviation}} .$$
The drift bias is $\le C_\beta L_aW^\beta\to0$ deterministically by (B3). Hence $\max_n|\hat g_n-(\ell_n+m_T)|\to0$ in probability iff the maximal carrier deviation does — which is verbatim the asymptotic form of (★). Both implications are immediate from this identity. (b) Theorem A′ (see Appendix B) is proved without any distributional assumption on the carrier order; the support-zero criterion is Corollary 2 (see Appendix A). (c1) Theorem A (see Appendix A) holds for *any* invertible $M$, in particular a random draw, conditionally on the realization; (★), a statement about the temporal law, is unaffected. (c2) Serfling's bound plus the union over windows; the multiset $\{g_k\}$, hence every order-independent (algebraic) functional of the data, is invariant under $\pi$. ∎

**What this does not claim.** Part (a) is an equivalence for *one estimator family* (windowed local averages of $\log R_n$; the same proof covers kernel weights of matching order). It is not a characterization of identifiability by all mechanisms — (b) and (c) are precisely the two failure modes of that over-reading. Nor does (★) by itself bound the *rate*: rates require the variance model of Theorem B, and reconstruction quality after gain correction additionally requires the corrected linear inverse problem to be well posed (see Appendix F).

### C.4 Theorem B — statistical relative-gain identifiability

**Theorem B.** Assume:

- **(B1) Signal model.** $Y_n=\log R_n=\ell_n+m_T+z_n$, $n=1,\dots,N$, where $m_T=\mathbb{E}\log B_n$ is a time-constant scalar (finite by $B_n>0$ a.s. and $\mathbb{E}|\log B_n|<\infty$), and $z_n=\log B_n-m_T$.
- **(B2) Carrier noise.** $\{z_n\}$ is centered and strictly stationary, and *either* (B2a) $\alpha$-mixing with $\mathbb{E}|z_0|^{2+\eta}<\infty$ and $\sum_{h\ge1}\alpha(h)^{\eta/(2+\eta)}<\infty$, which by Davydov's covariance inequality [Davydov, *Theory Probab. Appl.* 13 (1968) 691] gives absolutely summable autocovariances and a finite long-run variance $\sigma_{\mathrm{LR}}^2=\operatorname{Var}z_0+2\sum_{h\ge1}\operatorname{Cov}(z_0,z_h)$; *or* (B2b), for high-probability bounds, $\beta$-mixing with $\beta(k)\le\beta_0\exp[-(k/b)^\kappa]$ and $\|z_n\|_{\psi_1}\le M$.
- **(B3) Slow drift.** $\ell\in S$ embeds in a discrete Hölder ball $H_\beta(L_a)$, $\beta\in(0,2]$, matched to the window order: $|W^{-1}\sum_{k\in W_n}\ell_k-\ell_n|\le C_\beta L_aW^\beta$ (for $\beta\in(1,2]$ this requires centered symmetric windows so the first-order bias cancels).
- **(B4) Window asymptotics.** $W=W_N\to\infty$, $W/N\to0$, and $L_aW^\beta\to0$.

Then:

**(i) Pointwise consistency with rate.** Under (B2a), $\mathbb{E}\big[\hat g_n-(\ell_n+m_T)\big]^2\le C\big(L_a^2W^{2\beta}+\sigma_{\mathrm{LR}}^2/W\big)\to0.$ Under (B2b), with block length $q=\lceil b\,[\log(4W/\delta)]^{1/\kappa}\rceil$, with probability $\ge1-\delta$,
$$\big|\hat g_n-(\ell_n+m_T)\big|\ \le\ C_\beta L_aW^\beta+C\Big[\sqrt{\tfrac{\nu_q^2\,q\log(4/\delta)}{W}}+\tfrac{Mq\log(4/\delta)}{W}\Big],$$
where $\nu_q^2$ is a block-variance proxy bounded by a multiple of $\sigma_{\mathrm{LR}}^2$; uniformity over $n\le N$ follows with $\delta\mapsto\delta/N$.

**(ii) Centered-gain recovery.** $\hat\ell_n^{\,c}:=\hat g_n-N^{-1}\sum_{m}\hat g_m$ satisfies $\mathbb{E}\big[\hat\ell_n^{\,c}-(\ell_n-\bar\ell)\big]^2\le 4C\big(L_a^2W^{2\beta}+\sigma_{\mathrm{LR}}^2/W\big)$; hence the relative gain $\ell_n-\bar\ell$ (equivalently $a_n$ up to one multiplicative constant) is identifiable and consistently estimable.

**(iii) Gauge.** The scalar $m_T+\bar\ell$ is *not* identifiable: for every $c>0$, the substitution $a\mapsto ca$, $T\mapsto T/c$ leaves the law of $\{Y_n\}$ exactly invariant while shifting $\ell\mapsto\ell+\log c$, $m_T\mapsto m_T-\log c$. This is precisely the constant direction $\mathrm{span}\{1\}\subset S$ of Theorem A, and it is the only ambiguity remaining.

*Proof.* (i) Bias–variance split as in Proposition 2(a). Bias: (B3). Variance: for a stationary sequence, $\operatorname{Var}\big(W^{-1}\sum_{k\in W_n}z_k\big)=W^{-1}\sum_{|h|<W}(1-|h|/W)\gamma(h)\le W^{-1}\sum_h|\gamma(h)|$, finite by (B2a)/Davydov; $(x+y)^2\le2x^2+2y^2$ combines the two. For (B2b), partition the window into alternating blocks of length $q$; the exponential $\beta$-mixing coupling replaces blocks by independent copies up to total-variation cost $W\beta(q)/q\le\delta/2$ by the choice of $q$, and Bernstein's inequality for independent sub-exponential block sums [Merlevède–Peligrad–Rio, *Probab. Theory Relat. Fields* 151 (2011) 435, and the standard blocking scheme] gives the display. (ii) $\hat\ell_n^{\,c}-(\ell_n-\bar\ell)=[\hat g_n-(\ell_n+m_T)]-N^{-1}\sum_m[\hat g_m-(\ell_m+m_T)]$; Jensen bounds the second term's second moment by the maximal pointwise one, and $(x+y)^2\le2x^2+2y^2$ gives the factor 4. (iii) Direct computation: $B_n(T/c)=B_n(T)/c$, so $Y_n$ is unchanged term by term; conversely, consistency in (ii) implies identifiability of the estimand $\ell_n-\bar\ell$ (two parameter configurations inducing the same law of $\{Y_n\}$ would force the same limit), so the ambiguity is exactly one dimensional. ∎

**What this does not claim.** Theorem B is a **statistical, asymptotic** statement about *relative*-gain recovery in a triangular array; it is not exact finite-sample algebraic identifiability of $(a,T)$ — Theorem A still holds verbatim for a square random design, and the two results are complementary, not in tension. It presupposes $B_n>0$ and integrable logs: in photon-counting records with empty bins the theorem must be replaced by its calibrated soft-log variant (see Appendix D; issue #3 Sec. 7), where $\psi_\alpha(c)=\log(c+\alpha)$, the calibration curve $m_\alpha$ is inverted, and the same bias–variance structure holds with sensitivity $\kappa_\alpha$ and photon-starved variance $\sim1/(W\bar\lambda)$. The constant $\sigma_{\mathrm{LR}}^2$ is a model input; identifying it with $(\sigma_I/\mu_I)^2/K_{\mathrm{eff}}$ invokes the flagged expansion of Proposition 1(iv). Finally, consistent gain correction does not by itself guarantee good reconstruction — the corrected inverse problem must be independently well posed, and the propagation of the residual gain variance $v$ through a basis with leverage $B_L$, floor $C_0/N$, and the $\rho_{\mathrm{pair}}$ flip boundary is the subject of Appendix F.

## Appendix D — Estimation rates, minimax lower bounds, and Fisher geometry

This appendix proves the rate and optimality statements of Sec. 6: the high-probability windowed-estimator bound (Theorem C's engine), its minimax optimality at the level of rates (Theorem D), the quotient-Fisher geometry underlying the identifiability dichotomy, and the low-photon soft-log rate. Notation is locked to the main text: $R_n=a_nB_n$, $\ell=\log a\in S$ with $\dim S=p$ and $\mathrm{span}\{1\}\subset S$, $Y_n=\log R_n=\ell_n+m_T+z_n$ with $m_T=\mathbb{E}\log B_n$ a time-independent scalar, windows $W$, and the spread functionals $K_{\mathrm{eff}}$, $K_\infty$ as in Appendix C. The Hölder smoothness order is written $\beta\in(0,2]$ with seminorm $L_a$ (the drift constant of Theorem C); the symbol $\alpha$ is reserved for the soft-log offset $\psi_\alpha(c)=\log(c+\alpha)$.

Throughout, the *discrete Hölder ball* $H_\beta(L_a)$ is defined operationally: $\ell$ belongs to $H_\beta(L_a)$ relative to a window family $\{W_n\}$ of order $\beta$ if the deterministic smoothing bias obeys
$$\Big|\,W^{-1}\!\!\sum_{k\in W_n}\ell_k-\ell_n\Big|\;\le\;C_\beta\,L_a\,W^{\beta}\qquad\text{for all }n. \tag{D.1}$$
For $\beta\in(0,1]$ a one-sided moving average of $\ell$ with modulus $|\ell_k-\ell_n|\le L_a|k-n|^{\beta}$ satisfies (D.1). For $\beta\in(1,2]$, (D.1) requires a *centered symmetric* window (or a kernel of order $\lfloor\beta\rfloor$), so that the first-order bias cancels and only curvature $L_2$ survives; a one-sided window does not attain $\beta>1$.

### D.1 Lemma D.1 (windowed gain-estimation rate under mixing)

**Statement.** Assume:

1. *(Model)* $Y_n=\ell_n+m_T+z_n$, with $\{z_n\}$ strictly stationary and $\mathbb{E}z_n=0$.
2. *(Mixing)* $\{z_n\}$ is $\beta$-mixing with $\beta(k)\le\beta_0\exp[-(k/b)^{\kappa}]$ for some $\beta_0,b>0$, $\kappa>0$.
3. *(Tails)* $\|z_n\|_{\psi_1}\le M$ (sub-exponential).
4. *(Smoothness)* $\ell\in H_\beta(L_a)$ in the sense (D.1), with the window order matched to $\beta$ as above.

Let $\hat g_n=W^{-1}\sum_{k\in W_n}Y_k$ and set $q=\lceil b\,[\log(4W/\delta)]^{1/\kappa}\rceil$. Then for each fixed $n$ and $\delta\in(0,1)$, with probability at least $1-\delta$,
$$\big|\hat g_n-(\ell_n+m_T)\big|\;\le\;C_\beta L_a W^{\beta}\;+\;C\Big[\sqrt{\tfrac{\nu_q^2\,q\,\log(4/\delta)}{W}}\;+\;\tfrac{M\,q\,\log(4/\delta)}{W}\Big], \tag{D.2}$$
where $\nu_q^2=\operatorname{Var}\!\big(q^{-1/2}\sum_{i=1}^{q}z_i\big)$ is the block-variance proxy; when the autocovariances are absolutely summable, $\nu_q^2\le C'\sigma_{\mathrm{LR}}^2$ with the long-run variance $\sigma_{\mathrm{LR}}^2$ as in Appendix C (hypothesis (B2a)). Uniformity over $n=1,\dots,N$ follows by replacing $\delta$ with $\delta/N$ (a $\log N$ inflation inside the brackets).

*(Expectation version, weaker hypotheses.)* If instead $\{z_n\}$ is only $\alpha$-mixing with $\sum_{h\ge1}\alpha(h)^{\eta/(2+\eta)}<\infty$ and $\|z_0\|_{2+\eta}<\infty$ for some $\eta>0$, then
$$\mathbb{E}\big[\hat g_n-(\ell_n+m_T)\big]^2\;\le\;C\,L_a^2W^{2\beta}+C\,\sigma_{\mathrm{LR}}^2/W. \tag{D.3}$$

**Proof.** *Bias.* $\hat g_n-(\ell_n+m_T)=\big[W^{-1}\sum_k\ell_k-\ell_n\big]+W^{-1}\sum_k z_k$; the first bracket is bounded by $C_\beta L_aW^\beta$ by (D.1).

*Fluctuation, high probability.* Partition the window $W_n$ into $m=\lceil W/q\rceil$ consecutive blocks of length $q$ and separate them into odd- and even-indexed families. By Berbee's coupling lemma [Berbee 1979; see Rio, *Asymptotic Theory of Weakly Dependent Random Processes*, 2017], on an enlarged probability space each family can be replaced by a sequence of *independent* blocks with the same marginals, at total-variation cost at most $m\,\beta(q)\le \beta_0\,W\exp[-(q/b)^{\kappa}]$. The choice $q=\lceil b[\log(4W/\delta)]^{1/\kappa}\rceil$ makes this cost at most $\delta/2$ (adjusting $\beta_0$ into $C$). On the coupling event, each family is a sum of independent block sums $S_j=\sum_{i\in\text{block }j}z_i$ with $\|S_j\|_{\psi_1}\le CqM$ (triangle inequality for the $\psi_1$ norm) and $\operatorname{Var}(S_j)=q\,\nu_q^2$. Bernstein's inequality for sums of independent sub-exponential variables [e.g. Vershynin, *High-Dimensional Probability*, Thm. 2.8.1] applied to each family, with a union bound over the two families (whence the $4/\delta$), yields the bracketed term in (D.2) with the characteristic Gaussian-plus-linear tail: a $\sqrt{\nu_q^2 q\log(4/\delta)/W}$ moderate-deviation term and an $Mq\log(4/\delta)/W$ heavy-tail correction. When $\sum_h|\operatorname{Cov}(z_0,z_h)|<\infty$, $\nu_q^2=\operatorname{Var}(z_0)+2\sum_{h=1}^{q-1}(1-h/q)\operatorname{Cov}(z_0,z_h)\le C'\sigma_{\mathrm{LR}}^2$.

*Fluctuation, expectation.* Davydov's covariance inequality [Davydov 1968] gives $|\operatorname{Cov}(z_0,z_h)|\le 8\,\alpha(h)^{\eta/(2+\eta)}\|z_0\|_{2+\eta}^2$; the summability hypothesis makes the autocovariance series absolutely summable, so $\operatorname{Var}(W^{-1}\sum_{k\in W_n}z_k)\le \bar\sigma^2/W$ with $\bar\sigma^2\le C\sigma_{\mathrm{LR}}^2$. Combining with the squared bias via $(x+y)^2\le2x^2+2y^2$ gives (D.3). $\blacksquare$

**Corollary D.2 (optimized rate = Theorem C's high-photon case).** Minimizing the right side of (D.3) over $W$ gives
$$W^{*}\asymp\big(\sigma_{\mathrm{LR}}^2/L_a^2\big)^{1/(2\beta+1)},\qquad \mathrm{MSE}^{*}\asymp L_a^{2/(2\beta+1)}\,\sigma_{\mathrm{LR}}^{4\beta/(2\beta+1)}, \tag{D.4}$$
valid when $W^{*}\in[1,N]$ and $W^{*}$ is shorter than the gain coherence time; otherwise the boundary window $W=1$ or $W=N$ applies. For $\beta=1$ with per-frame drift scale $L_1\asymp s\rho_{\mathrm{pair}}$ (adjacent-frame decorrelation convention — *not* $\rho_{\mathrm{bw}}$), this is $\mathrm{MSE}^{*}\asymp\sigma_{\mathrm{LR}}^{4/3}(s\rho_{\mathrm{pair}})^{2/3}$; for random carriers, $\sigma_{\mathrm{LR}}^2\approx(\sigma_I/\mu_I)^2/K_{\mathrm{eff}}$ under the spikiness condition $K_\infty\to\infty$ of Prop. 1.

**What this does not claim.** The constants $C,C_\beta$ are not tracked and depend on the mixing constants $(\beta_0,b,\kappa)$ and $M$. The bound is for the *relative* gain $\ell_n+m_T$; the scalar $m_T+\text{gauge}(\ell)$ is not estimable (Theorem B). Nothing is claimed for $\beta>2$ (would need local polynomials), for non-stationary carriers, or about *adaptive* window selection when $(\beta,L_a)$ are unknown. The step $\nu_q^2\lesssim\sigma_{\mathrm{LR}}^2$ requires summable autocovariances, which the stated mixing plus moment hypotheses supply.

### D.2 Theorem D (minimax lower bounds; rate level, constants open)

**Statement.** *(Hölder / Assouad–two-point.)* Consider the i.i.d. Gaussian submodel $z_n\sim\mathcal N(0,\sigma^2)$ — a member of the model class of Lemma D.1. Then for every $n$ interior to the design,
$$\inf_{\hat\ell}\ \sup_{\ell\in H_\beta(L_a)}\ \mathbb{E}\big(\hat\ell_n-\ell_n\big)^2\;\ge\;c_\beta\,L_a^{2/(2\beta+1)}\,\sigma^{4\beta/(2\beta+1)}, \tag{D.5}$$
the infimum over all measurable estimators of the gauge-fixed log-gain. In normalized continuous time ($N$ samples on $[0,1]$, bandwidth $h=W/N$) the equivalent form is $\inf\sup\mathbb{E}(\hat\ell(t)-\ell(t))^2\ge c\,(\sigma^2/N)^{2\beta/(2\beta+1)}L^{2/(2\beta+1)}$.

*(Sobolev / van Trees–Pinsker.)* In the Gaussian sequence formulation — expand $\ell(t)=\sum_j\theta_j\varphi_j(t)$ in a Fourier basis and impose the Sobolev ellipsoid $\sum_j j^{2\beta}\theta_j^2\le L^2$ — the integrated risk obeys
$$\inf_{\hat\ell}\ \sup_{\|\ell\|_{H^\beta}\le L}\ \frac1N\sum_n\mathbb{E}(\hat\ell_n-\ell_n)^2\;\ge\;c_\beta\,L^{2/(2\beta+1)}(\sigma^2/N)^{2\beta/(2\beta+1)}, \tag{D.6}$$
with the gauge direction (the constant mode, confounded with $m_T$) excluded from the risk. Consequently the windowed estimator of Lemma D.1 is **minimax-rate optimal** over $H_\beta(L_a)$ for $\beta\le1$ with one-sided windows and for $\beta\le 2$ with centered symmetric windows. **Sharp minimax constants are open** (this is Theorem D of the main text).

**Proof.** *Two-point (pointwise).* Fix $n_0$ and let $\phi$ be a fixed $C^\infty$ bump, $\mathrm{supp}\,\phi\subset[-1,1]$, $\phi(0)=1$, $\|\phi\|_{H_\beta}\le1$. Take the hypotheses $\ell^{(0)}\equiv0$ and $\ell^{(1)}_k=L_a W_0^{\beta}\phi\big((k-n_0)/W_0\big)$; both lie in $H_\beta(L_a)$ (up to an absolute constant absorbed into $c_\beta$). Since the noise is i.i.d. Gaussian, the Kullback–Leibler divergence between the two data laws is $\mathrm{KL}=\tfrac{1}{2\sigma^2}\sum_k(\ell^{(1)}_k)^2\le C\,L_a^2W_0^{2\beta+1}/\sigma^2$. Choosing $W_0\asymp(\sigma^2/L_a^2)^{1/(2\beta+1)}$ makes $\mathrm{KL}\le c<\infty$, and the two hypotheses are separated at $n_0$ by $|\ell^{(1)}_{n_0}-\ell^{(0)}_{n_0}|=L_aW_0^{\beta}$. Le Cam's two-point lemma [Tsybakov, *Introduction to Nonparametric Estimation*, 2009, §2.4] then gives (D.5). The nuisance scalar $m_T$ only enlarges the model, so the bound holds a fortiori; the bumps can be taken mean-centered over the record so that the two hypotheses differ in the gauge-invariant component $\ell-\bar\ell$ itself. For the integrated version, tile $[1,N]$ with $\sim N/W_0$ disjoint bumps carrying independent signs and apply Assouad's lemma [Tsybakov 2009, Thm. 2.12].

*van Trees / Pinsker.* In the sequence model $y_j=\theta_j+ (\sigma/\sqrt N)\epsilon_j$ (exact for equispaced discrete-Fourier regression with white Gaussian noise), place independent priors $\theta_j\sim\mathcal N(0,\tau_j^2)$ truncated inside the ellipsoid. The van Trees inequality [Gill–Levit 1995] bounds the Bayes risk of each coordinate by the reciprocal of (data Fisher + prior Fisher): $\text{BayesRisk}\ge\sum_j(N/\sigma^2+\tau_j^{-2})^{-1}$, the constant mode omitted (gauge). Maximizing the right side over prior spectra supported in the ellipsoid is Pinsker's calculation [Pinsker 1980] and yields the scaling (D.6). Since minimax risk dominates Bayes risk, (D.6) follows. $\blacksquare$

**What this does not claim.** (i) Constants: neither $c_\beta$ nor a Pinsker-type sharp constant is claimed for our model; the exact Pinsker constant transfers only where the acquisition is genuinely the Gaussian sequence model — for mixing, non-Gaussian carriers the statement is at rate level only (a Brown–Low-type asymptotic-equivalence argument would be needed for more, and is not attempted). (ii) The lower bound is proven inside the i.i.d. Gaussian *submodel*; this suffices for minimaxity of the full class (sup over the class dominates sup over the submodel, while the upper bound (D.3) holds over the full class), but no lower bound is claimed *within* every fixed mixing law. (iii) No adaptivity claim: rate optimality is for known $(\beta,L_a)$.

### D.3 Proposition D.4 (quotient Fisher geometry: singularity ⇔ the Theorem-A ambiguity)

**Statement.** *(a) Linear-Gaussian window model.* Let $\ell=U\theta$ with $U\in\mathbb R^{N\times p'}$, and observe $Y=U\theta+m\mathbf 1+z$, $z\sim\mathcal N(0,\Sigma)$, $\Sigma\succ0$ known, $m\in\mathbb R$ the unknown carrier log-mean (confounded with global gain scale). The Fisher information for $\theta$ after eliminating the nuisance $m$ is
$$I_\theta\;=\;U^{\top}\Sigma^{-1/2}P_\perp\Sigma^{-1/2}U,\qquad P_\perp=I-\frac{\Sigma^{-1/2}\mathbf 1\mathbf 1^{\top}\Sigma^{-1/2}}{\mathbf 1^{\top}\Sigma^{-1}\mathbf 1}. \tag{D.7}$$
For a linear functional $L\theta$: if $\mathrm{row}(L)\subseteq\mathrm{range}(I_\theta)$, every unbiased estimator obeys $\operatorname{Cov}(L\hat\theta)\succeq L\,I_\theta^{+}L^{\top}$ (Moore–Penrose CRB for singular information [Rao–Mitra; Stoica–Marzetta 2001]); if $L$ has a nonzero component along $\ker I_\theta$, **no unbiased estimator of $L\theta$ exists and the CRB is infinite** — the functional is not locally estimable.

*(b) Quotient statement.* Let $\Theta$ be the parameter manifold, $G$ the global-scale group $(a,T)\mapsto(ca,T/c)$, and $P_\theta$ a dominated model differentiable in quadratic mean. Define the quotient score operator $S_\theta:T_{[\theta]}(\Theta/G)\to L_0^2(P_\theta)$ and $I_\theta=S_\theta^{*}S_\theta$. Then: $I_\theta\succ0$ on $T_{[\theta]}(\Theta/G)$ **iff** $[\theta]\mapsto P_\theta$ is an immersion, i.e. iff the model is *locally differentially identifiable* modulo scale. Any $C^1$ ambiguity curve $[\theta(t)]$ with $P_{\theta(t)}=P_{\theta(0)}$ satisfies $S_\theta\theta'(0)=0$, hence produces a Fisher null direction. For the Theorem-A ambiguity this implication is *exact*: the explicit data-preserving path $\ell'=\ell+ts$, $T'=M^{-1}(c\odot e^{-ts})$, $s\in S\setminus\mathrm{span}\{1\}$, is a genuine ambiguity curve for a square invertible design, so the Fisher matrix in the full $(\ell,T)$ parameterization is singular along its tangent, and the CRB is $+\infty$ for every functional that varies along it.

*(c) Local-window corollary.* For a window over which $\ell$ is approximately constant, the Gaussian CRB reduces to $\operatorname{Var}(\hat\ell_n)\ge\sigma_z^2/W_{\mathrm{eff}}$ with $W_{\mathrm{eff}}=W/(1+2\sum_h\rho_z(h))$ under weak dependence (equivalently, $\sigma_z^2$ replaced by the long-run variance) — the Fisher-side counterpart of the $\sigma_{\mathrm{LR}}^2/W$ term in (D.3).

**Proof.** *(a)* The joint Fisher matrix of $(\theta,m)$ in the Gaussian model is the block matrix $\begin{pmatrix}U^{\top}\Sigma^{-1}U & U^{\top}\Sigma^{-1}\mathbf 1\\ \mathbf 1^{\top}\Sigma^{-1}U & \mathbf 1^{\top}\Sigma^{-1}\mathbf 1\end{pmatrix}$. Nuisance elimination is the Schur complement with respect to the $m$-block [Lehmann–Casella, *Theory of Point Estimation*, §6], which is exactly (D.7). The pseudoinverse CRB for singular FIM is Stoica–Marzetta (2001). The infinite-CRB claim is cleanest without CRB machinery: a direction $u\in\ker I_\theta$ that is tangent to an exact ambiguity curve leaves the data law invariant, so any estimator has *identical* distribution under $\theta$ and $\theta+tu$; unbiasedness for a functional with $Lu\neq0$ would force $L\theta=L(\theta+tu)$, a contradiction — hence no unbiased finite-variance estimator exists.

*(b)* Differentiability in quadratic mean makes $S_\theta$ well defined and $I_\theta=S_\theta^*S_\theta$ the pullback metric [van der Vaart, *Asymptotic Statistics*, Ch. 7]. $I_\theta\succ0$ iff $S_\theta$ is injective iff the differential of $[\theta]\mapsto\sqrt{dP_\theta}$ is injective, i.e. an immersion. The ambiguity-curve implication is the chain rule: $t\mapsto P_{\theta(t)}$ constant $\Rightarrow$ its $L^2$ derivative $S_\theta\theta'(0)$ vanishes. For Theorem A the curve is explicit (see Appendix A), so no genericity is needed. $\blacksquare$

**What this does not claim.** The converse direction — Fisher singularity implying an actual *ambiguity manifold* — requires constant-rank (or analytic) regularity so that the rank defect integrates (rank theorem); Fisher singularity by itself only defeats *local differential* identifiability. Nonsingular Fisher does not exclude isolated *global* aliases. Part (a) assumes Gaussian noise with known $\Sigma$; part (c) is a Gaussian-model computation used as an order-of-magnitude floor, not a bound proven for the actual log-carrier distribution. No efficiency claim is made for the windowed estimator beyond rate (constants open, Theorem D).

### D.4 Theorem C (low-photon soft-log rate and the $1/(W\bar\lambda)$ law)

**Statement.** Let counts follow the calibrated model $C_n\mid B_n,\ell_n\sim\mathrm{Pois}(\lambda_n)$, $\lambda_n=\Lambda_0e^{\ell_n}B_n+d$, with $d\ge0$ dark counts and $\{B_n\}$ the stationary random carrier. Fix $\alpha>0$, let $\psi_\alpha(c)=\log(c+\alpha)$, define the calibration curve $m_\alpha(\theta)=\mathbb{E}[\psi_\alpha(C)]$ for $C\mid B\sim\mathrm{Pois}(\Lambda_0e^{\theta}B+d)$, and the estimator $\hat\theta_n=m_\alpha^{-1}\big(W^{-1}\sum_{k\in W_n}\psi_\alpha(C_k)\big)$ (global-scale gauge imposed). Assume:

1. $\{\psi_\alpha(C_n)\}$ is stationary and $\beta$-mixing after removing the slow gain, with long-run variance $\sigma_{\alpha,\mathrm{LR}}^2$;
2. $\ell\in H_\beta(L_a)$, $\beta\in(0,2]$, in the sense (D.1);
3. on the operating gain range, $0<\kappa_{\min}\le m_\alpha'(\theta)\le\kappa_{\max}<\infty$.

Then
$$\mathbb{E}\big(\hat\theta_n-\ell_n-\mathrm{gauge}\big)^2\;\le\;C\Big(\tfrac{\kappa_{\max}}{\kappa_{\min}}\Big)^{2}L_a^2W^{2\beta}\;+\;C\,\frac{\sigma_{\alpha,\mathrm{LR}}^2}{\kappa_{\min}^2\,W}, \tag{D.8}$$
and optimizing over $W$,
$$\mathrm{MSE}_\alpha^{*}\;\le\;C\,\kappa_{\min}^{-2}\,\big[\kappa_{\max}L_a\big]^{2/(2\beta+1)}\,\sigma_{\alpha,\mathrm{LR}}^{4\beta/(2\beta+1)} \tag{D.9}$$
— Theorem C of the main text. In the photon-starved regime $\bar\lambda\ll1$ the variance term of (D.8) becomes $C/(W\bar\lambda)$, which is minimax-*order* sharp: the Poisson Fisher information for the log-intensity parameter is $I(\theta)=\lambda$, so $W$ counts carry information $\asymp W\bar\lambda$ and no estimator improves on the $1/(W\bar\lambda)$ order (van Trees). Zeros only reduce Fisher information; they never make the estimator diverge.

**Proof.** *Sensitivity and variance of the soft-log.* The Poisson derivative identity $\frac{d}{d\lambda}\mathbb{E}f(C)=\mathbb{E}[f(C{+}1)-f(C)]$ (differentiate $\sum_c e^{-\lambda}\lambda^c f(c)/c!$ term by term) gives
$$\kappa_\alpha(\lambda):=\frac{d}{d\log\lambda}\mathbb{E}\log(C+\alpha)=\lambda\,\mathbb{E}\log\frac{C+1+\alpha}{C+\alpha},$$
with the expansions $\kappa_\alpha(\lambda)=1+O(1/\lambda)$ for $\lambda\gg1$ and $\kappa_\alpha(\lambda)=\lambda\log(1+1/\alpha)+O(\lambda^2)$ for $\lambda\ll1$. The Poisson Poincaré inequality [Klaassen 1985; Bobkov–Ledoux 1998], $\operatorname{Var}f(C)\le\lambda\,\mathbb{E}[(f(C{+}1)-f(C))^2]$, yields $\operatorname{Var}[\psi_\alpha(C)]=O(1/\lambda)$ at high $\lambda$ and $=\lambda\log^2(1+1/\alpha)+O(\lambda^2)$ at low $\lambda$. These verify that hypothesis 3 holds with $\kappa_{\min}\asymp c_\alpha\bar\lambda$ in the starved regime and $\kappa_{\min}\approx\kappa_{\max}\approx1$ at high counts.

*Rate.* Write $Y_k=\psi_\alpha(C_k)$ and decompose
$$W^{-1}\!\!\sum_{k\in W_n}\!Y_k-m_\alpha(\ell_n)=\Big[W^{-1}\!\!\sum_k m_\alpha(\ell_k)-m_\alpha(\ell_n)\Big]+\Big[W^{-1}\!\!\sum_k\big(Y_k-m_\alpha(\ell_k)\big)\Big].$$
Since $m_\alpha$ is $\kappa_{\max}$-Lipschitz on the gain range, $m_\alpha\circ\ell$ inherits the discrete Hölder modulus scaled by $\kappa_{\max}$, so the first bracket is $\le C\kappa_{\max}L_aW^{\beta}$ by (D.1). The second bracket is a window average of centered stationary $\beta$-mixing variables; the expectation bound of Lemma D.1 controls its variance by $C\sigma_{\alpha,\mathrm{LR}}^2/W$. Because $m_\alpha'\ge\kappa_{\min}>0$, $m_\alpha$ is strictly increasing and $m_\alpha^{-1}$ is $1/\kappa_{\min}$-Lipschitz (inverse function theorem); composing and squaring gives (D.8), and the standard bias–variance optimization gives (D.9).

*Photon-starved limit.* Substituting $\kappa_{\min}\asymp c_\alpha\bar\lambda$ and $\sigma_{\alpha,\mathrm{LR}}^2\asymp c_\alpha^2\bar\lambda$ into the variance term of (D.8) gives $\sigma_{\alpha,\mathrm{LR}}^2/(\kappa_{\min}^2W)\asymp1/(W\bar\lambda)$. **This substitution is a leading-order moment calculation**: it identifies the long-run variance with the single-count variance (neglecting residual temporal correlation of the carrier at low counts) and uses the small-$\lambda$ expansions above; the *order* is what is claimed, not the constant. Sharpness at rate level: for $\theta=\log$-intensity, $I(\theta)=(\partial_\theta\lambda)^2/\lambda=\lambda$; independence across frames gives total information $\asymp W\bar\lambda$, and the van Trees inequality converts this into a $c/(W\bar\lambda)$ lower bound on the local MSE of any estimator. $\blacksquare$

**Shrinkage-bias caveat (load-bearing, per Sec. 6).** For $\bar\lambda<1$ the estimator is *bias-dominated*: the mass at $C=0$ pulls $W^{-1}\sum\psi_\alpha$ toward $\log\alpha$, and the amplification factor $(\kappa_{\max}/\kappa_{\min})^2$ in the bias term of (D.8) blows up as $\kappa_{\min}\propto\bar\lambda\to0$. Empirically the MSE can then sit *below* the Fisher reference curve — that is bias, not super-efficiency, and it does not contradict the lower bound (which constrains variance-limited, locally unbiased behavior). The $1/(W\bar\lambda)$ law is asserted only in the variance-limited regime above the $\bar\lambda\sim1$ crossover; below it, honest accounting reports the bias floor. Recovering the rate there requires the offset-design, Anscombe ($2\sqrt{C+3/8}$), or full Poisson-mixture MLE variants; for the mixture MLE the claim $\mathrm{MSE}\approx1/(WJ(\theta))$ with $J\sim\mathbb{E}\lambda$ at low photons is standard parametric asymptotics under regularity of the mixture likelihood and is *not* re-proven here.

**What this does not claim.** No absolute gain scale is estimated (gauge remains). The calibration curve $m_\alpha$ is assumed known (flat-field) or jointly calibrated up to scale; miscalibration adds a bias not covered by (D.8). Constants in (D.8)–(D.9) depend on the mixing constants of $\psi_\alpha(C_n)$ and are not tracked. As $\Phi\to0$ with no offset and no reference, Fisher information for the gain vanishes — an information limit no estimator evades (Sec. 10). Finally, (D.9) is an upper bound whose minimax matching is at rate level only, inherited from Theorem D.

## Appendix E — SRHT whitening: exact Walsh condition and permutation bounds

This appendix proves the claims of Sec. 7: the exact covariance identity $\operatorname{Cov}_D(Z_g,Z_h)=\hat w(g+h)$, the necessary-and-sufficient Walsh-flatness conditions for sign-only whitening (pairwise, spectral-window, and window-average forms), the Bernstein–Serfling permutation bound and its union-bound corollary, the permutation-alone carrier-variance identity with its flat-object counterexample, and the Hanson–Wright window-energy bound. Full derivations first appeared in the public review record (issue #2, Secs. 2–3, with the window-energy bound from issue #1, Sec. 1); they are reproduced here in archival form.

### E.0 Setting and standing assumptions

**(E1)** $K=2^m$ and pixels are indexed by the Walsh group $G=\mathbb{F}_2^m$, with characters $\chi_g(j)=(-1)^{g\cdot j}$, unnormalized Hadamard matrix $H_{g,j}=\chi_g(j)$, and orthonormal carrier $U=K^{-1/2}H$. For every $g\neq 0$, $\chi_g$ is balanced: exactly $K/2$ entries equal $+1$.

**(E2)** The object $T\in\mathbb{R}^K$ is deterministic and nonzero. Write $w_j=T_j^2$; $S_1$, $S_2$, and the spread functionals $K_{\mathrm{eff}}$, $K_\infty$, $K_4$ are as in Appendix C. The Walsh transform of $w$ is $\hat w(h)=\sum_j \chi_h(j)\,w_j$, so $\hat w(0)=S_2$.

**(E3)** The SRHT coefficient vector is $x=UDPT$, where $D=\mathrm{diag}(\eta_1,\dots,\eta_K)$ with i.i.d. Rademacher signs $\eta_j$, and $P$ is a uniformly random pixel permutation independent of $D$. The normalized carrier is $Z_g=\sqrt{K}\,x_g=\sum_j \chi_g(j)\,\eta_j\,(PT)_j$. Physical nonnegative patterns are the offset form $B_g=\mu S_1+\sigma Z_g$ with positivity margin $\mu S_1>\sigma|Z_g|$; the bucket record is $R_n=a_nB_n$ with $\ell=\log a$ as in the main text. A *window* is a subset $A\subset G$ of $W=|A|$ rows.

Permutation leaves $S_1$, $S_2$, $K_{\mathrm{eff}}$, $K_4$, $K_\infty$ invariant; it only reorders $w$, i.e. replaces $\hat w$ by $\widehat{w^P}$ with $w^P_j=T^2_{Pj}$.

### E.1 The exact covariance identity

> **Lemma E.1.** Under (E1)–(E3) with $P$ fixed (in particular $P=\mathrm{id}$), $\mathbb{E}_D Z_g=0$ and for all $g,h\in G$
> $$\operatorname{Cov}_D(Z_g,Z_h)\;=\;\sum_j \chi_{g+h}(j)\,(PT)_j^2\;=\;\widehat{w^P}(g+h). \tag{E.1}$$

**Proof.** $\mathbb{E}\eta_j=0$ gives the mean. Since $\mathbb{E}\,\eta_i\eta_j=\delta_{ij}$,
$$\mathbb{E}_D Z_gZ_h=\sum_{i,j}\chi_g(i)\chi_h(j)(PT)_i(PT)_j\,\mathbb{E}\eta_i\eta_j=\sum_j \chi_g(j)\chi_h(j)(PT)_j^2,$$
and $\chi_g\chi_h=\chi_{g+h}$ by the character property of the Walsh group. $\blacksquare$

Consequently the covariance of any window $A$ is the pattern matrix $\Gamma_A(g,h)=\widehat{w^P}(g+h)$, and, normalized by the common marginal variance $S_2$, $\Gamma_A/S_2=I_A+R_A$ with off-diagonal entries $R_A(g,h)=\widehat{w^P}(g+h)/S_2$, $g\neq h$. The entire gain–object coupling of sign-randomized acquisition is therefore carried by the non-DC Walsh spectrum of the squared (permuted) object — nothing else.

### E.2 Sign-only whitening: necessary and sufficient conditions

> **Theorem E.2 (exact Walsh condition).** Under (E1)–(E3) with no permutation ($P=\mathrm{id}$):
> 1. *(exact pairwise)* $\operatorname{Cov}_D(Z_g,Z_h)=S_2\,\delta_{g,h}$ for all $g,h$ **iff** $\hat w(q)=0$ for every $q\neq0$, equivalently **iff** $T_j^2=S_2/K$ for all $j$ ($T^2$ flat).
> 2. *(pairwise $\varepsilon$-whitening)* $|\operatorname{Cov}_D(Z_g,Z_h)|\le\varepsilon S_2$ for all $g\neq h$ **iff** $\max_{q\neq0}|\hat w(q)|\le\varepsilon S_2$.
> 3. *(spectral window)* For a window class $\mathcal{A}$, $\|\Gamma_A/S_2-I_A\|_{\mathrm{op}}\le\varepsilon$ for all $A\in\mathcal{A}$ **iff** $\sup_{A\in\mathcal{A}}\|R_A\|_{\mathrm{op}}\le\varepsilon$.
> 4. *(window average)* With $\bar Z_A=W^{-1}\sum_{g\in A}Z_g$ and multiplicity $m_A(q)=\#\{(g,h)\in A\times A: g\neq h,\ g+h=q\}$, the variance $\operatorname{Var}(\bar Z_A)$ lies in $[(1\mp\varepsilon)S_2/W]$ for every $A\in\mathcal{A}$ **iff** $\sup_{A\in\mathcal{A}}\big|\sum_{q\neq0}m_A(q)\,\hat w(q)\big|\le\varepsilon\,W S_2$.

**Proof.** (1) If whitening holds, then for any $q\neq0$ pick $g,h$ with $g+h=q$ (always possible in $G$); (E.1) forces $\hat w(q)=0$. Conversely, vanishing non-DC coefficients make (E.1) equal $S_2\delta_{g,h}$. The flatness equivalence is Walsh inversion: the transform is invertible, so $\hat w$ supported on $\{0\}$ iff $w$ is constant, i.e. $T_j^2=S_2/K$. (2) Immediate from (E.1) after dividing by $S_2$. (3) The normalized window covariance *is* $I_A+R_A$; the statement is definitional. (4) Direct expansion:
$$\operatorname{Var}(\bar Z_A)=W^{-2}\!\!\sum_{g,h\in A}\hat w(g+h)=\frac{S_2}{W}+W^{-2}\sum_{q\neq0}m_A(q)\,\hat w(q),$$
and the two-sided requirement is exactly the stated inequality. $\blacksquare$

Two standard reductions relate the forms. If $\mathcal{A}$ contains all two-point windows, (3) implies (2), and (2) is the sharpest scalar condition. In the converse direction, since $R_A$ has zero diagonal, Gershgorin's disc theorem gives $\|R_A\|_{\mathrm{op}}\le(W-1)\max_{q\neq0}|\hat w(q)|/S_2$, so pairwise condition (2) at tolerance $\varepsilon/(W_{\max}-1)$ implies spectral condition (3) for all windows with $W\le W_{\max}$. This Gershgorin step is a (generally loose) sufficient bound, not an equivalence.

The obstruction is sharp: if $T^2$ is aligned with the positive support of a single character $\chi_q$, then $|\hat w(q)|=S_2$ and the row pair $(g,h)$ with $g+h=q$ is *perfectly* correlated under sign randomization. Signs cannot remove this; it is a property of the object's pixel ordering.

**What this does not claim.** Theorem E.2 characterizes second-moment decorrelation over the sign draw for a *fixed* object and ordering; it does not assert Gaussianity of $Z_g$ (a Rademacher sum, whose normal approximation requires $K_\infty\to\infty$ with Berry–Esseen error $\lesssim K_\infty^{-1/2}$), independence of rows, or anything about noise, gain drift, or estimation error — those enter through Secs. 5–6 and Appendix F. It is also a statement about the design/object pair, not a high-probability event: no randomness beyond $D$ is involved.

### E.3 Random permutation as a probabilistic Walsh-flattener

By Lemma E.1, Theorem E.2 holds verbatim for a realized permutation $P$ with $w$ replaced by $w^P$: the *deterministic* necessary-and-sufficient condition remains Walsh-flatness, now of the permuted squared object. A random $P$ makes that condition likely.

> **Theorem E.3 (Bernstein–Serfling permutation bound).** Under (E1)–(E3), there exist universal constants $c,C>0$ such that for every fixed $q\neq0$ and $\varepsilon>0$,
> $$\Pr_P\!\big(|\widehat{w^P}(q)|\ge\varepsilon S_2\big)\;\le\;2\exp\!\big[-c\min(\varepsilon^2K_4,\ \varepsilon K_\infty)\big], \tag{E.2}$$
> and by the union bound over the $K-1$ nonzero frequencies,
> $$\Pr_P\!\big(\max_{q\neq0}|\widehat{w^P}(q)|\ge\varepsilon S_2\big)\;\le\;2(K-1)\exp\!\big[-c\min(\varepsilon^2K_4,\ \varepsilon K_\infty)\big]. \tag{E.3}$$
> In particular, pairwise $\varepsilon$-whitening (Theorem E.2(2) for $w^P$) holds with probability at least $1-\delta$ whenever
> $$\min(\varepsilon^2K_4,\ \varepsilon K_\infty)\;\ge\;C\log(K/\delta). \tag{E.4}$$

**Proof.** Fix $q\neq0$ and let $A_q=\{j:\chi_q(j)=+1\}$, so $|A_q|=K/2$ by (E1). Then
$$\widehat{w^P}(q)=\sum_{j\in A_q}w^P_j-\sum_{j\notin A_q}w^P_j=2\sum_{j\in A_q}w^P_j-S_2,$$
a centered sum of $n=K/2$ draws *without replacement* from the finite population $\{w_1,\dots,w_K\}$ with mean $\mu_w=S_2/K$. Its exact variance is $n\sigma_w^2\frac{K-n}{K-1}\le\frac{K}{4}\sigma_w^2\le\frac14\sum_j w_j^2=\frac{S_2^2}{4K_4}$, where $\sigma_w^2=K^{-1}\sum_j(w_j-\mu_w)^2$; and each summand satisfies $0\le w_j\le\|T\|_\infty^2=S_2/K_\infty$. The Bernstein inequality for sampling without replacement (Serfling 1974; the Bernstein–Serfling form of Bardenet–Maillard 2015) then gives, for $t>0$,
$$\Pr\big(|\widehat{w^P}(q)|\ge t\big)\le2\exp\!\Big[-c\min\Big(\frac{t^2}{S_2^2/K_4},\ \frac{t}{S_2/K_\infty}\Big)\Big].$$
Setting $t=\varepsilon S_2$ yields (E.2); (E.3) is the union bound; (E.4) follows by requiring the right side of (E.3) to be at most $\delta$ and absorbing the factor $2(K-1)$ into $C\log(K/\delta)$. $\blacksquare$

**What this does not claim.** (E.2)–(E.4) are *sufficient* high-probability conditions with unspecified universal constants; they are not the deterministic criterion for a realized acquisition — that remains Walsh-flatness of $w^P$ (Theorem E.2), which can and should be checked numerically for the ordering actually used. For spectral whitening of all windows up to size $W_{\max}$, the simple route substitutes $\varepsilon\to\varepsilon/(W_{\max}-1)$ in (E.4) via Gershgorin; sharper window-size dependence via matrix-Bernstein or Hanson–Wright arguments (Sec. E.5) is a concentration refinement, again sufficient rather than necessary. Both branches of the min collapse when energy concentrates on few pixels ($K_4,K_\infty$ small): permutation cannot flatten a spike.

### E.4 Permutation alone: exact carrier variance and the flat-object counterexample

> **Theorem E.4 (permutation-alone variance).** Under (E1)–(E2), with no signs and a uniformly random permutation $P$, the carrier $Z_g(P)=\sum_j\chi_g(j)T_{Pj}$ of any non-DC row $g\neq0$ satisfies $\mathbb{E}_PZ_g=0$ and
> $$\operatorname{Var}_PZ_g\;=\;\frac{KS_2-S_1^2}{K-1}\;=\;S_2\,\frac{K-K_{\mathrm{eff}}}{K-1}. \tag{E.5}$$
> Consequently, for offset physical patterns $B_g=\mu S_1+\sigma Z_g(P)$ with positivity margin,
> $$\frac{\operatorname{Var}_PB_g}{(\mathbb{E}_PB_g)^2}=\Big(\frac{\sigma}{\mu}\Big)^2\frac{K-K_{\mathrm{eff}}}{(K-1)\,K_{\mathrm{eff}}}\;\le\;\Big(\frac{\sigma}{\mu}\Big)^2\frac{1}{K_{\mathrm{eff}}}. \tag{E.6}$$
> No matching lower bound of order $1/K_{\mathrm{eff}}$ holds uniformly over objects: for flat $T$ ($T_j$ constant), $K_{\mathrm{eff}}=K$ while $Z_g(P)=0$ for **every** permutation and every $g\neq0$.

**Proof.** For $g\neq0$, $\sum_i\chi_g(i)=0$, so $\mathbb{E}_PZ_g=\big(\sum_i\chi_g(i)\big)\mathbb{E}_PT_{P1}=0$. Exchangeability of $(T_{P1},\dots,T_{PK})$ gives $\mathbb{E}_PT_{Pi}^2=S_2/K$ and, for $i\neq j$, $\mathbb{E}_PT_{Pi}T_{Pj}=(S_1^2-S_2)/(K(K-1))$. Hence
$$\mathbb{E}_PZ_g^2=S_2+\frac{S_1^2-S_2}{K(K-1)}\sum_{i\neq j}\chi_g(i)\chi_g(j),$$
and $\sum_{i\neq j}\chi_g(i)\chi_g(j)=\big(\sum_i\chi_g(i)\big)^2-K=-K$, giving (E.5); the second form follows from $K_{\mathrm{eff}}=S_1^2/S_2$. For (E.6), $\mathbb{E}_PB_g=\mu S_1$ and $\operatorname{Var}_PB_g=\sigma^2\operatorname{Var}_PZ_g$; divide. The counterexample: if $T_j\equiv t$, every non-DC Walsh sum of a constant vector vanishes identically, while $S_1^2/S_2=K$. Note (E.5) also exhibits the finite-population correction — the relative variance is $(\sigma/\mu)^2(1/K_{\mathrm{eff}}-1/K)\cdot K/(K-1)$. $\blacksquare$

**What this does not claim.** Theorem E.4 does *not* say permutation-alone whitens: it provides finite-population stationarity (exchangeability of the carrier along the acquisition, the (★) mechanism of Sec. 5) and an $O(1/K_{\mathrm{eff}})$ *upper* variance scale, but it is not equivalent to i.i.d. Rademacher or nonnegative random-pattern carrier noise, and it guarantees no $\Theta(1/K_{\mathrm{eff}})$ *excitation* — a flat object has exactly zero. Two-sided coefficientwise control requires the sign flip *and* the spectral-spread condition (E.4) together (the "both" cell of the Fig. 6 ablation). An earlier claim (R1/v3) that permutation-alone "cannot attain variance $\sim1/K_{\mathrm{eff}}$" was too strong as an upper-scale statement and is corrected by (E.6); it is correct only in the two-sided reading.

### E.5 Hanson–Wright window-energy bound

Whitening of window *energy* — the quantity the window estimator of Sec. 6 actually averages — admits a direct quadratic-form bound. For a window $A$ of $W$ rows let $P_A$ select those rows and set
$$Q_A=\|P_A\,U D P T\|_2^2=\eta^\top M\eta,\qquad M=\mathrm{diag}(PT)\,U_A^\top U_A\,\mathrm{diag}(PT),$$
with $\eta$ the Rademacher sign vector and $U_A$ the selected rows of $U$.

> **Proposition E.5 (window-energy concentration).** Condition on any realized $P$. Then $\mathbb{E}_DQ_A=(W/K)S_2$, and there is a universal $c>0$ with
> $$\Pr_D\!\Big(\big|Q_A-\tfrac{W}{K}S_2\big|\ge\varepsilon\,\tfrac{W}{K}S_2\Big)\;\le\;2\exp\!\Big[-c\min\Big(\varepsilon^2\,\tfrac{WK_\infty}{K},\ \varepsilon\,\tfrac{WK_\infty}{K}\Big)\Big]. \tag{E.7}$$
> Over a specified family of $M$ windows, uniform relative energy whitening at tolerance $\varepsilon\le1$ holds with probability $\ge1-\delta$ once
> $$\frac{WK_\infty}{K}\;\ge\;C\varepsilon^{-2}\log(M/\delta). \tag{E.8}$$

**Proof.** Since $U$ has orthonormal rows, $U_AU_A^\top=I_W$, so $U_A^\top U_A$ is an orthogonal projector and $(U_A^\top U_A)_{jj}=\sum_{g\in A}U_{gj}^2=W/K$ (Hadamard entries are $\pm K^{-1/2}$). Hence $M\succeq0$, and $\mathbb{E}_DQ_A=\operatorname{tr}M=\sum_j(PT)_j^2\,(W/K)=(W/K)S_2$. Because $\eta_j^2=1$, the diagonal of $M$ contributes deterministically and $Q_A-\mathbb{E}Q_A$ is a pure off-diagonal Rademacher chaos, to which the Hanson–Wright inequality applies (Hanson–Wright 1971; sub-Gaussian form of Rudelson–Vershynin 2013):
$$\Pr(|Q_A-\operatorname{tr}M|\ge t)\le2\exp\Big[-c\min\Big(\frac{t^2}{\|M\|_F^2},\ \frac{t}{\|M\|_{\mathrm{op}}}\Big)\Big].$$
The proxies: $\|M\|_{\mathrm{op}}\le\|\mathrm{diag}(PT)\|_{\mathrm{op}}^2\,\|U_A^\top U_A\|_{\mathrm{op}}\le\|T\|_\infty^2=S_2/K_\infty$, and for PSD $M$, $\|M\|_F^2\le\|M\|_{\mathrm{op}}\operatorname{tr}M\le(W/K)S_2\|T\|_\infty^2$. Substituting $t=\varepsilon(W/K)S_2$ gives $t^2/\|M\|_F^2\ge\varepsilon^2WK_\infty/K$ and $t/\|M\|_{\mathrm{op}}\ge\varepsilon WK_\infty/K$, i.e. (E.7); for $\varepsilon\le1$ the quadratic branch is active. A union bound over $M$ windows gives (E.8). $\blacksquare$

For dense objects of bounded dynamic range, $K_\infty\asymp K_4\asymp K_{\mathrm{eff}}\asymp K$ and (E.8) reduces to the mild $W\gtrsim\varepsilon^{-2}\log M$ — the window only needs logarithmic length. For an object supported on $m$ comparable pixels, $K_\infty\asymp m$ and the condition hardens to $Wm/K\gtrsim\varepsilon^{-2}\log M$: this is precisely where $K_{\mathrm{eff}}$ alone is the wrong functional and the three spread parameters separate (Sec. 6).

**What this does not claim.** Proposition E.5 controls window *energy* over the sign draw for a pre-specified finite window family; it is a sufficient concentration tool, not the deterministic necessary-and-sufficient condition (which remains the spectral condition of Theorem E.2(3) applied to $w^P$), and it does not cover all $\binom{K}{W}$ windows simultaneously without paying for the larger union. The constants $c,C$ are universal but not optimized, and no claim is made that (E.8) is tight in its $W$- or $K_\infty$-dependence — Hanson–Wright and matrix-Bernstein refinements can improve window-family dependence for structured $\mathcal{A}$, but they do not change the deterministic criterion. Finally, all of Appendix E concerns the carrier statistics of the *design*; the translation of whitening into gain-estimation rates ($1/W$ per window) and into image error (leverage $B_L=1$ for full SRHT inversion) is carried out in Appendix D and Appendix F respectively.

## Appendix F — The master finite-noise identity and the flip boundary

This appendix proves Theorem 1 (the master finite-noise relMSE identity) and Prop 3 (the finite-$N$ flip boundary) of Sec. 8, together with the noise plug-ins and the three basis specializations quoted there. Throughout, $T\in\mathbb{R}^K$ is the object, with $S_1$, $S_2$, $K_{\mathrm{eff}}$ as in Appendix C; $A\in\mathbb{R}^{N\times K}$ is the design, $b=AT$ the ideal bucket vector; the raw bucket is $R_n=a_nB_n$ with gain $a_n=e^{\ell_n}$, $\ell\in S$ (the drift class of Sec. 4, $p=\dim S$). After the pipeline applies a gain estimate $\hat a_n=e^{\hat\ell_n}$, the corrected bucket is

$$z_n \;=\; R_n/\hat a_n \;=\; (1+\delta_n)\,b_n+\xi_n,\qquad \delta_n=\frac{a_n}{\hat a_n}-1=e^{\ell_n-\hat\ell_n}-1, \tag{F.1}$$

where $\delta_n$ is the *residual* multiplicative gain error and $\xi_n$ is additive bucket-domain noise after correction, with $\mathbb{E}\,\delta=m_\delta$, $\mathrm{Cov}(\delta)=V_\delta$, $\mathbb{E}\,\xi=0$, $\mathrm{Cov}(\xi)=\Sigma_\xi$, and $\delta\perp\xi$. The reconstruction is $\hat T=Lz$ for any fixed linear operator $L\in\mathbb{R}^{K\times N}$ (exact inverse, pseudoinverse, DGI correlator, or a regularized estimator linearized around a fixed design).

### F.1 The master identity

**Theorem 1 (exact second-moment bridge).** *Assume model (F.1) with $A,T,L$ fixed (all expectations conditional on them), $\delta$ and $\xi$ uncorrelated, and second moments $m_\delta,V_\delta,\Sigma_\xi$ finite. Then, exactly and with no Gaussian or small-noise approximation,*

$$\frac{\mathbb{E}\|\hat T-T\|_2^2}{S_2} =\underbrace{\frac{\|(LA-I)T+L\,\mathrm{diag}(b)\,m_\delta\|_2^2}{S_2}}_{\text{bias}} +\underbrace{\frac{\mathrm{tr}\!\big(L\,\mathrm{diag}(b)\,V_\delta\,\mathrm{diag}(b)\,L^\top\big)}{S_2}}_{\text{residual gain}} +\underbrace{\frac{\mathrm{tr}\!\big(L\,\Sigma_\xi L^\top\big)}{S_2}}_{\text{additive noise}}. \tag{F.2}$$

*(a) If moreover $\mathbb{E}\,\delta_n=0$ and the $\delta_n$ are uncorrelated with common variance $v$, the residual-gain term equals $v\,B_L(A,T)$ with the* **leverage**

$$B_L(A,T)=\frac{1}{S_2}\sum_{n=1}^N b_n^2\,\|Le_n\|_2^2. \tag{F.3}$$

*(b) If instead the residual gains are stationary with $\mathrm{Cov}(\delta_n,\delta_m)=v\,r_\delta(n-m)$, the residual-gain term equals*

$$R_{\mathrm{gain}}=\frac{v}{S_2}\sum_{n,m} r_\delta(n-m)\,b_n b_m\,\langle Le_n,Le_m\rangle. \tag{F.4}$$

**Proof.** Write $z=b+\mathrm{diag}(b)\,\delta+\xi$, so $\hat T-T=(LA-I)T+L\,\mathrm{diag}(b)\,\delta+L\xi$. Decompose $\delta=m_\delta+(\delta-m_\delta)$. The mean of $\hat T-T$ is $(LA-I)T+L\,\mathrm{diag}(b)\,m_\delta$; its squared norm is the bias term. By the bias–variance decomposition $\mathbb{E}\|X\|^2=\|\mathbb{E}X\|^2+\mathrm{tr}\,\mathrm{Cov}(X)$ and the uncorrelatedness of $\delta$ and $\xi$, the covariance of $\hat T$ is $L\,\mathrm{diag}(b)\,V_\delta\,\mathrm{diag}(b)\,L^\top+L\,\Sigma_\xi L^\top$; taking traces and dividing by $S_2$ gives (F.2). For (a), $V_\delta=vI$ and $\mathrm{tr}(L\,\mathrm{diag}(b)\,\mathrm{diag}(b)\,L^\top)=\sum_n b_n^2\|Le_n\|^2$, giving (F.3). Case (b) is the coordinate expansion of the same trace with $(V_\delta)_{nm}=v\,r_\delta(n-m)$. $\blacksquare$

**What this does not claim.** (F.2) is a second-moment accounting identity for a *linear* reconstructor with the design held fixed; it does not bound nonlinear or data-adaptive $L$, and for random-pattern pipelines the constants below are obtained by additionally averaging over the pattern draw. It says nothing about how small $v$ can be made — that is the estimation-rate question of Sec. 6. Finally, the scalar collapse $v\,B_L$ *requires* uncorrelated residuals: for smooth (coherent) residual gain — the generic output of a windowed blind estimator — only the matrix form (F.4) is correct. This supersedes the earlier round-1 slogan "orthogonal inversion gives $v$," which holds only for independent coefficient-wise residuals under exact inversion.

### F.2 Noise plug-ins

**Proposition F.2 (read and Poisson noise, exact).** *(a) Gaussian read.* If detector-domain noise $\eta_n\sim\mathcal N(0,\sigma_{\mathrm{read},n}^2)$ (independent across frames) precedes gain correction, then $\xi_n=\eta_n/\hat a_n$ and, for calibrated gains $\hat a_n\approx a_n$, $\mathrm{Var}(\xi_n)=\tau_{G,n}^2:=\sigma_{\mathrm{read},n}^2/a_n^2$. *(b) Poisson.* If counts obey $C_n\mid T,a\sim\mathrm{Pois}(\Phi_n)$ with $\Phi_n=\gamma_n a_n b_n$ and $z_n=C_n/(\gamma_n\hat a_n)$, then exactly

$$\mathbb{E}[z_n\mid T,a]=\frac{a_n}{\hat a_n}b_n,\qquad \mathrm{Var}(z_n\mid T,a)=\frac{b_n^2}{\Phi_n}\Big(\frac{a_n}{\hat a_n}\Big)^2. \tag{F.5}$$

**Proof.** (a) is scaling of a Gaussian. (b): a Poisson variable has mean $=$ variance $=\Phi_n$; dividing by $\gamma_n\hat a_n$ scales the mean by $(\gamma_n\hat a_n)^{-1}$ and the variance by $(\gamma_n\hat a_n)^{-2}$, and $\Phi_n/(\gamma_n\hat a_n)= (a_n/\hat a_n) b_n$, $\Phi_n/(\gamma_n\hat a_n)^2=(b_n^2/\Phi_n)(a_n/\hat a_n)^2$. $\blacksquare$

Hence, after calibration, $\Sigma_\xi=\mathrm{diag}(\tau_{G,n}^2+b_n^2/\Phi_n)$ plugs into (F.2), and the Poisson term is **exact at all photon counts**, including $\Phi_n\ll1$; no log or Gaussian approximation enters the reconstruction layer. Under a total budget $\Phi_n=\omega_n\Phi_{\mathrm{tot}}$, $R_{\mathrm{Pois}}=(S_2\Phi_{\mathrm{tot}})^{-1}\sum_n(b_n^2/\omega_n)\|Le_n\|^2$.

**What this does not claim.** Exactness holds *conditionally on the gains*; the difficulty of low photons lives entirely in estimating $\hat a_n$ (the calibrated soft-log analysis; see Appendix D / issue #3 §7), not in propagating noise through $L$. The optimal allocation $\omega_n\propto|b_n|\,\|Le_n\|$ requires knowing $T$ and is not claimed to be achievable.

### F.3 Specializations

**F.3.1 Orthogonal / full-SRHT inversion ($B_L=1$).** If $A=U$ is orthonormal ($N=K$, signed coefficients available) and $L=U^\top$, then $LA=I$ and $\|Le_n\|=1$, so $B_L=(1/S_2)\sum_n b_n^2=1$ by Parseval. With independent residuals,

$$\mathrm{relMSE}_{\mathrm{orth}}=v+\frac{1}{S_2}\sum_n\big(\tau_{G,n}^2+b_n^2/\Phi_n\big). \tag{F.6}$$

Exact orthogonal inversion transmits independent coefficient-wise residual gain at unit leverage. A full SRHT acquisition $A=P_{\mathrm{row}}UDP_{\mathrm{col}}$, $L=A^\top$ has identically the same propagation; SRHT's role is *not* a better inverse but temporal stationarization of the carrier so that the blind estimator can shrink $v$ (Sec. 5/7).

**F.3.2 Pairwise Hadamard: exact perturbation law.** Let $c_k=h_k^\top T$, $h_k\in\{\pm1\}^K$, with physical masks $B_k^\pm=(S_1\pm c_k)/2$ and reconstruction $T=K^{-1}H^\top c$, so coefficient errors $e_k$ give $\mathrm{relMSE}=(KS_2)^{-1}\sum_k\mathbb{E}e_k^2$. If the paired masks carry gains $a_k^+$ and $a_k^-=a_k^+(1+\Delta_k)$, the pairwise-normalized estimator satisfies the **exact** algebraic law

$$\hat c_k-c_k=-\,\frac{S_1\,\Delta_k\,(1-x_k^2)}{2+\Delta_k(1-x_k)},\qquad x_k=c_k/S_1, \tag{F.7}$$

whence, exactly, $R_{\mathrm{pair,gain}}=\dfrac{S_1^2}{KS_2}\displaystyle\sum_k\mathbb{E}\Big[\frac{\Delta_k^2(1-x_k^2)^2}{(2+\Delta_k(1-x_k))^2}\Big]$. For small mismatch with $\Delta_k$ independent of the coefficient index,

$$R_{\mathrm{pair,gain}}=\frac{K_{\mathrm{eff}}}{4}\,D_H(T)\,\mathrm{Var}(\Delta)+O\!\big(K_{\mathrm{eff}}\,\mathbb{E}|\Delta|^3\big),\qquad D_H(T)=\frac{1}{K}\sum_k(1-x_k^2)^2, \tag{F.8}$$

by Taylor expansion of (F.7) in $\Delta_k$. For most non-DC Hadamard coefficients of a nonnegative object $|x_k|\ll1$, so $D_H\approx1$; $D_H$ is nevertheless a *pipeline constant to be measured*, not assumed. The $K_{\mathrm{eff}}$ amplification is structural: pairwise normalization converts a differential gain error into a coefficient error of order $S_1$, and Parseval then divides by $S_2$. Noise terms: read noise gives exactly $R_{\mathrm{pair,read}}=2\sigma_{\mathrm{read}}^2/S_2$; for Poisson counts with pair budget $\Phi_{\mathrm{pair}}$, using $B_k^++B_k^-=S_1$, the coefficient shot variance is $\mathrm{Var}(e_k\mid c_k)\approx S_1^2/\Phi_{\mathrm{pair},k}$ — an approximation, exact only up to the $c_k$-dependent split between the two buckets — giving $R_{\mathrm{pair,Pois}}=K_{\mathrm{eff}}/\Phi_{\mathrm{pair}}$ (equal-pair budget) or $(K_{\mathrm{eff}}+1)/(2\Phi_{\mathrm{mask}})$ (equal-mask budget); these differ only by allocation convention.

**What F.3.2 does not claim.** (F.7)–(F.8) presuppose a stable DC/$S_1$ normalization; at low photons the denominator bucket sum can be noisy or zero, and a robust implementation needs offset/clipping or a likelihood-ratio estimator. The exact law (F.7) is algebra; only the moment step (F.8) invokes small $\Delta$ and index-independence.

**F.3.3 Random patterns / DGI: the one-sample constant $C_0$.** Let $I_n=\mu\mathbf 1+\sigma x_n$ with iid coordinates, $\mathbb{E}x=0$, $\mathbb{E}x^2=1$, $\mathbb{E}x^3=\gamma_3$, $\mathbb{E}x^4=\beta_4$, and the ideal correlator $\hat T_{\mathrm{DGI}}=(N\sigma)^{-1}\sum_n x_n z_n$. Define the one-sample vector $Z=\sigma^{-1}x\,(\mu S_1+\sigma x^\top T)$; then $\mathbb{E}Z=T$ and, with known gain and no detector noise,

$$\frac{\mathbb{E}\|\hat T_{\mathrm{DGI}}-T\|^2}{S_2}=\frac{C_0}{N},\qquad C_0:=\frac{\mathbb{E}\|Z-T\|^2}{S_2}, \tag{F.9}$$

which is the implementation-independent *definition* of $C_0$. **The evaluation of $C_0$ for iid patterns is a moment calculation** (as in the source): expanding $\mathbb{E}\|Z\|^2$ with $Z=(\mu S_1/\sigma)x+xx^\top T$ gives the three terms $K(\mu/\sigma)^2S_1^2$, $2(\mu/\sigma)\gamma_3S_1^2$, and $(K+\beta_4-1)S_2$; subtracting $\|\mathbb{E}Z\|^2=S_2$,

$$C_0=K+\beta_4-2+K_{\mathrm{eff}}\big[K(\mu/\sigma)^2+2\gamma_3(\mu/\sigma)\big] \;\xrightarrow[\ \mu=0,\ \gamma_3=0\ ]{}\; K+\beta_4-2. \tag{F.10}$$

The $K_{\mathrm{eff}}K(\mu/\sigma)^2$ term is the familiar nonnegative-background penalty. Residual gain, read, and Poisson terms (equal-count convention $\Phi_n=\Phi_{\mathrm{frame}}$):

$$\mathrm{relMSE}_{\mathrm{DGI}}=\frac{C_0}{N}+\frac{(1+C_0)v}{N}+\frac{K\tau_G^2}{N\sigma^2S_2}+\frac{1+C_0}{N\,\Phi_{\mathrm{frame}}}. \tag{F.11}$$

The gain term follows from Theorem 1(a) with the *leverage $\times N$ framing*: for the correlator, $\|Le_n\|^2=\|x_n\|^2/(N^2\sigma^2)$, so averaging over pattern draws, $N\,\mathbb{E}B_L=\mathbb{E}\|Z\|^2/S_2=1+C_0$ — i.e., $R_{\mathrm{DGI,gain}}=(1+C_0)v/N$, and in residual-injection experiments the measurable slope is $N B_L\to 1+C_0$. **Status (labeled).** This pattern-averaging step treats the residuals $\delta$ as independent of the pattern draw — exact for injected residuals (the Fig. 4 protocol), a heuristic decoupling for blind pipelines, where $\hat a$ is computed from the same record the patterns generated. Correlated residuals multiply $v$ by $\chi_\delta=1+2\sum_{h\ge1}\mathrm{corr}(\delta_0,\delta_h)$ — a heuristic long-run-variance correction valid only when correlations are weak enough that pattern cross-terms still average; the rigorous object remains (F.4).

**What F.3.3 does not claim.** There is **no universal $C_0$**: (F.10) is exact only for the ideal known-$(\mu,\sigma)$ correlator with iid coordinates. Mean subtraction, reference normalization, and photon allocation all change the constant (not the $C_0/N$ structure), so $C_0$ must be measured from the pipeline via definition (F.9). The flux-limited convention $\Phi_n=\gamma b_n$ replaces the last term of (F.11) by $(N\sigma^2S_2)^{-1}\mathbb{E}[\|x\|^2 b_n/\gamma]$.

### F.4 Prop 3: the finite-$N$ flip boundary

**Drift model and assumptions.** Let $s^2$ be the variance scale of the log-gain process $\ell$ and let $\rho_{\mathrm{pair}}$ be the **adjacent-pair decorrelation parameter**, meaning the paired-mask gain increment obeys $\mathrm{Var}(\Delta_k)\approx\mathrm{Var}(\ell_k^--\ell_k^+)=2s^2\,r(\rho_{\mathrm{pair}})$ with $r(\rho)=\rho+O(\rho^2)$ small-$\rho$; for an Ornstein–Uhlenbeck log-gain, $r(\rho)=1-e^{-\rho}$. Assume the small-mismatch regime of (F.8) (so $R_{\mathrm{pair,gain}}(\rho_{\mathrm{pair}})\approx\tfrac12 K_{\mathrm{eff}}D_H(T)\,s^2\,r(\rho_{\mathrm{pair}})$) and the DGI decomposition (F.11) with blind residual variance $v_{\mathrm{blind}}(\rho_{\mathrm{pair}},N)$ — the window-optimized output of the Sec.-6 rate theorem, $v_{\mathrm{blind}}\lesssim\min_{W\in[1,N]}[\sigma_{\mathrm{eff}}^2/W+C(s\rho_{\mathrm{pair}} W)^2]\lesssim C\,\sigma_{\mathrm{eff}}^{4/3}(s\rho_{\mathrm{pair}})^{2/3}$ when the optimizer is interior.

**Prop 3 (implicit flip boundary).** *Define $\rho^*=\inf\{\rho_{\mathrm{pair}}\ge0: R_{\mathrm{pair}}(\rho_{\mathrm{pair}})\ge R_{\mathrm{rand}}(\rho_{\mathrm{pair}},N)\}$, where $R_{\mathrm{pair}}=R_{\mathrm{pair,gain}}+R_{\mathrm{pair,read}}+R_{\mathrm{pair,Pois}}$ and $R_{\mathrm{rand}}$ is (F.11) with $v=v_{\mathrm{blind}}(\rho_{\mathrm{pair}},N)$. Under the small-drift expansion, $\rho^*$ solves the implicit equation*

$$r(\rho^*)=\frac{2\Big[\dfrac{C_0}{N}+\dfrac{(1+C_0)\,v_{\mathrm{blind}}(\rho^*,N)}{N}+R_{\mathrm{DGI,noise}}-R_{\mathrm{pair,noise}}\Big]}{K_{\mathrm{eff}}\,D_H(T)\,s^2}. \tag{F.12}$$

*For the OU convention this is explicit: $\rho^*=-\log(1-Q)$ with $Q=2\Delta_R/(K_{\mathrm{eff}}D_Hs^2)$, $\Delta_R$ the bracket of (F.12). If $Q\le0$, random/DGI is already worse at $\rho=0$ (sampling/noise floor dominates); if $Q\ge1$, pairwise never flips within the OU small-to-moderate range.*

**Proof.** At the boundary, $R_{\mathrm{pair}}(\rho^*)=R_{\mathrm{rand}}(\rho^*,N)$. Substituting $R_{\mathrm{pair,gain}}=\tfrac12K_{\mathrm{eff}}D_Hs^2\,r(\rho^*)$ (from F.8 with $\mathrm{Var}\Delta=2s^2r$) and (F.11), and solving for $r(\rho^*)$, gives (F.12); monotonicity of $r$ makes the crossing the infimum. The OU form inverts $r(\rho)=1-e^{-\rho}$. Note (F.12) is a fixed-point equation because $v_{\mathrm{blind}}$ is evaluated at $\rho^*$; existence/uniqueness of the crossing uses that $R_{\mathrm{pair,gain}}$ is increasing in $\rho_{\mathrm{pair}}$ while the right side varies slowly ($v_{\mathrm{blind}}\propto\rho_{\mathrm{pair}}^{2/3}$) — a regularity argument at the same heuristic level as the small-drift expansion, not separately proven. $\blacksquare$

**Leading-order heuristic (labeled as such).** If $r(\rho)=\rho$, $D_H=1$, noise differences are negligible, $v_{\mathrm{blind}}$ is negligible (or absorbed into $C_0$), and $\rho$ *means* adjacent-pair decorrelation, (F.12) collapses to the engineering rule

$$\rho^*\approx\frac{2C_0}{N\,K_{\mathrm{eff}}\,s^2}, \tag{F.13}$$

with first corrections $\rho^*\approx 2\big(C_0+(1+C_0)v_{\mathrm{blind}}\big)/[NK_{\mathrm{eff}}D_Hs^2]+2(R_{\mathrm{DGI,noise}}-R_{\mathrm{pair,noise}})/(K_{\mathrm{eff}}D_Hs^2)$ and the nonlinear replacement $\rho\mapsto r^{-1}(\cdot)$ when adjacent increments are not infinitesimal. (F.13) is a *leading-order heuristic*, not a theorem; the theorem is (F.12).

**$\rho$-convention warning.** Throughout, $\rho_{\mathrm{pair}}$ (adjacent-pair decorrelation) is the variable of (F.12)–(F.13); it is **not** the normalized bandwidth $\rho_{\mathrm{bw}}$ of the tall-design thresholds ($p\approx\rho_{\mathrm{bw}}N$, Sec. 4). If a bandwidth parameter with adjacent-increment variance $\sim2s^2\rho_{\mathrm{bw}}/N$ is substituted, the explicit $1/N$ in (F.13) cancels and the boundary reads $\rho^*_{\mathrm{bw}}\approx2C_0/(K_{\mathrm{eff}}s^2)$ — same physics, different symbol. Every phase-diagram axis must declare its convention.

**What Prop 3 does not claim.** The boundary compares two *specific* pipelines (pairwise-normalized Hadamard vs. blind random+DGI with the ideal correlator); it does not rank SRHT-paired pipelines, externally calibrated systems, or prior-regularized reconstructions, each of which shifts $\Delta_R$. It inherits every assumption of its ingredients: small mismatch (F.8), a measured pipeline $C_0$ and $D_H$, a stationary drift with a declared $r(\rho)$, and a $v_{\mathrm{blind}}$ from the window rate theorem whose constants are implementation-specific. It is a mean-square crossing, not a guarantee about any single realization, and at $\rho_{\mathrm{pair}}$ beyond the small-drift expansion only the defining infimum — not (F.12) — is meaningful.
