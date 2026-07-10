# Theorem A′ re-proof — parametric-transversality route (v1, for adversarial review)

> **SUPERSEDED (2026-07-10): see `THEORY_APRIME_REPROOF_v2.md`, which incorporates all mandatory fixes from review R11 (`REVIEWS/GPT_R11_aprime_reproof_review.md`) and is the canonical proof document.**

> Status: PROOF DRAFT. Written 2026-07-10 in response to audit blocker P0-1
> ("Theorem A′ as a sharp iff theorem does not currently hold": dominant-stratum /
> witness / transversality steps incomplete; same-M-for-all-drifts only a heuristic
> dimension count; K=1, N=p=2 counterexample to the claimed generic threshold).
> This note REPLACES the incidence-variety strategy of Appendix B with a
> parametric-transversality argument that (i) proves the two sufficiency
> thresholds as genuine theorems, (ii) closes the same-M-for-all-drifts gap by
> construction, (iii) proves the local iff for K ≥ 2, (iv) proves genuine
> (not just local-rank) non-identifiability below the local threshold, and
> (v) absorbs the K=1 counterexample as a stated degenerate stratum.
> Sharpness of the exact/uniform thresholds (necessity directions) is NOT
> claimed as a theorem; it stays an explicitly-labeled dimension-count
> prediction. Every lemma below is intended to be checked adversarially.

## 0. Setting and notation

- Object: T ∈ R^K, K ≥ 1 (unconstrained; positivity remarks in §8).
- Design: M ∈ R^{N×K}, N ≥ K (tall). Rows m_n^⊤. Lebesgue measure on R^{N×K}.
- Drift: s ∈ S, a FIXED subspace of R^N with dim S = p ≥ 2 and 1 := (1,…,1)^⊤ ∈ S.
  (S is arbitrary but fixed and known — no genericity assumption on S anywhere.)
- Data: R = D_{e^s} M T, where D_x = diag(x) and e^s is componentwise.
- Carrier: y := M T. Nonvanishing-carrier set:
  U := {(M,T) : (MT)_n ≠ 0 for all n}. U is open with full-measure complement of
  a closed null set (for each n, {(M,T): m_n^⊤T = 0} is a proper algebraic subset).
- Gauge: (T, s) ~ (cT, s − (log c)1), c > 0. Identifiability of (M,T) at drift
  class S means: the only solutions (T′, s′) of D_{e^{s′}}MT′ = D_{e^s}MT with
  s′ ∈ S are the gauge orbit of (T, s).

**Reduction (R).** Fix (M,T) ∈ U and any s ∈ S. (T′,s′) is an alias iff, with
d := s − s′ ∈ S,
    M T′ = D_{e^d} M T.                                                   (R)
The alias is gauge-trivial iff d ∈ R·1 (then T′ = e^{−c}T … i.e. T′ = c′T with
c′ = e^{d_1}). So: **(M,T) is identifiable ⇔ (R) has no solution (T′,d) with
d ∈ S \ R·1.** Note (R) no longer involves s: identifiability is a property of
(M,T,S) alone, uniform over the true drift — the "same M for all drifts" issue
is dissolved at the level of the formulation, not patched afterwards.

Normalization of the gauge inside (R): for c ∈ R, (T′,d) ↦ (e^{c}T′, d + c1)
maps solutions to solutions. Fix a complement S₀ of R·1 in S (dim S₀ = p−1) and
normalize d ∈ S₀. Then: identifiable ⇔ (R) has no solution with d ∈ S₀ \ {0}.

## 1. Lemma 1 (row dichotomy)

**Lemma 1.** Let (M,T) ∈ U and let (T′,d) solve (R) with d nonconstant
(d ∉ R·1). Then T′ is not a scalar multiple of T; consequently
    T′ − e^{d_n} T ≠ 0 for every n = 1,…,N.

*Proof.* Suppose T′ = βT for some β ∈ R. Row n of (R): m_n^⊤T′ = e^{d_n} m_n^⊤T,
i.e. β y_n = e^{d_n} y_n. Since y_n ≠ 0 on U, e^{d_n} = β for all n, so d is
constant — contradiction. Hence T′ ∦ T. For the display: if T′ = e^{d_n}T for
some single n, then T′ ∥ T (T ≠ 0 because y = MT ≠ 0). ∎

## 2. Lemma 2 (joint submersivity)

Define F : R^{N×K} × R^K × R^K × S₀ → R^N,
    F(M, T, T′, d) := M T′ − D_{e^d} M T,
so F_n = m_n^⊤(T′ − e^{d_n} T).

**Lemma 2.** At every zero of F with (M,T) ∈ U and d ≠ 0 (in S₀), the
differential of F with respect to M alone is surjective onto R^N.

