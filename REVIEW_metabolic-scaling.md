# Critical review — *Metabolic Scaling Theory and Biological Fractals* (Part II)

**Reviewer role:** internal critical/adversarial reader
**Scope:** the seven section pages under `docs/metabolic-scaling/` (abstract, introduction, methods, results, discussion, conclusion, references), cross-checked against the companion derivation `docs/notebooks/metabolic-scaling/mst_claude.md` and the existing notebooks.
**Date:** 2026-07-13

> This is a referee-style report on a *prototype* manuscript. The thesis — that biological branching networks are **self-affine**, not self-similar, and are routinely mis-measured — is worth pursuing and, in my view, probably correct in its qualitative direction. The problems below are about **rigor, internal consistency, and testability**, not about the core idea. The accompanying companion notebooks (`docs/notebooks/metabolic-scaling/review/`) turn each of the major points into something runnable.

---

## Summary verdict

The manuscript currently **asserts** its central quantitative result rather than **demonstrating** it, and the numbers it does report are internally inconsistent about *what the prediction even is*. The single experiment that would prove the thesis — measuring an object of **known** self-affine dimension with both a self-similar and a self-affine estimator and showing the self-similar one is biased — is not present. Several equations in Methods are dimensionally or algebraically broken as printed, and the key value (`d = 3/2`) is sourced to "West et al., *unpublished*." The Results claim of statistical agreement is not backed by any test. None of this sinks the idea, but as written the paper is not yet falsifiable and would not survive review.

Below, **Major** issues affect the conclusions; **Moderate** issues affect credibility/reproducibility; **Minor** are editorial.

---

## MAJOR — 1. The paper contradicts itself about what dimension MST predicts

The manuscript compares data against *three different theoretical targets* and never reconciles them:

| Target | Where it appears | Object it describes | Valid range |
|---|---|---|---|
| **D = 3** | `mst_claude.md` (your own companion): WBE space-filling network, `D_H = ln n / ln(1/γ) = 3` | the full 3-D network | 2–3 (Hausdorff) |
| **D = 3/2** | Methods Eq 15–17; Results; Table 4 caption ("predicted … is 3/2 or 1.5") | 2-D projected silhouette | 1–2 (binary box-count) |
| **D = 4/3** | Results, line 9: *"a differential mass dimension for such an image is expected to equal 4/3 rather than 3/2"* | the *same* projected image | 1–2 |

The Results section literally states the expected value is **4/3 rather than 3/2** one paragraph after using **3/2** as the benchmark the data "confirm," and Table 4's caption reinstates **3/2**. Meanwhile the canonical WBE result (in your own `mst_claude.md`) is **D = 3** for the network and **3/4** for the *metabolic* exponent via `θ = D/(D+1)`. A reader cannot tell which number is the hypothesis. **This must be resolved before anything else**: state one prediction, for one clearly-defined object (3-D network vs. 2-D projection vs. binary silhouette vs. grayscale surface), and derive it in full.
→ tested in `methods_companion.ipynb` (symbolic re-derivation) and `results_companion.ipynb`.

## MAJOR — 2. The Methods equation chain is broken and partly missing

