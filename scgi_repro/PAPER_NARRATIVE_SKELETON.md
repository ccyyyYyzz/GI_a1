# Paper narrative skeleton (write-from-able)

**Synthesis of the mature theory (v5, issues #1–#3) + the framing pass (issue #4).** This replaces the
old theorem-list plan with a discovery arc. Everything below is chosen to read as a *reversal of an
imaging instinct*, not a taxonomy.

## The one thing to get right
> **The basis that is safest when the gain is KNOWN is the most treacherous when the gain is DRIFTING.**
Start there. Make the reader feel the paradox before any theorem, so Thm A lands as a discovery, not bookkeeping.

**Distilled hook (use in intro + conclusion):** *making gain observable — not by measuring the gain
directly, but by making the object stop pretending to be time.*

## Recommended arc — HYBRID (for PRA / IEEE-TCI)
Open with **Arc A's paradox** (hook) → run **Arc B's rigorous three-notion spine** (algebraic /
statistical / conditioning) → land on **Arc C's phase diagram** (the practical payoff). This buys the
discovery feel without sacrificing PRA/TCI rigor.

**Title** (sober for the venue; keep "paradox" as framing, not the title):
- primary: *Identifiability by stationarity: blind gain–object separation in self-calibrating ghost imaging*
- alts: *When exact inversion is not enough: temporal anchors for blind gain calibration in ghost imaging* · *A phase diagram for self-calibrating single-pixel imaging under gain drift*

**Abstract/intro anchor (one-sentence "what's new / why it matters"):**
> Blind gain calibration can be *designed in acquisition time*: random/SRHT illumination makes the
> object carrier stationary, turning gain–object separation from a square-design algebraic ambiguity
> into a predictable self-calibration problem with explicit identifiability thresholds, rates, and
> finite-noise phase boundaries.

## Section-by-section beats  (story job · hook line · key result · figure)

**1. Introduction — the calibration paradox.**
- *Story job:* trust the safe method (ordered Hadamard: one coefficient per frame, exact inverse waiting), then spring the trap — under drift the very ordering that makes the scan interpretable gives the object a *temporal signature*; a slow gain trace and a slow object-coefficient trace cast the same shadow on the bucket record.
- *Hook:* **"Hadamard is not defeated by randomness; it is defeated by chronology."**
- *Confounder named:* object-as-time-signature.  *Fig 1:* setup + the two-axis map (conditioning vs identifiability) with ordered-Hadamard / iid-random-DGI / tall-random / SRHT placed.

**2. Setup & three notions of identifiability.**
- *Story job:* the paradox forces three different lenses — you cannot judge an acquisition by inversion conditioning alone. Model `R_n=a_n B_n`, global-scale gauge; **algebraic / statistical / conditioning**. (This section IS a contribution.)

**3. Related work & positioning.** Bilinear-inverse / blind-deconvolution identifiability (Kech–Krahmer, Choudhary–Mitra, Li–Lee–Bresler, Ahmed–Recht–Romberg; verified in #2). **What's new = the temporal stationarity anchor**, not generic bilinear injectivity.

**4. The algebraic obstruction (Thm A + tall thresholds).**
- *Story job:* the paradox is *real* — a genuine algebraic orbit, not estimator weakness (square unconstrained: any invertible design absorbs a nonconstant gain into a new object). Then the FIRST escape: overdetermination, `N≥K+p` (generic) / `2K+p−1` (uniform), proven to hold for the physical low-pass gain space.
- *Metaphor (Image 2):* the object is a **barcode printed onto time**; gain drift is a **smudge**; if the barcode has slow structure, smudge and ink-thickness entangle — the theorem says the smudge can be reread as a *different barcode*, not merely that the scanner is noisy.

**5. The stationarity anchor (Thm B — the heart).**
- *Story job:* the SECOND, different escape — make the object's carrier look statistically the same at every time; then slow gain is the only non-stationary thing left.
- *Hook:* **"a reference process whose distribution does not know what time it is."**
- *Metaphor (Image 1):* drifting gain = a **boat in a slow current**; ordered coefficients = waves that change with position (can't tell current from coastline); random carriers = statistically the same waves everywhere → local averaging **drops an anchor into the distribution** (pins *relative* drift; absolute scale stays gauged).
- *Fig 2:* `B_n` sequences — random (stationary) vs Hadamard (object envelope).  *Fig 3 (killer):* blind gain-estimation error `‖â−a‖/‖a‖` vs window W, multi-object (random = tight `1/√W` bundle, object-independent; Hadamard = scattered, non-decaying).

**6. Estimation rate & low-photon.** *Story job:* not just possible — *efficient and predictable*. Windowed estimator, minimax rate; robust soft-log/Poisson `1/(Wλ)` (zeros only cut Fisher info, don't blow up).

**7. SRHT — the synthesis.**
- *Story job:* answer the reader's natural objection "must I give up orthogonal conditioning to self-calibrate?" — **no.**
- *Hook:* **"an orthogonal imager with randomized temporal handwriting"** / *"shuffle the deck without bending the cards."*
- Walsh N&S whitening condition; sign vs permutation; ablation.  *Fig 6:* SRHT ablation (none/perm/sign/both).

**8. Phase diagram — the go/no-go map (payoff).**
- *Story job:* the practical deliverable is a *pre-acquisition design chart*, not a theorem number.
- Master finite-noise relMSE bridge (leverage `B_L`); finite-N flip boundary with the heuristic as leading order. **Keep `ρ_pair` (adjacent-pair decorrelation) and `ρ_bw` (bandwidth, `p≈ρ_bw N`) separate** — label every axis before plotting.  *Fig 5:* phase diagram (basis × ρ × σ) + flip boundary.

**9. Discussion — significance & scope (honest).**
- *Deliverables to claim:* (i) **go/no-go identifiability predictor** — the thresholds above tell you your regime before you build; (ii) **SRHT design rule** ("don't run ordered Hadamard when blind slow gain is the problem; randomize the carrier; verify Walsh-flatness/spikiness or use permutation; keep a positivity/offset margin; pick the gain window from bias–variance"); (iii) **phase diagram** as a falsifiable design map; (iv) **cross-domain principle** — *to self-calibrate a multiplicative nuisance, design the carrier so its distribution is stationary in the nuisance coordinate* (blind gain/phase calibration, flat-fielding, coded-aperture/computational microscopy, single-pixel spectroscopy — as analogues/motivation, not proven domains).
- *Do NOT overclaim (put this list in, near-verbatim):* not hardware validation (theory+sim); uniqueness near `N=K+p` ≠ conditioning; random is NOT algebraically identifiable in the square unconstrained case; no universal `C0`/`D_H` (measure per pipeline); low-photon soft-log avoids log-zero but zero photons = zero Fisher info; keep `ρ_pair` ≠ `ρ_bw`.

**10. Conclusion.** Reprise the distilled hook: *making gain observable by making the object stop pretending to be time.*

## Where the SCGI/OWT reproduction sits
Motivation + concrete testbed only ("executable diagnostic model"), NOT a "we reproduced SCGI" claim.
Per the ceiling diagnostic: SCGI correction = oracle = static (perfect); the reproduction gap is the
object static ceiling + denoiser, which the theory *explains* — that's the honest, stronger framing.

## Metaphor placement (keep them in prose as intuition pumps, never as formal claims)
anchor → §5 (Thm B) · barcode/smudge → §4 (Thm A) · two-axis map + "shuffle the deck" → Fig 1 & §7 (SRHT).

*(Framing basis: issue #4. Math basis: THEORY_IDENTIFIABILITY_v5.md + issues #1–#3.)*
