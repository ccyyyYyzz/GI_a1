# Theorem A′ re-proof — parametric-transversality route (v2, R11 fixes incorporated)

> Status: CANONICAL PROOF DOCUMENT. v2 incorporates every mandatory fix from the
> GPT adversarial verification round R11
> (`paper_draft/REVIEWS/GPT_R11_aprime_reproof_review.md`, verdict: "major
> revision, mathematically salvageable; no reviewed lemma has a fatal
> counterexample after the stated corrections"). It supersedes
> `THEORY_APRIME_REPROOF_v1.md` and the incidence-variety Appendix B of earlier
> drafts. The final manuscript statements (Theorem A′ (i)–(iv) and the
> sharpness-status paragraph) are reproduced verbatim from R11 in §7.
> Changes vs v1, by R11 item: (1) Reduction (R) — full column rank explicit,
> sign fixed, normalized final form; (2) A′-2 — exceptional-set inclusion,
> precise C¹ measure-zero theorem, quantifier order, fixed-T slice; (3) A′-3 —
> U_M kept throughout, zero-carrier counterexample, rank-deficient designs in
> the bad set; (4) Lemma W — complete proof written out; (5) local iff —
> independent kernel derivation; (6) below-wall theorem — bookkeeping
> amendments, T′(d) construction, N=K consistency check; K=1 phrased as a
> vacuous local threshold plus a global theorem. Sharpness of the two global
> thresholds is NOT claimed as a theorem (§8).

## 0. Setting, notation, and the reduction

- Object: T ∈ R^K, K ≥ 1 (unconstrained; positivity remarks in §9).
- Design: M ∈ R^{N×K}, N ≥ K (tall). Rows m_n^⊤. Lebesgue measure on R^{N×K}.
- Rank-deficient designs: R := {M ∈ R^{N×K} : rank M < K}. R is a proper
  algebraic subset (vanishing of all K×K minors), hence closed and
  Lebesgue-null. **Every exceptional set below explicitly includes R (or
  R × R^K).**
- Drift: s ∈ S, a FIXED subspace of R^N with dim S = p ≥ 2 and
  1 := (1,…,1)^⊤ ∈ S. S is arbitrary but fixed and known — **no genericity
  assumption on S anywhere** (in particular the physical Fourier low-pass space
  S_LP is covered with no transfer argument).
- Data: Φ_M(T,s) := D_{e^s} M T, where D_x = diag(x) and e^s is componentwise.
- Carrier: y := M T. Nonvanishing-carrier sets:
  U := {(M,T) : (MT)_n ≠ 0 for all n} (open, complement a closed null set:
  each {(M,T) : m_n^⊤T = 0} is a proper algebraic subset), and for fixed M,
  U_M := {T ∈ R^K : (MT)_n ≠ 0 for all n}.
- Gauge: (T, s) ~ (cT, s − (log c)·1), c > 0. Identifiability of (M,T) at
  drift class S means: the only solutions (T′, s′) ∈ R^K × S of
  D_{e^{s′}}MT′ = D_{e^s}MT are the gauge orbit of (T, s).

**Reduction (R).** *Assume rank M = K and (M,T) ∈ U, and fix any s ∈ S. Then
(T′,s′) ∈ R^K × S is an alias of (T,s) iff, with d := s − s′ ∈ S,*

    M T′ = D_{e^d} M T.                                                   (R)

*If d = a·1 is constant, then (R) reads MT′ = e^{a}MT, and full column rank
gives T′ = e^{a}T — exactly the gauge orbit with c = e^{a} (matching the gauge
(T,s) ↦ (cT, s − log c·1): s′ = s − a·1, T′ = e^{a}T). Conversely every gauge
point solves (R) with constant d. Hence:*

**(M,T) is identifiable ⇔ (R) has no solution (T′,d) with d ∈ S \ R·1.**

Note (R) no longer involves s: identifiability is a property of (M,T,S) alone,
uniform over the true drift — the "same M for all drifts" issue is dissolved at
the level of the formulation, not patched afterwards. This is also the source
of the quantifier order in §3: the exceptional (M,T)-set is independent of s.

**Full column rank is necessary for the reduction.** For rank-deficient M the
equivalence "constant d ⇔ gauge-trivial" is FALSE even on U. Counterexample
(rank M = 1): N = K = 2, M with both rows equal to (0,1) — i.e.
M = [[0,1],[0,1]] — T = (0,1)^⊤, T′ = (1,1)^⊤: MT = MT′ = (1,1)^⊤ ∈ (R*)^2, so
(M,T) ∈ U and (T′, d = 0) solves (R) with constant d, yet T′ ∉ R·T — an
object-kernel ambiguity invisible to the normalized d ≠ 0 incidence set below.
This is harmless for the a.e. theorems, because R = {rank M < K} is an
algebraic null set — but every proof below EXPLICITLY adds R (resp. R × R^K)
to its exceptional set.

**Normalization of the gauge inside (R).** For a ∈ R, (T′,d) ↦ (e^{a}T′, d + a·1)
maps solutions of (R) to solutions. Fix a complement S₀ of R·1 in S
(dim S₀ = p − 1) and write d = d₀ + a·1 with d₀ ∈ S₀; the normalization
(T′,d) ↦ (e^{−a}T′, d₀) maps every solution to a solution with drift-difference
in S₀. **Final form: assume rank M = K and (M,T) ∈ U; the non-gauge aliases of
(M,T) are exactly the solutions of (R) with normalized d₀ ∈ S₀ \ {0}.** In
particular: (M,T) identifiable ⇔ (R) has no solution with d ∈ S₀ \ {0}.

## 1. Lemma 1 (row dichotomy)

**Lemma 1.** *Let (M,T) ∈ U and let (T′,d) solve (R) with d nonconstant
(d ∉ R·1). Then T′ is not a scalar multiple of T; consequently*

    T′ − e^{d_n} T ≠ 0 for every n = 1,…,N.

*Proof.* Suppose T′ = βT for some β ∈ R. Row n of (R): m_n^⊤T′ = e^{d_n} m_n^⊤T,
i.e. β y_n = e^{d_n} y_n. Since y_n ≠ 0 on U, e^{d_n} = β for all n, so d is
constant — contradiction. Hence T′ ∦ T. For the display: if T′ = e^{d_n}T for
some single n, then T′ ∥ T (and T ≠ 0 because y = MT ≠ 0). ∎

Only global nonconstancy of d is used; partial constancy (some equal
components) is harmless, and the only division is by y_n, legitimate on U.

## 2. Lemma 2 (joint submersivity)

Define F : R^{N×K} × R^K × R^K × S₀ → R^N,

    F(M, T, T′, d) := M T′ − D_{e^d} M T,     so F_n = m_n^⊤(T′ − e^{d_n} T).

**Lemma 2.** *At every zero of F with (M,T) ∈ U and d ≠ 0 (in S₀), the
differential of F with respect to M alone is surjective onto R^N.*

*Proof.* Perturb row n only: δM = e_n δm_n^⊤. Then
δF = e_n · δm_n^⊤(T′ − e^{d_n}T), which spans R·e_n as δm_n ranges over R^K,
provided T′ − e^{d_n}T ≠ 0 — which holds at every such zero for every n by
Lemma 1. Rows are decoupled (δM with a single nonzero row changes only that
component of F), so the image contains every e_n and the differential is onto
R^N. ∎

Remark: only δM is used; no genericity of S, no structure of d beyond
nonconstancy, and the object T is untouched. This rowwise M-perturbation is a
genuine global witness, uniform over the whole zero set.

## 3. Theorem A′-2 (generic exact identifiability, N ≥ K + p)

We first record the precise measure fact the projection argument uses.

**Lemma 3.1 (C¹ image of a lower-dimensional manifold is null).** *Let X be a
second-countable C¹ manifold with dim X = m < q, and let f : X → R^q be C¹.
Then f(X) has q-dimensional Lebesgue measure zero.*

*Proof.* By second countability, X is covered by countably many charts
φ_i : U_i → R^m, and each chart domain is exhausted by countably many compact
cubes; it suffices (countable union of null sets is null) to show
f(φ_i^{−1}(Q)) is null for one compact cube Q ⊂ R^m of side ℓ. On Q the map
g := f ∘ φ_i^{−1} is C¹, hence Lipschitz with some constant L (compactness).
Subdivide Q into k^m subcubes of side ℓ/k; each image g(subcube) lies in a
ball of radius L√m·ℓ/k in R^q, so the outer Lebesgue measure of g(Q) is at most
k^m · c_q (2L√m·ℓ/k)^q = C·k^{m−q} → 0 as k → ∞ (using m < q). ∎

No properness or compactness of f is needed. The manifolds Z, Z′ below are
embedded submanifolds of a Euclidean space, hence second countable (and
σ-compact) automatically. The statement would be FALSE for merely continuous
maps — space-filling curves — so the C¹ regularity of the zero manifolds,
supplied by Lemma 2, is load-bearing.

**Theorem A′-2.** *Fix S ∋ 1, dim S = p ≥ 2. If N ≥ K + p, then there is a
Lebesgue-null set E_gen ⊂ R^{N×K} × R^K such that every (M,T) ∉ E_gen is
identifiable: for EVERY s ∈ S, the only (T′,s′) ∈ R^K × S with
D_{e^{s′}}MT′ = D_{e^s}MT are the gauge orbit of (T,s).*

*Proof.* Work on the open set Ω := {(M,T,T′,d) : (M,T) ∈ U, T′ ∈ R^K,
d ∈ S₀ \ {0}}. By Lemma 2, 0 is a regular value of F on Ω, so
Z := F^{−1}(0) ∩ Ω is an embedded C^∞ (indeed real-analytic) submanifold of
codimension N:

    dim Z = (NK + K) + K + (p−1) − N.

Let π : Z → R^{N×K} × R^K be the C¹ (indeed analytic) projection onto (M,T).
Then

    dim Z − dim(R^{N×K} × R^K) = K + p − 1 − N ≤ −1   (when N ≥ K + p),

so by Lemma 3.1, π(Z) is Lebesgue-null in R^{N×K} × R^K.

Exceptional-set inclusion. By Reduction (R) — which requires rank M = K —

    {non-identifiable pairs (M,T) ∈ U} ⊂ (R × R^K) ∪ π(Z),

and the full non-identifiable set is contained in (R × R^K) ∪ π(Z) ∪ U^c.
All three terms are Lebesgue-null (R algebraic null; π(Z) by the above; U^c a
finite union of proper algebraic sets). Set E_gen := (R × R^K) ∪ π(Z) ∪ U^c. ∎

Three remarks fixing the scope precisely:

(a) T′ is unconstrained in Ω; T′ = 0 forces D_{e^d}y = 0, impossible on U, so
    such points are simply not zeros of F.

(b) **Quantifier order (proved).** For a.e. (M,T): for EVERY s ∈ S there is no
    non-gauge alias. The null set E_gen is independent of s, because the
    reduction (R) eliminated s before any measure-theoretic step. This does
    NOT imply that one design M works for every object T — that uniform
    statement is Theorem A′-3, at its own (larger) threshold.

(c) **Fixed-T slice statement (stronger in a useful direction).** For each
    FIXED T ≠ 0, almost every design M identifies that particular T when
    N ≥ K + p; the exceptional design set may depend on T. Proof: freeze T and
    run the same argument with F_T(M,T′,d) := MT′ − D_{e^d}MT on
    {M : (M,T) ∈ U} × R^K × (S₀ \ {0}); Lemma 2's witness uses only δM, so 0
    is a regular value of F_T; the zero set Z_T has dim
    NK + K + (p−1) − N ≤ NK − 1 when N ≥ K + p, and its projection to R^{N×K}
    is null by Lemma 3.1; add R and {M : (M,T) ∉ U} (a proper algebraic set for
    T ≠ 0). This slice form is what covers fixed structured objects in the
    Fig. 8 protocol: a.e. M for each fixed T ≠ 0.

## 4. Theorem A′-3 (uniform identifiability on U_M, N ≥ 2K + p − 1)

**Theorem A′-3.** *Fix S ∋ 1, dim S = p ≥ 2. If N ≥ 2K + p − 1, then there is
a Lebesgue-null set E_unif ⊂ R^{N×K} such that for every M ∉ E_unif: every
T ∈ U_M is identifiable — for every s ∈ S and every (T′,s′) ∈ R^K × S,
D_{e^{s′}}MT′ = D_{e^s}MT implies T′ = cT, s′ = s − log c·1 for a unique
c > 0.*

*Proof.* Sphere normalization: the solution set of (R) is scaling-equivariant —
(T,T′,d) solves (R) iff (cT, cT′, d) does, for every c ≠ 0 — and the
nonvanishing-carrier and nonconstancy conditions are scale-invariant. So it
suffices to rule out solutions with |T| = 1. Let

    Ω′ := {(M, T, T′, d) : |T| = 1, (M,T) ∈ U, T′ ∈ R^K, d ∈ S₀ \ {0}},

an open subset of R^{N×K} × S^{K−1} × R^K × S₀. Lemma 2's proof used only δM
and holds verbatim on Ω′ (the sphere constraint restricts T, not M). So
Z′ := F^{−1}(0) ∩ Ω′ is an embedded real-analytic manifold of codimension N,

    dim Z′ = NK + (K−1) + K + (p−1) − N = NK + (2K + p − 2 − N).

The projection π′ : Z′ → R^{N×K} (onto M alone) has

    dim Z′ − NK = 2K + p − 2 − N ≤ −1   (when N ≥ 2K + p − 1),

so π′(Z′) is Lebesgue-null by Lemma 3.1. Set E_unif := R ∪ π′(Z′) (the
rank-deficient designs are added explicitly: the reduction needs rank M = K).

Now take M ∉ E_unif and suppose (T′,d) solves (R) for some T ∈ U_M and
d ∈ S₀ \ {0}. Since T ∈ U_M, the carrier MT has no zero coordinate, so T ≠ 0;
rescale c = 1/|T|: (cT, cT′, d) is a solution with |cT| = 1 and (M, cT) ∈ U
(the carrier scales by c ≠ 0, staying nonvanishing), i.e. (M, cT, cT′, d) ∈ Z′
and M ∈ π′(Z′) — contradiction. By Reduction (R) (valid since rank M = K),
every T ∈ U_M is identifiable, for every s ∈ S simultaneously. ∎

**Remark 4.1 (why U_M cannot be dropped: a zero-carrier counterexample at the
threshold).** The scaling argument rules out nonzero T with NONVANISHING
carrier only, and this is essential: "every nonzero object" is FALSE even at
N = 2K + p − 1. Counterexample: K = 2, p = 2, N = 5 = 2K + p − 1,
S = span{1, e₁}, T = (1,1)^⊤, and

    M = [[1,−1],[1,0],[0,1],[1,1],[1,2]]   (rows m_1,…,m_5),

so MT = (0,1,1,2,3)^⊤ — full column rank, but the first carrier coordinate is
zero. For every t ≠ 0 take d = t·e₁ ∈ S (nonconstant) and T′ = T: row 1 of (R)
reads m_1^⊤T′ = e^{t}·0 = 0 ✓, rows 2–5 read m_n^⊤T′ = y_n ✓. So (T, s) and
(T, s − t·e₁) produce identical records for every t: a one-parameter family of
nonconstant non-gauge aliases. More generally, for ANY design M, every object
on the hyperplane {m_1^⊤T = 0} acquires such aliases whenever S contains a
vector supported on the zero-carrier row — so no generic-design statement can
rescue "every nonzero object". The correct conclusion is the one stated:
**for a.e. M, every T ∈ U_M := {T : (MT)_n ≠ 0 ∀n}, every s ∈ S.**

The drift-difference d is a fiber variable in Z′ — the "one M for all drifts
AND all nonvanishing-carrier objects" statement is what the projection argument
delivers by construction.

## 5. Lemma W (position of the twisted column space)

For (M,T) ∈ U with rank M = K define the twisted space

    W(M,T) := D_y^{−1} col(M) ⊂ R^N,   y = MT,

a K-dimensional subspace with 1 ∈ W (since D_y 1 = y ∈ col(M)). Aliases relate
to W by:

**d ∈ S solves (R) for some T′ ⇔ e^d ∈ W(M,T).**
(Indeed D_{e^d}y = D_y e^d, so (R) reads MT′ = D_y e^d, i.e.
e^d = D_y^{−1}MT′ ∈ W; conversely e^d = D_y^{−1}Mu gives the solution T′ = u,
unique since rank M = K.)

**Lemma W.** *Fix any subspace S ∋ 1 with dim S = p ≤ N, and K ≥ 1. For a.e.
(M,T) ∈ U:*

    dim(S ∩ W(M,T)) = 1 + max{0, (p−1) + (K−1) − (N−1)}
                    = 1 + max{0, K + p − N − 1}.

*No genericity of S is assumed or used — only 1 ∈ S.*

*Proof.* **(Step 1: basis completion; fixed T.)** Fix T ≠ 0 and complete it to
a basis B_T = [T, b₂, …, b_K] ∈ GL_K of R^K. The map
M ↦ M B_T = (y, v₂, …, v_K) is a linear isomorphism of R^{N×K}, hence maps
Lebesgue-null sets to Lebesgue-null sets both ways: "a.e. M" ⇔
"a.e. (y, v₂,…,v_K)".

**(Step 2: fixed-y isomorphism.)** For fixed y ∈ (R*)^N (all coordinates
nonzero — a co-null condition on y), set w_j := D_y^{−1} v_j, j = 2,…,K. For
FIXED y this is a linear isomorphism of R^{N(K−1)} in the variables
(v₂,…,v_K), so it preserves "a.e." and introduces no correlation between the
w_j and the fixed subspace S. Then

    W = D_y^{−1} span(y, v₂, …, v_K) = span(1, w₂, …, w_K).

**(Step 3: quotient.)** Let q : R^N → R^N/R·1 be the canonical quotient
(dim N − 1). Set A := q(S), of dimension p − 1 (the kernel R·1 lies in S).
Also q(W) = span(q w₂, …, q w_K).

**(Step 4: general position of q(W) against the FIXED A.)** For a.e.
(w₂,…,w_K) ∈ R^{N(K−1)}: the vectors q(w_j) are linearly independent and

    dim(A ∩ q(W)) = max{0, (p−1) + (K−1) − (N−1)}.

Failure of either statement is the vanishing of suitable maximal minors of the
matrix [A-basis | q(w₂) … q(w_K)] (expressed in any fixed basis of R^N/R·1):
the intersection dimension exceeds the generic value iff the rank of that
concatenated matrix drops below min{N−1, (p−1)+(K−1)}, a polynomial condition
in the entries of the w_j. It is not identically zero — a witness exists: since
A is a FIXED subspace of the (N−1)-dimensional quotient, one may choose
q(w₂),…,q(w_K) to extend a basis of A as far as dimensions permit (general
position against one fixed subspace only requires choosing vectors outside a
finite union of proper subspaces at each step). Hence the failure set is a
proper algebraic subset of R^{N(K−1)}, so Lebesgue-null. Note this is general
position with respect to the fixed A only — no genericity of S is invoked.

**(Step 5: q(S ∩ W) = q(S) ∩ q(W), via 1 ∈ W.)** The inclusion ⊆ is trivial.
For ⊇: take x ∈ S and x′ ∈ W with q(x) = q(x′); then x − x′ ∈ R·1 ⊆ W, so
x ∈ W, i.e. x ∈ S ∩ W and q(x) is the given element. The kernel of q
restricted to S ∩ W is exactly R·1 (as 1 ∈ S ∩ W), whence

    dim(S ∩ W) = 1 + dim(q(S) ∩ q(W)).

**(Step 6: Fubini, in this order, and measurability.)** The order of
quantifiers established so far: for every fixed T ≠ 0, for a.e. y, for a.e.
(v₂,…,v_K), the dimension formula holds — hence (Steps 1–2, Fubini on
R^N × R^{N(K−1)}) for every fixed T ≠ 0, for a.e. M, the formula holds. The
failure set

    B := {(M,T) ∈ U : dim(S ∩ W(M,T)) ≠ 1 + max{0, K+p−N−1}}

is Borel (indeed semialgebraic in a neighborhood of each point of U): the
dimension condition is a finite Boolean combination of rank conditions —
vanishing/nonvanishing of minors — on matrices whose entries are rational
functions of (M, T) on U (the entries of the w_j are entries of M divided by
coordinates of MT). Measurability licenses a SECOND application of Fubini, now
over T: every T-slice of B is M-null, hence B is Lebesgue-null in
R^{N×K} × R^K. ∎

**Remark 5.1 (K = 1).** For K = 1 the lemma HOLDS, it does not fail:
W = D_y^{−1} col(M) = R·1 identically (col(M) = R·y), so dim(S ∩ W) = 1, and
the formula also gives 1 + max{0, 1 + p − N − 1} = 1 since p ≤ N. What
degenerates at K = 1 is the NECESSITY of the global thresholds (see §6 and
Theorem A′(iv)), not Lemma W.

## 6. Local threshold (iff, K ≥ 2), genuine failure below the wall, and K = 1

### 6.1 Independent kernel derivation of the rank defect

Fix (M,T) ∈ U with rank M = K and any s ∈ S. The differential of
Φ_M(T,s) = D_{e^s}MT at (T,s) in the direction (δT, δs) ∈ R^K × S is

    DΦ_M(T,s)[δT, δs] = D_{e^s}(M δT + D_y δs),      y = MT.

The diagonal factor D_{e^s} is invertible, so

    (δT, δs) ∈ ker DΦ_M(T,s) ⇔ M δT = −D_y δs.

Given δs ∈ S, the right side lies in col(M) iff δs ∈ D_y^{−1}col(M) = W(M,T),
and then δT = −(M^⊤M)^{−1}M^⊤ D_y δs is UNIQUE (full column rank). Hence the
kernel is isomorphic to S ∩ W(M,T) via (δT,δs) ↦ δs, and

    dim ker DΦ_M(T,s) = dim(S ∩ W),      rank DΦ_M(T,s) = K + p − dim(S ∩ W),

independently of s. The gauge orbit c ↦ (cT, s − log c·1) has tangent
(δT, δs) = (T, −1) at c = 1 — equivalently the line spanned by (−T, 1) — and
it lies in the kernel (MT = D_y 1). Since 1 ∈ S ∩ W always,
dim(S ∩ W) ≥ 1 and rank DΦ_M ≤ K + p − 1: the maximal gauge-compatible rank is
K + p − 1, and the defect from it equals dim(S ∩ W) − 1. This derivation is
self-contained — nothing is imported from the superseded Appendix B
computation, and no genericity of S is used.

By Lemma W, for a.e. (M,T) ∈ U:

    rank DΦ_M(T,s) = K + p − 1 − max{0, K + p − 1 − N} = min{N, K + p − 1},

for every s ∈ S; maximal rank K + p − 1 holds iff N ≥ K + p − 1.

### 6.2 Theorem (generic local iff, K ≥ 2)

**Theorem (local iff).** *Fix S ∋ 1, dim S = p ≥ 2, and K ≥ 2. There is a
Lebesgue-null set E_loc ⊂ R^{N×K} × R^K such that for every (M,T) ∉ E_loc with
T ∈ U_M and every s ∈ S:*

    rank DΦ_M(T,s) = min{N, K + p − 1},

*and consequently (T,s) is locally identifiable modulo gauge iff
N ≥ K + p − 1. The failure below the wall is genuine (exact nearby aliases),
by the theorem of §6.3.*

*Proof.* Take E_loc := (R × R^K) ∪ U^c ∪ B with B the null failure set of
Lemma W. The rank formula is §6.1 + Lemma W.

Sufficiency at N ≥ K + p − 1 (ordinary local injectivity modulo gauge): write
S = R·1 ⊕ S₀ and use the decomposition (proved by the argument of Step 5,
Lemma W, applied to S₀ ∋ 0):

    S ∩ W = R·1 ⊕ (S₀ ∩ W)

(for x ∈ S ∩ W write x = a·1 + x₀, x₀ ∈ S₀; then x₀ = x − a·1 ∈ W). At maximal
rank, dim(S ∩ W) = 1 forces S₀ ∩ W = 0. Restrict Φ_M to the gauge slice
R^K × (s + S₀), of dimension K + p − 1: by §6.1 its differential at (T,s) has
kernel isomorphic to S₀ ∩ W = 0, so the restricted map is an immersion at
(T,s), hence (constant-rank/immersion theorem) a local embedding — locally
injective on the slice. Any alias sufficiently near (T,s) is gauge-normalized
into the slice by a factor c near 1 (continuity), so local identifiability
modulo gauge holds in the ordinary sense.

Necessity at N ≤ K + p − 2: the below-wall theorem of §6.3 supplies a
positive-dimensional real-analytic manifold of exact aliases through (T,s), so
ordinary local identifiability fails — not merely the rank test. ∎

### 6.3 Theorem (genuine failure below the wall)

**Theorem (below-wall exact aliases).** *Fix S ∋ 1, K ≥ 2, and
N ≤ K + p − 2. For a.e. (M,T) ∈ U (namely off E_loc of §6.2), and every
s ∈ S: through (T,s) there passes a real-analytic manifold of exact aliases of
dimension K + p − N − 1 ≥ 1, parametrized by d in a neighborhood of 0 in the
zero set of φ below; every point with d ≠ 0 is a genuine non-gauge alias, and
T′(d) → T as d → 0.*

*Proof.* Let P := Π_{W^⊥} be the orthogonal projection onto W^⊥
(dim W^⊥ = N − K, using rank M = K), and define the real-analytic map

    φ : S₀ → W^⊥,      φ(d) = P(e^d).

Then e^d ∈ W ⇔ φ(d) = 0, and φ(0) = P·1 = 0 (1 ∈ W). The differential at 0 is
Dφ₀ = P|_{S₀} (d/dt|₀ e^{td} = d componentwise; P linear). By the bookkeeping
S ∩ W = R·1 ⊕ (S₀ ∩ W) and Lemma W with N ≤ K + p − 2 (so the max is
attained):

    dim(S₀ ∩ W) = dim(S ∩ W) − 1 = K + p − N − 1,

hence rank Dφ₀ = dim S₀ − dim(S₀ ∩ ker P) = (p−1) − dim(S₀ ∩ W)
= (p−1) − (K+p−N−1) = N − K = dim W^⊥: Dφ₀ is SURJECTIVE. By the
submersion/implicit-function theorem (real-analytic version), φ^{−1}(0) is,
near 0, a real-analytic manifold of dimension (p−1) − (N−K) = K + p − N − 1 ≥ 1.

For each d in this manifold, e^d ∈ W, so with the left inverse
L := (M^⊤M)^{−1}M^⊤ define

    T′(d) := L D_y e^d.

Then MT′(d) = D_y e^d (because D_y e^d = D_{e^d}y ∈ col(M) precisely when
e^d ∈ W), i.e. (T′(d), d) solves (R); T′(0) = L y = T and T′(d) → T as d → 0
(continuity). Every point d ≠ 0 of the manifold lies in S₀ \ {0}, hence
d ∉ R·1, hence (via (R)) is a genuine non-gauge alias: (T,s) and
(T′(d), s − d) produce identical records but are gauge-inequivalent. ∎

**Consistency check at N = K.** At N = K (square, rank M = K), W = R^N, so
W^⊥ = 0 and φ ≡ 0: the alias manifold is all of a neighborhood of 0 in S₀,
of dimension p − 1 = K + p − N − 1|_{N=K} — exactly Theorem A's square-design
ambiguity count. There is no hidden N ≥ K + 1 assumption, and no
contradiction: p ≥ 2 gives K < K + p ≤ 2K + p − 1, so the square case lies
strictly below both global thresholds.

Together with §6.2 this upgrades the interpretation of the Fig. 8 experiment:
below the wall the failure is genuine non-uniqueness (a positive-dimensional
exact alias family), not merely a rank diagnostic; at/above the wall local
uniqueness holds a.e.; and from N ≥ K + p, global (exact) uniqueness holds
a.e. (Theorem A′-2).

### 6.4 The K = 1 stratum

For K = 1 and (M,T) with T ∈ U_M (so T ≠ 0 and every m_n ≠ 0), any solution of
(R) satisfies e^{d_n} = (m_n T′)/(m_n T) = T′/T for every n, so d is constant
and T′/T = e^{d_1} > 0: **for K = 1, every (M,T) with T ∈ U_M is GLOBALLY
identifiable modulo gauge, for every M, every s ∈ S, and every admissible N.**
The local threshold reads N ≥ K + p − 1 = p, which is AUTOMATICALLY satisfied
(S ⊆ R^N forces p ≤ N) — i.e. the threshold is vacuous at K = 1, not
"inapplicable". Consequently neither N ≥ K + p nor N ≥ 2K + p − 1 is necessary
when K = 1: corner strata break naive universal-necessity claims, which is why
all necessity statements in this document are restricted to K ≥ 2.

## 7. Final manuscript statements (verbatim, per R11)

**Theorem A′ (proved tall-design identifiability results).** Let K ≥ 1, N ≥ K,
and let S ≤ R^N be a fixed, known linear subspace of dimension p ≥ 2 with
1 ∈ S. For M ∈ R^{N×K} define Φ_M(T,s) = D_{e^s}MT and
U_M = {T ∈ R^K : (MT)_n ≠ 0 for every n}. Parameters are identified modulo the
positive global-scale gauge (T,s) ~ (cT, s − log c·1), c > 0.

(i) **Generic local threshold and genuine failure below it (K ≥ 2).** There is
a Lebesgue-null set E_loc ⊂ R^{N×K} × R^K such that for every (M,T) ∉ E_loc
with T ∈ U_M and every s ∈ S: rank DΦ_M(T,s) = min{N, K+p−1}. Consequently
(T,s) is locally identifiable modulo gauge iff N ≥ K+p−1. If N ≤ K+p−2 then a
gauge-normalized neighborhood of (T,s) contains a real-analytic manifold of
exact aliases of dimension K+p−N−1 ≥ 1, and every other sufficiently nearby
point of it is gauge-inequivalent.

(ii) **Generic exact-identifiability sufficiency.** If N ≥ K+p, there is a
Lebesgue-null set E_gen ⊂ R^{N×K} × R^K such that for every (M,T) ∉ E_gen and
every s ∈ S: D_{e^{s′}}MT′ = D_{e^s}MT with (T′,s′) ∈ R^K × S implies T′ = cT,
s′ = s − log c·1 for a unique c > 0. Exact identifiability holds simultaneously
for every possible true drift s ∈ S. This statement is NOT uniform over all
objects for one fixed M.

(iii) **Uniform exact-identifiability sufficiency on the nonvanishing-carrier
set.** If N ≥ 2K+p−1, there is a Lebesgue-null set E_unif ⊂ R^{N×K} such that
for every M ∉ E_unif, every T ∈ U_M, every s ∈ S, and every
(T′,s′) ∈ R^K × S: D_{e^{s′}}MT′ = D_{e^s}MT implies T′ = cT, s′ = s − log c·1
for a unique c > 0. The same generic design works simultaneously for all
nonvanishing-carrier objects and all true drifts in S.

(iv) **Degenerate one-dimensional object stratum.** If K = 1 then for every M
and every T ∈ U_M and every s ∈ S, the pair (T,s) is globally identifiable
modulo gauge, for every admissible N. Neither N ≥ K+p nor N ≥ 2K+p−1 is
necessary when K = 1.

**Sharpness status (insert immediately after the theorem).** Parts (ii) and
(iii) are sufficient conditions, not proved if-and-only-if thresholds. For
K ≥ 2, the below-wall part of (i) proves generic exact failure whenever
N ≤ K+p−2. The remaining necessity assertion for the K+p bound is the boundary
case N = K+p−1: dimension counting predicts nonlocal aliases there, but
dominance of the bad-pair projection has not been proved. Likewise, dimension
counting predicts that a generic design fails uniform identifiability for some
object when N ≤ 2K+p−2, but this necessity direction has not been proved in
the intermediate regime. Thus K+p and 2K+p−1 are conjecturally sharp for K ≥ 2
under generic/nondegenerate drift geometry, not universal sharp thresholds for
every fixed S. The K = 1 stratum explicitly rules out any universal necessity
claim.

Provenance of the parts: (i) = §6.1–§6.3 (E_loc from Lemma W); (ii) = §3;
(iii) = §4; (iv) = §6.4 (note (iv) holds for EVERY M, not just a.e.).

## 8. What remains a prediction (sharpness), stated honestly

- Necessity of N ≥ K+p for generic EXACT identifiability: at N = K+p−1 the
  count in §3 gives dim Z − dim(M,T) = 0; the projection can (and, per the
  dimension count, should) cover a positive-measure set with finitely many far
  aliases, while local uniqueness already holds. We do NOT prove existence of
  far aliases at N = K+p−1; dominance of the bad-pair projection is open, and
  sharpness of K+p stays a dimension-count prediction, supported numerically
  (solver-vs-rank gap in Fig. 8).
- Necessity of N ≥ 2K+p−1 for uniform identifiability on U_M: same status —
  dimension counting predicts a bad nonvanishing-carrier object for a generic
  design throughout N ≤ 2K+p−2, but this is not proved in the intermediate
  regime K+p ≤ N ≤ 2K+p−2.
- The K=1 stratum (§6.4) shows corner strata can break naive universal
  necessity claims; all necessity statements above are restricted to K ≥ 2,
  and only the LOCAL threshold iff + below-wall genuine failure are claimed as
  theorems.
- Fig. 8 protocol scope: the experiment validates the LOCAL rank wall (and
  probes algorithmic recovery); protocol hygiene requires recording
  min_n |(MT)_n| per cell and flagging/regenerating below a documented
  tolerance, and the runner's wording is narrowed from "validates Theorem A′"
  to "validates the local-rank component and probes algorithmic recovery".
  Lemma W's slice form (§3, remark (c)) covers the fixed structured objects
  used there: a.e. M for each fixed T ≠ 0.

## 9. Scope remarks

- Positivity of the physical object: restricting T to any open subset of R^K
  (e.g. positive objects with nonvanishing carrier) preserves all a.e.
  statements (null sets intersect open subsets in relatively-null sets; the
  a.e.-(M,T) claims restrict to a.e.-(M, T ∈ O)). Constrained objects on
  lower-dimensional sets (e.g. exactly sparse) are NOT covered.
- s real (a_n = e^{s_n} > 0): built into the model; e^d > 0 automatic — no
  separate positive-domain argument needed.
- Noise: all of A′ is the noiseless exact-identifiability layer; statistical
  identifiability is Theorem B's business, unchanged.
- All statements are for the FIXED, known drift subspace S ∋ 1; no genericity
  of S is assumed or used (Lemma W's quotient step uses only 1 ∈ S; the
  general-position step is against the fixed A = q(S)). In particular the
  Fourier low-pass space S_LP is covered directly, and the low-pass transfer
  lemmas of the superseded Appendix B route are no longer needed for the main
  theorems.
- Deterministic structured designs (e.g. ordered Hadamard) are NOT covered by
  any a.e. statement here and must be checked separately.
