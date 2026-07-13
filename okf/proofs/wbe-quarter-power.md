---
type: Fractal Proof
title: WBE Derivation of the 3/4-Power Metabolic Scaling Law
description: Area-preserving branching plus space-filling delivery in a fractal transport network yields Kleiber's law, $B\propto M^{3/4}$.
tags: [biological, allometry, wbe, metabolic-scaling, power-law]
timestamp: '2026-07-13T00:00:00Z'
result: "B proportional to M^(3/4)"
concept: ../concepts/biological/allometry.md
historical_source: G. B. West, J. H. Brown, B. J. Enquist, "A general model for the origin of allometric scaling laws in biology" (Science, 1997).
verification_status: partially-verified
---

# Statement

Consider a hierarchical branching transport network with $N$ daughter branches
per node, feeding $N_c$ invariant terminal units (capillaries). Under two
network constraints — **area-preserving branching** and **space-filling
delivery** — the whole-organism metabolic rate scales with body mass as

$$B \propto M^{3/4}.$$

# Assumptions

1. **[asserted]** *Space-filling:* the network fills the body volume, forcing
   the branch-length ratio $\ell_{k+1}/\ell_k = N^{-1/3}$ (a length scale set by
   the cube root of the volume served).
2. **[asserted]** *Area-preserving branching:* total cross-sectional area is
   conserved across a node, forcing the radius ratio
   $r_{k+1}/r_k = N^{-1/2}$.
3. **[asserted]** Terminal units (capillaries) are size-invariant across
   species; metabolic rate is proportional to their number, $B\propto N_c$.
   These three are biological modeling premises, not theorems.

# Proof

1. **[verified]** *(Per-level volume scaling.)* Level $k$ has $N^k$ tubes each
   of volume $\propto r_k^2\ell_k$ with $r_k=r_0 N^{-k/2}$,
   $\ell_k=\ell_0 N^{-k/3}$. The per-level network volume therefore scales as
   $$N^k\cdot r_k^2\ell_k \;\propto\; \big(N\cdot N^{-1}\cdot N^{-1/3}\big)^k = N^{-k/3}.$$
   SymPy simplifies the growth factor $N\cdot(N^{-1/2})^2\cdot N^{-1/3}$ to
   $N^{-1/3}$.
2. **[asserted]** *(Volume-to-terminal-count relation.)* Summing the geometric
   series over levels, total network volume $V$ is dominated by its scaling
   with the number of terminal units and yields $V\propto N_c^{4/3}$;
   equivalently $N_c\propto V^{3/4}$.
3. **[verified]** *(Kleiber's law.)* With $M\propto V$ (mass proportional to
   network/blood volume) and $B\propto N_c$ (metabolic rate proportional to
   capillary count), $B\propto N_c\propto V^{3/4}\propto M^{3/4}$. SymPy gives
   the inverse exponent $1/(4/3)=3/4$.

# Verification

- **Symbolic (SymPy):** per-level volume growth factor
  $N\cdot(N^{-1/2})^2\cdot N^{-1/3}$ simplifies to $N^{-1/3}$ (confirmed), and
  the reciprocal of the WBE volume exponent, $1/(4/3)=3/4$, was computed to
  confirm the final power (confirmed).
- **Asserted (not re-derived in code):** the intermediate relation
  $V\propto N_c^{4/3}$ itself is the WBE geometric-series result quoted from
  West-Brown-Enquist (1997); only the per-level scaling feeding it and the
  final reciprocal were machine-checked. Hence step 2 is tagged [asserted].
- **Asserted:** the two network constraints (space-filling
  $\ell$-ratio $=N^{-1/3}$; area-preserving $r$-ratio $=N^{-1/2}$) and the
  proportionalities $B\propto N_c$, $M\propto V$ are the WBE biological
  modeling assumptions — they are inputs, not derived results. Hence the
  document is partially-verified: the **algebra** is machine-checked, the
  **premises** are asserted.

# Historical source

The model was published by West, Brown, and Enquist in *Science* (1997), giving
a mechanistic origin for Kleiber's empirical 1932 observation that metabolic
rate scales as roughly the 3/4 power of body mass.

# Related concepts

- [Allometry](../concepts/biological/allometry.md)
- [Power law](../concepts/foundations/power-law.md)

# Citations

1. West, G. B., Brown, J. H., Enquist, B. J. "A general model for the origin of allometric scaling laws in biology." *Science* 276 (1997): 122-126.
2. Kleiber, M. "Body size and metabolism." *Hilgardia* 6 (1932): 315-353.
