# Appendices

Appendix A supports Sec. 4 (Theorem A and Corollaries 1-2); Appendix B supports Sec. 4 (Theorem A′, parametric-transversality proof); Appendix C supports Sec. 5 (Propositions 1–2, condition (★), Theorem B); Appendix D supports Sec. 6 (Theorems C-D, Fisher geometry, low-photon); Appendix E supports Sec. 7 (SRHT Walsh condition, permutation bounds); Appendix F supports Sec. 8 (Theorem 1, specializations, Prop 3).
Heuristic or genericity steps are labeled as such inside each proof; every appendix ends its theorems with a 'What this does not claim' paragraph.

## Appendix A — Square-design non-identifiability

This appendix proves Theorem A of Sec. 4 together with its two corollaries, in the notation of the main text: noiseless bucket record $R_n = a_n B_n$, carrier $B_n = (MT)_n$, log-gain $\ell = \log a$ (entrywise), drift class $S$ a linear subspace of $\mathbb{R}^N$ with $\operatorname{span}\{\mathbf 1\}\subseteq S$ and $\dim S = p$. This appendix is the archival form of these results under the manuscript labels Theorem A, Corollary 1, Corollary 2.

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

**What this does not claim.** Theorem A is a statement about the square case $N = K$ and an unconstrained object; for $N > K$ the construction fails unless $e^{-s}\odot MT$ remains in $\operatorname{range}(M)$, and the correct analysis is the tall-design identifiability theory of Theorem A′ (see Appendix B). It does not say the record is uninformative about the gain in a statistical model: under random illumination, the *relative* gain is consistently estimable (Theorem B; see Appendix C), a different — statistical, asymptotic — notion of identifiability which Theorem A neither contradicts nor implies. Finally, Theorem A is about uniqueness, not conditioning: it makes no claim about how well- or ill-posed any estimator is.

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

*(ii) (Known support zeros; differential criterion and ordinary-local sufficiency.) Let $\Omega \subset \{1,\dots,K\}$, $|\Omega| = q$, and $\mathcal T_\Omega = \{T : T_{\Omega^c} = 0,\ T \ge 0\}$, with the true $T \in \mathcal T_\Omega$, $T_\Omega > 0$. The constrained model is locally **differentially** identifiable modulo gauge at $T$ if and only if*

$$\ker\!\big(P_{\Omega^c} H^{-1}\operatorname{diag}(HT)\,\big|_S\big) \;=\; S \cap \operatorname{span}\{\mathbf 1\},$$

*where $P_{\Omega^c}$ is coordinate projection onto $\Omega^c$. The gauge direction always lies in the kernel. Equality of the kernel with the gauge is also sufficient for ordinary local identifiability: with $\gamma$ the smallest singular value of the linearized map on a complement $S_\perp$ of $\operatorname{span}\{\mathbf 1\}$ in $S$ and $C_H$ the second-order remainder constant below, every $s$ with $0 < \lVert s_\perp\rVert_2 < \min\{1,\gamma/C_H\}$ violates the support constraint. The exact necessary-and-sufficient condition for ordinary local identifiability is instead that $0$ be an isolated zero of the gauge-fixed nonlinear map $F|_{S_\perp}$ defined below; derivative injectivity is sufficient for this isolation but is not necessary.*

*(iii) (Rank counts — dimension-counting arguments, labeled as such.) The linearized map in (ii) sends the $(p-1)$-dimensional quotient $S/\operatorname{span}\{\mathbf 1\}$ into $\mathbb{R}^{K-q}$. Thus $K_0:=K-q\ge p-1$ is necessary for the **full-rank differential criterion**. It is not a necessary condition for ordinary local identifiability, because a rank-deficient analytic zero may still be isolated, and the count alone is not sufficient without an explicit full-rank witness. Conditional on such a witness, full column rank is generic in $(H,T_\Omega)$. For unknown support of size $\le q$, $K\ge2q+(p-1)$ remains only a dimension-counting prediction, up to endpoint conventions.*

*Proof.* **(i)** $M_0T = T$ and $\lVert M_sT - T\rVert_2 = \lVert H^{-1}\big((e^{-s} - \mathbf 1)\odot HT\big)\rVert_2 \le \lVert H^{-1}\rVert_2\,\lVert HT\rVert_2\,\max_n|e^{-s_n} - 1| \le \lVert H^{-1}\rVert_2\,\lVert HT\rVert_2\,(e^{\lVert s\rVert_\infty} - 1)$. If this is below $\min_j T_j$ then $M_sT > 0$ entrywise. Since the positive orthant is open and $s \mapsto M_sT$ is continuous, positivity excludes nothing locally; Theorem A supplies the distinctness. $\blacksquare$ (i)

**(ii)** Define the support-constraint map $F : S \to \mathbb{R}^{K-q}$, $F(s) = P_{\Omega^c} M_s T$. It is real-analytic, $F(0) = P_{\Omega^c}T = 0$, and its differential at $0$ is

$$DF_0\,u = -\,P_{\Omega^c} H^{-1}\operatorname{diag}(HT)\,u,$$

by differentiating $e^{-tu} = \mathbf 1 - tu + O(t^2)$ inside $M_{tu}$. The gauge is always in the kernel: $H^{-1}\operatorname{diag}(HT)\mathbf 1 = H^{-1}(HT) = T$ and $P_{\Omega^c}T = 0$; consistently, $F(t\mathbf 1) = e^{-t}F(0) = 0$ exactly, for all $t$.

*Differential criterion.* If the kernel strictly exceeds the gauge, some nonconstant $u \in S$ satisfies the linearized support constraint, so differential identifiability on the gauge quotient fails. Conversely, if the kernel is exactly the gauge, $DF_0|_{S_\perp}$ is injective, hence the gauge-fixed constrained map is an immersion at $0$. A null derivative need not integrate to an exact ambiguity curve: an analytic zero can be isolated even when its derivative is singular. This is why the displayed kernel equality is an iff only for *differential* identifiability.

*Sufficiency in a ball.* Suppose the kernel equals the gauge and let $\gamma = \sigma_{\min}(DF_0|_{S_\perp}) > 0$. Entrywise Taylor with remainder, $|e^{-x} - 1 + x| \le \tfrac{x^2}{2}e^{|x|}$, gives for $\lVert s\rVert_\infty \le 1$

$$\lVert F(s) - DF_0\,s\rVert_2 \;\le\; C_H\,\lVert s\rVert_2^2, \qquad C_H := \tfrac{e}{2}\,\lVert H^{-1}\rVert_2\,\lVert HT\rVert_2 .$$

For gauge-fixed $s = s_\perp \in S_\perp$ (any $s$ may be reduced to this form using $F(s + t\mathbf 1) = e^{-t}F(s)$, which rescales but never annihilates $F$),

$$\lVert F(s_\perp)\rVert_2 \;\ge\; \gamma\,\lVert s_\perp\rVert_2 - C_H\,\lVert s_\perp\rVert_2^2 \;>\; 0 \quad\text{for } 0 < \lVert s_\perp\rVert_2 < \min\{1,\gamma/C_H\} .$$

A nonzero $F(s)$ means $M_sT \notin \mathcal T_\Omega$ (support constraint violated), so no non-gauge ambiguity exists in that ball. More generally, after gauge fixing, ordinary local identifiability holds exactly when $F^{-1}(0)\cap S_\perp$ contains no nonzero point in some neighborhood of $0$, i.e. exactly when $0$ is an isolated zero of $F|_{S_\perp}$. This proves both the quantitative sufficient condition and the exact nonlinear criterion. $\blacksquare$ (ii)

**(iii)** *These are rank/dimension arguments, not an ordinary-identifiability theorem.* A linear map from a $(p-1)$-dimensional space cannot be injective into $\mathbb{R}^{K-q}$ if $K-q<p-1$, proving the stated necessity for differential full rank. When $K-q\ge p-1$, clear denominators in the maximal minors of $P_{\Omega^c}H^{-1}\operatorname{diag}(HT)|_{S_\perp}$: if one admissible pair $(H,T_\Omega)$ has a nonzero maximal minor, that minor is not identically zero, so full column rank holds off a proper algebraic set. The dimension count does not supply that witness, and a fixed named basis must be checked directly. Neither a failed rank count nor a singular derivative rules out higher-order zero isolation. The unknown-support count $K \ge 2q + (p-1)$ arises from demanding that the $q$-sparse model avoid all of its gain-transformed copies $M_s\Sigma_q$, in analogy with the generic sparsity thresholds of Kech–Krahmer [13]; it is a heuristic prediction, unverified for structured designs, and the uniform no-support-switching condition it summarizes is strictly stronger than (ii). $\blacksquare$ (heuristic scope)

**What this does not claim.** Part (i) says nonnegativity fails to restore *identifiability*; it may still improve estimator conditioning and is routinely useful as regularization — no claim is made either way. Part (ii) is local and fixed-support: derivative full rank is a checkable sufficient condition for ordinary local identifiability, whereas zero isolation is the exact nonlinear condition. Neither excludes isolated global aliases. Part (iii) concerns differential rank only; it supplies neither a necessary zero count for ordinary local identifiability nor a witness for any fixed basis. For unknown support only its heuristic count is offered. These qualifications apply only to Corollary 2; they do not alter the generic ordinary-local iff or the exact below-wall alias manifold of Theorem A′(i) (Appendix B).

### A.4 Remarks