*Proof.* Perturb row n only: δM = e_n δm_n^⊤. Then δF = e_n · δm_n^⊤(T′ − e^{d_n}T),
which spans R·e_n as δm_n ranges over R^K provided T′ − e^{d_n}T ≠ 0 — which
holds at every such zero for every n by Lemma 1. Rows are decoupled (δM with a
single nonzero row changes only that component of F), so the image contains
every e_n and the differential is onto R^N. ∎

Remark: only δM is used; no genericity of S, no structure of d beyond
nonconstancy, and the object T is untouched. This is the witness the previous
draft lacked, and it is uniform over the whole zero set.

## 3. Theorem A′-2 (generic exact identifiability, N ≥ K+p)

**Theorem.** Fix S ∋ 1, dim S = p. If N ≥ K + p, then for Lebesgue-a.e.
(M,T) ∈ R^{N×K} × R^K, the pair (M,T) is identifiable (no alias with
nonconstant drift difference, for ANY true drift s ∈ S).

*Proof.* Work on the open set Ω := U × R^K × (S₀ \ {0}) ∋ (M,T,T′,d). By
Lemma 2, 0 is a regular value of F on Ω, so
    Z := F^{−1}(0) ∩ Ω
is an embedded C^∞ (indeed real-analytic) submanifold of codimension N:
    dim Z = (NK + K) + K + (p−1) − N.
Let π : Z → R^{N×K} × R^K be the projection onto (M,T). Since
    dim Z − dim(R^{N×K} × R^K) = K + p − 1 − N ≤ −1   (when N ≥ K+p),
