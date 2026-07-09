# Known fixes queued for the final review pass (do not lose)

Found on first read-through of MANUSCRIPT_DRAFT.md (assembled from the section-drafting workflow).
Apply in the final review pass together with whatever the adversarial review finds.

1. **§4 Corollary 2** — support-zero count: draft says "$K_0 \ge p$ generic support zeros restore local
   identifiability"; per issue #1 / v5 the generic criterion is #zeros $\ge \dim(S/\mathrm{span}\,1) = p-1$
   (known support). Fix the count and add "known support" qualifier.
2. **§6 Theorem C setup** — typo in the Poisson model: "$C\sim\mathrm{Pois}(\Lambda_0 e^{\theta B}+d)$"
   must be $\mathrm{Pois}(\Lambda_0 e^{\theta} B + d)$ (gain multiplies the carrier; not in the exponent).
3. **§6 framing** — the general windowed estimator (Thm B/B1, plain log) and the low-photon soft-log
   variant are conflated into one estimator. Separate: plain windowed log-average for the main rate;
   soft-log $\psi_\alpha$ introduced only for the low-photon regime (α→0 recovers the plain log).
4. **§5 Fig. 3 sentence** — "collapses onto a single tight $1/\sqrt W$ bundle, independent of the object"
   overstates: absolute error depends on the object through $\mathrm{CV}_B \propto 1/\sqrt{K_\mathrm{eff}}$
   (that IS the theory). Correct claim: curves collapse after normalizing by the theory floor
   $\sqrt{\mathrm{CV}_B^2/W}$; object enters only through $K_\mathrm{eff}$. Must match the r2 Fig. 3
   normalized-collapse panel (fig3c) — this is exactly the referee trap fixed in the figure round.
5. **References** — the two source-paper stub titles are paraphrases. Real titles:
   [PengChen2024APL] "Deep learning-enhanced ghost imaging through dynamic and complex scattering
   media with supervised corrections of dynamic scaling factors", Appl. Phys. Lett. 124, 181104 (2024).
   [PengXiaoChen2025OE] "High-fidelity optical wireless transmission in complex environments around a
   corner using the design of a single-layer neural network for data encoding", Opt. Express 33, 30123 (2025).
   Also expand the arXiv-key stubs into full author/title/year entries at conversion time.