- **Missing equations.** Methods is numbered **9, 10, 11, … 17**; the Introduction shows only **Eq 1** and **Eq 2**. Equations **3–8 are never shown anywhere on the site**, yet Methods Eq 15 cites "from **Equation 7**" and Results cites "**Equation 18**." Both Eq 7 and Eq 18 — and the "Supplementary Information" the Results point to — are dangling references. The derivation is not followable as published.
- **Eq 11** — `V_B = π Σ n_k r_k² l_k ≈ γ ξ² V_N (1 − n^{−4/3}) V_N`. `V_N` appears **twice**, giving units of volume². Almost certainly a typo, but it is the bridge equation for the volume argument.
- **Eq 12** — the "sphere" volume is written `v_n = (4/3) π l_n^{2/3}`. A sphere's volume is `(4/3) π r³`; the exponent should be **3**, not **2/3**, and the line immediately above correctly states `v_n ∝ l_n³`. Eq 12 contradicts both the geometry and the preceding line.
- **Eq 16** — `A ∝ V_B^{1/2} l_N^{3/2} r_N`. With `V_B ∝ L³`, the right-hand side scales as `L^{3/2}·L^{3/2}·L¹ = L⁴`. An **area** must scale as `L²`. The exponents are off by `L²`; the equation is not dimensionally an area.
- **Eq 17 and the punchline** — `N(ε) ∝ A/ε²`, then *"As ε → 0, dim → 2,"* then `N(ε) ∝ ε^{3/2}`, concluding `d = 3/2`. Two independent problems: **(a)** a box count must scale as `N(ε) ∝ ε^{−D}` — a **positive** power `ε^{+3/2}` means *fewer* boxes as boxes shrink, which is impossible; the sign is wrong. **(b)** "`dim → 2`" and "`d = 3/2`" are stated in the same breath and cannot both be the answer.
- **Provenance.** The load-bearing result `d = 3/2` is attributed to **"West et al., unpublished."** The paper's central number cannot be checked against a source.

→ every item above is re-derived symbolically in `methods_companion.ipynb`; where a correct derivation exists (e.g., the genuine WBE `D = 3`), the notebook shows it.

## MAJOR — 3. The one decisive control experiment is missing

The thesis is: *self-similar estimators give wrong dimensions for self-affine objects.* The clean way to prove that is to take objects whose self-affine dimension is **known analytically** (e.g., fractional Brownian surfaces with prescribed Hurst `H`, where `D = 3 − H`), measure them with **both** a self-similar and a self-affine method, and show (i) the self-affine method recovers the truth and (ii) the self-similar method is biased by a predictable amount. The paper never does this. Without it, "self-similar methods are wrong" is an assertion.
→ implemented in `introduction_companion.ipynb`: fBm surfaces of known `D`, measured both ways, with the bias quantified.

## MAJOR — 4. "Statistically indistinguishable" is claimed but never tested

Results: *"observed mass dimensions … are statistically indistinguishable from the MST and fBm predictions of 3/2"* and *"remarkable consistency."* No test is reported — no CI, no *t*-test, no equivalence test. Crucially, **"indistinguishable from 3/2" is an equivalence claim**, and equivalence cannot be established by *failing to reject* a point null (that is just low power). The correct tool is a **TOST equivalence test** against an interval `[3/2 − δ, 3/2 + δ]` with a pre-declared margin `δ`. With n = 5 leaves, n = 3 branches, n = 6 canopies, power is very low and the margin will be wide.
→ `results_companion.ipynb` runs TOST on the paper's own tabulated values. Outcome (worth reporting honestly): at a ±0.10 margin the leaf/branch/canopy means *are* equivalent to 3/2 and *not* to 4/3 — so the tabulated data do lean toward 3/2. But the margin is arbitrary and its band (0.20) exceeds the 3/2↔4/3 separation (0.167), so the two equivalence regions overlap; with n = 3–6 this is not confirmation, and it is premature while the target itself is unsettled (issue #1).

## MAJOR — 5. The reported dimensions are in the wrong range for the named method

Methods says the numbers come from **differential box-counting** (the Sarkar–Chaudhuri grayscale technique in FracLac). A genuine grayscale DBC treats intensity as a height surface and returns dimensions in **[2, 3]**. **Every value the paper reports is < 2** — synthetic 1.47–1.85 (Table 1), leaves 1.48–1.55 (Table 2), branches 1.45–1.49 (Table 3), canopy 1.33–1.54 (Table 4). Values in [1, 2] are the **binary** Minkowski–Bouligand range, not the differential/grayscale range. So either the estimator is actually a binary mass box-count mislabeled "differential," or DBC is being applied to thin binary silhouettes where it degenerates. The **method name and the tabulated outputs are inconsistent**, and the theoretical target (3/2, a value that only lives in [1, 2]) is being compared to a method the text describes as producing [2, 3]. (Confirmed numerically: grayscale DBC of fBm surfaces returns 2.1–2.4 in the companion notebook; binary counts return < 2.)
→ `results_companion.ipynb` computes **both** dimensions on the same images so the range mismatch is explicit.