π is a C^1 map from a manifold of dimension strictly less than the target, so
π(Z) is Lebesgue-null (image of a null-dimensional-deficit manifold under a C^1
map; countable atlas + the standard "C^1 image of lower-dimensional manifold is
null" fact). Every non-identifiable (M,T) ∈ U lies in π(Z) by Reduction (R);
U^c is null. Hence the non-identifiable set is null. ∎

Two remarks the reviewers should attack:
(a) T′ is unconstrained in Ω — the theorem does not need T′ ≠ 0 excluded:
    T′ = 0 forces D_{e^d}y = 0, impossible on U, so such points are simply not
    zeros of F. (b) The statement is "a.e. (M,T)"; it implies in particular
    a.e. M works for a.e. T, but NOT "a.e. M works for all T" — that is A′-3.

## 4. Theorem A′-3 (uniform identifiability, N ≥ 2K+p−1)

**Theorem.** Fix S ∋ 1. If N ≥ 2K + p − 1, then for Lebesgue-a.e.
M ∈ R^{N×K}: every T with (M,T) ∈ U is identifiable.

*Proof.* Put T on the sphere: by gauge/scaling it suffices to rule out solutions
with |T| = 1 (aliasing is invariant under T ↦ cT jointly with T′ ↦ cT′). Let
    Ω′ := {(M, T, T′, d) : |T| = 1, (M,T) ∈ U, T′ ∈ R^K, d ∈ S₀ \ {0}},
an open subset of R^{N×K} × S^{K−1} × R^K × S₀. Lemma 2's proof used only δM
and holds verbatim on Ω′ (the sphere constraint restricts T, not M). So
Z′ := F^{−1}(0) ∩ Ω′ is a manifold of codimension N and
    dim Z′ = NK + (K−1) + K + (p−1) − N = NK + (2K + p − 2 − N).
Projection π′ : Z′ → R^{N×K} (onto M alone) has
    dim Z′ − NK = 2K + p − 2 − N ≤ −1   (when N ≥ 2K+p−1),
so π′(Z′) is null. For M ∉ π′(Z′): no (T, T′, d) with |T|=1, nonvanishing
carrier and nonconstant d solves (R); by scaling, no T ≠ 0 at all does. ∎

This is the uniform threshold, and the drift-difference d is a fiber variable —
the "one M for all drifts AND all objects" statement is what the projection
argument delivers by construction.

## 5. Lemma W (position of the twisted column space; K ≥ 2)

For (M,T) ∈ U define the twisted space
    W(M,T) := D_y^{−1} col(M) ⊂ R^N,   y = MT,
a K-dim subspace with 1 ∈ W (since D_y 1 = y ∈ col(M)). Aliases relate to W by:
d ∈ S solves (R) for some T′ ⇔ e^d ∈ W(M,T).

**Lemma W.** Fix any subspace S ∋ 1, dim S = p, and K ≥ 2. For a.e. (M,T) ∈ U:
    dim(S ∩ W(M,T)) = 1 + max(0, (p−1) + (K−1) − (N−1)).

*Proof sketch (to be verified line-by-line).* Fix T ≠ 0. Parametrize M by
(y, V₀): choose G ∈ GL_K with G e_1 = T… concretely, complete T to a basis
(T, b_2, …, b_K) of R^K; then M is determined by y := MT and v_j := M b_j,
j = 2..K, and (y, v_2, …, v_K) ↦ M is a linear isomorphism onto R^{N×K}. So
Lebesgue-a.e. M ⇔ a.e. (y, v_2,…,v_K). Now
    W = D_y^{−1} span(y, v_2, …, v_K) = span(1, D_y^{−1}v_2, …, D_y^{−1}v_K).
For fixed y with all y_n ≠ 0, the map (v_2,…,v_K) ↦ (D_y^{−1}v_2,…,D_y^{−1}v_K)
is a linear isomorphism, so a.e. (v_j) gives vectors (w_j := D_y^{−1}v_j) that
are a.e. in R^{N(K−1)}. Pass to the quotient q : R^N → R^N/R·1 (dim N−1).
q(S) has dim p−1, q(W) = span(q w_2,…,q w_K) is the span of K−1 a.e.-generic
vectors in R^{N−1}: standard general position gives, for a.e. (w_j),
    dim(q(S) ∩ q(W)) = max(0, (p−1)+(K−1)−(N−1)),
and dim(S ∩ W) = 1 + dim(q(S) ∩ q(W)) because both S and W contain 1 and
S ∩ W ⊇ R·1 with S ∩ W = R·1 ⊕ (lift of q(S)∩q(W) ∩ …) — precisely:
q(S ∩ W) = q(S) ∩ q(W) requires justification; it holds here because
1 ∈ S ∩ W, so q^{−1}(q(S)∩q(W)) ∩ S ∩ W maps onto q(S)∩q(W) with kernel R·1.
[REVIEW POINT 1: q(S ∩ W) ⊆ q(S) ∩ q(W) is trivial; the reverse needs
x ∈ S, x′ ∈ W with q(x) = q(x′) ⇒ x − x′ ∈ R·1 ⊆ W ⇒ x ∈ W. ✓ So equality holds
whenever 1 ∈ W. Verify.] For K = 1 the lemma is FALSE in spirit: W = span(1)
identically, and dim(S∩W) ≡ 1 regardless of N — this is the degenerate stratum
behind the audit's counterexample. ∎(sketch)

## 6. Theorem A′-1 (local threshold, iff, K ≥ 2) and genuine failure below it

Local identifiability at (M,T): the Jacobian of (T̃, s̃) ↦ D_{e^{s̃}} M T̃ at
(T, s) has the maximal rank K + p − 1 (full parameter dimension minus gauge).
A direct computation (Appendix B of the current draft, unchanged) shows the
rank defect equals dim(S ∩ W(M,T)) − 1.

**Theorem (local iff).** Fix S ∋ 1 and K ≥ 2. For a.e. (M,T) ∈ U:
(M,T) is locally identifiable ⇔ N ≥ K + p − 1.
For K = 1: every (M,T) ∈ U is identifiable (globally, any N ≥ 1), and the
threshold formula does not apply.

*Proof.* By Lemma W, for a.e. (M,T): dim(S∩W) = 1 ⇔ (p−1)+(K−1) ≤ N−1
⇔ N ≥ K+p−1. Rank defect zero iff dim(S∩W)=1. K=1 case: W = R·1, so e^d ∈ W
forces d constant; by Reduction (R) there is no nonconstant alias at all. ∎

**Theorem (genuine failure below the wall).** Fix S ∋ 1, K ≥ 2, and
N ≤ K + p − 2. For a.e. (M,T) ∈ U there exist genuine aliases: a manifold of
dimension K + p − N − 1 ≥ 1 of gauge-inequivalent solutions d ∈ S₀ \ {0}
(with their T′) through every neighborhood of 0.

*Proof.* Consider φ : S₀ → W^⊥ (dim N−K), φ(d) = Π_{W^⊥} e^d. φ(0) = Π 1 = 0.
dφ_0 = Π_{W^⊥}|_{S₀}. rank dφ_0 = dim S₀ − dim(S₀ ∩ W) and, by Lemma W,
a.e. dim(S ∩ W) = 1 + (K+p−N−1) = K+p−N (using N ≤ K+p−2 ⇒ the max is attained),
so dim(S₀ ∩ W) = K+p−N−1 and rank dφ_0 = (p−1) − (K+p−N−1) = N−K: dφ_0 is
SURJECTIVE. By the submersion/implicit-function theorem, φ^{−1}(0) is, near 0,
a manifold of dimension (p−1) − (N−K) = K+p−N−1 ≥ 1, consisting of d with
e^d ∈ W, each yielding T′ with (R) (T′ := any preimage; M injective for a.e. M
so T′ unique). Points d ≠ 0 of this manifold are nonconstant (S₀ ∩ R·1 = 0). ∎
[REVIEW POINT 2: dφ_0 computation: d/dt|₀ e^{td} = d componentwise; Π linear. ✓]
[REVIEW POINT 3: "a.e. M injective": tall M has full column rank a.e. ✓]

Together with A′-1 this upgrades Fig. 8's interpretation: below the wall the
failure is genuine non-uniqueness (a positive-dimensional alias family), not
merely a rank diagnostic; at/above the wall local uniqueness holds a.e., and
from N ≥ K+p global (exact) uniqueness holds a.e. (A′-2).

## 7. What remains a prediction (sharpness), stated honestly

- Necessity of N ≥ K+p for generic EXACT identifiability: at N = K+p−1 the
  count in §3 gives dim Z − dim(M,T) = 0; the projection can (and, per the
  dimension count, should) cover a positive-measure set with finitely many far
  aliases, while local uniqueness already holds. We do NOT prove existence of
  far aliases at N = K+p−1; sharpness of K+p stays a dimension-count
  prediction, supported numerically (solver-vs-rank gap in Fig. 8).
- Necessity of N ≥ 2K+p−1 for uniform identifiability: same status.
- The K=1 stratum shows corner strata can break naive necessity claims; all
  necessity statements above are restricted to K ≥ 2, and only the LOCAL
  threshold + below-wall failure are claimed as theorems.

## 8. Scope remarks

- Positivity of the physical object: restricting T to any open subset of R^K
  (e.g. positive objects with nonvanishing carrier) preserves all a.e.
  statements (null sets intersect open subsets in relatively-null sets; the
  a.e.-(M,T) claims restrict to a.e.-(M, T ∈ O)). Constrained objects on
  lower-dimensional sets (e.g. exactly sparse) are NOT covered.
- s real (a_n = e^{s_n} > 0): built into the model; e^d > 0 automatic — no
  separate positive-domain argument needed (audit's "实数正域" item).
- Noise: all of A′ is the noiseless exact-identifiability layer; statistical
  identifiability is Theorem B's business, unchanged.
- All statements are for the FIXED, known drift subspace S ∋ 1; no genericity
  of S is assumed or used. [REVIEW POINT 4: check no step secretly needs S
  generic — Lemma W quotient step uses only 1 ∈ S.]

## 9. Requested adversarial checks (for the GPT round)

1. Lemma 1/2: any zero of F with d nonconstant but T = 0? (T=0 ⇒ y=0 ∉ U. ✓)
   Any issue with d having SOME equal components (partial constancy)? Lemma 1
   needs only global nonconstancy — verify no hidden per-row division.
2. The measure-zero projection argument (manifold of deficit ≥ 1 ⇒ null image):
   state the precise fact and check second countability / σ-compactness use.
3. Lemma W: the parametrization (y, v_2..v_K) ↔ M — is the change of measure
   harmless for "a.e." statements (linear iso ⇒ yes)? The general-position claim
   for K−1 vectors vs fixed q(S): verify as stated for ALL fixed S, and that
   y-dependence (w_j = D_y^{−1} v_j) does not correlate w_j with S: for FIXED y
   the map is a linear iso, then Fubini over y. Write this order of quantifiers
   out and check it.
4. A′-3 sphere normalization: does restricting |T|=1 lose solutions? (Scaling
   equivariance of (R): (T,T′,d) solution ⇔ (cT, cT′, d) solution. ✓ Check.)
5. Local iff: the identification "rank defect = dim(S∩W) − 1" is imported from
   the existing Appendix B computation — re-derive it independently.
6. The below-wall failure theorem gives aliases NEAR the gauge point. Confirm
   these are genuine (T′ not gauge-equivalent: d ∉ R·1 suffices by (R)). ✓?
7. Anything in the argument that silently requires N ≥ K+1 (strictly tall)?
   At N = K (square, invertible a.e.): A′-2 threshold cannot hold (K+p > K);
   consistency with Theorem A (square designs never identifiable, p ≥ 2):
   check A′-2/A′-3 machinery reproduces/does not contradict Theorem A.
8. Compare against Fig. 8 protocol (K=64/128, K ≥ 2 ✓; nonvanishing carrier
   enforced? check the runner's object panel) — the theorem now matches what
   the experiment measures (local rank wall at N = K+p−1) plus predicts genuine
   below-wall aliasing; confirm no experimental claim now overreaches.