**Remark A.1 (Fisher-theoretic reading).** Because the ambiguity of Theorem A is an explicit real-analytic curve $t \mapsto (\ell + ts, T'(ts))$ along which the noiseless data are constant, every nonconstant $s \in S/\operatorname{span}\{\mathbf 1\}$ yields an exact null direction of the (gauge-quotient) Fisher information in any regular dominated noise model built on this record: the Cramér–Rao bound is infinite for any functional that varies along the curve. Here the implication "explicit ambiguity curve $\Rightarrow$ Fisher null direction" is exact, not merely first-order.

**Remark A.2 (zero buckets).** If some $c_n = (MT)_n = 0$, two separate pathologies arise, which the statements above deliberately quarantine via (A4): the gain values $a_n$ at zero-carrier frames are entirely unobservable (a trivial extra ambiguity, of dimension $\dim(S \cap \{s : s = 0 \text{ on } \operatorname{supp}(c)\})$ beyond the count of Theorem A), and log-domain processing of $R_n = 0$ is undefined, an estimation-side issue treated by the calibrated soft-log machinery of the low-photon analysis (Sec. 6; see Appendix D), not an identifiability issue.

## Appendix B — Tall-Design Identifiability: the Parametric-Transversality Proof

This appendix proves the tall-design identifiability results quoted as **Theorem A′** in Sec. 4, restated in full as Theorem A′(i)–(iv) in Sec. B.8: the generic local threshold with a genuine *iff* at $N = K+p-1$ for $K\ge2$, genuine (exact, positive-dimensional) failure below that wall, generic exact identifiability at $N\ge K+p$, uniform identifiability over the nonvanishing-carrier set at $N\ge 2K+p-1$, and the degenerate $K=1$ stratum. The proof route is **parametric transversality** (a rowwise design-perturbation witness plus Fubini), verified adversarially in review round R11; it holds for **every fixed drift subspace $S\ni\mathbf 1$** — no genericity of $S$ is assumed anywhere, so the physical Fourier low-pass space $S_{\mathrm{LP}}$ is covered directly, with no transfer lemmas. Sharpness (necessity) of the two global thresholds is **not** claimed as a theorem; its status is stated precisely after Theorem A′. This appendix **supersedes** the earlier incidence-variety/stratum-counting route (see Sec. B.9); the superseded "sharp iff" statements at $N=K+p$ and $N=2K+p-1$ are withdrawn.

### B.0 Setting, notation, and the reduction

The bucket record is $R_n=a_nB_n$ with $B=MT$: in vector form the data map is

$$\Phi_M(T,s)\;=\;D_{e^{s}}\,M\,T,\qquad M\in\mathbb R^{N\times K},\ N\ge K,\qquad s\in S,\ T\in\mathbb R^{K},$$

where $D_x=\operatorname{diag}(x)$, $e^{s}$ is componentwise, $\ell=s$ is the log-gain trajectory confined to the fixed, known drift class $S\subset\mathbb R^{N}$ with $\dim S=p\ge2$ and $\mathbf 1\in S$. Write $y=MT$ for the carrier and define

$$\mathcal U=\{(M,T):(MT)_n\neq0\ \forall n\},\qquad \mathcal U_M=\{T\in\mathbb R^K:(MT)_n\neq0\ \forall n\},$$

$$\mathcal R=\{M\in\mathbb R^{N\times K}:\operatorname{rank}M<K\}.$$

$\mathcal U$ is open with null complement (each $\{m_n^\top T=0\}$ is a proper algebraic subset); $\mathcal R$ is a proper algebraic subset (vanishing of all $K\times K$ minors), hence Lebesgue-null. **Every exceptional set below explicitly includes $\mathcal R$ (or $\mathcal R\times\mathbb R^K$).** The gauge is $(T,s)\sim(cT,\,s-\log c\,\mathbf 1)$, $c>0$; identifiability is always modulo this gauge. "For a.e." always refers to Lebesgue measure on the stated parameter space.

**Lemma B.0 (reduction).** *Assume $\operatorname{rank}M=K$ and $(M,T)\in\mathcal U$, and fix any $s\in S$. Then $(T',s')\in\mathbb R^K\times S$ is an alias of $(T,s)$ — i.e. $\Phi_M(T',s')=\Phi_M(T,s)$ — iff, with $d:=s-s'\in S$,*

$$M\,T'\;=\;D_{e^{d}}\,M\,T.
\tag{B.1}$$

*If $d=a\mathbf 1$ is constant, then (B.1) reads $MT'=e^{a}MT$ and full column rank gives $T'=e^{a}T$ — exactly the gauge orbit with $c=e^{a}$; conversely every gauge point solves (B.1) with constant $d$. Hence $(M,T)$ is identifiable iff (B.1) has no solution $(T',d)$ with $d\in S\setminus\mathbb R\mathbf 1$. Moreover, fixing a complement $S_0$ of $\mathbb R\mathbf 1$ in $S$ ($\dim S_0=p-1$) and writing $d=d_0+a\mathbf 1$, the normalization $(T',d)\mapsto(e^{-a}T',d_0)$ maps solutions to solutions; so $(M,T)$ is identifiable iff (B.1) has no solution with $d\in S_0\setminus\{0\}$.*

**Proof.** $D_{e^{s}}$ is invertible, so record equality is equivalent to (B.1) with $d=s-s'$. Constant $d=a\mathbf 1$: row $n$ reads $m_n^\top T'=e^{a}y_n$, i.e. $MT'=e^{a}MT$, and $\operatorname{rank}M=K$ forces $T'=e^{a}T$, which is the gauge point $(cT,\,s-\log c\,\mathbf 1)$ with $c=e^{a}>0$. The equivariance $(T',d)\mapsto(e^{a}T',d+a\mathbf 1)$ is a direct substitution in (B.1). $\blacksquare$

Two structural remarks. *(a) The reduction eliminates $s$:* identifiability is a property of $(M,T,S)$ alone, uniform over the true drift — this is the source of the "for every $s\in S$ simultaneously" quantifier in every theorem below. *(b) Full column rank is necessary:* for rank-deficient $M$ the equivalence "constant $d$ $\Leftrightarrow$ gauge-trivial" is **false** even on $\mathcal U$. Counterexample ($\operatorname{rank}M=1$): $N=K=2$, both rows of $M$ equal to $(0,1)$, $T=(0,1)^\top$, $T'=(1,1)^\top$: $MT=MT'=(1,1)^\top$, so $(T',d=0)$ solves (B.1) with constant $d$, yet $T'\notin\mathbb R T$ — an object-kernel ambiguity invisible to the normalized $d\neq0$ incidence set. This is why $\mathcal R$ is carried explicitly in every exceptional set.

**What this does not claim.** The reduction is exact but presupposes $\operatorname{rank}M=K$ and a nonvanishing carrier; neither is a restriction for the a.e. statements (both failure sets are null), but both must be — and are — carried explicitly.

### B.1 Lemma B.1 (row dichotomy)

**Lemma B.1.** *Let $(M,T)\in\mathcal U$ and let $(T',d)$ solve (B.1) with $d$ nonconstant ($d\notin\mathbb R\mathbf 1$). Then $T'$ is not a scalar multiple of $T$; consequently $T'-e^{d_n}T\neq0$ for every $n=1,\dots,N$.*

**Proof.** Suppose $T'=\beta T$. Row $n$ of (B.1): $\beta y_n=e^{d_n}y_n$; since $y_n\neq0$ on $\mathcal U$, $e^{d_n}=\beta$ for all $n$, so $d$ is constant — contradiction. For the display: if $T'=e^{d_n}T$ for a single $n$, then $T'\parallel T$ ($T\neq0$ because $y=MT\neq0$). $\blacksquare$

Only *global* nonconstancy of $d$ is used — partial constancy (some equal components) is harmless — and the only division is by $y_n$, legitimate on $\mathcal U$.

### B.2 Lemma B.2 (joint submersivity)

Define $F:\mathbb R^{N\times K}\times\mathbb R^K\times\mathbb R^K\times S_0\to\mathbb R^N$,

$$F(M,T,T',d)\;=\;MT'-D_{e^{d}}MT,\qquad F_n=m_n^\top\bigl(T'-e^{d_n}T\bigr).
\tag{B.2}$$

**Lemma B.2.** *At every zero of $F$ with $(M,T)\in\mathcal U$ and $d\in S_0\setminus\{0\}$, the differential of $F$ with respect to $M$ alone is surjective onto $\mathbb R^N$.*

**Proof.** Perturb row $n$ only: $\delta M=e_n\,\delta m_n^\top$ gives $\delta F=e_n\cdot\delta m_n^\top(T'-e^{d_n}T)$, which spans $\mathbb R e_n$ as $\delta m_n$ ranges over $\mathbb R^K$, provided $T'-e^{d_n}T\neq0$ — which holds at every such zero for every $n$ by Lemma B.1. Rows are decoupled, so the image contains every $e_n$. $\blacksquare$

Only $\delta M$ is used: no genericity of $S$, no structure of $d$ beyond nonconstancy, and the object is untouched. This rowwise witness is uniform over the whole zero set — the ingredient the superseded route lacked.

### B.3 A measure lemma, and generic exact identifiability at $N\ge K+p$

**Lemma B.3 ($C^1$ image of a lower-dimensional manifold is null).** *Let $X$ be a second-countable $C^1$ manifold with $\dim X=m<q$, and $f:X\to\mathbb R^q$ a $C^1$ map. Then $f(X)$ has $q$-dimensional Lebesgue measure zero.*

**Proof.** Second countability gives a countable chart cover $\varphi_i:U_i\to\mathbb R^m$, and each chart domain is exhausted by countably many compact cubes; by countable subadditivity it suffices to treat one compact cube $Q$ of side $\ell$. On $Q$, $g=f\circ\varphi_i^{-1}$ is $C^1$, hence Lipschitz with some constant $L$. Subdividing $Q$ into $k^m$ subcubes of side $\ell/k$, each image lies in a ball of radius $L\sqrt m\,\ell/k$ in $\mathbb R^q$, so the outer measure of $g(Q)$ is at most $k^m\,c_q(2L\sqrt m\,\ell/k)^q=C\,k^{m-q}\to0$ since $m<q$. $\blacksquare$

No properness or compactness of $f$ is needed; the zero manifolds below are embedded in Euclidean space, hence second countable and $\sigma$-compact automatically. The statement is **false** for merely continuous maps (space-filling curves) — the $C^1$ regularity supplied by Lemma B.2 is load-bearing.

**Theorem B.4 (generic exact identifiability; Theorem A′(ii)).** *Fix $S\ni\mathbf 1$, $\dim S=p\ge2$. If $N\ge K+p$, there is a Lebesgue-null set $E_{\mathrm{gen}}\subset\mathbb R^{N\times K}\times\mathbb R^K$ such that every $(M,T)\notin E_{\mathrm{gen}}$ is identifiable: for every $s\in S$, the only $(T',s')\in\mathbb R^K\times S$ with $\Phi_M(T',s')=\Phi_M(T,s)$ are the gauge orbit of $(T,s)$.*

**Proof.** Work on the open set $\Omega=\{(M,T,T',d):(M,T)\in\mathcal U,\ T'\in\mathbb R^K,\ d\in S_0\setminus\{0\}\}$. By Lemma B.2, $0$ is a regular value of $F$ on $\Omega$, so $Z=F^{-1}(0)\cap\Omega$ is an embedded real-analytic submanifold of codimension $N$:

$$\dim Z=(NK+K)+K+(p-1)-N.$$

The projection $\pi:Z\to\mathbb R^{N\times K}\times\mathbb R^K$ onto $(M,T)$ is $C^1$ and

$$\dim Z-\dim(\mathbb R^{N\times K}\times\mathbb R^K)=K+p-1-N\le-1\quad(N\ge K+p),$$

so $\pi(Z)$ is Lebesgue-null by Lemma B.3. By the reduction (Lemma B.0, which requires $\operatorname{rank}M=K$),

$$\{\text{non-identifiable pairs in }\mathcal U\}\;\subset\;(\mathcal R\times\mathbb R^K)\,\cup\,\pi(Z),$$

and the full non-identifiable set is contained in $(\mathcal R\times\mathbb R^K)\cup\pi(Z)\cup\mathcal U^{c}$ — three null sets. Set $E_{\mathrm{gen}}$ to their union. $\blacksquare$

**Remark B.4.1 (quantifier order, proved).** For a.e. $(M,T)$: for **every** $s\in S$, no non-gauge alias — the null set $E_{\mathrm{gen}}$ is independent of $s$, because the reduction eliminated $s$ before any measure-theoretic step. This does **not** imply that one design works for every object; that is Theorem B.5 at its own larger threshold. ($T'=0$ needs no special handling: $T'=0$ forces $D_{e^{d}}y=0$, impossible on $\mathcal U$.)

**Remark B.4.2 (fixed-object slice).** For each **fixed** $T\neq0$: a.e. $M$ identifies that particular $T$ when $N\ge K+p$ (the exceptional design set may depend on $T$). Proof: freeze $T$, run the same argument with $F_T(M,T',d)=MT'-D_{e^{d}}MT$ on $\{M:(M,T)\in\mathcal U\}\times\mathbb R^K\times(S_0\setminus\{0\})$; Lemma B.2's witness uses only $\delta M$, the zero set has dimension $NK+K+(p-1)-N\le NK-1$, and Lemma B.3 applies; add $\mathcal R$ and the proper algebraic set $\{M:(M,T)\notin\mathcal U\}$. This slice form is what covers the fixed structured objects of the Fig. 6 protocol.

**What this does not claim.** No claim of uniformity over objects for a fixed design (see Theorem B.5 and its counterexample); no claim at the boundary $N=K+p-1$ (necessity is open — Sec. B.8, sharpness paragraph); nothing about conditioning, noise, or estimators; deterministic structured designs are not covered by any a.e. statement.

### B.4 Uniform identifiability on the nonvanishing-carrier set at $N\ge 2K+p-1$

**Theorem B.5 (uniform sufficiency on $\mathcal U_M$; Theorem A′(iii)).** *Fix $S\ni\mathbf 1$, $\dim S=p\ge2$. If $N\ge 2K+p-1$, there is a Lebesgue-null set $E_{\mathrm{unif}}\subset\mathbb R^{N\times K}$ such that for every $M\notin E_{\mathrm{unif}}$: every $T\in\mathcal U_M$ is identifiable, for every $s\in S$ simultaneously.*

**Proof.** The solution set of (B.1) is scaling-equivariant — $(T,T',d)$ solves iff $(cT,cT',d)$ does, $c\neq0$ — and nonvanishing carrier and nonconstancy are scale-invariant, so it suffices to rule out solutions with $|T|=1$. Let

$$\Omega'=\{(M,T,T',d):|T|=1,\ (M,T)\in\mathcal U,\ T'\in\mathbb R^K,\ d\in S_0\setminus\{0\}\},$$

an open subset of $\mathbb R^{N\times K}\times S^{K-1}\times\mathbb R^K\times S_0$. Lemma B.2 holds verbatim on $\Omega'$ (the sphere constrains $T$, not $M$), so $Z'=F^{-1}(0)\cap\Omega'$ is an embedded real-analytic manifold of codimension $N$ with

$$\dim Z'=NK+(K-1)+K+(p-1)-N=NK+(2K+p-2-N),$$

and the projection $\pi':Z'\to\mathbb R^{N\times K}$ onto $M$ has deficit $2K+p-2-N\le-1$ when $N\ge2K+p-1$; $\pi'(Z')$ is null by Lemma B.3. Set $E_{\mathrm{unif}}=\mathcal R\cup\pi'(Z')$ (rank-deficient designs added explicitly: the reduction needs $\operatorname{rank}M=K$). If $M\notin E_{\mathrm{unif}}$ and $(T',d)$ solved (B.1) for some $T\in\mathcal U_M$, $d\in S_0\setminus\{0\}$, then rescaling by $c=1/|T|$ would put $(M,cT,cT',d)\in Z'$, i.e. $M\in\pi'(Z')$ — contradiction. Lemma B.0 concludes. $\blacksquare$

**Remark B.5.1 (why $\mathcal U_M$ cannot be dropped: a zero-carrier counterexample at the threshold).** "Every nonzero object" is **false** even at $N=2K+p-1$. Take $K=2$, $p=2$, $N=5=2K+p-1$, $S=\operatorname{span}\{\mathbf 1,e_1\}$, $T=(1,1)^\top$, and $M$ with rows $(1,-1),(1,0),(0,1),(1,1),(1,2)$, so $MT=(0,1,1,2,3)^\top$ — full column rank, first carrier coordinate zero. For every $t\neq0$, $d=t\,e_1\in S$ is nonconstant and $(T',d)=(T,\,t\,e_1)$ solves (B.1): row 1 reads $m_1^\top T'=e^{t}\cdot0=0$, rows 2–5 are unchanged. So $(T,s)$ and $(T,s-t\,e_1)$ produce identical records for every $t$ — a one-parameter family of non-gauge aliases. This mechanism is available for **any** design: every object on the hyperplane $\{m_1^\top T=0\}$ acquires such aliases whenever $S$ contains a vector supported on the zero-carrier row. The correct conclusion is the stated one: for a.e. $M$, every $T\in\mathcal U_M$, every $s\in S$.

**What this does not claim.** Uniformity is over nonvanishing-carrier objects and drifts, not over designs: an adversarially chosen $M$ can defeat the bound. Necessity of $2K+p-1$ is not claimed (Sec. B.8). No claim about recovery algorithms or noise.

### B.5 Lemma W: position of the twisted column space

For $(M,T)\in\mathcal U$ with $\operatorname{rank}M=K$ define

$$W(M,T)\;:=\;D_y^{-1}\operatorname{col}(M)\subset\mathbb R^N,\qquad y=MT,$$

a $K$-dimensional subspace with $\mathbf 1\in W$ (since $D_y\mathbf 1=y\in\operatorname{col}(M)$). Aliases relate to $W$ by: *$d\in S$ solves (B.1) for some $T'$ iff $e^{d}\in W(M,T)$* — indeed $D_{e^{d}}y=D_y e^{d}$, so (B.1) reads $MT'=D_ye^{d}$, i.e. $e^{d}=D_y^{-1}MT'\in W$; conversely $e^{d}=D_y^{-1}Mu$ gives the (unique, by full column rank) solution $T'=u$.

**Lemma W.** *Fix any subspace $S\ni\mathbf 1$ with $\dim S=p\le N$, and $K\ge1$. For a.e. $(M,T)\in\mathcal U$:*

$$\dim\bigl(S\cap W(M,T)\bigr)\;=\;1+\max\{0,\ (p-1)+(K-1)-(N-1)\}\;=\;1+\max\{0,\,K+p-N-1\}.
\tag{B.3}$$

*No genericity of $S$ is assumed or used — only $\mathbf 1\in S$.*

**Proof.** *(Step 1: basis completion; fixed $T$.)* Fix $T\neq0$ and complete it to a basis $B_T=[T,b_2,\dots,b_K]\in GL_K$. The map $M\mapsto MB_T=(y,v_2,\dots,v_K)$ is a linear isomorphism of $\mathbb R^{N\times K}$, hence maps null sets to null sets both ways: a.e. $M$ $\Leftrightarrow$ a.e. $(y,v_2,\dots,v_K)$.

*(Step 2: fixed-$y$ isomorphism.)* For fixed $y\in(\mathbb R^*)^N$ (a co-null condition), set $w_j:=D_y^{-1}v_j$. For fixed $y$ this is a linear isomorphism of $\mathbb R^{N(K-1)}$ in $(v_2,\dots,v_K)$ — it preserves "a.e." and introduces no correlation between the $w_j$ and the fixed $S$. Then $W=D_y^{-1}\operatorname{span}(y,v_2,\dots,v_K)=\operatorname{span}(\mathbf 1,w_2,\dots,w_K)$.

*(Step 3: quotient.)* Let $q:\mathbb R^N\to\mathbb R^N/\mathbb R\mathbf 1$ (dimension $N-1$). $A:=q(S)$ has dimension $p-1$ (the kernel $\mathbb R\mathbf 1$ lies in $S$); $q(W)=\operatorname{span}(qw_2,\dots,qw_K)$.

*(Step 4: general position against the fixed $A$.)* For a.e. $(w_2,\dots,w_K)$: the $q(w_j)$ are independent and $\dim(A\cap q(W))=\max\{0,(p-1)+(K-1)-(N-1)\}$. Failure is the vanishing of suitable maximal minors of the matrix $[A\text{-basis}\mid qw_2\cdots qw_K]$ — a polynomial condition in the $w_j$, not identically zero (a witness exists: against one fixed subspace, vectors can be chosen stepwise outside a finite union of proper subspaces), hence a proper algebraic — null — subset. This is general position with respect to the fixed $A$ only; no genericity of $S$.

*(Step 5: $q(S\cap W)=q(S)\cap q(W)$, via $\mathbf 1\in W$.)* "$\subseteq$" is trivial. "$\supseteq$": if $x\in S$, $x'\in W$ and $q(x)=q(x')$, then $x-x'\in\mathbb R\mathbf 1\subseteq W$, so $x\in W$, i.e. $x\in S\cap W$. The kernel of $q$ on $S\cap W$ is exactly $\mathbb R\mathbf 1$ (as $\mathbf 1\in S\cap W$), whence $\dim(S\cap W)=1+\dim(q(S)\cap q(W))$.

*(Step 6: Fubini twice, with Borel measurability.)* The quantifier order so far: for every fixed $T\neq0$, for a.e. $y$, for a.e. $(v_j)$ — hence, by Steps 1–2 and Fubini on $\mathbb R^N\times\mathbb R^{N(K-1)}$, for every fixed $T\neq0$, for a.e. $M$, formula (B.3) holds. The failure set $B=\{(M,T)\in\mathcal U:\text{(B.3) fails}\}$ is Borel: the dimension condition is a Boolean combination of rank conditions (minor vanishing/nonvanishing) on matrices whose entries are rational in $(M,T)$ on $\mathcal U$ (the $w_j$ are entries of $M$ divided by coordinates of $MT$). Measurability licenses a second Fubini, over $T$: every $T$-slice of $B$ is $M$-null, so $B$ is null in $\mathbb R^{N\times K}\times\mathbb R^K$. $\blacksquare$

**Remark W.1 ($K=1$).** For $K=1$ the lemma **holds**: $W=\mathbb R\mathbf 1$ identically, $\dim(S\cap W)=1$, and (B.3) also gives $1+\max\{0,p-N\}=1$ since $p\le N$. What degenerates at $K=1$ is the necessity of the global thresholds (Sec. B.7), not Lemma W.

**What this does not claim.** (B.3) is an a.e. statement over $(M,T)$; it says nothing about any *particular* design (e.g. structured $M$), and nothing about the conditioning of the intersection, only its dimension.

### B.6 The generic local threshold ($K\ge2$) and genuine failure below the wall

**Kernel derivation (independent; no import from the superseded route).** Fix $(M,T)\in\mathcal U$ with $\operatorname{rank}M=K$ and any $s\in S$. The differential of $\Phi_M$ at $(T,s)$ is

$$D\Phi_M(T,s)[\delta T,\delta s]\;=\;D_{e^{s}}\bigl(M\,\delta T+D_y\,\delta s\bigr),\qquad y=MT.
\tag{B.4}$$

The diagonal factor is invertible, so $(\delta T,\delta s)\in\ker\Leftrightarrow M\delta T=-D_y\delta s$; the right side lies in $\operatorname{col}(M)$ iff $\delta s\in D_y^{-1}\operatorname{col}(M)=W(M,T)$, and then $\delta T=-(M^\top M)^{-1}M^\top D_y\delta s$ is unique. Hence $\ker D\Phi_M(T,s)\cong S\cap W$ via $(\delta T,\delta s)\mapsto\delta s$, and

$$\dim\ker D\Phi_M(T,s)=\dim(S\cap W),\qquad \operatorname{rank}D\Phi_M(T,s)=K+p-\dim(S\cap W),$$

independently of $s$. The gauge tangent is the line spanned by $(-T,\mathbf 1)$ (from $c\mapsto(cT,s-\log c\,\mathbf 1)$), and it lies in the kernel since $MT=D_y\mathbf 1$; as $\mathbf 1\in S\cap W$ always, the maximal gauge-compatible rank is $K+p-1$ and the defect from it is $\dim(S\cap W)-1$. By Lemma W, for a.e. $(M,T)\in\mathcal U$ and every $s$:

$$\operatorname{rank}D\Phi_M(T,s)=\min\{N,\ K+p-1\}.$$

**Theorem B.6 (generic local iff; Theorem A′(i), rank part).** *Fix $S\ni\mathbf 1$, $\dim S=p\ge2$, and $K\ge2$. There is a Lebesgue-null set $E_{\mathrm{loc}}\subset\mathbb R^{N\times K}\times\mathbb R^K$ — take $E_{\mathrm{loc}}=(\mathcal R\times\mathbb R^K)\cup\mathcal U^c\cup B$ with $B$ the failure set of Lemma W — such that for every $(M,T)\notin E_{\mathrm{loc}}$ with $T\in\mathcal U_M$ and every $s\in S$: $\operatorname{rank}D\Phi_M(T,s)=\min\{N,K+p-1\}$, and $(T,s)$ is locally identifiable modulo gauge **iff** $N\ge K+p-1$.*

**Proof.** The rank formula is the kernel derivation plus Lemma W. *Sufficiency at $N\ge K+p-1$ (ordinary local injectivity modulo gauge):* write $S=\mathbb R\mathbf 1\oplus S_0$; the bookkeeping

$$S\cap W=\mathbb R\mathbf 1\oplus(S_0\cap W)$$

holds because for $x\in S\cap W$, $x=a\mathbf 1+x_0$ with $x_0\in S_0$ gives $x_0=x-a\mathbf 1\in W$. At maximal rank $\dim(S\cap W)=1$, so $S_0\cap W=0$. Restrict $\Phi_M$ to the gauge slice $\mathbb R^K\times(s+S_0)$, of dimension $K+p-1$: by (B.4) its differential at $(T,s)$ has kernel $\cong S_0\cap W=0$, so the restricted map is an immersion there, hence (constant-rank/immersion theorem) a local embedding — locally injective on the slice. Any nearby alias is gauge-normalized into the slice by a factor $c$ near $1$, so ordinary local identifiability modulo gauge holds. *Necessity at $N\le K+p-2$:* Theorem B.7 below supplies a positive-dimensional manifold of exact aliases through $(T,s)$ — genuine failure, not merely a rank diagnostic. $\blacksquare$

**Theorem B.7 (genuine failure below the wall; Theorem A′(i), below-wall part).** *Fix $S\ni\mathbf 1$, $K\ge2$, $N\le K+p-2$. For every $(M,T)\notin E_{\mathrm{loc}}$ with $T\in\mathcal U_M$ and every $s\in S$: through $(T,s)$ passes a real-analytic manifold of exact aliases of dimension $K+p-N-1\ge1$; every point with $d\neq0$ is gauge-inequivalent to $(T,s)$, and the aliased objects satisfy $T'(d)\to T$ as $d\to0$.*

**Proof.** Let $P=\Pi_{W^\perp}$ be the orthogonal projection onto $W^\perp$ ($\dim W^\perp=N-K$ by full column rank) and define the real-analytic map $\varphi:S_0\to W^\perp$, $\varphi(d)=P(e^{d})$. Then $e^{d}\in W\Leftrightarrow\varphi(d)=0$ and $\varphi(0)=P\mathbf 1=0$. The differential is $D\varphi_0=P|_{S_0}$ ($\tfrac{d}{dt}\big|_0e^{td}=d$ componentwise; $P$ linear). By the bookkeeping $S\cap W=\mathbb R\mathbf 1\oplus(S_0\cap W)$ and Lemma W with $N\le K+p-2$ (the max in (B.3) is attained), $\dim(S_0\cap W)=K+p-N-1$, so

$$\operatorname{rank}D\varphi_0=(p-1)-(K+p-N-1)=N-K=\dim W^\perp:$$

$D\varphi_0$ is surjective. By the (real-analytic) submersion/implicit-function theorem, $\varphi^{-1}(0)$ is, near $0$, a real-analytic manifold of dimension $(p-1)-(N-K)=K+p-N-1\ge1$. For each $d$ in it, $e^{d}\in W$; with the left inverse $L=(M^\top M)^{-1}M^\top$ set

$$T'(d)\;:=\;L\,D_y\,e^{d},$$

so that $MT'(d)=D_ye^{d}$ ($D_ye^{d}=D_{e^{d}}y\in\operatorname{col}(M)$ precisely when $e^{d}\in W$): $(T'(d),d)$ solves (B.1), $T'(0)=Ly=T$, and $T'(d)\to T$ by continuity. Every $d\neq0$ lies in $S_0\setminus\{0\}$, hence $d\notin\mathbb R\mathbf 1$: a genuine non-gauge alias — $(T,s)$ and $(T'(d),s-d)$ produce identical records. $\blacksquare$

**Consistency check at $N=K$.** At $N=K$ (square, $\operatorname{rank}M=K$): $W=\mathbb R^N$, $W^\perp=0$, $\varphi\equiv0$, and the alias manifold is a full neighborhood of $0$ in $S_0$ — ambiguity dimension $p-1$, exactly Theorem A. No hidden $N\ge K+1$ assumption; no contradiction ($p\ge2$ gives $K<K+p\le2K+p-1$, so the square case lies strictly below both global thresholds).

**What this does not claim.** The local iff is generic in $(M,T)$ — a particular structured design must be checked separately. Local identifiability at $N\ge K+p-1$ does not imply global uniqueness (far aliases at the boundary are exactly the open sharpness question, Sec. B.8). Nothing about the singular values of the Jacobian, i.e. conditioning.

### B.7 The $K=1$ stratum

**Theorem B.8 ($K=1$: global identifiability; Theorem A′(iv)).** *Let $K=1$. For every $M$, every $T\in\mathcal U_M$, and every $s\in S$, the pair $(T,s)$ is globally identifiable modulo gauge, for every admissible $N$.*

**Proof.** $T\in\mathcal U_M$ means $T\neq0$ and $m_n\neq0$ for all $n$ (scalars $m_nT\neq0$). Any solution of (B.1) satisfies $e^{d_n}=m_nT'/(m_nT)=T'/T$ for every $n$, so $d$ is constant and $c:=T'/T=e^{d_1}>0$ — the gauge. $\blacksquare$

The local threshold at $K=1$ reads $N\ge K+p-1=p$, which is **automatically satisfied** ($S\subseteq\mathbb R^N$ forces $p\le N$) — the threshold is vacuous, not "inapplicable". Consequently neither $N\ge K+p$ nor $N\ge2K+p-1$ is necessary at $K=1$: corner strata break naive universal-necessity claims, which is why all necessity statements in this appendix are restricted to $K\ge2$.

### B.8 Theorem A′ — the manuscript statement, and sharpness status

**Theorem A′ (proved tall-design identifiability results).** Let $K\ge1$, $N\ge K$, and let $S\le\mathbb R^N$ be a fixed, known linear subspace of dimension $p\ge2$ with $\mathbf 1\in S$. For $M\in\mathbb R^{N\times K}$ define $\Phi_M(T,s)=D_{e^{s}}MT$ and $\mathcal U_M=\{T\in\mathbb R^K:(MT)_n\neq0$ for every $n\}$. Parameters are identified modulo the positive global-scale gauge $(T,s)\sim(cT,\,s-\log c\,\mathbf 1)$, $c>0$.

*(i) (Generic local threshold and genuine failure below it, $K\ge2$.)* There is a Lebesgue-null set $E_{\mathrm{loc}}\subset\mathbb R^{N\times K}\times\mathbb R^K$ such that for every $(M,T)\notin E_{\mathrm{loc}}$ with $T\in\mathcal U_M$ and every $s\in S$: $\operatorname{rank}D\Phi_M(T,s)=\min\{N,K+p-1\}$. Consequently $(T,s)$ is locally identifiable modulo gauge iff $N\ge K+p-1$. If $N\le K+p-2$ then a gauge-normalized neighborhood of $(T,s)$ contains a real-analytic manifold of exact aliases of dimension $K+p-N-1\ge1$, and every other sufficiently nearby point of it is gauge-inequivalent.

*(ii) (Generic exact-identifiability sufficiency.)* If $N\ge K+p$, there is a Lebesgue-null set $E_{\mathrm{gen}}\subset\mathbb R^{N\times K}\times\mathbb R^K$ such that for every $(M,T)\notin E_{\mathrm{gen}}$ and every $s\in S$: $D_{e^{s'}}MT'=D_{e^{s}}MT$ with $(T',s')\in\mathbb R^K\times S$ implies $T'=cT$, $s'=s-\log c\,\mathbf 1$ for a unique $c>0$. Exact identifiability holds simultaneously for every possible true drift $s\in S$. This statement is **not** uniform over all objects for one fixed $M$.

*(iii) (Uniform exact-identifiability sufficiency on the nonvanishing-carrier set.)* If $N\ge2K+p-1$, there is a Lebesgue-null set $E_{\mathrm{unif}}\subset\mathbb R^{N\times K}$ such that for every $M\notin E_{\mathrm{unif}}$, every $T\in\mathcal U_M$, every $s\in S$, and every $(T',s')\in\mathbb R^K\times S$: $D_{e^{s'}}MT'=D_{e^{s}}MT$ implies $T'=cT$, $s'=s-\log c\,\mathbf 1$ for a unique $c>0$. The same generic design works simultaneously for all nonvanishing-carrier objects and all true drifts in $S$.

*(iv) (Degenerate one-dimensional object stratum.)* If $K=1$ then for every $M$ and every $T\in\mathcal U_M$ and every $s\in S$, the pair $(T,s)$ is globally identifiable modulo gauge, for every admissible $N$. Neither $N\ge K+p$ nor $N\ge2K+p-1$ is necessary when $K=1$.

**Proof.** (i) = Theorems B.6–B.7 ($E_{\mathrm{loc}}$ from Lemma W); (ii) = Theorem B.4; (iii) = Theorem B.5; (iv) = Theorem B.8 (which holds for every $M$, not just a.e.). $\blacksquare$

**Sharpness status.** Parts (ii) and (iii) are sufficient conditions, not proved if-and-only-if thresholds. For $K\ge2$, the below-wall part of (i) proves generic exact failure whenever $N\le K+p-2$. The remaining necessity assertion for the $K+p$ bound is the boundary case $N=K+p-1$: dimension counting predicts nonlocal aliases there, but dominance of the bad-pair projection has not been proved. Likewise, dimension counting predicts that a generic design fails uniform identifiability for some object when $N\le2K+p-2$, but this necessity direction has not been proved in the intermediate regime. Thus $K+p$ and $2K+p-1$ are conjecturally sharp for $K\ge2$ under generic/nondegenerate drift geometry, not universal sharp thresholds for every fixed $S$. The $K=1$ stratum explicitly rules out any universal necessity claim.

**What this does not claim.** Necessity of the two global thresholds (see the sharpness paragraph); anything about deterministic structured designs (the ordered-Hadamard obstruction of Theorem A is unaffected, and no a.e. statement covers a fixed named design); anything about conditioning, noise robustness, or estimators — uniqueness at a threshold is compatible with arbitrarily bad stability; and no coverage of objects constrained to lower-dimensional sets (e.g. exactly sparse) — open constraint sets (e.g. positivity with nonvanishing carrier) inherit all a.e. statements by restriction. The Fig. 6 experiment (Sec. 9) is evidence for the *local rank wall* of part (i) — with the fixed-object slice covered by Remark B.4.2 — and probes algorithmic recovery; it neither tests nor proves the sharpness predictions.

### B.9 Relation to the superseded incidence-variety route

Earlier versions of this appendix proved Theorem A′ through a collision incidence variety: a stratum-counting lemma over the gain-ratio manifold, a dominant-stratum rank hypothesis $\operatorname{rank}[M,-D_bM]=\min(N,2K)$, a determinantal-transversality argument for the rank-drop locus, and two low-pass lemmas (a level-multiplicity bound for $S_{\mathrm{LP}}$ and a generic-rank lemma for $[M,-DM]$) feeding a three-level transfer proposition. **That route is superseded (R11), and its claims are withdrawn or replaced as follows.**

- The former "sharp iff" statements at $N\ge K+p$ (generic) and $N\ge2K+p-1$ (uniform) are **withdrawn**: their necessity directions rested on unproved dominant-projection and determinantal-transversality assertions. The proved statements are the sufficiency directions, now established by Theorems B.4–B.5 above, together with the genuinely sharp *local* iff at $N=K+p-1$ (Theorem B.6) and genuine below-wall failure (Theorem B.7). Sharpness of the two global thresholds is a labeled prediction (Sec. B.8).
- The former uniform claim quantified over "every nonzero object"; that is **false** at the stated threshold (Remark B.5.1) and is replaced by uniformity over the nonvanishing-carrier set $\mathcal U_M$.
- The former route needed genericity of the drift family (or the low-pass transfer lemmas to emulate it). The parametric-transversality proof holds for **every fixed $S\ni\mathbf 1$**, so the low-pass transfer machinery (level-multiplicity bound, generic-rank lemma, three-level transfer hierarchy, and the $L_S$ multiplicity check) is no longer needed for Theorem A′ and is not restated here; the withdrawn material remains available in the archived drafts (`paper_draft/THEORY_APRIME_REPROOF_v1.md` header note, and git history of this file) for provenance.
- The $K=1$, $N=p=2$ counterexample that broke the old claimed generic threshold is absorbed as the degenerate stratum, Theorem A′(iv).

**What this section does not claim.** Nothing in the superseded route is relied upon anywhere in Secs. B.0–B.8; conversely, no assertion of the superseded route beyond the ones re-proved above should be quoted from earlier drafts.

## Appendix C — Carrier statistics and the stationarity anchor

This appendix proves Proposition 1, formalizes condition (★) quantitatively, proves Proposition 2 (with counterexamples in both directions), and proves Theorem B. Throughout, $R_n = a_n B_n$ is the bucket record, $B_n = \langle I_n, T\rangle = \sum_{j=1}^K I_{n,j} T_j$ the carrier, $\ell_n = \log a_n$ the log-gain, $S$ the drift class with $p=\dim S$, $S_1=\sum_j T_j$, $S_2=\|T\|_2^2$, $K_{\mathrm{eff}}=S_1^2/S_2$, $K_\infty=S_2/\|T\|_\infty^2$, $K_4=S_2^2/\sum_j T_j^4$, and $W$ denotes the window length of the blind estimator $\hat g_n = W^{-1}\sum_{k\in W_n} Y_k$ applied to $Y_n=\log R_n$. Asymptotic statements are for a triangular array indexed by $(K,N)$: the object $T=T^{(K)}$ and pattern law may vary with $K$, and limits are taken along $K,N\to\infty$.
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

**(iv) Higher cumulants and a conditional log-carrier expansion.** For every $r\ge2$ for which $\kappa_r(I)$ exists, $\kappa_r(B_n)=\kappa_r(I)\sum_jT_j^r$, so the standardized law can depend on all existing higher-moment ratios, not on $K_{\mathrm{eff}}$ alone. Write $B_n=\mu_IS_1(1+u_n)$. The log expansion needs assumptions not implied by (P1)–(P4): $B_n>0$ a.s., $\mathbb E|\log B_n|^2<\infty$, $\mathbb E|u_n|^3\to0$, and $\mathbb E[|\log(1+u_n)|^2\mathbf1\{|u_n|>1/2\}]=O(\mathbb E|u_n|^3)$. Under these additional assumptions,
$$\mathbb{E}\log B_n=\log(\mu_I S_1)-\tfrac12\operatorname{Var}(u_n)+O(\mathbb{E}|u_n|^3),\qquad \operatorname{Var}(\log B_n)=\frac{(\sigma_I/\mu_I)^2}{K_{\mathrm{eff}}}+O(\mathbb{E}|u_n|^3).$$

*Proof.* (i) Linearity of expectation and independence across $j$ give the mean and (Bienaymé) the variance; independence across $n$ gives the i.i.d. claim. (ii) Apply the Lindeberg–Feller CLT [Billingsley1995, Thm. 27.2] to the triangular array $X_j=T_j(I_{n,j}-\mu_I)$ with $s^2=\sigma_I^2 S_2$. Since $|X_j|\le \|T\|_\infty|I-\mu_I|$, the event $\{|X_j|>\varepsilon s\}$ is contained in $\{|I-\mu_I|>\varepsilon\sigma_I\sqrt{K_\infty}\}$, so the Lindeberg fraction is
$$\frac{1}{\sigma_I^2 S_2}\sum_j T_j^2\,\mathbb{E}\big[(I-\mu_I)^2\mathbf 1\{|X_j|>\varepsilon s\}\big]\;\le\;\frac{1}{\sigma_I^2}\,\mathbb{E}\big[(I-\mu_I)^2\mathbf 1\{|I-\mu_I|>\varepsilon\sigma_I\sqrt{K_\infty}\}\big]\;\longrightarrow\;0$$
by uniform integrability as $K_\infty\to\infty$. (iii) Esseen's inequality for sums of independent, non-identically distributed variables [Petrov1975, Ch. V] gives the bound with third-moment ratio $\nu_3\sum_j|T_j|^3/S_2^{3/2}$, and $\sum_j|T_j|^3\le\|T\|_\infty S_2$ yields the $K_\infty^{-1/2}$ form. (iv) Cumulant homogeneity ($\kappa_r(cX)=c^r\kappa_r(X)$) and additivity over independent summands give the cumulant formula. The log expansion is Taylor's theorem with Lagrange remainder applied to $\log(1+u)$ on the event $\{|u_n|\le\tfrac12\}$. ∎

**Status of the log expansion (conditional).** Step (iv) is a controlled delta-method expansion under its explicit positivity, integrability, and lower-tail assumptions; it is **not** a consequence of (P1)–(P4). An atom at $B_n=0$ makes $\mathbb E\log B_n=-\infty$ even if its probability decays with $K$. A strictly positive pattern floor together with suitable concentration is one sufficient route. Photon records with zeros instead use the separate oracle-known-carrier soft-log theorem of Appendix D, not a blind extension of Theorem B.

**What this does not claim.** The proposition does not say the carrier law is determined by $(\mu_B,\sigma_B)$ — that reduction holds only at the Gaussian-approximation level; the exact law feels every weighted cumulant of $T$. For gain recovery, the shape-dependent contribution to $m_T=\mathbb{E}\log B_n$ is a *time-constant* scalar absorbed by the global-scale gauge, but the shape-dependent log variance and tails remain in finite-sample concentration and rate constants. Because the iid law is still time-homogeneous, this extra dependence does not create temporal bias or defeat consistency once (★) holds. The proposition also does not assert cross-row decorrelation or window-energy whitening for structured (SRHT) carriers — those require the Walsh-spectrum/$K_4$ conditions of Appendix E, where $K_{\mathrm{eff}}$ alone is again insufficient.

### C.2 The quantitative stationarity condition (★)

**Definition (★)$(W,\epsilon,\delta)$.** Let $\{B_n\}_{n\le N}$ be the carrier and $W_n$ length-$W$ windows covering $\{1,\dots,N\}$. The carrier satisfies the *quantitative stationarity anchor* with tolerance $\epsilon$ and confidence $1-\delta$ if there exists a scalar $m_T\in\mathbb R$ (allowed to depend on $T$, not on $n$) such that
$$P\Big(\max_{1\le n\le N}\Big|\,W^{-1}\!\!\sum_{k\in W_n}\log B_k-m_T\Big|\le \epsilon\Big)\ \ge\ 1-\delta .$$
We say **(★) holds asymptotically** if for every $\delta>0$ there are windows $W=W_N\to\infty$, $W/N\to0$, with $\epsilon=\epsilon_{W,N,\delta}\to0$. The scalar $m_T$ is exactly the quantity absorbed by the global-scale gauge $a\mapsto ca$, $T\mapsto T/c$ (which shifts $m_T\mapsto m_T-\log c$, $\ell\mapsto\ell+\log c$, leaving $Y$ invariant).

### C.3 Proposition 2 — (★) is a window-estimator criterion, not a universal one

**Proposition 2.** Assume the drift is slow in the sense of hypothesis (B3) below, with $C_\beta L\,(W/N)^\beta\to0$. Then:

**(a) Equivalence for the windowed corrector.** The blind windowed estimator $\hat g_n=W^{-1}\sum_{k\in W_n}Y_k$ is uniformly consistent for $\ell_n+m_T$ (in probability, uniformly over $n$) **if and only if** (★) holds asymptotically.

**(b) (★) is not necessary for identifiability.** There are designs violating (★) that are nonetheless identifiable: a tall design with $N\ge K+p$ is exactly algebraically identifiable modulo scale for a.e. design–object pair $(M,T)$, simultaneously for every drift $s\in S$ (Theorem A′(ii); see Appendix B.4 and Remark B.4.1), with *no* stationarity whatsoever. Likewise, at fixed known support, ordinary local identifiability may follow from the explicit full-rank criterion of Corollary 2; the count $K_0\ge p-1$ alone is only necessary for that differential full-rank test.

**(c) (★) is not sufficient for algebraic identifiability.** There are settings where (★) holds yet exact separation of $(a,T)$ is impossible: (c1) any *square* iid random design $N=K$ whose positive carrier satisfies the stated log-tail and window-scaling conditions — those conditions give (★), yet Theorem A applies to every invertible realization, so a nonconstant $s\in S$ still maps $(\ell,T)$ to an exact alias; (c2) a uniform row re-ordering $\pi$ of a positive-offset full square Hadamard record with finite log range and variance obeys (★) under the scaling below, while the row-permuted matrix remains invertible and therefore still falls under Theorem A. Quantitatively, Serfling's inequality for sampling without replacement [31] gives, for the finite population $g_k=\log B_k$ with variance $\tau_g^2$ and range $R_g$,
$$P\Big(\Big|W^{-1}\!\!\sum_{i=n}^{n+W-1} g_{\pi(i)}-\overline g\Big|\ge t\Big)\ \le\ 2\exp\!\Big[-\frac{W t^2}{2\tau_g^2+\tfrac23 R_g t}\Big],$$
so a union bound over the $\le N$ windows yields (★)$(W,\epsilon,\delta)$ whenever $\log N\ll W$ (and $W$ remains below the drift coherence time). This device fails when some $g_k$ are undefined (nonpositive buckets) or the population log-variance/range is uncontrolled, and it does **not** deliver the small carrier variance $\sigma_{\mathrm{LR}}^2\asymp1/K_{\mathrm{eff}}$ of genuinely random nonnegative patterns.

*Proof.* (a) Decompose exactly
$$\hat g_n-(\ell_n+m_T)\;=\;\underbrace{\Big(W^{-1}\!\!\sum_{k\in W_n}\ell_k-\ell_n\Big)}_{\text{drift bias}}\;+\;\underbrace{\Big(W^{-1}\!\!\sum_{k\in W_n}\log B_k-m_T\Big)}_{\text{carrier deviation}} .$$
The drift bias is $\le C_\beta L\,(W/N)^\beta\to0$ deterministically by (B3). Hence $\max_n|\hat g_n-(\ell_n+m_T)|\to0$ in probability iff the maximal carrier deviation does — which is verbatim the asymptotic form of (★). Both implications are immediate from this identity. (b) Theorem A′ (see Appendix B) is proved without any distributional assumption on the carrier order; the support-zero criterion is Corollary 2 (see Appendix A). (c1) The iid log-tail/window hypotheses give (★), while Theorem A (see Appendix A) holds for every invertible realized square matrix. (c2) Serfling's bound plus the union over windows gives (★) under the displayed positive-log scaling; row permutation preserves invertibility, so Theorem A still supplies the exact alias. ∎

**What this does not claim.** Part (a) is an equivalence for *one estimator family* (windowed local averages of $\log R_n$; the same proof covers kernel weights of matching order). It is not a characterization of identifiability by all mechanisms — (b) and (c) are precisely the two failure modes of that over-reading. Nor does (★) by itself bound the *rate*: rates require the variance model of Theorem B, and reconstruction quality after gain correction additionally requires the corrected linear inverse problem to be well posed (see Appendix F).

### C.4 Theorem B — statistical relative-gain identifiability

**Theorem B.** For each record length $N$, assume:

- **(B1) Triangular-array signal model.** $Y_{N,n}=\log R_{N,n}=\ell_{N,n}+m_{T,N}+z_{N,n}$, $n=1,\dots,N$, where $m_{T,N}=\mathbb E\log B_{N,n}$ is constant within row, $B_{N,n}>0$ a.s., and $z_{N,n}=\log B_{N,n}-m_{T,N}$ is centered.
- **(B2) Carrier noise.** Each row is strictly stationary. Under (B2a) its rowwise autocovariances $\gamma_N(h)$ are absolutely summable; define $\sigma_{\mathrm{abs},N}^2=\sum_h|\gamma_N(h)|$ and $V_{N,n}(W)=\operatorname{Var}\{W^{-1}\sum_{k\in W_{N,n}}z_{N,k}\}$. Hence $V_{N,n}(W)\le\sigma_{\mathrm{abs},N}^2/W$ for $W$ distinct equal-weight frames. Under (B2b), the high-probability constants are uniform in $N$: $\beta_N(k)\le\beta_0e^{-(k/b)^\kappa}$ and $\|z_{N,n}\|_{\psi_1}\le M$.
- **(B3) Slow drift and window order.** Define $b_{N,n}(W)=W^{-1}\sum_{k\in W_{N,n}}\ell_{N,k}-\ell_{N,n}$. For normalized-time Hölder radius $L_N$ and a matched window, $|b_{N,n}(W)|\le C_\beta L_N(W/N)^\beta$. Arbitrary truncated or one-sided windows are covered for $\beta\in(0,1]$; for $\beta\in(1,2]$ this order is asserted only where the weights annihilate the first moment, or for a separately defined boundary local-polynomial rule.
- **(B4) Vanishing bias and variance.** $W_N\to\infty$, $W_N/N\to0$, and $b_{N,n}(W_N)\to0$, $V_{N,n}(W_N)\to0$ at every covered index. Sufficient conditions are $L_N(W_N/N)^\beta\to0$ and $\sigma_{\mathrm{abs},N}^2/W_N\to0$. Uniform conclusions require the corresponding suprema to vanish.

Then:

**(i) Pointwise consistency with rate.** For $\hat g_{N,n}=W_N^{-1}\sum_{k\in W_{N,n}}Y_{N,k}$,
$$\mathbb E[\hat g_{N,n}-(\ell_{N,n}+m_{T,N})]^2=b_{N,n}(W_N)^2+V_{N,n}(W_N)\le C\left[L_N^2(W_N/N)^{2\beta}+\sigma_{\mathrm{abs},N}^2/W_N\right]\to0.$$
For a fixed stationary law, $V(W)=\sigma_{\mathrm{LR}}^2/W+o(W^{-1})$. For a triangular array the additive expansion $V_{N,n}(W_N)=\sigma_{\mathrm{LR},N}^2/W_N+o(W_N^{-1})$ additionally requires $\lim_{H\to\infty}\sup_N\sum_{|h|\ge H}|\gamma_N(h)|=0$. Under (B2b), with $q=\lceil b[\log\{\max(e,4\beta_0W_N/\delta)\}]^{1/\kappa}\rceil$, the same bias plus the standard block-Bernstein fluctuation bound holds with probability at least $1-\delta$; uniformity uses $\delta/N$ and a uniform bias bound.

**(ii) Centered-gain recovery.** If (B4) holds uniformly, $\hat\ell_{N,n}^{c}=\hat g_{N,n}-N^{-1}\sum_m\hat g_{N,m}$ obeys
$$\sup_n\mathbb E[\hat\ell_{N,n}^{c}-(\ell_{N,n}-\bar\ell_N)]^2\le4\sup_m\{b_{N,m}(W_N)^2+V_{N,m}(W_N)\}\to0.$$

**(iii) Gauge.** $m_{T,N}+\bar\ell_N$ is not identifiable under $a\mapsto ca$, $T\mapsto T/c$. Within the additive bucket-only experiment (B1), with its carrier-noise law held fixed, part (ii) recovers the centered-gain estimand; no assertion is made that scale is the only ambiguity in a richer joint pattern–bucket model.

*Proof.* Put $e_{N,n}=\hat g_{N,n}-(\ell_{N,n}+m_{T,N})=b_{N,n}(W_N)+W_N^{-1}\sum_kz_{N,k}$. Centering makes its mean-square the exact sum of squared bias and window variance, and stationarity gives $V_{N,n}(W)=W^{-1}\sum_{|h|<W}(1-|h|/W)\gamma_N(h)\le\sigma_{\mathrm{abs},N}^2/W$. Dominated convergence proves the fixed-law long-run-variance limit. Splitting the triangular-array covariance sum at a fixed lag proves the additive uniform remainder under the stated uniform-tail condition; a multiplicative $1+o(1)$ form is invalid when the signed long-run variance vanishes. Berbee coupling with the displayed $q$ and block Bernstein give the high-probability bound. Jensen applied to $e_{N,n}-N^{-1}\sum_me_{N,m}$ gives part (ii). Part (iii) is the direct scale transformation. ∎

**What this does not claim.** Rowwise stationarity and a finite rowwise covariance sum do not alone imply consistency. The all-index conclusion for $\beta>1$ needs an implemented boundary rule with moment cancellation; ordinary truncated averages are covered only for $\beta\le1$. The theorem is not finite-sample algebraic identifiability. Empty-bin photon records instead use the oracle-known-carrier soft-log theorem in Appendix D, not a blind extension of this result. The covariance constants are model inputs, and consistent gain correction does not itself guarantee good reconstruction.

## Appendix D — Estimation rates, minimax lower bounds, and Fisher geometry

This appendix proves the rate statements of Sec. 6: a high-probability windowed-estimator upper bound under mixing, a matching interior minimax rate for a separately specified fixed iid-Gaussian quotient experiment (Theorem D), the quotient-Fisher geometry underlying the identifiability dichotomy, and the direct oracle-known-carrier Poisson soft-log rate. Notation is locked to the main text: $R_n=a_nB_n$, $\ell=\log a\in S$ with $\dim S=p$ and $\mathrm{span}\{1\}\subset S$, $Y_n=\log R_n=\ell_n+m_T+z_n$ with $m_T=\mathbb{E}\log B_n$ a time-independent scalar, windows $W$, and the spread functionals $K_{\mathrm{eff}}$, $K_\infty$ as in Appendix C. The Hölder smoothness order is written $\beta\in(0,2]$ with seminorm $L_a$; the symbol $\alpha$ is reserved for the soft-log offset $\psi_\alpha(c)=\log(c+\alpha)$.

Throughout, the *discrete Hölder ball* $H_\beta(L_a)$ is defined operationally: $\ell$ belongs to $H_\beta(L_a)$ relative to a window family $\{W_n\}$ of order $\beta$ if the deterministic smoothing bias obeys
$$\Big|\,W^{-1}\!\!\sum_{k\in W_n}\ell_k-\ell_n\Big|\;\le\;C_\beta\,L_a\,W^{\beta}\qquad\text{for all }n. \tag{D.1}$$
For $\beta\in(0,1]$ a one-sided moving average of $\ell$ with modulus $|\ell_k-\ell_n|\le L_a|k-n|^{\beta}$ satisfies (D.1). For $\beta\in(1,2]$, (D.1) requires a *centered symmetric* window (or a kernel of order $\lfloor\beta\rfloor$), so that the first-order bias cancels and only curvature $L_2$ survives; a one-sided window does not attain $\beta>1$.

### D.1 Lemma D.1 (windowed gain-estimation rate under mixing)

**Statement.** Assume:

1. *(Model)* $Y_n=\ell_n+m_T+z_n$, with $\{z_n\}$ strictly stationary and $\mathbb{E}z_n=0$.
2. *(Mixing)* $\{z_n\}$ is $\beta$-mixing with $\beta(k)\le\beta_0\exp[-(k/b)^{\kappa}]$ for some $\beta_0,b>0$, $\kappa>0$.
3. *(Tails)* $\|z_n\|_{\psi_1}\le M$ (sub-exponential).
4. *(Smoothness)* $\ell\in H_\beta(L_a)$ in the sense (D.1), with the window order matched to $\beta$ as above.

Let $\hat g_n=W^{-1}\sum_{k\in W_n}Y_k$ and set $q=\lceil b[\log\{\max(e,4\beta_0W/\delta)\}]^{1/\kappa}\rceil$. Then for each fixed $n$ and $\delta\in(0,1)$, with probability at least $1-\delta$,
$$\big|\hat g_n-(\ell_n+m_T)\big|\;\le\;C_\beta L_a W^{\beta}\;+\;C\Big[\sqrt{\tfrac{\nu_q^2\,q\,\log(4/\delta)}{W}}\;+\;\tfrac{M\,q\,\log(4/\delta)}{W}\Big], \tag{D.2}$$
where $\nu_q^2=\operatorname{Var}\!\big(q^{-1/2}\sum_{i=1}^{q}z_i\big)$ is the block-variance proxy; when the autocovariances are absolutely summable, $\nu_q^2\le C'\sigma_{\mathrm{abs}}^2$ with the summable-autocovariance constant $\sigma_{\mathrm{abs}}^2=\sum_h|\gamma(h)|$ of Appendix C (hypothesis (B2a)) — the signed long-run variance $\sigma_{\mathrm{LR}}^2\le\sigma_{\mathrm{abs}}^2$ of Appendix C is the asymptotic variance of window means and plays no role in these non-asymptotic bounds. Uniformity over $n=1,\dots,N$ follows by replacing $\delta$ with $\delta/N$ (a $\log N$ inflation inside the brackets).

*(Expectation version, weaker hypotheses.)* If instead $\{z_n\}$ is only $\alpha$-mixing with $\sum_{h\ge1}\alpha(h)^{\eta/(2+\eta)}<\infty$ and $\|z_0\|_{2+\eta}<\infty$ for some $\eta>0$, then
$$\mathbb{E}\big[\hat g_n-(\ell_n+m_T)\big]^2\;\le\;C\,L_a^2W^{2\beta}+C\,\sigma_{\mathrm{abs}}^2/W. \tag{D.3}$$

**Proof.** *Bias.* $\hat g_n-(\ell_n+m_T)=\big[W^{-1}\sum_k\ell_k-\ell_n\big]+W^{-1}\sum_k z_k$; the first bracket is bounded by $C_\beta L_aW^\beta$ by (D.1).

*Fluctuation, high probability.* Partition the window into alternating blocks of length $q$. Berbee coupling costs at most $\beta_0W\exp[-(q/b)^\kappa]$; the displayed choice of $q$, including $\beta_0$, makes this at most $\delta/4$ (if $q\ge W$, the result is a one-block, possibly vacuous boundary bound). Bernstein's inequality on the coupled block sums gives (D.2). When $\sum_h|\operatorname{Cov}(z_0,z_h)|<\infty$, $\nu_q^2\le C'\sigma_{\mathrm{abs}}^2$.

*Fluctuation, expectation.* Davydov's covariance inequality [32] gives $|\operatorname{Cov}(z_0,z_h)|\le 8\,\alpha(h)^{\eta/(2+\eta)}\|z_0\|_{2+\eta}^2$; the summability hypothesis makes the autocovariance series absolutely summable, so $\operatorname{Var}(W^{-1}\sum_{k\in W_n}z_k)\le \bar\sigma^2/W$ with $\bar\sigma^2\le C\sigma_{\mathrm{abs}}^2$. Combining with the squared bias via $(x+y)^2\le2x^2+2y^2$ gives (D.3). $\blacksquare$

**Corollary D.2 (optimized blind high-count upper rate).** Minimizing the right side of (D.3) over $W$ gives
$$W^{*}\asymp\big(\sigma_{\mathrm{abs}}^2/L_a^2\big)^{1/(2\beta+1)},\qquad \mathrm{MSE}^{*}\asymp L_a^{2/(2\beta+1)}\,\sigma_{\mathrm{abs}}^{4\beta/(2\beta+1)}, \tag{D.4}$$
valid when $W^{*}\in[1,N]$ and $W^{*}$ is shorter than the gain coherence time; otherwise the boundary window $W=1$ or $W=N$ applies. For iid random carriers, $\sigma_{\mathrm{abs}}^2=\sigma_{\mathrm{LR}}^2\approx(\sigma_I/\mu_I)^2/K_{\mathrm{eff}}$ to leading Gaussian/log-variance order under the spikiness condition $K_\infty\to\infty$ of Prop. 1. No identification of the deterministic Hölder constant $L_a$ with the OU decorrelation parameter is made; the OU protocol has the separate $\rho^{1/2}$ analysis in Appendix F.

**What this does not claim.** The constants $C,C_\beta$ are not tracked and depend on $(\beta_0,b,\kappa,M)$. For $\beta>1$, the bias order covers only weights that cancel the first moment; a truncated one-sided edge average needs a defined boundary local-polynomial rule. Nothing is claimed for $\beta>2$, non-stationary carriers, or adaptive window selection. The step $\nu_q^2\lesssim\sigma_{\mathrm{abs}}^2$ requires summable autocovariances.

### D.2 Theorem D (fixed-Gaussian interior minimax equivalence)

Observe $Y_n=m+f(t_n)+\varepsilon_n$, $t_n=n/N$, with iid $\varepsilon_n\sim\mathcal N(0,\sigma^2)$ and unknown $m$. Fix the gauge by $N^{-1}\sum_nf(t_n)=0$. Let $\mathcal H_\beta^0(L,A)$ be the gauge-fixed Hölder class with $\|f\|_\infty\le A$: for $0<\beta\le1$, $|f(x)-f(y)|\le L|x-y|^\beta$; for $1<\beta\le2$, $f\in C^1$ and $|f'(x)-f'(y)|\le L|x-y|^{\beta-1}$. The loss is pointwise squared error at a fixed interior grid point. Feasible bandwidths are centered windows with $3\le W\le Nh_0$, where $h_0$ is smaller than the fixed interior margin. Put
$$h_*=(\sigma^2/(NL^2))^{1/(2\beta+1)},\qquad r_N=L^{2/(2\beta+1)}(\sigma^2/N)^{2\beta/(2\beta+1)}.$$

**Theorem D (fixed-Gaussian interior rate).** If the rounded $h_*$ is feasible and $Lh_*^\beta\le A/4$, then
$$c_\beta r_N\le\inf_{\hat f}\sup_{f\in\mathcal H_\beta^0(L,A)}\mathbb E_f(\hat f_{n_0}-f(t_{n_0}))^2\le C_\beta r_N. \tag{D.5}$$
The upper bound is attained by the centered local average (or order-one local polynomial), after subtracting the record mean.

**Proof.** With $W\asymp Nh_*$, symmetry cancels the affine term for $\beta>1$, the squared bias is at most $CL^2h_*^{2\beta}$, and the variance is at most $C\sigma^2/(Nh_*)+C\sigma^2/N$. For the lower bound, use a smooth interior bump $g_h=cLh^\beta\phi((t-t_{n_0})/h)$ and subtract its discrete mean. At $h\asymp h_*$ the pointwise separation is $\gtrsim Lh_*^\beta$, while $\operatorname{KL}(P_0,P_1)\le CNL^2h^{2\beta+1}/\sigma^2=O(1)$. Le Cam's lemma [25] gives the reverse inequality. $\blacksquare$

**Integrated Sobolev counterpart.** In the same iid-Gaussian experiment, expand in a discrete Fourier basis orthonormal for the empirical inner product $N^{-1}\sum_nu_nv_n$, omit the constant coefficient, and set $\Theta_\beta(L)=\{\theta:\sum_{j\ne0}|j|^{2\beta}\theta_j^2\le L^2\}$. Integrated loss then equals the sum of coefficient risks and each coefficient has noise variance $\sigma^2/N$. When $J_*\asymp(NL^2/\sigma^2)^{1/(2\beta+1)}$ satisfies $1\ll J_*\ll N$,
$$\inf_{\hat f}\sup_{\theta\in\Theta_\beta(L)}\frac1N\sum_n\mathbb E(\hat f_n-f_n)^2\asymp_\beta L^{2/(2\beta+1)}(\sigma^2/N)^{2\beta/(2\beta+1)}. \tag{D.6}$$
Fourier truncation gives the upper bound and the standard Assouad/Pinsker Gaussian-sequence result [25], [27] gives the lower bound.

**What this does not claim.** This is not a minimax theorem for each fixed mixing or non-Gaussian carrier law; Lemma D.1 supplies upper bounds there. It makes no boundary or adaptive claim. Outside the feasible interior regime, one-frame noise, finite class diameter, and full-record averaging yield separate bounds, but they are not combined here into a three-segment finite-$N$ minimax equivalence because matching bounds in every saturation regime have not been proved.

### D.3 Proposition D.4 (Theorem-A ambiguity implies quotient-Fisher singularity)

**Statement.** *(a) Linear-Gaussian window model.* Let $\ell=U\theta$ with $U\in\mathbb R^{N\times p'}$, and observe $Y=U\theta+m\mathbf 1+z$, $z\sim\mathcal N(0,\Sigma)$, $\Sigma\succ0$ known, $m\in\mathbb R$ the unknown carrier log-mean (confounded with global gain scale). The Fisher information for $\theta$ after eliminating the nuisance $m$ is
$$I_\theta\;=\;U^{\top}\Sigma^{-1/2}P_\perp\Sigma^{-1/2}U,\qquad P_\perp=I-\frac{\Sigma^{-1/2}\mathbf 1\mathbf 1^{\top}\Sigma^{-1/2}}{\mathbf 1^{\top}\Sigma^{-1}\mathbf 1}. \tag{D.7}$$
For a linear functional $L\theta$: if $\mathrm{row}(L)\subseteq\mathrm{range}(I_\theta)$, every unbiased estimator obeys $\operatorname{Cov}(L\hat\theta)\succeq L\,I_\theta^{+}L^{\top}$ (Moore–Penrose CRB for singular information [38], [39]); if $L$ has a nonzero component along $\ker I_\theta$, **no unbiased estimator of $L\theta$ exists and the CRB is infinite** — the functional is not locally estimable.

*(b) Quotient statement.* Let $\Theta$ be the parameter manifold, $G$ the global-scale group $(a,T)\mapsto(ca,T/c)$, and $P_\theta$ a dominated model differentiable in quadratic mean. Define the quotient score operator $S_\theta:T_{[\theta]}(\Theta/G)\to L_0^2(P_\theta)$ and $I_\theta=S_\theta^{*}S_\theta$. Then: $I_\theta\succ0$ on $T_{[\theta]}(\Theta/G)$ **iff** $[\theta]\mapsto P_\theta$ is an immersion, i.e. iff the model is *locally differentially identifiable* modulo scale. Any $C^1$ ambiguity curve $[\theta(t)]$ with $P_{\theta(t)}=P_{\theta(0)}$ satisfies $S_\theta\theta'(0)=0$, hence produces a Fisher null direction. For the Theorem-A ambiguity this implication is *exact*: the explicit data-preserving path $\ell'=\ell+ts$, $T'=M^{-1}(c\odot e^{-ts})$, $s\in S\setminus\mathrm{span}\{1\}$ — the *exact collision curve* $\ell_u=\ell+u$, $T_u=M^{-1}D_{e^{-u}}MT$ in the notation of Appendix A — is a genuine ambiguity curve for a square invertible design, so the Fisher matrix in the full $(\ell,T)$ parameterization is singular along its tangent, and the CRB is $+\infty$ for every functional that varies along it. For a *tall* full-column-rank design the exact collision exists for a given $u\in S$ iff the range condition $(I-P_M)D_{e^{-u}}MT=0$ holds ($P_M$ the column-space projector); under the nonvanishing-carrier assumption $T_u\propto T$ only when $u$ is constant, and the quotient tangent null space is $\mathcal N_{\ell,T}=\{(u,h):D_{MT}u+Mh=0\}\supseteq\operatorname{span}\{(\mathbf1,-T)\}$, with local differential identifiability modulo scale exactly when equality holds.

*(c) Local-window corollary.* For a common shift and known Gaussian covariance $\Sigma_W$, the exact information is $I_W=\mathbf1^\top\Sigma_W^{-1}\mathbf1$ and $\operatorname{Var}(\hat t)\ge I_W^{-1}$. Only under standard Toeplitz/short-range conditions does this become $\sigma_{\mathrm{LR}}^2/W+o(W^{-1})$; the usual effective-sample-size formula is an asymptotic heuristic, not the finite-window Fisher object.

**Proof.** *(a)* The joint Fisher matrix of $(\theta,m)$ in the Gaussian model is the block matrix $\begin{pmatrix}U^{\top}\Sigma^{-1}U & U^{\top}\Sigma^{-1}\mathbf 1\\ \mathbf 1^{\top}\Sigma^{-1}U & \mathbf 1^{\top}\Sigma^{-1}\mathbf 1\end{pmatrix}$. Nuisance elimination is the Schur complement with respect to the $m$-block [40], which is exactly (D.7). The pseudoinverse CRB for singular FIM is Stoica–Marzetta [39]. The infinite-CRB claim is cleanest without CRB machinery: a direction $u\in\ker I_\theta$ that is tangent to an exact ambiguity curve leaves the data law invariant, so any estimator has *identical* distribution under $\theta$ and $\theta+tu$; unbiasedness for a functional with $Lu\neq0$ would force $L\theta=L(\theta+tu)$, a contradiction — hence no unbiased finite-variance estimator exists.

*(b)* Differentiability in quadratic mean makes $S_\theta$ well defined and $I_\theta=S_\theta^*S_\theta$ the pullback metric [vanderVaart1998, Ch. 7]. $I_\theta\succ0$ iff $S_\theta$ is injective iff the differential of $[\theta]\mapsto\sqrt{dP_\theta}$ is injective, i.e. an immersion. The ambiguity-curve implication is the chain rule: $t\mapsto P_{\theta(t)}$ constant $\Rightarrow$ its $L^2$ derivative $S_\theta\theta'(0)$ vanishes. For Theorem A the curve is explicit (see Appendix A), so no genericity is needed. $\blacksquare$

**What this does not claim.** The converse direction — Fisher singularity implying an actual *ambiguity manifold* — requires constant-rank (or analytic) regularity so that the rank defect integrates (rank theorem); Fisher singularity by itself only defeats *local differential* identifiability. Nonsingular Fisher does not exclude isolated *global* aliases. Part (a) assumes Gaussian noise with known $\Sigma$; part (c) is a Gaussian-model computation used as an order-of-magnitude floor, not a bound proven for the actual log-carrier distribution. No efficiency claim is made for the windowed estimator beyond rate (constants open, Theorem D).

### D.4 Theorem C (low-photon calibrated soft-log rate and the conditional $1/(W\bar\lambda)$ law)

**Statement (exact finite-window identity with known carriers, weighted form).** Let $C_n\mid\ell_n\sim\mathrm{Pois}(\lambda_n)$, $\lambda_n=\Lambda_0e^{\ell_n}b_n+d$, and assume conditional independence across distinct frames given the gain path and known positive carriers. The Fig. 5 carriers are oracle simulation truth. Fix $\alpha>0$, $\psi_\alpha(c)=\log(c+\alpha)$, and $m_\alpha(\lambda)=\mathbb E\psi_\alpha(C)$. For a fixed window, aggregate repeated frame occurrences into one nonnegative weight before defining $M_n$, $B_n$, and $V_n$ as below.
$$q_k(t)=m_\alpha(\Lambda_0e^t b_k+d),\qquad v_k(t)=\operatorname{Var}\!\left[\psi_\alpha(\operatorname{Pois}(\Lambda_0e^t b_k+d))\right],$$
$$M_n(t)=\sum_{k\in\mathcal I_n}w_{nk}q_k(t),\qquad y_n=\sum_{k\in\mathcal I_n}w_{nk}\psi_\alpha(C_k),$$
and define
$$B_n=\sum_{k\in\mathcal I_n}w_{nk}\{q_k(\ell_k)-q_k(\ell_n)\},\qquad V_n=\sum_{k\in\mathcal I_n}w_{nk}^2v_k(\ell_k).$$
Fix a compact operating range $\Theta=[\theta_{\min},\theta_{\max}]$ and let
$$\underline\kappa_n=\inf_{t\in\Theta}M_n'(t)>0,\qquad D_\Theta=\theta_{\max}-\theta_{\min}.$$
In the implementation $\Theta$ is the *calibration-safe interval*: if the calibration curve is certified only for $\lambda\in[\lambda_-,\lambda_+]$ and $d<\lambda_-$, the largest safe interval before intersection with the physical parameter range is
$$\left[\max_{k\in\mathcal I_n}\log\frac{\lambda_--d}{\Lambda_0b_k},\quad\min_{k\in\mathcal I_n}\log\frac{\lambda_+-d}{\Lambda_0b_k}\right],$$
and **nonemptiness of this interval is an assumption of the theorem** — a clamp cannot repair an empty calibration-safe interval. The estimator is the *endpoint-clamped generalized inverse* applied to the window statistic:
$$\hat\theta_n\;=\;G_n(y_n),\qquad G_n(y)\;=\;M_n^{-1}\!\big[\Pi_{M_n(\Theta)}\,y\big], \tag{D.8a}$$
where $\Pi_{M_n(\Theta)}$ projects onto the compact interval $M_n(\Theta)$ before inversion, so $G_n$ returns the corresponding endpoint of $\Theta$ when $y_n$ falls outside $M_n(\Theta)$ (an all-zero window has $y_n=\log\alpha$ and returns $\theta_{\min}$; without the clamp the inverse would diverge to $-\infty$ there — the clamp is part of the estimator, not an implementation afterthought). Assume:

1. *(Operating range; per-frame sensitivities and noise)* for every $k$ and every $\theta\in\Theta$, $\lambda_k(\theta)=\Lambda_0e^{\theta}b_k+d\in[\lambda_-,\lambda_+]\subset(0,\infty)$; consequently the per-frame sensitivity bound $\overline\kappa_k=\sup_{t\in\Theta}q_k'(t)$ and the per-frame noise $v_k(t)$ are finite, with $v_k(t)\le\bar\sigma_\alpha^2:=\sup_{\lambda\in[\lambda_-,\lambda_+]}\operatorname{Var}[\psi_\alpha(\mathrm{Pois}(\lambda))]<\infty$, $\kappa_{\max}:=\sup_k\overline\kappa_k<\infty$, and $\underline\kappa_n>0$;
2. *(Smoothness)* $\ell\in H_\beta(L_a)$ with the *pointwise* modulus $|\ell_k-\ell_n|\le L_a|k-n|^{\beta}$ and $\beta\in(0,1]$ (the paper's operative case is $\beta=1$; the precise obstruction above one and its partial repair are Remark D.4.2);
3. *(Membership)* $\ell_n\in\Theta$ for all $n$. (A positive margin $\Delta:=\min_n\operatorname{dist}(\ell_n,\partial\Theta)>0$ enters only the clamp-*probability* diagnostic of Remark D.4.4; the risk bound below does not use it.)

Then, conditionally on the gain path and known carriers,
$$\operatorname{Var}\!\left[\sum_{k\in\mathcal I_n}w_{nk}\{\psi_\alpha(C_k)-q_k(\ell_k)\}\right]=V_n$$
*exactly*, and no mixing or stationarity assumption is required. Then, conditionally on the gain path and the known carriers,
$$\mathbb E\big[(\hat\theta_n-\ell_n)^2\mid\ell,b\big]\le\frac{B_n^2+V_n}{\underline\kappa_n^2}. \tag{D.8}$$
There is **no separate clamp-event risk term**: the endpoint-clamped generalized inverse $G_n$ is globally $\underline\kappa_n^{-1}$-Lipschitz on all of $\mathbb R$ (proof below), so all-zero and out-of-range windows are already covered by (D.8); the clamp probability survives only as a diagnostic (Remark D.4.4). This is a finite-window statement: it requires neither stationarity nor mixing of the known carrier sequence.
Moreover, the pointwise modulus gives
$$|B_n|\le L_a\sum_{k\in\mathcal I_n}w_{nk}\overline\kappa_k|k-n|^\beta.$$
For an unpadded average of $W$ distinct frames, $w_{nk}=1/W$ and hence
$$V_n=\frac{\bar v_{n,\alpha}}{W},\qquad \bar v_{n,\alpha}=\frac1W\sum_{k\in W_n}v_k(\ell_k)\le\bar\sigma_\alpha^2,$$
while $|B_n|\le C\,\kappa_{\max}L_aW^{\beta}$, so (D.8) specializes to
$$\mathbb{E}\big(\hat\theta_n-\ell_n\big)^2\;\le\;C\Big(\tfrac{\kappa_{\max}}{\underline\kappa_n}\Big)^{2}L_a^2W^{2\beta}\;+\;\frac{\bar\sigma_\alpha^2}{\underline\kappa_n^2\,W}$$
(no clamp term: the global Lipschitz property already covers clamped windows). Minimize the displayed finite-window bound only over widths for which frames are distinct after aggregation, the calibration-safe interval is nonempty, and the smoothness bound applies. If the sensitivity ratios are uniformly controlled and the unconstrained optimizer is feasible,
$$\mathrm{MSE}_\alpha^{*}\;\le\;C\,\underline\kappa^{-2}\,\big[\kappa_{\max}L_a\big]^{2/(2\beta+1)}\,\bar\sigma_\alpha^{4\beta/(2\beta+1)}. \tag{D.9}$$
The loss is log-domain squared error. In the photon-starved regime the variance-to-sensitivity ratio obeys the *general* window law
$$\frac{V_n}{M_n'(\ell_n)^2}=\frac{\sum_kw_{nk}^2\lambda_k(\ell_k)}{\big[\sum_kw_{nk}\lambda_k(\ell_n)\big]^2}\{1+O_\alpha(\varepsilon)\}$$
(low-photon corollary below), with the *actual* intensities $\lambda_k(\ell_k)$ in the numerator and the *anchor* intensities $\lambda_k(\ell_n)$ in the sensitivity denominator; it simplifies to $\{1+O_\alpha(\varepsilon)\}/(W\bar\lambda_n)$ only for distinct equal-weight frames under *local gain flatness* (see the counterexample below), and in that flat regime it is minimax-*order* sharp *in this centered log-domain loss at $d=0$* by the centered-loss lower bound following the proof. As the expected intensity tends to zero, the Poisson information for log intensity vanishes; with the clamp (D.8a), empty observed bins never make the estimator diverge.

**Proof.** *Sensitivity and variance of the soft-log.* The Poisson derivative identity $\frac{d}{d\lambda}\mathbb{E}f(C)=\mathbb{E}[f(C{+}1)-f(C)]$ (differentiate $\sum_c e^{-\lambda}\lambda^c f(c)/c!$ term by term) gives
$$\kappa_\alpha(\lambda):=\frac{d}{d\log\lambda}\mathbb{E}\log(C+\alpha)=\lambda\,\mathbb{E}\log\frac{C+1+\alpha}{C+\alpha},$$
with the expansions $\kappa_\alpha(\lambda)=1+O(1/\lambda)$ for $\lambda\gg1$ and $\kappa_\alpha(\lambda)=c_\alpha\lambda+O(\lambda^2)$ for $\lambda\ll1$, where $c_\alpha=\log(1+1/\alpha)$. Since $q_k'(t)=\kappa_\alpha(\lambda_k(t))\cdot\Lambda_0e^{t}b_k/\lambda_k(t)$ ($=\kappa_\alpha(\lambda_k(t))$ at $d=0$), hypothesis 1 holds on any compact operating range. No uniform identification $\underline\kappa_n\asymp c_\alpha\bar\lambda_n$ is claimed: under unrestricted heteroscedastic carriers the infimum of $M_n'$ over $\Theta$ can sit far below $c_\alpha\bar\lambda_n$ (two-frame example $\lambda_1=\varepsilon^2$, $\lambda_2=2\varepsilon-\varepsilon^2$), so $\underline\kappa_n$-based displays are conservative bounds only; the correct low-photon law is the window-average corollary below. The Poisson Poincaré inequality [41], [42], $\operatorname{Var}f(C)\le\lambda\,\mathbb{E}[(f(C{+}1)-f(C))^2]$, yields $v_k=O(1/\lambda)$ at high $\lambda$ and $v_k=c_\alpha^2\lambda+O(\lambda^2)$ at low $\lambda$, whence $\bar\sigma_\alpha^2<\infty$ on $[\lambda_-,\lambda_+]$.

*Risk bound.* Write
$$y_n-M_n(\ell_n)=B_n+Z_n,\qquad Z_n=\sum_{k\in\mathcal I_n}w_{nk}\{\psi_\alpha(C_k)-q_k(\ell_k)\}.$$
The variables in $Z_n$ are independent and centered conditionally on the gain path and known carriers (Poisson counts are independent across frames given their intensities — the carrier is known, so no carrier randomness remains; this *conditional count independence* is an assumption of the theorem), so $\mathbb EZ_n=0$ and $\operatorname{Var}(Z_n)=V_n$ *exactly* — a finite-window identity requiring no mixing and no long-run variance.

*Global Lipschitz property of the clamped inverse.* $M_n$ is continuous and strictly increasing on the compact $\Theta$ with $M_n'\ge\underline\kappa_n>0$, so its ordinary inverse is $\underline\kappa_n^{-1}$-Lipschitz on $M_n(\Theta)$. Projection onto the interval $M_n(\Theta)$ is nonexpansive, hence the composition $G_n=M_n^{-1}\circ\Pi_{M_n(\Theta)}$ satisfies
$$|G_n(y_2)-G_n(y_1)|\le\frac{|y_2-y_1|}{\underline\kappa_n}\qquad\text{for *all* }y_1,y_2\in\mathbb R.$$
Since $\ell_n\in\Theta$ gives $G_n\{M_n(\ell_n)\}=\ell_n$,
$$|\hat\theta_n-\ell_n|=|G_n(y_n)-G_n\{M_n(\ell_n)\}|\le\frac{|B_n+Z_n|}{\underline\kappa_n}$$
with no case split on whether $y_n$ lands inside $M_n(\Theta)$: taking conditional second moments and using $\mathbb E[(B_n+Z_n)^2\mid\ell,b]=B_n^2+V_n$ gives (D.8) directly. The bound on $B_n$ follows by applying the mean value theorem to each $q_k$ and then the pointwise modulus; for equal weights the triangle inequality gives $|B_n|\le C\kappa_{\max}L_aW^{\beta}$ (valid for the pointwise modulus with $\beta\le1$; no cancellation across the window is invoked — cf. Remark D.4.2), and the standard bias–variance optimization gives (D.9). $\blacksquare$

**Approximate calibration and numerical inversion.** Let $\widetilde M_n$ be a continuous strictly increasing approximation to $M_n$ on the same interval $\Theta$ with $\sup_{t\in\Theta}|\widetilde M_n(t)-M_n(t)|\le\varepsilon_{\mathrm{cal},n}$, let $\widetilde G_n$ be its clamped generalized inverse (same endpoint convention), and suppose the numerical solver returns $\hat\theta_n^{\mathrm{num}}$ with $|\hat\theta_n^{\mathrm{num}}-\widetilde G_n(y_n)|\le\varepsilon_{\mathrm{bis},n}$, where $\varepsilon_{\mathrm{bis},n}$ is measured in the *log-parameter* domain. Inverse bracketing under the shared endpoint convention gives $G_n(y-\varepsilon_{\mathrm{cal},n})\le\widetilde G_n(y)\le G_n(y+\varepsilon_{\mathrm{cal},n})$, hence $\sup_y|\widetilde G_n(y)-G_n(y)|\le\varepsilon_{\mathrm{cal},n}/\underline\kappa_n$, and the conservative implementation bound is the RMSE (Minkowski) form
$$\big\{\mathbb E[(\hat\theta_n^{\mathrm{num}}-\ell_n)^2\mid\ell,b]\big\}^{1/2}\le\frac{\sqrt{B_n^2+V_n}}{\underline\kappa_n}+\frac{\varepsilon_{\mathrm{cal},n}}{\underline\kappa_n}+\varepsilon_{\mathrm{bis},n}. \tag{D.8b}$$
The quantities with the same (log-parameter) units are $\varepsilon_{\mathrm{cal},n}/\underline\kappa_n$ and $\varepsilon_{\mathrm{bis},n}$; a response-domain calibration error and a log-parameter bisection error must *not* be added before division by the sensitivity. If tabulation and interpolation have separately certified forward-error budgets, replace $\varepsilon_{\mathrm{cal},n}$ by their sum. For $J$ midpoint bisections on a log-parameter interval of diameter $D_n$, the numerical error is certified by $\varepsilon_{\mathrm{bis},n}\le D_n/2^{J+1}$.

**A theorem-level interpolation certificate.** A midpoint probe of the interpolation error is an empirical diagnostic, not by itself a uniform bound over the calibration interval. Put $x=\log\lambda$ and $f_\alpha(x)=m_\alpha(e^x)$. For a log-intensity grid of maximum spacing $\Delta_x$, piecewise-linear interpolation from exact node values obeys
$$\|f_\alpha-I_{\Delta_x}f_\alpha\|_\infty\le\frac{\Delta_x^2}{8}\,\|f_\alpha''\|_\infty, \tag{D.8c}$$
and with $\Delta g(c)=g(c{+}1)-g(c)$ the Poisson difference identities give
$$f_\alpha''(x)=\lambda\,\mathbb E\Delta\psi_\alpha(C)+\lambda^2\,\mathbb E\Delta^2\psi_\alpha(C),\qquad\lambda=e^x.$$
A certified bound $K_{\alpha,2}\ge\sup_{\lambda\in[\lambda_-,\lambda_+]}|f_\alpha''|$ together with a certified node-evaluation error $\varepsilon_{\mathrm{tab}}$ yields $\varepsilon_{\mathrm{cal}}\le\varepsilon_{\mathrm{tab}}+K_{\alpha,2}\Delta_x^2/8$; the expectations and Poisson tails may be enclosed analytically or by interval arithmetic. **Until such an enclosure is generated, the measured midpoint maximum of Remark D.4.1 must be labeled empirical**, and the manuscript so labels it.

**Low-photon corollary (the general leading term).** Let $d=0$ and define the *anchor* and *actual* per-frame intensities
$$\lambda_{k,n}^{0}=\Lambda_0e^{\ell_n}b_k=\lambda_k(\ell_n),\qquad\lambda_k^\star=\Lambda_0e^{\ell_k}b_k=\lambda_k(\ell_k),$$
$$A_n=\sum_kw_{nk}\lambda_{k,n}^{0},\qquad D_n=\sum_kw_{nk}^2\lambda_k^\star.$$
Fix $\alpha>0$, put $c_\alpha=\log(1+1/\alpha)$, and suppose $\max_{k\in\mathcal I_n}\{\lambda_{k,n}^{0},\lambda_k^\star\}\le\varepsilon$. The fixed-$\alpha$ Poisson expansions of the proof give, uniformly over arbitrary positive carrier heterogeneity,
$$M_n'(\ell_n)=c_\alpha A_n\{1+O_\alpha(\varepsilon)\},\qquad V_n=c_\alpha^2D_n\{1+O_\alpha(\varepsilon)\},$$
and therefore
$$\frac{V_n}{M_n'(\ell_n)^2}=\frac{D_n}{A_n^2}\{1+O_\alpha(\varepsilon)\}=\frac{\sum_kw_{nk}^2\lambda_k(\ell_k)}{\big[\sum_kw_{nk}\lambda_k(\ell_n)\big]^2}\{1+O_\alpha(\varepsilon)\}. \tag{D.10}$$
For $m=|\mathcal I_n|$ equal-weight *distinct* frames, writing $I_{n,\mathrm{ref}}=\sum_k\lambda_{k,n}^{0}$ and $I_{n,\mathrm{act}}=\sum_k\lambda_k^\star$, (D.10) reads $I_{n,\mathrm{act}}/I_{n,\mathrm{ref}}^2\cdot\{1+O_\alpha(\varepsilon)\}$, and with $h_{\ell,n}=\max_k|\ell_k-\ell_n|$,
$$e^{-h_{\ell,n}}\le I_{n,\mathrm{act}}/I_{n,\mathrm{ref}}\le e^{h_{\ell,n}}.$$
Only under *local gain flatness* $h_{\ell,n}=o(1)$ may the leading term be simplified to $\{1+O_\alpha(\varepsilon+h_{\ell,n})\}/I_{n,\mathrm{ref}}$; when the gain is constant in the window, $I_{n,\mathrm{act}}=I_{n,\mathrm{ref}}=m\bar\lambda_n$ and only then does (D.10) become $\{1+O_\alpha(\varepsilon)\}/(m\bar\lambda_n)$ — the $1/(W\bar\lambda)$ statement quoted in the main text. Carrier comparability is *not* needed; local gain flatness *is*. These expansions are stated for fixed $\alpha$; $c_\alpha\to\infty$ as $\alpha\to0$, so the fixed-$\alpha$ small-$\lambda$ statement must not be read as a triangular $\alpha\to0$ asymptotic.

**Counterexample to the unqualified $1/(W\bar\lambda)$ claim.** Take two equal-weight frames with equal carriers, target gain $\ell_n=0$, the other frame's gain $\ell=\log2$, and reference intensity $\varepsilon$. Then $I_{n,\mathrm{ref}}=2\varepsilon$ but $I_{n,\mathrm{act}}=3\varepsilon$, so (D.10) gives $3/(4\varepsilon)$ whereas the unqualified formula gives $1/(2\varepsilon)$: the ratio is $3/2$ and does *not* converge to one as $\varepsilon\downarrow0$. The unconditional window-average law asserted in earlier drafts is therefore false as stated and is withdrawn; (D.10) is the correct general statement.

**From a variance factor to estimator asymptotics.** Display (D.10) is an algebraic expansion of the local variance-to-sensitivity factor. To identify it with the estimator's leading MSE one additionally needs a local variance regime — $I_{n,\mathrm{act}}\to\infty$, $|B_n|=o(\sqrt{V_n})$, a Lindeberg condition, negligible clamp probability, and inverse-map linearization such as $\sup_{\Theta}|M_n''|\sqrt{V_n}/M_n'(\ell_n)^2\to0$. For bounded total information the compact clamp makes the risk saturate; one cannot globally identify the MSE with $1/I_n$.

**Centered-loss low-photon lower bound.** To compare with the blind task, evaluate the oracle experiment under the scale-invariant centered loss
$$d_{\mathrm{quot}}^2(\hat g,g)=\inf_{a\in\mathbb R}\frac1N\|\log\hat g-\log g-a\mathbf1\|_2^2=\frac1N\|P_N(\log\hat g-\log g)\|_2^2,\qquad P_N=I-\tfrac1N\mathbf1\mathbf1^\top.$$
This is the centered-log-gain loss reported in Fig. 5. Multiplying either gain profile by an arbitrary positive scalar leaves the loss unchanged, even though known $\Lambda_0$ and carriers make absolute scale identifiable in this oracle experiment.

*Pointwise lower bound (Le Cam two-point).* Let $0<\beta\le1$ and, conditionally on known positive carriers $q_1,\dots,q_N$, observe independent counts $C_i\sim\operatorname{Pois}(q_ie^{\ell_i})$. Estimate the quotient coordinate $P_N\ell$. Fix an interior index $n_0$, a baseline $\ell^{(0)}$ lying strictly inside both the amplitude and Hölder constraints (e.g. $\|\ell^{(0)}\|_\infty\le a_0/2$ and seminorm at most $L_a/2$), and a window $A$ of order $W$ containing $n_0$. Choose a contrast $\psi^{(W)}$ with
$$\operatorname{supp}\psi^{(W)}\subseteq A,\quad\mathbf1^\top\psi^{(W)}=0,\quad\|\psi^{(W)}\|_\infty\le1,\quad\psi^{(W)}_{n_0}=1,$$
$$\|\psi^{(W)}\|_2^2\ge cW,\qquad|\psi^{(W)}_i-\psi^{(W)}_j|\le CW^{-\beta}|i-j|^\beta.$$
Put $\lambda_i^{(0)}=q_ie^{\ell_i^{(0)}}$ and $I_A(\psi)=\sum_{i\in A}\lambda_i^{(0)}\psi_i^2\le W\bar\lambda_A$ with $\bar\lambda_A=W^{-1}\sum_{i\in A}\lambda_i^{(0)}$. For amplitude $a\le c_0\min\{a_0,\,L_aW^\beta,\,I_A(\psi)^{-1/2}\}$, both $\ell^{(0)}$ and $\ell^{(1)}=\ell^{(0)}+a\psi^{(W)}$ lie in a rescaled $H_\beta(L_a)$ ball; the Poisson KL obeys
$$\operatorname{KL}(P_0,P_1)=\sum_i\lambda_i^{(0)}\{e^{a\psi_i}-1-a\psi_i\}\le\tfrac{e^{a_0}}{2}a^2I_A(\psi),$$
kept below a numerical constant by the amplitude choice. Because $\mathbf1^\top\psi=0$, quotient projection does not reduce the separation at $n_0$, and Pinsker followed by Le Cam's two-point lemma [25] gives
$$R_{n_0}^{\mathrm{quot}}\ge c\min\left\{a_0^2,\;L_a^2W^{2\beta},\;\frac1{W\bar\lambda_A}\right\}. \tag{D.11}$$
When local photon rates have common order $\bar\lambda$, optimizing $W$ yields $R_{n_0}^{\mathrm{quot}}\gtrsim L_a^{2/(2\beta+1)}\bar\lambda^{-2\beta/(2\beta+1)}$, the direct Poisson counterpart of the upper rate (D.9); these optimized displays assume $1\lesssim W_*\lesssim N$, and otherwise (D.11) stays in the one-frame or finite-record saturation regime. Thus the $1/(W\bar\lambda)$ law is a *local-minimax* statement in the regime $W\bar\lambda\to\infty$; for bounded total information the risk saturates at the squared diameter of the local parameter neighborhood. It does *not* route through Theorem D's Gaussian bound (a Gaussian model is not a submodel of the mixed-Poisson experiment).

*Integrated lower bound (guarded Assouad hypercube).* Le Cam's two-point argument controls the pointwise loss only; the integrated quotient loss needs a hypercube. Partition an interior fraction of $\{1,\dots,N\}$ into $m\asymp N/W$ cells of length $CW$; inside each cell reserve a guard band of order $W$ and place a translated, rescaled copy $\psi_j$ of one fixed compactly supported, mean-zero $H_\beta$ template that vanishes on the cell boundary, with active supports separated by at least $cW$ and $\|\psi_j\|_2^2\ge cW$. Set $\ell^\omega=\ell^{(0)}+a\sum_j\omega_j\psi_j$, $\omega\in\{0,1\}^m$, with
$$\bar\lambda_*=\max_j|A_j|^{-1}\sum_{i\in A_j}\lambda_i^{(0)},\qquad a\le c_0\min\{a_0,\,L_aW^\beta,\,(W\bar\lambda_*)^{-1/2}\}.$$
The guard bands and the vanishing boundary keep the Hölder constant of the sum bounded independently of $m$, and the interior baseline keeps every vertex in the ball. Adjacent vertices differ on one block with $\operatorname{KL}\le Ca^2W\bar\lambda_*\le\kappa<1$; all pairwise differences are mean-zero, so quotient projection loses no distance, and Assouad's lemma [25] gives
$$R_{\mathrm{int}}^{\mathrm{quot}}=\inf_{\hat\ell}\sup_\omega\frac1N\mathbb E_\omega\|P_N(\hat\ell-\ell^\omega)\|_2^2\ge c\min\left\{a_0^2,\;L_a^2W^{2\beta},\;\frac1{W\bar\lambda_*}\right\}. \tag{D.12}$$

*Random carriers: choose alternatives before observing $B$.* If $q_i=\Lambda_0B_i$ is random with a parameter-independent law and $\mathbb EB_i<\infty$, the alternatives and their amplitude must be chosen *before* observing $B$, using the *expected* block information $\overline{\mathcal I}_A=\mathbb E_B\sum_{i\in A}\lambda_i^{(0)}\psi_i^2$ — not the realized one. The calculation then applies verbatim to the carrier-observed *joint oracle* experiment $(C,B)$, whose KL is $\operatorname{KL}(P_0^{C,B},P_1^{C,B})=\mathbb E_B\operatorname{KL}(P_0^{C\mid B},P_1^{C\mid B})$; marginalization gives $\operatorname{KL}(P_0^{C},P_1^{C})\le\operatorname{KL}(P_0^{C,B},P_1^{C,B})$, so the oracle lower bound transfers to the less-informative count-only experiment. This transfers *hardness*; it does not construct a blind estimator. For dark count $d>0$, replace the total count information by
$$\overline{\mathcal I}_A(\psi)=\mathbb E_B\sum_{i\in A}\frac{s_i^2}{s_i+d}\,\psi_i^2,\qquad s_i=\Lambda_0e^{\ell_i}b_i,$$
the local quadratic-KL information in the contrast direction (the bounded-perturbation remainder must be controlled uniformly); the identity $I(\theta)=\lambda$ does not hold for log gain in the presence of additive dark counts.

**Oracle local-shift information (the Fig. 5 reference line).** For a fixed window $A$, suppose independently $C_k\sim\operatorname{Pois}\{\lambda_k(t)\}$ with $\lambda_k(t)=s_ke^t+d_k$, where $s_k>0$ and $d_k\ge0$ are *known*. The score and Fisher information for the one-dimensional common shift $t$ are
$$S_t(C)=\sum_{k\in A}\{C_k-\lambda_k(t)\}\frac{s_ke^t}{\lambda_k(t)},$$
$$I_A(t)=\sum_{k\in A}\frac{s_k^2e^{2t}}{s_ke^t+d_k},\qquad I_A(t)=\sum_{k\in A}\lambda_k(t)\ \text{at }d_k=0. \tag{D.13}$$
Therefore $1/I_A(t)$ is the scalar Cramér–Rao reference for a regular unbiased estimator of a *common log-intensity shift* with carriers, offsets, and all other path coordinates held fixed — an **oracle common-shift diagnostic**, *not* the nuisance-path quotient CRB. For bias $b(t)=\mathbb E_t\hat t-t$ the biased CR inequality reads
$$\operatorname{MSE}_t(\hat t)\ge b(t)^2+\frac{\{1+b'(t)\}^2}{I_A(t)}:$$
MSE *below* $1/I_A$ is compatible with shrinkage bias, and MSE *above* $1/I_A$ does not establish unbiasedness. For a path model $\ell=U\theta$ at $d=0$ with estimable contrast coordinates separated from the constant direction and $D_\lambda=\operatorname{diag}(\lambda_1,\dots,\lambda_N)$, the information is $I_\theta=U^\top D_\lambda U$; eliminating a common nuisance scale $m$ entering as $\ell+m\mathbf1$ gives the Schur complement
$$I_{\theta\mid m}=U^\top D_\lambda U-U^\top D_\lambda\mathbf1(\mathbf1^\top D_\lambda\mathbf1)^{-1}\mathbf1^\top D_\lambda U,$$
the quotient Fisher object of this known-carrier parametric path model. It does not include unknown-object or unknown-carrier nuisance parameters; a contrast outside the range of the information matrix has no finite CR bound, and overlapping windows create cross-window covariance, so an average of $1/I_n$ is not an exact whole-record centered-loss CRB. Sharp minimax constants beyond these local calculations are not claimed.

**Remark D.4.1 (instantiation in the Fig. 5 protocol).** Here $d=0$ and $b_k$ are oracle carrier values. With $\Lambda_0$ fixed, the safe log-gain interval is
$$\Theta=\left[\max_k\log\frac{\lambda_-}{\Lambda_0b_k},\ \min_k\log\frac{\lambda_+}{\Lambda_0b_k}\right]$$
intersected with the physical range, and must be nonempty. The implementation solves $M_n(\hat\theta_n)=y_n$ by bisection using $m_\alpha(\Lambda_0e^\theta b_k)$, clamps endpoints, and uses truncated renormalized distinct-frame boundary windows. The measured midpoint interpolation error is $1.6410165\times10^{-6}$ (empirical, not a certified continuous-interval bound); 60 bisections contribute at most $1.5396755\times10^{-17}$ in log-parameter units. Only the per-window carrier-aware inverse is the theorem estimator; the mean-Poisson inverse is a proxy.

**Remark D.4.2 (the $\beta\le1$ theorem and the precise obstruction above one).** For $\beta\in(0,1]$, the pointwise modulus $|\ell_k-\ell_n|\le L_a|k-n|^\beta$ and the mean value theorem give
$$|q_k(\ell_k)-q_k(\ell_n)|\le\overline\kappa_kL_a|k-n|^\beta,$$
so the triangle-inequality bias bound used in Theorem C is valid for arbitrary known carriers.

For $\beta\in(1,2]$, standard smoothness has the local form
$$\ell_k-\ell_n=v_nu_k+r_{nk},\qquad u_k=(k-n)/N,\qquad |r_{nk}|\le L|u_k|^\beta,$$
rather than a pointwise modulus of order $\beta$ on the function itself. Let $w_k\ge0$ be the window weights and write $q_k(t)=m_\alpha(\Lambda_0e^tb_k+d)$. Taylor's theorem gives
$$|B_n|\le|v_n|\left|\sum_kw_kq_k'(\ell_n)u_k\right|+Q_1L\sum_kw_k|u_k|^\beta+Q_2\left\{v_n^2\sum_kw_ku_k^2+L^2\sum_kw_k|u_k|^{2\beta}\right\}, \tag{D.14}$$
where $Q_1=\sup_{k,t\in\Theta}q_k'(t)$ and $Q_2=\sup_{k,t\in\Theta}|q_k''(t)|$.

The first term in (D.14) is the load-bearing obstruction: an $O(h_n^\beta)$ deterministic bias requires the *sensitivity-weighted first-moment balance*
$$|v_n|\left|\sum_kw_kq_k'(\ell_n)u_k\right|\lesssim\underline\kappa_n(W/N)^\beta.$$
An *internal symmetric equal-weight window with a homogeneous carrier* satisfies it exactly ($q_k'$ constant and $\sum_kw_ku_k=0$ — the interior identity). A heterogeneous carrier generally does not: ordinary centering cancels $\sum_kw_ku_k$ but not the carrier-weighted moment, which is then $O(W/N)$, so an $O((W/N)^\beta)$ claim is false for $\beta>1$ under the present assumptions. Crucially, a **truncated one-sided edge window fails the balance even with a homogeneous carrier**: for the implementation's first truncated window $k=0,\dots,32$ with target $n=0$,
$$\frac1{33}\sum_{k=0}^{32}\frac kN=\frac{16}{N},$$
first order in the window radius, so the current local-constant estimator cannot support an all-frame uniform $\beta>1$ rate — the $\beta>1$ statement is restricted to *internal balanced windows*.

Under the balance condition the remaining nonlinear term is $O((W/N)^2)$ and is therefore no larger than $O((W/N)^\beta)$ for $1<\beta\le2$, provided the local slope is bounded. Thus the calibrated inverse recovers the $\beta$-order deterministic bias on internal windows under homogeneous or sensitivity-balanced carriers, with a constant depending also on the slope bound and on $Q_2$.

A second-order Taylor expansion of $M_n^{-1}$ by itself does not remove an unbalanced first moment. For arbitrary carriers, or for edge frames, recovery of the $\beta>1$ rate requires carrier-adapted moment conditions, carrier-adapted local-linear weights, or a separately proved local-polynomial edge estimator (for $\beta>2$, moments through order $\lfloor\beta\rfloor$ must be cancelled). Theorem C therefore remains restricted to $\beta\le1$, while the internal-window homogeneous-carrier and sensitivity-balanced extensions above are valid weaker statements.

**Remark D.4.3 (unknown random carrier; nonstationary finite-$W$ covariance bound).** Let $\{B_k\}$ be an unobserved stationary random carrier with known law, independent of the parameter, and let
$$\bar m_{\alpha,k}(t)=\mathbb E_B\,m_\alpha(\Lambda_0e^tB_k+d).$$
Because the gain path $\ell_k$ may vary, stationarity of $\{B_k\}$ does not in general make the soft-log sequence stationary. Define
$$z_k=\psi_\alpha(C_k)-\mathbb E\psi_\alpha(C_k),\qquad g_k(b)=m_\alpha(\Lambda_0e^{\ell_k}b+d).$$
Conditional independence of the Poisson randomization gives, for $i\ne j$,
$$\operatorname{Cov}(z_i,z_j)=\operatorname{Cov}(g_i(B_i),g_j(B_j)).$$
Consequently the exact finite-window identity is
$$\operatorname{Var}\!\left(W^{-1}\sum_{i=1}^Wz_i\right)=W^{-2}\sum_{i=1}^W\operatorname{Var}(z_i)+2W^{-2}\sum_{h=1}^{W-1}\sum_{i=1}^{W-h}\operatorname{Cov}(z_i,z_{i+h}). \tag{D.15}$$
Let $p=2+\eta$, $r_\eta=\eta/(2+\eta)$, and assume
$$v_*:=\sup_i\operatorname{Var}(z_i)<\infty,\qquad G_p:=\sup_i\|g_i(B_i)-\mathbb Eg_i(B_i)\|_p<\infty.$$
If the carrier is strongly mixing with coefficient $\alpha_B(h)$, Davydov's inequality [32] gives
$$|\operatorname{Cov}(z_i,z_{i+h})|\le8\,\alpha_B(h)^{r_\eta}G_p^2.$$
Substitution into (D.15) yields the explicit finite-$W$ bound
$$\operatorname{Var}\!\left(W^{-1}\sum_{i=1}^Wz_i\right)\le\frac1W\left[v_*+16G_p^2\sum_{h=1}^{W-1}\left(1-\frac hW\right)\alpha_B(h)^{r_\eta}\right]\le\frac{v_*+16G_p^2\sum_{h\ge1}\alpha_B(h)^{r_\eta}}{W}.$$
The factor $16$ is the constant obtained from Davydov's constant $8$ and the two covariance triangles. It is sharper to apply Davydov to the conditional means $g_i(B_i)$ than to $z_i$ itself, because independent Poisson shot noise contributes only to the diagonal variance $v_*$.

If $\ell_k$ is constant and the resulting marked process is strictly stationary, write $\gamma_\psi(h)=\operatorname{Cov}(z_0,z_h)$. Then
$$\operatorname{Var}\!\left(W^{-1}\sum_{k=1}^Wz_k\right)=W^{-1}\sum_{|h|<W}\left(1-\frac{|h|}{W}\right)\gamma_\psi(h)\le\frac{\sum_h|\gamma_\psi(h)|}{W},$$
and when $\sum_h|\gamma_\psi(h)|<\infty$,
$$\operatorname{Var}\!\left(W^{-1}\sum_{k=1}^Wz_k\right)=\frac{\sigma_{\psi,\mathrm{LR}}^2}{W}+o(W^{-1}),\qquad \sigma_{\psi,\mathrm{LR}}^2=\sum_h\gamma_\psi(h).$$
The multiplicative notation $\sigma_{\psi,\mathrm{LR}}^2W^{-1}\{1+o(1)\}$ is valid only when $\sigma_{\psi,\mathrm{LR}}^2>0$. For $z_n=\epsilon_n-\epsilon_{n-1}$ the signed long-run variance is zero while the finite-window variance is $2\sigma_\epsilon^2/W^2$.

**Remark D.4.4 (clamp probability: a diagnostic, not an extra risk term).** By the global Lipschitz property of the clamped inverse, (D.8) already covers clamped, all-zero, and out-of-range windows; no term $D_\Theta^2\,\mathbb P(\mathcal E_n^c)$ is added to the risk. The clamp probability remains useful as a *diagnostic* for whether the localized variance regime of the low-photon expansion applies (low total information drives clamp saturation, in which case the inverse-information reading of (D.10) is off scope). With $\mathcal E_n=\{y_n\in M_n(\Theta)\}$, use the notation $B_n,V_n,\underline\kappa_n$ of the finite-window proof and put
$$r_n=\min\{M_n(\ell_n)-M_n(\theta_{\min}),M_n(\theta_{\max})-M_n(\ell_n)\}.$$
If $\ell_n$ has margin $\Delta_n$ from $\partial\Theta$, then $r_n\ge\underline\kappa_n\Delta_n$. Since $y_n-M_n(\ell_n)=B_n+Z_n$, with $\mathbb EZ_n=0$ and $\operatorname{Var}(Z_n)=V_n$,
$$\mathcal E_n^c\subseteq\{|B_n+Z_n|\ge r_n\}.$$
Therefore
$$\mathbb P(\mathcal E_n^c)\le\min\left\{1,\frac{B_n^2+V_n}{r_n^2}\right\}\le\min\left\{1,\frac{B_n^2+V_n}{(\underline\kappa_n\Delta_n)^2}\right\}.$$
If $|B_n|<r_n$, the sharper centered bound is
$$\mathbb P(\mathcal E_n^c)\le\min\left\{1,\frac{V_n}{(r_n-|B_n|)^2}\right\}.$$
An exponential Bernstein bound requires a positive residual margin $r_n-|B_n|$; it is not available merely from a positive parameter margin when the deterministic smoothing bias can reach the boundary.

On $\mathcal E_n^c$, both the clamped estimate and the target lie in $\Theta$, so the clamp-event slice of the MSE is trivially at most $D_\Theta^2\,\mathbb P(\mathcal E_n^c)$ — but this bound is *never added* to (D.8), which already dominates it through the global Lipschitz argument; it is recorded only to size the diagnostic.

For a window containing $W$ distinct, conditionally independent Poisson counts,
$$\mathbb P(C_k=0\ \text{for all }k\in W_n)=\exp\!\left(-\sum_{k\in W_n}\lambda_k(\ell_k)\right)\le e^{-W\lambda_-}.$$
If a padding convention repeats observations, the sum and the cardinality in this formula are over distinct frames after repeated weights have been aggregated; in that case the exponent need not be $W\lambda_-$ (the first width-65 replicate-padded window of the former convention had only 33 distinct frames, so its all-zero probability was $e^{-33\lambda}$, not $e^{-65\lambda}$ — at $\lambda=0.25$, $2.6\times10^{-4}$ versus $8.8\times10^{-8}$).

**Remark D.4.5 (scope: oracle carriers, known carrier law, and blind recovery — three distinct estimators).** Theorem C is conditional on the realized per-frame carriers $(b_k)$ being *known*: this is precisely the oracle-known-carrier arm implemented in the low-photon experiment (Fig. 5), and it does **not** establish blind low-photon recovery from an unknown carrier law. Theorem B, by contrast, is the *blind high-count* stationary-carrier result; the two must not be merged. If an unobserved carrier $B$ has a fully *known law* $F_B$, one may instead calibrate the different marginal curve
$$\bar q_{F_B}(t)=\mathbb E_{B\sim F_B}\,m_\alpha(\Lambda_0e^tB+d),$$
a *third*, law-calibrated estimator that needs its own variance or long-run-variance theorem (Remark D.4.3 supplies the covariance tool); it is not the per-frame known-carrier estimator above. If $F_B$ is *unknown*, $\bar q_{F_B}$ is an unknown nonlinear function which, unlike the high-count logarithmic model, cannot generally be absorbed into one additive gauge constant: with $s=\Lambda_0e^t$,
$$m_\alpha(sB)=\log\alpha+c_\alpha sB+a_{2,\alpha}s^2B^2+O(s^3B^3),\qquad a_{2,\alpha}=\tfrac12\log\frac{\alpha(\alpha+2)}{(\alpha+1)^2}\ne0,$$
so the laws $B\equiv1$ and $\Pr(B=\tfrac12)=\Pr(B=\tfrac32)=\tfrac12$ — same mean, different second moments — produce *different* soft-log response curves. The known-carrier theorem plus one homogeneous calibration inverse therefore does not yield an unknown-law blind theorem (though this does not rule out every joint semiparametric method).

**Centered-log quotient risk.** Let $e=\hat\ell-\ell$ and $P_N=I-N^{-1}\mathbf1\mathbf1^\top$. Since $P_N$ is an orthogonal projection,
$$\frac1N\,\mathbb E\|P_Ne\|_2^2\le\frac1N\sum_{n=1}^N\mathbb Ee_n^2,$$
so the pointwise bounds transfer directly to the record-centered log-gain loss of Fig. 5; overlapping windows need not be independent for this expectation bound.

**Shrinkage-bias caveat (load-bearing, per Sec. 6).** For $\bar\lambda<1$ the windowed soft-log statistic is *bias-fragile*: the mass at $C=0$ pulls the weighted mean of $\psi_\alpha$ toward $\log\alpha$, and the amplification factor $(\kappa_{\max}/\underline\kappa_n)^2$ in the specialized bias term of (D.8) blows up as the window sensitivity vanishes with $\bar\lambda_n\to0$ (at $d=0$; window-average form $M_n'(\ell_n)\approx c_\alpha\bar\lambda_n$). Empirically the MSE of the *uncalibrated* proxy (and of Anscombe) can then sit *below* the pointwise Fisher reference curve — that is bias, not super-efficiency. It does not contradict (D.11)–(D.12), whose minimax bounds apply to all estimators over a local parameter neighborhood: a biased estimator may beat $1/I_n$ at selected parameters only by paying risk elsewhere. The $1/(W\bar\lambda)$ law is asserted only in the variance-limited regime above the $\bar\lambda\sim1$ crossover (and under the local gain flatness of (D.10)); below it, honest accounting reports the bias floor, and all Fisher comparisons are made in the log-domain loss of this theorem (Fig. 5's `log_gain_mse` metric, against the *oracle common-shift diagnostic* $\mathrm{mean}_n[1/I_n]$ with $I_n=\sum_{k\in W_n}\lambda_k$ at $d=0$, per (D.13) — *not* a nuisance-path quotient CRB) — the gain-domain relMSE column retained for continuity is a different loss and is not Fisher-comparable. Recovering the rate below the crossover requires the offset-design, Anscombe [28] ($2\sqrt{C+3/8}$), or full Poisson-mixture MLE variants; for the mixture MLE the claim $\mathrm{MSE}\approx1/(WJ(\theta))$ with $J\sim\mathbb{E}\lambda$ at low photons is standard parametric asymptotics under regularity of the mixture likelihood and is *not* re-proven here.

**What this does not claim.** The oracle experiment can identify absolute log gain because $\Lambda_0$ and the carriers are fixed and known; the implementation and reported loss deliberately center the record to align with the blind task, so no separate absolute-scale performance claim is reported. In the Fig. 5 protocol the carriers are *oracle* values from the simulation truth (a flat-field-calibrated benchmark), so Fig. 5 upper-bounds what a real flat-field calibration could achieve rather than demonstrating blind carrier recovery — Theorem C is an oracle-known-carrier result, Theorem B is the blind high-count result, and the known-law estimator of Remark D.4.5 is a third object; none substitutes for the others. Miscalibration beyond the measured interpolation term ($\varepsilon_{\mathrm{cal}}/\underline\kappa_n+\varepsilon_{\mathrm{bis}}$ of (D.8b), with $\varepsilon_{\mathrm{cal}}$ an empirical midpoint maximum pending the (D.8c) certificate) adds a bias not covered by (D.8). Constants in (D.8)–(D.9) are not tracked. Smoothness beyond $\beta=1$ is claimed only in the internal-window homogeneous-carrier / sensitivity-balanced form of Remark D.4.2 (display (D.14)); for arbitrary carriers the carrier-weighted first moment obstructs every $\beta>1$ rate, and the implementation's truncated edge windows are not covered even under a homogeneous carrier. The unconditional $1/(W\bar\lambda)$ law is withdrawn in favor of (D.10); the flat-gain specialization is the only $1/(W\bar\lambda)$ statement retained. The minimax matching of (D.9) is at rate level only, *in the centered log-domain loss and at $d=0$*, proved by the direct Poisson Le Cam/Assouad bounds (D.11)–(D.12) — not inherited from Theorem D, whose Gaussian model is not a submodel of the mixed-Poisson experiment; for $d>0$ every information statement must replace $W\bar\lambda$ by $\sum_k\mathbb{E}_B\,s_k^2/(s_k+d)$. The plotted reference $\mathrm{mean}_n[1/I_n]$ is the oracle common-shift diagnostic of (D.13): MSE above it does not establish unbiasedness, and MSE below it signals shrinkage bias, not super-efficiency. No optimality of any kind is claimed in the gain-domain (linear) metric, and no claim is made that the calibrated estimator beats bias-accepting transforms (e.g. Anscombe) in MSE below the $\bar\lambda\sim1$ crossover — empirically it does not (Sec. 9). As $\Phi\to0$ with no offset and no reference, Fisher information for the gain vanishes — an information limit no estimator evades (Sec. 10).

## Appendix E — SRHT whitening: exact Walsh condition and permutation bounds

This appendix proves the claims of Sec. 7: the exact covariance identity $\operatorname{Cov}_D(Z_g,Z_h)=\hat w(g+h)$, the necessary-and-sufficient Walsh-flatness conditions for sign-only whitening (pairwise, spectral-window, and window-average forms), the Bernstein–Serfling permutation bound and its union-bound corollary, the permutation-alone carrier-variance identity with its flat-object counterexample, and the Hanson–Wright window-energy bound.
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
a centered, doubled sum of $n=K/2$ draws *without replacement* from the finite population $\{w_1,\dots,w_K\}$ with mean $\mu_w=S_2/K$. Writing $S_q=\sum_{j\in A_q}w_j^P$, $\operatorname{Var}(S_q)=K^2\sigma_w^2/[4(K-1)]$ and $\operatorname{Var}(2S_q-S_2)=K^2\sigma_w^2/(K-1)\le2\sum_jw_j^2$ for $K\ge2$, where $\sigma_w^2=K^{-1}\sum_j(w_j-\mu_w)^2$. Also $0\le w_j\le\|T\|_\infty^2=S_2/K_\infty$, so the variance proxy is at most a universal constant times $\sum_jw_j^2=S_2^2/K_4$. The Bernstein inequality for sampling without replacement (Serfling [31]; the Bernstein–Serfling form of Bardenet–Maillard [43]) then gives, for $t>0$,
$$\Pr\big(|\widehat{w^P}(q)|\ge t\big)\le2\exp\!\Big[-c\min\Big(\frac{t^2}{S_2^2/K_4},\ \frac{t}{S_2/K_\infty}\Big)\Big].$$
Setting $t=\varepsilon S_2$ yields (E.2); (E.3) is the union bound; (E.4) follows by requiring the right side of (E.3) to be at most $\delta$ and absorbing the factor $2(K-1)$ into $C\log(K/\delta)$. $\blacksquare$

**What this does not claim.** (E.2)–(E.4) are *sufficient* high-probability conditions with unspecified universal constants; they are not the deterministic criterion for a realized acquisition — that remains Walsh-flatness of $w^P$ (Theorem E.2), which can and should be checked numerically for the ordering actually used. For spectral whitening of all windows up to size $W_{\max}$, the simple route substitutes $\varepsilon\to\varepsilon/(W_{\max}-1)$ in (E.4) via Gershgorin; sharper window-size dependence via matrix-Bernstein or Hanson–Wright arguments (Sec. E.5) is a concentration refinement, again sufficient rather than necessary. Both branches of the min collapse when energy concentrates on few pixels ($K_4,K_\infty$ small): permutation cannot flatten a spike.

### E.4 Permutation alone: exact carrier variance and the flat-object counterexample

> **Theorem E.4 (permutation-alone variance).** Under (E1)–(E2), with no signs and a uniformly random permutation $P$, the carrier $Z_g(P)=\sum_j\chi_g(j)T_{Pj}$ of any non-DC row $g\neq0$ satisfies $\mathbb{E}_PZ_g=0$ and
> $$\operatorname{Var}_PZ_g\;=\;\frac{KS_2-S_1^2}{K-1}\;=\;S_2\,\frac{K-K_{\mathrm{eff}}}{K-1}. \tag{E.5}$$
> If additionally $S_1\ne0$ and $K_{\mathrm{eff}}\ge1$ — in particular, for a nonnegative physical object — then for offset patterns $B_g=\mu S_1+\sigma Z_g(P)$ with positivity margin,
> $$\frac{\operatorname{Var}_PB_g}{(\mathbb{E}_PB_g)^2}=\Big(\frac{\sigma}{\mu}\Big)^2\frac{K-K_{\mathrm{eff}}}{(K-1)\,K_{\mathrm{eff}}}\;\le\;\Big(\frac{\sigma}{\mu}\Big)^2\frac{1}{K_{\mathrm{eff}}}. \tag{E.6}$$
> No matching lower bound of order $1/K_{\mathrm{eff}}$ holds uniformly over objects: for flat $T$ ($T_j$ constant), $K_{\mathrm{eff}}=K$ while $Z_g(P)=0$ for **every** permutation and every $g\neq0$.

**Proof.** For $g\neq0$, $\sum_i\chi_g(i)=0$, so $\mathbb{E}_PZ_g=\big(\sum_i\chi_g(i)\big)\mathbb{E}_PT_{P1}=0$. Exchangeability of $(T_{P1},\dots,T_{PK})$ gives $\mathbb{E}_PT_{Pi}^2=S_2/K$ and, for $i\neq j$, $\mathbb{E}_PT_{Pi}T_{Pj}=(S_1^2-S_2)/(K(K-1))$. Hence
$$\mathbb{E}_PZ_g^2=S_2+\frac{S_1^2-S_2}{K(K-1)}\sum_{i\neq j}\chi_g(i)\chi_g(j),$$
and $\sum_{i\neq j}\chi_g(i)\chi_g(j)=\big(\sum_i\chi_g(i)\big)^2-K=-K$, giving (E.5); the second form follows from $K_{\mathrm{eff}}=S_1^2/S_2$. For (E.6), $\mathbb{E}_PB_g=\mu S_1$ and $\operatorname{Var}_PB_g=\sigma^2\operatorname{Var}_PZ_g$; divide. The counterexample: if $T_j\equiv t$, every non-DC Walsh sum of a constant vector vanishes identically, while $S_1^2/S_2=K$. Note (E.5) also exhibits the finite-population correction — the relative variance is $(\sigma/\mu)^2(1/K_{\mathrm{eff}}-1/K)\cdot K/(K-1)$. $\blacksquare$

**What this does not claim.** In the $K_{\mathrm{eff}}\ge1$ physical-object regime, a shared pixel permutation gives common non-DC one-dimensional mean/variance and an $O(1/K_{\mathrm{eff}})$ upper scale, but neither temporal stationarity/mixing nor joint row exchangeability. Full finite-population exchangeability belongs to random acquisition order $P_{\mathrm{row}}$ (with adjacent pairs as blocks). Once any randomization is conditioned upon, the realized sequence is deterministic; concentration is with respect to the declared ensemble.

> **Proposition E.4′ (Walsh triple-moment counterexample to joint row exchangeability).** Let $K=2^m\ge8$, let $\chi_g$ be the Walsh characters, and $Z_g(P)=\sum_{j}\chi_g(j)T_{Pj}$ under one uniform pixel permutation $P$ shared by all rows. Let $\bar T=K^{-1}\sum_jT_j$ and $S_{3,c}=\sum_j(T_j-\bar T)^3$. For distinct nonzero rows $g,h,r$,
> $$\mathbb E_P[Z_gZ_hZ_r]=\begin{cases}\dfrac{K^2}{(K-1)(K-2)}\,S_{3,c},&g+h+r=0,\\[4pt]0,&g,h,r\ \text{linearly independent}.\end{cases} \tag{E.9}$$
> For a generic object with $S_{3,c}\neq0$, relational triples ($g+h+r=0$) and independent triples therefore have different joint laws, disproving full row exchangeability under a common pixel permutation.

**Proof.** Replace $T_j$ by $x_j=T_j-\bar T$ (non-DC Walsh coefficients unchanged). For the without-replacement sample $X_i=x_{P(i)}$, standard finite-population moments give $\mathbb EX_i^3=S_{3,c}/K$, $\mathbb EX_i^2X_j=-S_{3,c}/\{K(K-1)\}$ for $i\ne j$, and $\mathbb EX_iX_jX_k=2S_{3,c}/\{K(K-1)(K-2)\}$ for distinct $i,j,k$. If $g+h+r=0$, character orthogonality gives sign sums $K$ over the diagonal class, $-K$ over each exactly-two-equal pairing, and $2K$ over the all-distinct class; substitution gives the first line of (E.9). If $g+h+r\neq0$, all the corresponding character sums vanish. $\blacksquare$

### E.5 Hanson–Wright window-energy bound

Whitening of window *energy* — the quantity the window estimator of Sec. 6 actually averages — admits a direct quadratic-form bound. For a window $A$ of $W$ rows let $P_A$ select those rows and set
$$Q_A=\|P_A\,U D P T\|_2^2=\eta^\top M\eta,\qquad M=\mathrm{diag}(PT)\,U_A^\top U_A\,\mathrm{diag}(PT),$$
with $\eta$ the Rademacher sign vector and $U_A$ the selected rows of $U$.

> **Proposition E.5 (window-energy concentration).** Condition on any realized $P$. Then $\mathbb{E}_DQ_A=(W/K)S_2$, and there is a universal $c>0$ with
> $$\Pr_D\!\Big(\big|Q_A-\tfrac{W}{K}S_2\big|\ge\varepsilon\,\tfrac{W}{K}S_2\Big)\;\le\;2\exp\!\Big[-c\min\Big(\varepsilon^2\,\tfrac{WK_\infty}{K},\ \varepsilon\,\tfrac{WK_\infty}{K}\Big)\Big]. \tag{E.7}$$
> Over a specified family of $M$ windows, uniform relative energy whitening at tolerance $\varepsilon\le1$ holds with probability $\ge1-\delta$ once
> $$\frac{WK_\infty}{K}\;\ge\;C\varepsilon^{-2}\log(M/\delta). \tag{E.8}$$

**Proof.** Since $U$ has orthonormal rows, $U_AU_A^\top=I_W$, so $U_A^\top U_A$ is an orthogonal projector and $(U_A^\top U_A)_{jj}=\sum_{g\in A}U_{gj}^2=W/K$ (Hadamard entries are $\pm K^{-1/2}$). Hence $M\succeq0$, and $\mathbb{E}_DQ_A=\operatorname{tr}M=\sum_j(PT)_j^2\,(W/K)=(W/K)S_2$. Because $\eta_j^2=1$, the diagonal of $M$ contributes deterministically and $Q_A-\mathbb{E}Q_A$ is a pure off-diagonal Rademacher chaos, to which the Hanson–Wright inequality applies (Hanson–Wright [44]; sub-Gaussian form of Rudelson–Vershynin [45]):
$$\Pr(|Q_A-\operatorname{tr}M|\ge t)\le2\exp\Big[-c\min\Big(\frac{t^2}{\|M\|_F^2},\ \frac{t}{\|M\|_{\mathrm{op}}}\Big)\Big].$$
The proxies: $\|M\|_{\mathrm{op}}\le\|\mathrm{diag}(PT)\|_{\mathrm{op}}^2\,\|U_A^\top U_A\|_{\mathrm{op}}\le\|T\|_\infty^2=S_2/K_\infty$, and for PSD $M$, $\|M\|_F^2\le\|M\|_{\mathrm{op}}\operatorname{tr}M\le(W/K)S_2\|T\|_\infty^2$. Substituting $t=\varepsilon(W/K)S_2$ gives $t^2/\|M\|_F^2\ge\varepsilon^2WK_\infty/K$ and $t/\|M\|_{\mathrm{op}}\ge\varepsilon WK_\infty/K$, i.e. (E.7); for $\varepsilon\le1$ the quadratic branch is active. A union bound over $M$ windows gives (E.8). $\blacksquare$

For dense objects of bounded dynamic range, $K_\infty\asymp K_4\asymp K_{\mathrm{eff}}\asymp K$ and (E.8) reduces to the mild $W\gtrsim\varepsilon^{-2}\log M$ — the window only needs logarithmic length. For an object supported on $m$ comparable pixels, $K_\infty\asymp m$ and the condition hardens to $Wm/K\gtrsim\varepsilon^{-2}\log M$: this is precisely where $K_{\mathrm{eff}}$ alone is the wrong functional and the three spread parameters separate (Sec. 6).

**What this does not claim.** Proposition E.5 controls window *energy* over the sign draw for a pre-specified finite window family; it is a sufficient concentration tool, not the deterministic necessary-and-sufficient condition (which remains the spectral condition of Theorem E.2(3) applied to $w^P$), and it does not cover all $\binom{K}{W}$ windows simultaneously without paying for the larger union. The constants $c,C$ are universal but not optimized, and no claim is made that (E.8) is tight in its $W$- or $K_\infty$-dependence — Hanson–Wright and matrix-Bernstein refinements can improve window-family dependence for structured $\mathcal{A}$, but they do not change the deterministic criterion. Finally, all of Appendix E concerns the carrier statistics of the *design*; the translation of whitening into gain-estimation rates ($1/W$ per window) and into image error (leverage $B_L=1$ for full SRHT inversion) is carried out in Appendix D and Appendix F respectively.

### E.6 Two randomization semantics: pixel randomization ($P_{\mathrm{col}}$, $D$) vs. acquisition-order randomization ($P_{\mathrm{row}}$)

**This subsection separates two operations that earlier drafts conflated under the single word "permutation".** Write $P_{\mathrm{col}}$ for a uniformly random **pixel (column) permutation** of the object — the $P$ of assumption (E3) — write $D$ for the i.i.d. Rademacher **pixel sign** diagonal of (E3), and write $P_{\mathrm{row}}$ for a uniformly random reordering of the **acquisition (Hadamard row / time) order**. These control different claims:

- **Appendix E's theorems govern cross-row covariance.** By Lemma E.1, the sign-draw covariance $\operatorname{Cov}_D(Z_g,Z_h)=\widehat{w^P}(g+h)$ is a function of the permuted squared object $w^P$ alone; it is therefore **invariant to the acquisition order** — $P_{\mathrm{row}}$ does not enter Lemma E.1 or Theorems E.2–E.3 at all. The whitening randomization of the theory is $x=UDP_{\mathrm{col}}T$: pixel signs plus pixel permutation, in *natural* acquisition order.
- **The manuscript's temporal-stationarity screen is controlled by acquisition-order structure.** The Brown–Forsythe/Levene screen [29], [30] of Sec. 7 probes temporal homogeneity of the acquired time series; it responds to whatever breaks the coarse-to-fine sequency-energy ordering of natural Hadamard rows — which either $P_{\mathrm{col}}$ **or** $P_{\mathrm{row}}$ accomplishes.

**Factorized ablation (empirical attribution; `results/perm_ablation_r1/`).** All arms share the same ordered natural-Hadamard baseline ($K=4096$, $64\times64$, 8192 paired frames, noiseless carrier), the same 10-object panel, and the same Levene protocol (8 chunks, reject at $p<10^{-3}$); 32 draws per randomized arm. Levene rejection rates:

| arm | $P_{\mathrm{col}}$ | $D$ | $P_{\mathrm{row}}$ | rejection rate |
|---|:--:|:--:|:--:|:--:|
| ordered (baseline) | – | – | – | **0.700** |
| $P_{\mathrm{col}}$ only (theory's $P$) | Y | – | – | **0.056** |
| $P_{\mathrm{row}}$ only | – | – | Y | **0.122** |
| $D$ only | – | Y | – | **0.434** |
| $P_{\mathrm{col}}+D$ (theory's randomization) | Y | Y | – | **0.119** |
| $P_{\mathrm{row}}+D$ (code's `srht_paired`) | – | Y | Y | **0.059** |
| $P_{\mathrm{col}}+P_{\mathrm{row}}$ (old Experiment-B arm) | Y | – | Y | **0.059** |

The $P_{\mathrm{col}}+P_{\mathrm{row}}$ arm reproduces the historical headline (19/320 = 5.9%) exactly, confirming the seed-compatible reconstruction of the old experiment; that historical 5.9% is attributable to *either* permutation alone ($P_{\mathrm{col}}$: 5.6%; $P_{\mathrm{row}}$: 12.2%).

**Code caveat (stated plainly).** The implemented basis `make_srht_paired_basis` (`src/basis.py`, `permute_rows=True`) applies pixel signs $D$ but permutes **Hadamard rows** (acquisition order), i.e. it implements $P_{\mathrm{row}}+D$ — **not** the theorem's $P_{\mathrm{col}}+D$. Both combinations are empirically sufficient for the temporal-stationarity screen (5.9% and 11.9%, versus 70% ordered), while **$D$ alone is not** (43.4%): sign flips whiten carrier *amplitudes* (chunk-std CV collapses from 0.76 to 0.03) but leave the temporal sequency ordering intact, so the chunk-variance test still rejects. Text and captions must therefore attach each claim to its own arm: the covariance-whitening claims of E.1–E.3 attach to $P_{\mathrm{col}}$ (+$D$); the temporal-screen results attach to the arm actually acquired ($P_{\mathrm{row}}+D$ for the code's SRHT).

**What this does not claim.** The table is an empirical attribution on one object panel and one protocol, not a theorem; no claim is made that $P_{\mathrm{row}}$ enjoys the concentration guarantees (E.2)–(E.4), which are proved for $P_{\mathrm{col}}$. The small increase from adding $D$ on top of $P_{\mathrm{col}}$ (5.6% → 11.9%) is a property of the variance-homogeneity test on near-white sequences, not a whitening failure. Nothing here alters the theorems of E.1–E.5; it fixes which experimental arm may cite them.

## Appendix F — The master finite-noise identity and the flip boundary

This appendix proves Theorem 1 (the master finite-noise relMSE identity) and Prop 3 (the finite-$N$ flip boundary) of Sec. 8, together with the noise plug-ins and the three basis specializations quoted there. Throughout, $T\in\mathbb{R}^K$ is the object, with $S_1$, $S_2$, $K_{\mathrm{eff}}$ as in Appendix C; $A\in\mathbb{R}^{N\times K}$ is the design, $b=AT$ the ideal bucket vector; the raw bucket is $R_n=a_nB_n$ with gain $a_n=e^{\ell_n}$, $\ell\in S$ (the drift class of Sec. 4, $p=\dim S$). After the pipeline applies a gain estimate $\hat a_n=e^{\hat\ell_n}$, the corrected bucket is

$$z_n \;=\; R_n/\hat a_n \;=\; (1+\delta_n)\,b_n+\xi_n,\qquad \delta_n=\frac{a_n}{\hat a_n}-1=e^{\ell_n-\hat\ell_n}-1, \tag{F.1}$$

where $\delta_n$ is the *residual* multiplicative gain error and $\xi_n$ is additive bucket-domain noise after correction, with $\mathbb{E}\,\delta=m_\delta$, $\mathrm{Cov}(\delta)=V_\delta$, $\mathbb{E}\,\xi=0$, $\mathrm{Cov}(\xi)=\Sigma_\xi$, and $\delta\perp\xi$ (uncorrelated, $C_{\delta\xi}=\operatorname{Cov}(\delta,\xi)=0$ — a hypothesis, revisited in the cross-term note below). The reconstruction is $\hat T=Lz$ for any fixed linear operator $L\in\mathbb{R}^{K\times N}$ (exact inverse, pseudoinverse, DGI correlator, or a regularized estimator linearized around a fixed design).

### F.1 The master identity

**Theorem 1 (exact second-moment bridge).** *Assume model (F.1) with $A,T,L$ fixed (all expectations conditional on them), and assume — as part of the hypothesis, not as background convention — that:*

*(H1) $\mathbb{E}\,\xi=0$;*

*(H2) $\delta$ and $\xi$ are uncorrelated, $C_{\delta\xi}:=\operatorname{Cov}(\delta,\xi)=0$;*

*(H3) the gain estimate $\hat a$ is **exogenous** with respect to the reconstruction record — computed independently of the noise realization $\xi$ (injected/synthetic residuals, an independent calibration record, or a cross-fitted estimate from held-out frames) — so that (H1)–(H2) hold conditionally on the record being reconstructed;*

*(H4) the second moments $m_\delta,V_\delta,\Sigma_\xi$ are finite.*

*Then, exactly and with no Gaussian or small-noise approximation,*

$$\frac{\mathbb{E}\|\hat T-T\|_2^2}{S_2} =\underbrace{\frac{\|(LA-I)T+L\,\mathrm{diag}(b)\,m_\delta\|_2^2}{S_2}}_{\text{bias}} +\underbrace{\frac{\mathrm{tr}\!\big(L\,\mathrm{diag}(b)\,V_\delta\,\mathrm{diag}(b)\,L^\top\big)}{S_2}}_{\text{residual gain}} +\underbrace{\frac{\mathrm{tr}\!\big(L\,\Sigma_\xi L^\top\big)}{S_2}}_{\text{additive noise}}. \tag{F.2}$$

*(a) If moreover $\mathbb{E}\,\delta_n=0$ and the $\delta_n$ are uncorrelated with common variance $v$, the residual-gain term equals $v\,B_L(A,T)$ with the* **leverage**

$$B_L(A,T)=\frac{1}{S_2}\sum_{n=1}^N b_n^2\,\|Le_n\|_2^2. \tag{F.3}$$

*(b) If instead the residual gains are stationary with $\mathrm{Cov}(\delta_n,\delta_m)=v\,r_\delta(n-m)$, the residual-gain term equals*

$$R_{\mathrm{gain}}=\frac{v}{S_2}\sum_{n,m} r_\delta(n-m)\,b_n b_m\,\langle Le_n,Le_m\rangle. \tag{F.4}$$

**Proof.** Write $z=b+\mathrm{diag}(b)\,\delta+\xi$, so $\hat T-T=(LA-I)T+L\,\mathrm{diag}(b)\,\delta+L\xi$. Decompose $\delta=m_\delta+(\delta-m_\delta)$. The mean of $\hat T-T$ is $(LA-I)T+L\,\mathrm{diag}(b)\,m_\delta$ (using (H1)); its squared norm is the bias term. By the bias–variance decomposition $\mathbb{E}\|X\|^2=\|\mathbb{E}X\|^2+\mathrm{tr}\,\mathrm{Cov}(X)$ and (H2), the covariance of $\hat T$ is $L\,\mathrm{diag}(b)\,V_\delta\,\mathrm{diag}(b)\,L^\top+L\,\Sigma_\xi L^\top$; taking traces and dividing by $S_2$ gives (F.2). For (a), $V_\delta=vI$ and $\mathrm{tr}(L\,\mathrm{diag}(b)\,\mathrm{diag}(b)\,L^\top)=\sum_n b_n^2\|Le_n\|^2$, giving (F.3). Case (b) is the coordinate expansion of the same trace with $(V_\delta)_{nm}=v\,r_\delta(n-m)$. $\blacksquare$

**Remark F.1.1 (same-record gain estimates violate the hypotheses; scope of the exact identity).** Hypothesis (H3) is not decorative. When $\hat a$ is estimated from the *same* noisy record that carries $\xi$ — the generic situation for a blind pipeline — the conditional mean $\mathbb{E}[\xi\mid\text{record}]$ is generically nonzero and $\delta$ is correlated with $\xi$, so (H1)–(H2) fail: the mean of $\hat T-T$ acquires an additional bias term $L\,m_\xi$ (with $m_\xi=\mathbb{E}\,\xi\neq0$) inside the bias norm, and the covariance acquires the cross-term $(2/S_2)\,\operatorname{tr}\!\big[L\,\mathrm{diag}(b)\,C_{\delta\xi}\,L^\top\big]$. Neither term is included in (F.2). The exact identity therefore covers the **exogenous / injected-residual case** — which is precisely what the injected-residual protocol of Sec. 9 (experiment E4, Fig. 4) validates — and cross-fitted estimates that restore (H1)–(H2) by construction; for same-record blind pipelines, (F.2) is exact only up to the two extra terms above.

**What this does not claim.** With (H1)–(H3) now stated *in* the theorem, the caveat is Remark F.1.1: (F.2) is not claimed for same-record blind gain estimation, where the $L\,m_\xi$ bias and the $C_{\delta\xi}$ cross-term appear. Beyond that, (F.2) is a second-moment accounting identity for a *linear* reconstructor with the design held fixed; it does not bound nonlinear or data-adaptive $L$, and for random-pattern pipelines the constants below are obtained by additionally averaging over the pattern draw. It says nothing about how small $v$ can be made — that is the estimation-rate question of Sec. 6. Finally, the scalar collapse $v\,B_L$ *requires* uncorrelated residuals: for smooth (coherent) residual gain — the generic output of a windowed blind estimator — only the matrix form (F.4) is correct. In particular, the simple summary "orthogonal inversion gives $v$" holds only for independent coefficient-wise residuals under exact inversion.

### F.2 Noise plug-ins

**Proposition F.2 (read and physical nonnegative-Poisson noise, exact).** *(a) Gaussian read.* If detector-domain noise $\eta_n\sim\mathcal N(0,\sigma_{\mathrm{read},n}^2)$ is independent across frames and $\hat a_n$ is exogenous to it, then conditional on $(a,\hat a)$, $\xi_n=\eta_n/\hat a_n$ and $\operatorname{Var}(\xi_n\mid a,\hat a)=\sigma_{\mathrm{read},n}^2/\hat a_n^2$. *(b) Poisson.* If physical counts have $\Phi_n=\gamma_na_nb_n>0$ with $b_n\ge0$, $\gamma_n>0$, and $\hat a_n$ is exogenous to the count conditional on $(T,a)$, then

$$\mathbb{E}[z_n\mid T,a,\hat a]=\frac{a_n}{\hat a_n}b_n,\qquad \mathrm{Var}(z_n\mid T,a,\hat a)=\frac{b_n^2}{\Phi_n}\Big(\frac{a_n}{\hat a_n}\Big)^2. \tag{F.5}$$

**Proof.** (a) is scaling of a Gaussian. (b): a Poisson variable has mean $=$ variance $=\Phi_n$; dividing by $\gamma_n\hat a_n$ scales the mean by $(\gamma_n\hat a_n)^{-1}$ and the variance by $(\gamma_n\hat a_n)^{-2}$, and $\Phi_n/(\gamma_n\hat a_n)= (a_n/\hat a_n) b_n$, $\Phi_n/(\gamma_n\hat a_n)^2=(b_n^2/\Phi_n)(a_n/\hat a_n)^2$. $\blacksquare$

For fixed calibrated gains $\hat a_n=a_n$, $\Sigma_\xi=\mathrm{diag}(\tau_{G,n}^2+b_n^2/\Phi_n)$ plugs into (F.2), and the Poisson term is **exact at all photon counts**, including $\Phi_n\ll1$; no log or Gaussian approximation enters the reconstruction layer. If exogenous $\hat a$ is random, the unconditional diagonal uses the expectation of the displayed conditional variances; a same-record $\hat a$ falls under Remark F.1.1. Under a total budget $\Phi_n=\omega_n\Phi_{\mathrm{tot}}$, $R_{\mathrm{Pois}}=(S_2\Phi_{\mathrm{tot}})^{-1}\sum_n(b_n^2/\omega_n)\|Le_n\|^2$.

**What this does not claim.** The displayed plug-ins are exact conditionally on the gains and exogenous correction factors. A signed coefficient $b_n=(UT)_n$ is not a Poisson mean; signed transforms require complementary masks or a positive offset and their separately derived photon allocation and differencing covariance.

### F.3 Specializations

**F.3.1 Orthogonal / full-SRHT inversion ($B_L=1$).** If $A=U$ is orthonormal ($N=K$, signed coefficients available) and $L=U^\top$, then $B_L=1$. With independent residuals and signed-coefficient-domain additive covariance $\Sigma_c$,

$$\mathrm{relMSE}_{\mathrm{orth}}=v+\operatorname{tr}(\Sigma_c)/S_2. \tag{F.6}$$

No direct Poisson term is assigned to signed $UT$. A complementary-mask or positive-offset realization must first derive its physical covariance and then supply $\Sigma_c$. Full SRHT has the same algebraic propagation once that covariance is defined.

**F.3.2 Pairwise Hadamard: exact perturbation law.** Let $c_k=h_k^\top T$, $h_k\in\{\pm1\}^K$, with physical masks $B_k^\pm=(S_1\pm c_k)/2$ and reconstruction $T=K^{-1}H^\top c$, so coefficient errors $e_k$ give $\mathrm{relMSE}=(KS_2)^{-1}\sum_k\mathbb{E}e_k^2$. If the paired masks carry gains $a_k^+$ and $a_k^-=a_k^+(1+\Delta_k)$, the pairwise-normalized estimator satisfies the **exact** algebraic law

$$\hat c_k-c_k=-\,\frac{S_1\,\Delta_k\,(1-x_k^2)}{2+\Delta_k(1-x_k)},\qquad x_k=c_k/S_1, \tag{F.7}$$

for true-$S_1$ normalization. If $\widehat S_1=\gamma S_1$ and the denominator is not clamped,

$$e_k^{(\gamma)}=S_1\frac{2x_k(\gamma-1)-\Delta_k(1-x_k)(\gamma+x_k)}{2+\Delta_k(1-x_k)}=\gamma e_k^{(1)}+(\gamma-1)c_k. \tag{F.7a}$$

Hence the raw risk is exactly the sum of the $\gamma^2$ F.7 component, $(\gamma-1)^2$, and the normalization–increment cross term $2\gamma(\gamma-1)(KS_2)^{-1}\sum_ke_k^{(1)}c_k$ (F.7b). This identity passed the coefficient-wise regression gate before entering the manuscript.

whence, exactly (Parseval),

$$R_{\mathrm{pair,gain}}=\frac{K_{\mathrm{eff}}}{K}\sum_{k=1}^K\mathbb{E}\!\left[\frac{\Delta_k^2(1-x_k^2)^2}{\{2+\Delta_k(1-x_k)\}^2}\right]. \tag{F.8a}$$

*Second-moment expansion (bounded increments).* If $|\Delta_k|\le\eta<1$ almost surely, then for $g_x(t)=\{2+t(1-x)\}^{-2}$ the mean value theorem with $|x|\le1$, $|t|\le\eta$ gives $|g_x(t)-g_x(0)|\le|t|/\{2(1-\eta)^3\}$, whence

$$\left|R_{\mathrm{pair,gain}}-\frac{K_{\mathrm{eff}}}{4K}\sum_{k=1}^K(1-x_k^2)^2\,\mathbb{E}\Delta_k^2\right|\le\frac{K_{\mathrm{eff}}}{2(1-\eta)^3K}\sum_{k=1}^K\mathbb{E}|\Delta_k|^3. \tag{F.8b}$$

If the pair increments share a common marginal distribution (no cross-pair independence required),

$$R_{\mathrm{pair,gain}}=\frac{K_{\mathrm{eff}}}{4}\,D_H(T)\,\mathbb{E}\Delta^2+O_\eta\!\big(K_{\mathrm{eff}}\,\mathbb{E}|\Delta|^3\big),\qquad D_H(T)=\frac{1}{K}\sum_k(1-x_k^2)^2. \tag{F.8}$$

**The second moment is $\mathbb{E}\Delta^2$, not $\operatorname{Var}(\Delta)$**: the two may be interchanged only under the *extra* assumption $\mathbb{E}\Delta=0$. A deterministic mismatch $\Delta\equiv\epsilon$ is the immediate counterexample — its $\operatorname{Var}(\Delta)=0$, yet (F.8a) gives a strictly positive risk of order $K_{\mathrm{eff}}\epsilon^2$. For most non-DC Hadamard coefficients of a nonnegative object $|x_k|\ll1$, so $D_H\approx1$; $D_H$ is nevertheless a *pipeline constant to be measured*, not assumed.

*OU increment corollary (exact lognormal moments).* For a stationary Gaussian OU/AR(1) log gain with $\operatorname{Var}(\ell_n)=s^2$ and adjacent correlation $e^{-\rho}$, put $r(\rho)=1-e^{-\rho}$ and $u=s^2r(\rho)$. The adjacent log increment $X=\ell_{n+1}-\ell_n$ is $\mathcal N(0,2u)$ and $\Delta=e^X-1$, so

$$\mathbb{E}\Delta=e^{u}-1,\qquad\mathbb{E}\Delta^2=e^{4u}-2e^{u}+1=2u+7u^2+O(u^3), \tag{F.8c}$$

with $\operatorname{Var}(\Delta)=e^{4u}-e^{2u}$ and $\mathbb{E}\Delta^2-\operatorname{Var}(\Delta)=(e^{u}-1)^2$. The bounded-increment proposition does not apply directly to this lognormal $\Delta$; instead, split (F.8a) on $\{|X|\le c\}$: on the central event Taylor's theorem gives $\Delta^2(1-x^2)^2/\{2+\Delta(1-x)\}^2=\tfrac14(1-x^2)^2X^2+O_c(|X|^3)$ uniformly in $x\in[-1,1]$, while on the complement the exact fraction admits an exponential envelope $C_c(1+e^{2|X|})$ whose Gaussian-tail expectation is $o(u^m)$ for every $m$. Since $\mathbb{E}X^2=2u$ and $\mathbb{E}|X|^3=O(u^{3/2})$,

$$R_{\mathrm{pair,gain}}=\tfrac12K_{\mathrm{eff}}D_H(T)\,s^2r(\rho)+O\!\big(K_{\mathrm{eff}}\,u^{3/2}\big): \tag{F.8d}$$

the leading pair law survives. The read-noise value $2\sigma_{\mathrm{read}}^2/S_2$ is exact only for fixed/noiseless normalization. An unregularized Gaussian ratio has no finite second moment. Under common pair gain $a$ and high SNR, the delta method gives $R_{\mathrm{pair,read}}\approx2\sigma_{\mathrm{read}}^2(a^2S_2)^{-1}(1+1/K_{\mathrm{eff}})$; clamping makes the risk regularization-dependent. Pairwise Poisson terms require the explicit complementary-mask allocation.

**What F.3.2 does not claim.** (F.7)–(F.8) presuppose stable normalization. F.7/F.7a are algebra on the unclamped branch; the moment step uses small $\Delta$ and a common marginal across coefficient indices, not cross-pair independence.

**F.3.3 Random patterns / DGI: floor, leverage, and population-moment constants.** **Three distinct constants must carry three distinct names; no generic "pipeline $C_0$" label is permitted.** For a *fixed* design $A$, linear reconstruction $L$, object $T$, and $b=AT$, define the *raw fixed-design sampling floor* and the *residual leverage*

$$C_0^{\mathrm{floor}}(A,L,T):=\frac{N}{S_2}\,\|(LA-I)T\|_2^2, \tag{F.9a}$$
$$\Lambda_{\mathrm{lev}}(A,L,T):=N\,B_L(A,T)=\frac{N}{S_2}\sum_{n=1}^Nb_n^2\|Le_n\|_2^2, \tag{F.9b}$$
$$C_0^{\mathrm{lev}}(A,L,T):=\Lambda_{\mathrm{lev}}-1. \tag{F.9c}$$

The first is the raw-MSE sampling floor of the fixed operator; the second propagates exogenous multiplicative residuals and equal-count Poisson noise ($C_0^{\mathrm{lev}}$ is merely the shifted notation $\Lambda_{\mathrm{lev}}-1$). Third, for $N$ iid pattern draws $I_n=\mu\mathbf 1+\sigma x_n$ with iid coordinates ($\mathbb{E}x=0$, $\mathbb{E}x^2=1$, $\mathbb{E}x^3=\gamma_3$, $\mathbb{E}x^4=\beta_4$), the ideal known-$(\mu,\sigma)$ correlator $\hat T_{\mathrm{DGI}}=(N\sigma)^{-1}\sum_nx_nz_n$ and one-sample vector $Z=\sigma^{-1}x(\mu S_1+\sigma x^\top T)$ define the *population raw-moment constant*

$$\frac{\mathbb{E}\|\hat T_{\mathrm{DGI}}-T\|^2}{S_2}=\frac{C_0^{\mathrm{raw,moment}}}{N},\qquad C_0^{\mathrm{raw,moment}}:=\frac{\mathbb{E}\|Z-T\|^2}{S_2}, \tag{F.9}$$

whose evaluation is a moment calculation: expanding $\mathbb{E}\|Z\|^2$ with $Z=(\mu S_1/\sigma)x+xx^\top T$ and subtracting $\|\mathbb{E}Z\|^2=S_2$,

$$C_0^{\mathrm{raw,moment}}=K+\beta_4-2+K_{\mathrm{eff}}\big[K(\mu/\sigma)^2+2\gamma_3(\mu/\sigma)\big] \;\xrightarrow[\ \mu=0,\ \gamma_3=0\ ]{}\; K+\beta_4-2. \tag{F.10}$$

The $K_{\mathrm{eff}}K(\mu/\sigma)^2$ term is the familiar nonnegative-background penalty. For the ideal correlator, independence and unbiasedness give $\mathbb{E}_AC_0^{\mathrm{floor}}=C_0^{\mathrm{raw,moment}}$ and $\mathbb{E}_A\Lambda_{\mathrm{lev}}=1+C_0^{\mathrm{raw,moment}}$; **for a mean-subtracted or scale-aligned implementation these are not definition-level identities**. The R15 provisional contract output reproduces the historical grid's raw fixed-design floor range $980.110$–$1114.529$; its ten-object mean agrees with $K+\beta_4-2=1023.800$ to $0.8\%$, while objectwise deviations are larger. These numbers remain provisional until the required clean-commit rerun.

> **Proposition (exact pipeline specialization).** Suppose the residuals are exogenous to detector noise and design, with common mean $m_\delta$, common second moment $q_\delta=\mathbb{E}\delta_n^2$, and $\operatorname{Cov}(\delta)=(q_\delta-m_\delta^2)I$. Under the hypotheses of Theorem 1,
> $$\frac{\mathbb{E}\|\hat T-T\|_2^2}{S_2}=\frac{\|(LA-I)T+m_\delta LAT\|_2^2}{S_2}+\frac{\Lambda_{\mathrm{lev}}}{N}(q_\delta-m_\delta^2)+R_\xi, \tag{F.10a}$$
> with $R_\xi=\operatorname{tr}(L\Sigma_\xi L^\top)/S_2$. If $m_\delta=0$,
> $$\frac{\mathbb{E}\|\hat T-T\|_2^2}{S_2}=\frac{C_0^{\mathrm{floor}}}{N}+\frac{1+C_0^{\mathrm{lev}}}{N}\,q_\delta+R_\xi; \tag{F.10b}$$
> and if $\Sigma_\xi=\tau_G^2I+\Phi_{\mathrm{frame}}^{-1}\operatorname{diag}(b^2)$,
> $$R_\xi=\frac{\tau_G^2\operatorname{tr}(LL^\top)}{S_2}+\frac{1+C_0^{\mathrm{lev}}}{N\,\Phi_{\mathrm{frame}}}. \tag{F.10c}$$

**Proof.** The residual mean vector is $m_\delta\mathbf1$ and $L\operatorname{diag}(b)\mathbf1=Lb=LAT$; substitute this mean and the stated covariance into the exact identity (F.2). The Poisson specialization uses $(S_2\Phi_{\mathrm{frame}})^{-1}\sum_nb_n^2\|Le_n\|_2^2=\Lambda_{\mathrm{lev}}/(N\Phi_{\mathrm{frame}})$. $\blacksquare$

For the ideal iid correlator with centered residuals the pattern-averaged bookkeeping is the familiar display

$$\mathrm{relMSE}_{\mathrm{DGI}}=\frac{C_0^{\mathrm{floor}}}{N}+\frac{(1+C_0^{\mathrm{lev}})\,v}{N}+\frac{K\tau_G^2}{N\sigma^2S_2}+\frac{1+C_0^{\mathrm{lev}}}{N\,\Phi_{\mathrm{frame}}}, \tag{F.11}$$

where for the ideal correlator $\mathbb{E}_A\Lambda_{\mathrm{lev}}=1+C_0^{\mathrm{raw,moment}}$. This decoupling is exact for injected residuals and heuristic for same-record blind pipelines. There is no universal long-run-variance multiplier: one may define a pipeline-specific $\chi_{\mathrm{eff}}=R_{\mathrm{gain}}/(vB_L)$ from (F.4), but it depends on $(A,L,T)$ and the full covariance.

**Correction (drift-leverage constant of the gain term; measured, no fitted parameters).** As previously written, the gain term of (F.11) evaluated with the *scale-aligned floor* constant in place of the leverage is **wrong for mean-subtracted DGI pipelines** under time-structured (drift-like) residual gain: on the published grid it underpredicts the measured random-arm drift excess by a median factor $\approx1.4\times10^3$ (1364 / 1527 / 1521 across the none / AGC / SCGI-proxy corrections; white-drift diagnostic, `results/prop3_nofreeparam_r1/`). The correct leverage is the **nonnegative-background constant** $\Lambda_{\mathrm{lev}}=1+C_0^{\mathrm{lev,raw\ background}}$, obtained from (F.10) evaluated at the measured raw pattern moments (at the grid's operating point $C_0^{\mathrm{lev,raw\ background}}\approx0.7$–$1.2\times10^6$, versus the scale-aligned floor $\approx6.2$–$7.2\times10^2$ and the *raw* fixed-design floor $\approx1.0$–$1.1\times10^3$); with it the measured excess is reproduced to 0.3–4.7% (median ratios 1.003 / 1.047 / 1.039), still with zero fitted parameters. Mechanism: mean subtraction removes the $K_{\mathrm{eff}}K(\mu/\sigma)^2$ background penalty from the **sampling floor** — hence the small floor constant in the $C_0^{\mathrm{floor}}/N$ term, confirmed exactly by the flat oracle arm — but **not** from the **drift leverage**: a time-varying gain modulates the large DC background coherently, and the correlator pays the full background leverage. For mean-subtracted pipelines the gain term of (F.11) must therefore carry $\Lambda_{\mathrm{lev}}=1+C_0^{\mathrm{lev,raw\ background}}$, while the sampling-floor term keeps the (raw or aligned, *consistently chosen*) floor constant. This vindicates — and extends to the gain term — the "no universal $C_0$" warning below, which earlier versions applied to the floor term only.

**What F.3.3 does not claim.** There is no universal $C_0$. The sampling floor and drift leverage differ by about $10^3$ here, and raw versus aligned floors by about $1.54$. Table I reports the exact fixed-operator calculation averaged over ten objects, $NB_L\in[7.527,7.544]\times10^5$, not a residual probe or Prop. 3 floor. Flux-limited formulas apply only to nonnegative physical buckets.

### F.4 Prop 3: the finite-$N$ flip boundary

**Drift model and assumptions.** Let $s^2$ be the variance scale of the log-gain process $\ell$ and let $\rho_{\mathrm{pair}}$ be the **adjacent-pair decorrelation parameter**: for an Ornstein–Uhlenbeck log-gain the paired-mask gain increment obeys $\mathbb{E}[\Delta_k^2]=2s^2r(\rho_{\mathrm{pair}})+O(s^4r^2)$ with $r(\rho)=1-e^{-\rho}$ (exact moments: (F.8c); $r(\rho)=\rho+O(\rho^2)$ at small $\rho$). Assume the small-mismatch regime of (F.8) (so $R_{\mathrm{pair,gain}}(\rho_{\mathrm{pair}})\approx\tfrac12 K_{\mathrm{eff}}D_H(T)\,s^2\,r(\rho_{\mathrm{pair}})$, per (F.8d)) and the DGI decomposition (F.11) with blind residual variance $v_{\mathrm{blind}}(\rho_{\mathrm{pair}},N)$, treated here as an **externally measured function of $(\rho_{\mathrm{pair}},N)$** (the runner measures it on the grid). **No deterministic-Lipschitz $\rho^{2/3}$ rate is attributed to the OU drift**: OU paths are not Lipschitz, and the correct interior OU window analysis (lemma below, (F.14)–(F.16)) gives stochastic drift error $s^2\rho W/6$ to first order and window-optimized risk $\propto\rho^{1/2}$, not $\rho^{2/3}$.

**Prop 3 (raw-MSE flip boundary; fixed-point form).** *All risks in this proposition are raw relative MSEs of Theorem 1 (the metric caution below explains why a scale-aligned analogue is a different number). Define $\rho^*=\inf\{\rho_{\mathrm{pair}}\ge0: R_{\mathrm{pair}}(\rho_{\mathrm{pair}})\ge R_{\mathrm{rand}}(\rho_{\mathrm{pair}},N)\}$, where $R_{\mathrm{pair}}=R_{\mathrm{pair,gain}}+R_{\mathrm{pair,read}}+R_{\mathrm{pair,Pois}}$ and, for the random arm,*

$$R_{\mathrm{rand}}(\rho,N)=\frac{C_0^{\mathrm{floor}}}{N}+\Gamma_{\mathrm{blind}}(\rho,N)+R_{\mathrm{rand,noise}}. \tag{F.12a}$$

*For an **oracle-known-gain** arm, $\Gamma_{\mathrm{blind}}=0$ (the validated skeleton below). For an **exogenous, centered, frame-uncorrelated** residual with $q_{\mathrm{blind}}(\rho,N)=\mathbb{E}\delta_n^2$,*

$$\Gamma_{\mathrm{blind}}(\rho,N)=\frac{1+C_0^{\mathrm{lev}}}{N}\,q_{\mathrm{blind}}(\rho,N), \tag{F.12b}$$

*with $C_0^{\mathrm{lev}}$ the pipeline's drift-leverage constant of (F.9c) (equal to $C_0^{\mathrm{lev,raw\ background}}\approx10^6$ for the mean-subtracted pipeline — the F.3.3 correction). **No scalar representation is asserted for a same-record blind estimator**: there the full covariance, nonzero-mean, and residual–noise cross terms of Theorem 1 are required, and any scalar display must be labeled a conditional proxy. At first order define $A_T=\tfrac12K_{\mathrm{eff}}D_H(T)s^2$, $Q(\rho)=\Delta_R(\rho)/A_T$ with $\Delta_R(\rho)=C_0^{\mathrm{floor}}/N+\Gamma_{\mathrm{blind}}(\rho,N)+R_{\mathrm{rand,noise}}-R_{\mathrm{pair,noise}}$. Assume $A_T>0$ (equivalently $s>0$ and $D_H(T)>0$) and that the risks, hence $Q$, are continuous in $\rho$ on the comparison interval. Then the leading boundary is the **fixed-point equation***

$$1-e^{-\rho^*}=Q(\rho^*), \tag{F.12}$$

*up to the remainder in (F.8d). If $\Delta_R(0)\le0$ then $\rho^*=0$ (the flip is immediate, not absent). If $\Delta_R(0)>0$, a finite crossing on $[0,\rho_{\max}]$ **exists** when $1-e^{-\rho}\ge Q(\rho)$ somewhere on that interval, and is **unique** only under an additional single-crossing condition (e.g. strict increase of $1-e^{-\rho}-Q(\rho)$); if the difference stays negative, no crossing occurs in range. Only if $Q(\rho)\equiv Q_0$ is **constant** may one write the explicit solution: $Q_0\le0\Rightarrow\rho^*=0$; $0<Q_0<1\Rightarrow\rho^*=-\log(1-Q_0)$; $Q_0\ge1\Rightarrow$ no finite crossing in the leading OU model. When $q_{\mathrm{blind}}$ depends on $\rho$, the logarithmic display is a fixed point, **not an explicit solution**.*

**Proof.** At the boundary, $R_{\mathrm{pair}}(\rho^*)=R_{\mathrm{rand}}(\rho^*,N)$. Substituting $R_{\mathrm{pair,gain}}=\tfrac12K_{\mathrm{eff}}D_Hs^2\,r(\rho^*)$ (from (F.8d), whose proof starts from $\mathbb{E}\Delta^2$, *not* $\operatorname{Var}\Delta$) and (F.12a)–(F.12b), and solving for $r(\rho^*)=1-e^{-\rho^*}$, gives (F.12). Existence under the stated sign/continuity conditions is the intermediate value theorem applied to $\rho\mapsto1-e^{-\rho}-Q(\rho)$; the infimum is a crossing by continuity; uniqueness is exactly the single-crossing assumption and is not otherwise proven. $\blacksquare$

**Empirical status of Prop 3.** The R15 directory is provisional pending a clean-commit rerun.

- **True-$S_1$ same-estimator validation.** At $\sigma_a\ge0.1$, 40/40 raw crossings are observed; median/max agreement factors are $1.02041/1.03686$. The empirical slope is $-2.12044$ ($R^2=0.97669$), versus prediction $-2.11371$ ($R^2=0.97807$).
- **Production median normalization.** The same traces give 40/40 crossings, factors $1.04394/1.19985$, and slope $-2.00656$. F.7a/F.7b, rather than F.7 alone, describe this arm; no denominator clamp fires.
- **Same-record blind proxy.** Ordered pairwise Hadamard remains better in all 100 scanned cells. Raw $q_\delta$ exceeds aligned gain error by median factor $1.019$, lag-one residual correlation has median $0.882$, and the exact projected decomposition closes to $1.74\times10^{-5}$. The scalar proxy is close in this protocol but remains conditional; detector noise is absent, so no $C_{\delta\xi}$ term is tested.

**Leading-order heuristic (labeled as such).** If $r(\rho)=\rho$, $D_H=1$, noise differences are negligible, $v_{\mathrm{blind}}$ is negligible, $Q$ is treated as constant, and $\rho$ *means* adjacent-pair decorrelation, (F.12) collapses to the engineering rule

$$\rho^*\approx\frac{2C_0^{\mathrm{floor}}}{N\,K_{\mathrm{eff}}\,s^2}, \tag{F.13}$$

with first corrections $\rho^*\approx 2\big(C_0^{\mathrm{floor}}+(1+C_0^{\mathrm{lev}})v_{\mathrm{blind}}\big)/[NK_{\mathrm{eff}}D_Hs^2]+2(R_{\mathrm{DGI,noise}}-R_{\mathrm{pair,noise}})/(K_{\mathrm{eff}}D_Hs^2)$ and the nonlinear replacement $\rho\mapsto r^{-1}(\cdot)$ when adjacent increments are not infinitesimal. Note that for mean-subtracted pipelines "negligible $v_{\mathrm{blind}}$" means $(1+C_0^{\mathrm{lev,raw\ background}})v_{\mathrm{blind}}\ll C_0^{\mathrm{floor}}$ — a far stronger requirement than $v_{\mathrm{blind}}\ll C_0^{\mathrm{floor}}$, and the reason the blind-arm flip vanished on the published grid (empirical-status point (c) above). (F.13) is a *leading-order heuristic*, not a theorem; the theorem is (F.12).

**Lemma (OU window risk; not a Lipschitz-path theorem).** Let $\ell_n$ be stationary Gaussian with $\operatorname{Cov}(\ell_n,\ell_{n+h})=s^2e^{-\rho|h|}$, and let $\varepsilon_n$ be an independent centered stationary carrier-noise sequence with autocovariance $\gamma_\varepsilon(h)$. For an interior centered window $W=2m+1$ and $\hat\ell_n=W^{-1}\sum_{j=-m}^m(\ell_{n+j}+\varepsilon_{n+j})$,

$$\mathbb E(\hat\ell_n-\ell_n)^2=s^2\Big[1-\tfrac2W\sum_{j=-m}^me^{-\rho|j|}+\tfrac1{W^2}\sum_{i,j=-m}^me^{-\rho|i-j|}\Big]+\tfrac1{W^2}\sum_{i,j=-m}^m\gamma_\varepsilon(i-j). \tag{F.14}$$

If $\rho W\to0$, the OU contribution is

$$s^2\rho\,\frac{W^2-1}{6W}+O(s^2\rho^2W^2), \tag{F.15}$$

and if $\sum_h|\gamma_\varepsilon(h)|\le\sigma_{\mathrm{abs}}^2$,

$$\mathbb E(\hat\ell_n-\ell_n)^2\le\frac{\sigma_{\mathrm{abs}}^2}{W}+Cs^2\rho W. \tag{F.16}$$

When $1\ll W^*\ll\min(N,1/\rho)$, an interior optimizer has $W^*\asymp\sigma_{\mathrm{abs}}/(s\sqrt\rho)$ and $\mathrm{MSE}^*\asymp\sigma_{\mathrm{abs}}\,s\sqrt\rho$ (for iid carrier noise, $W^*\sim\sqrt6\,\sigma_\varepsilon/(s\sqrt\rho)$ and $\mathrm{MSE}^*\sim\sqrt{2/3}\,\sigma_\varepsilon s\sqrt\rho$); outside this feasible band the appropriate boundary window applies. **The deterministic Lipschitz $\rho^{2/3}$ rate is therefore not an OU output.** Prop 3 may treat $q_{\mathrm{blind}}(\rho,N)$ as an externally measured function — as the empirical analysis does — but any OU *estimator theorem* must use this stochastic $\rho^{1/2}$ analysis instead.

**Metric and implementation cautions (raw versus scale-aligned).** The Prop.-3 runner's scale-aligned gain error $\min_c\|c\hat a-a\|^2/\|a\|^2$ is not $q_\delta=N^{-1}\sum_n(a_n/\hat a_n-1)^2$ and is not $\operatorname{Var}(\delta)$; they agree only to first order after a fixed small-error gauge. Likewise, a scale-aligned reconstruction floor is not the raw $C_0^{\mathrm{floor}}$ required by Prop. 3. If $\hat T=T+e$, put $a=\langle e,T\rangle/S_2$ and $b=\|e\|^2/S_2$; the implementation's scale-aligned error, minimizing over $c\in\mathbb R$, is

$$R_{\mathrm{align}}=\frac{b-a^2}{1+2a+b}, \tag{F.17}$$

which is not generally proportional to the raw risk $b$ (even for $e\perp T$ it is $b/(1+b)$, not $b$). Therefore a raw-MSE theorem and an aligned-MSE empirical boundary must not be called an exact no-free-parameter validation of one another. The R15 true-$S_1$ arm compares raw with raw using the same estimator on both sides; its present directory is provisional until the clean-commit rerun required for submission-authoritative status.

**$\rho$-convention warning.** Throughout, $\rho_{\mathrm{pair}}$ (adjacent-pair decorrelation) is the variable of (F.12)–(F.13); it is **not** the normalized bandwidth $\rho_{\mathrm{bw}}$ of the tall-design thresholds ($p\approx\rho_{\mathrm{bw}}N$, Sec. 4). If a bandwidth parameter with adjacent-increment variance $\sim2s^2\rho_{\mathrm{bw}}/N$ is substituted, the explicit $1/N$ in (F.13) cancels and the boundary reads $\rho^*_{\mathrm{bw}}\approx2C_0/(K_{\mathrm{eff}}s^2)$ — same physics, different symbol. Every phase-diagram axis must declare its convention.

**What Prop 3 does not claim.** The boundary compares two *specific* pipelines (pairwise-normalized Hadamard vs. blind random+DGI with the ideal correlator); it does not rank SRHT-paired pipelines, externally calibrated systems, or prior-regularized reconstructions, each of which shifts $\Delta_R$. It inherits every assumption of its ingredients: small mismatch (F.8b)–(F.8d), measured constants $C_0^{\mathrm{floor}}$, $C_0^{\mathrm{lev}}$, and $D_H$ (with the floor/leverage distinction of the F.3.3 correction *and* the raw/aligned metric distinction of (F.17)), a stationary drift with a declared $r(\rho)$, and a $q_{\mathrm{blind}}$ that is an externally measured function, not an OU theorem (the $\rho^{2/3}$ attribution is withdrawn; the OU lemma gives $\rho^{1/2}$). Every prediction and every observation must be stated in the *same* raw or aligned metric. The strict no-free-parameter claim attaches only to the R15 true-$S_1$ raw-vs-raw comparison, which remains provisional until a clean-commit rerun; a purely aligned comparison is a different empirical analogue. It is a mean-square crossing, not a guarantee about any single realization; the single-crossing property itself is assumed, not derived; and at $\rho_{\mathrm{pair}}$ beyond the small-drift expansion only the defining infimum — not (F.12) — is meaningful. Finally, the validated regime is the $v=0$ skeleton (empirical-status point (a)); no scalar flip theorem is currently claimed for the blind arm — the corrected conditional proxy and the data both give no flip on the published grid.