## MAJOR — 6. The synthetic controls undercut the biological "match"

Table 1's synthetic objects have **known** dimensions, and the method does **not** recover them: a **Peano curve is space-filling (D = 2)** but is measured at **1.85** and **1.80**; the spread across synthetic "trees" is **1.47–1.85**. The biological samples all land near **1.5** — but so do several synthetic objects of *different* true dimension (Barnsley fern 1.576, Fibonacci tree 1.470). This is consistent with the estimator having a **central tendency near ~1.5–1.6 for sparse tree-like binary images regardless of true dimension**. If so, the biological agreement with 3/2 is an artifact of the estimator + object sparsity, not confirmation of MST. The synthetic table is the control, and as printed it argues *against* the method's ability to distinguish 3/2 from 4/3 from 1.6.
→ `results_companion.ipynb` reproduces this: measures objects of known D and shows the compression toward ~1.5.

## MODERATE — 7. Conceptual/terminology errors in a paper about dimensional rigor

- **Topological vs. fractal dimension conflated.** Intro (after Eq 2): *"A fractal object's **topological** dimension is given by `β = log N / log(1/ε)`."* That formula is the **fractal (similarity) dimension**; the *topological* dimension is an integer by definition. In a paper whose entire point is dimensional precision, this is a load-bearing slip.
- **Symbol `α` is overloaded.** In the Introduction `α` is a *fractal dimension* (in `β = 2α − H`); in Methods Eq 9 `α` is the *allometric/dynamic exponent* of a power law. Same symbol, two unrelated meanings, no disambiguation.
- **`β = 2α − H` is nonstandard and undefined.** The standard fBm relations are `β = 2H + 1` (1-D trace power spectrum) and `D = E + 1 − H`. The manuscript's `β = 2α − H` is neither, and `α`/`β` are not defined consistently with their other uses. Please give the exact relation you intend, with `E` (embedding dimension) explicit.
- **fBm 3/2 is a 1-D trace value.** `D = 3/2` for fBm corresponds to a **1-D** Brownian trace (`H = 1/2`, `D = 2 − H`). Leaves/branches/canopies are **2-D images**. Comparing a 2-D image mass dimension to a 1-D-trace fBm value is a category mismatch unless explicitly bridged.

→ `introduction_companion.ipynb` states each relation with its embedding dimension and shows the fBm spectral/Hurst/dimension bookkeeping numerically.

## MODERATE — 8. The mechanism (maximum entropy production) is presented as established but is unfalsifiable as posed

Key Finding #2 and Conclusion #3 make **maximum entropy production (MEP)** the *mechanism* ("the maximization of entropy through mass transfer and enzyme kinetics"). MEP is a **contested, non-universal principle**, and here it is stated as fact ("appears to be a fundamental mechanism") with **no measurement that could falsify it**. What observable, computed from an image or a network, would be *inconsistent* with "entropy production sets the fractal dimension"? Until that is specified, this is narrative, not a testable claim. Either (a) demote it to an explicitly speculative hypothesis, or (b) give the operational prediction.
→ `discussion_companion.ipynb` lays out what an MEP test would need and shows the claim is currently not operationalized.

## MODERATE — 9. Discussion overreach and unsupported specific numbers

- *"The fractal dimension of such organisms often aligns with … Kolmogorov turbulence, β = −5/3."* `−5/3` is the slope of the turbulent **energy spectrum**, not a spatial fractal dimension of an organism. Equating an organism's geometric dimension with a spectral exponent of the surrounding fluid is a conflation, and no data or citation is given.
- *"Colonies … exhibit diffusion-limited aggregation (DLA), a **self-similar** fractal pattern."* In a paper arguing biological growth is self-affine, asserting (without measurement) that DLA colonies are self-similar is in tension with the thesis and unsupported here.
- *"sponges and xenophyophores have evolved hyperbolic geometries to maximize substrate delivery"* — strong, specific, and uncited.
- **Scope mismatch with the Abstract.** The Abstract promises empirical treatment of *single-cell colonies, algae, lichens, bryophytes, higher plants, and heterotrophs*. The Results deliver only leaves, branches/roots, and forest canopies. Most of the promised empirical scope is absent.

## MODERATE — 10. Discrepancies with the paper's own referenced literature

The user asked specifically for discrepancies **not detailed in the literature review**. These are cases where the manuscript's narrative contradicts sources it *itself* cites in Table 1 / References:

- **The 3/4-vs-2/3 controversy is ignored.** Discussion asserts the 3/4 exponent "remains robust." Table 1 lists **Darveau et al. 2002** (allocation-based, multiple-causes model) and **Hochachka et al. 2003** — both prominent challenges to a single universal 3/4 exponent — and the broader literature (Dodds et al. 2001; White & Seymour 2003, mammals ≈ 2/3; Kolokotrones et al. 2010, curvature in the scaling) is not engaged. The manuscript cites the critics in the table but does not address them in the text.
- **"23 orders of magnitude" attributed to Kleiber 1932.** Kleiber's 1932 data spanned roughly mouse-to-steer (a few orders of magnitude). The ~23–27 orders figure comes from later microbe-to-whale syntheses (e.g., West & Brown 2002). As written, the Discussion misattributes the range to Kleiber.
- **Table 1 undercuts the "almost exclusively self-similar" framing.** The Introduction says plants/forests are "almost exclusively" called self-similar. Yet Table 1's own **Self-affinity** column is checked for Bradbury & Reichelt 1983, Milne 1992, Loehle & Li 1996, Li 2000, Seuront 2011, and Maryenko & Stepanenko 2024. The table partly refutes the claim the text builds on; the claim should be quantified ("N of M canopy-dimension papers used self-similar box-counting") rather than asserted.
- **Bentley et al. 2013 / Smith et al. 2014 are described as unaware of self-affinity**, but both explicitly model *asymmetric/deviating* branching; the manuscript should engage whether their "path fraction" asymmetry *is* a self-affine parameterization, not just note they "didn't use the word."

→ `references_companion.ipynb` audits Table 1 / References programmatically (see Moderate-11), and `discussion_companion.ipynb` flags the 3/4-vs-2/3 omission.

## MODERATE — 11. Citation and DOI hygiene

Table 1 (on the abstract/intro page) and the References page need a cleanup pass; several problems are checkable by script:

- **Empty/placeholder DOIs**: Rubner 1883, Kleiber 1932, Calder 1996, Banavar et al. 1999, and others render as `[DOI: ]()` or `[DOI:xx](…)`.
- **Duplicate DOI**: `10.1016/0304-3800(94)00177-4` is attached to **both** Bradbury & Reichelt 1983 **and** Loehle & Li 1996 (and appears again in the Zeide-era rows) — at most one can be correct.
- **Year/DOI mismatches**: "West et al. 2010" is given `10.1038/s41586-019-0976-6` (a **2019** Nature DOI). West et al. 1999 is given `10.1126/science.276.5309.122`, which is the 1997 *Science* slot (Enquist/West/Brown 1997), not the 1999 *Nature* plant-vascular paper.
- **In-text citations not in References**: "Brown et al. 2002" (Intro) is absent (References list Brown & West 2000 and Brown et al. 2004); "West et al. 1999a/1999b" are not disambiguated in References; Peano 1890, Bosman 1942, Darveau 2002, Hochachka 2003, Seely & Macklem 2012 appear in text/table with inconsistent presence in References.
- **Coinage year**: Intro says Mandelbrot "introduced 'fractal' in 1975" but cites *Mandelbrot 1977*; the 1975 coinage is *Les objets fractals*. Pick one.

→ `references_companion.ipynb` runs `audit_citations()` over the Table 1 rows and prints every missing/duplicate/placeholder DOI.

## MINOR / editorial

- Results line 5: `1.90 ± 0.66` — a `± 0.66` uncertainty on a dimension bounded in [1, 2] spans almost the whole range; presumably `0.066`. As printed it is meaningless.
- Methods, FracLac paragraph: *"an exponentially increasing box size factor of 0.1"* — a factor of 0.1 *shrinks*; the sentence is ambiguous. State the grid caliber series, min/max box size, number of grid positions/orientations, and the binarization/threshold used for each image class. As written the analysis is not reproducible.
- No **resolution normalization**: pixel counts range from 144k to 5M across objects; box-count dimension depends on the available scaling range (∝ log of the size span), so cross-object comparisons need the scaling range held fixed or reported.
- `μr²` (0.98–0.99) is used as a quality signal, but a high `r²` does **not** imply the dimension is correct — the companion shows an r² = 0.997 fit returning a *wrong* dimension (2.02 for a set whose true dimension is 1.89) when the box ladder is misaligned. Report CIs on the slope, not just `r²`.
- Eq 1 vs Eq 2 vs the `1/f^β` discussion: `β` is used as (i) a scaling exponent in Eq 1, (ii) a spectral exponent in `1/f^β`, and (iii) a topological dimension after Eq 2. Three meanings for one symbol.

---

## The testable hypotheses this paper should commit to

Right now the manuscript has a thesis but no falsifiable predictions with an error model. I'd ask the authors to state (and the companion notebooks operationalize) something like:

- **H1 (estimator bias).** On objects of known self-affine dimension `D = 3 − H`, a self-similar box-count is biased high by `ΔD(H) > 0`, while a self-affine estimator recovers `D` within its CI. *Falsified if the two estimators agree on self-affine objects.* → `introduction_companion.ipynb`
- **H2 (which prediction).** The projected 2-D silhouette of a WBE space-filling network has box dimension **exactly one of** {3/2, 4/3}, derivable in closed form. *The paper must pick one and derive it; the two cannot both be "the prediction."* → `methods_companion.ipynb`
- **H3 (equivalence, not absence-of-difference).** Measured biological dimensions are **equivalent** to the chosen target within a pre-declared margin `δ` by TOST. *Falsified if the 90% CI is not contained in `[target ± δ]`.* → `results_companion.ipynb`
- **H4 (discrimination).** The method can distinguish 3/2 from 4/3 from 1.6 on synthetic objects at the achieved sample sizes. *If it cannot, no biological result can confirm 3/2 over the alternatives.* → `results_companion.ipynb`
- **H5 (asymmetry ↔ self-affinity).** Smith et al. (2014) path-fraction asymmetry correlates with the deviation of the measured dimension from the self-similar prediction. *This is the bridge from your thesis to the existing MST literature.* → sketched in `discussion_companion.ipynb`

---

## Companion notebooks (this review, made runnable)

All under `docs/notebooks/metabolic-scaling/review/`, sharing `fractal_review_utils.py`:

| Notebook | Section | What it tests |
|---|---|---|
| `abstract_companion.ipynb` | Abstract | Restates the 3 claims as falsifiable hypotheses; reviewer scorecard; CyVerse data bootstrap |
| `introduction_companion.ipynb` | Introduction | Self-similar vs self-affine; **the missing estimator-bias control** (fBm of known D, both estimators) |
| `methods_companion.ipynb` | Methods | Symbolic re-derivation; equation-by-equation audit; reconciles 3 vs 3/2 vs 4/3 |
| `results_companion.ipynb` | Results | Both dimensions on the same images; reproduces synthetic controls; **TOST equivalence test**; pulls empirical data from CyVerse |
| `discussion_companion.ipynb` | Discussion | DLA/Eden/KPZ vs self-affine; where the MEP claim is not falsifiable; 3/4-vs-2/3 omission |
| `conclusion_companion.ipynb` | Conclusion | Synthesis: what would have to be true; decision table |
| `references_companion.ipynb` | References | Programmatic DOI/citation audit of Table 1 and References |

**Data note.** The empirical cells pull from `/iplant/home/tswetnam/fractal-notebooks/data/` via the reader's own iRODS credentials (`gocmd`/`iget`). If the pull fails or the data are not shared, the notebooks fall back to deterministic synthetic objects and say so — nothing is silently fabricated as "empirical."
