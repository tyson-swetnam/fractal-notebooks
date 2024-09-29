# Introduction

"Allometry" is the study of organismal size and physiological rates of change in relation to body parts (Huxley 1932, [1950](https://doi.org/10.1098/rspb.1950.0055){target=_blank}). The term "allometric" translates from Latin as "different measure," while "isometric" means "equal measure" (Huxley and Tessier [1936](https://www.nature.com/articles/137780b0){target=_blank}). Allometric scaling refers to the way that physiological or morphological traits, such as metabolism or limb size, change at different rates compared to overall size of an organism. Isometric 

In 1975, Benoit Mandelbrot introduced the word 'fractal' to describe self-similar and irregular patterns found in nature (Mandelbrot [1977](https://riocuarto.gov.ar/files/documentos/1603551413_Literatura%20de%20Rio%20Cuarto%20entre%20Todos%20-%20A%C3%91O%202%20.%20N%C2%BA11.pdf)). In 1985 Mandelbrot published his book on self-affine fractals and fractal dimensions (Mandelbrot [1985](https://iopscience.iop.org/article/10.1088/0031-8949/32/4/001/pdf)) 


![The Julia Set](assets/julia_set.png){ width="500" }

Plate 1: [Gaston Julia]([Wikipedia](https://en.wikipedia.org/wiki/Gaston_Julia)) created so-called [Julia sets](https://en.wikipedia.org/wiki/Julia_set) using interative functions over 100 years ago. [code](../apps/julia.py) written in Python.


![The Mandelbrot Set](assets/mandelbrot_set.png){ width="500" }

Plate 2: The so-called [Mandelbrot Set](https://en.wikipedia.org/wiki/Mandelbrot_set), named in honor of Benoit Mandelbrot. [code](../apps/mandelbrot.py) written in Python. 


Importantly, natural phenomena, including hierarchical branching networks, are "fractal-like" over a limited range, unlike true fractals, which repeat infinitely. However, our review of the most widely cited research on allometric scaling and fractals finds that vascular organisms and forests are almost exclusively referred to as being "self-similar," and, critically, they were measured using self-similar fractal dimension techniques ([Table 1](#table-1-reported-fractal-dimensions-and-techniques-measuring-fractal-behavior-in-plants-or-forests)).

For a phenomenon to be self-similar, it must have the same appearance at all scales. This is clearly not the case for organisms, as allometric theory describes changes in appearance as they grow and age (Huxley 1932, Kleiber 1932). This misuse of terminology appears to have started as an oversight by authors incorporating fractals into allometric scaling theory, affecting how ecologists think about scaling processes in relation to fractals. In other cases, the misuse of "self-similar" has limited consequences. For example, predictions from Metabolic Scaling Theory (MST) (West et al. 1999a, West et al. 1999b, Brown et al. 2002) remain unaffected since allometric equations complement self-affinity. Acknowledging self-affinity may reconcile inconsistencies between MST and observed asymmetry in branching architectures (Bentley et al. 2013, Smith et al. 2014).

### Differentiating Between Self-Similarity and Self-Affinity

Reported fractal dimensions of trees and forests using self-similar dimensional analysis are likely to be incorrect based on these facts. Specifically, papers that report the length dimension [Hausdorff-Besicovitch] or box-counting dimension [Minkowski-Bouligand] of hierarchical branching phenomena (leaves, branches, forests) (Table 1) are problematic. Mandelbrot (1985) explained how evaluating fractals using self-similar techniques yields inaccurate results for measuring self-affine fractals because self-affine processes change their dimension between local and global scales. Since vascular plants have self-affine geometries, measuring them with self-similar fractal dimensions is likely to produce spurious values, as demonstrated in this study.

The basic fractal concept requires an object to exhibit a self-similar signal or shape, which can be measured as:

\[
N \propto \frac{1}{\varepsilon^{\beta}} \equiv \varepsilon^{-\beta}
\]

Equation 1

where \(N\) is the number of scalars \( \varepsilon \) required to measure the whole object, and \( \beta \) is a scaling exponent. Mandelbrot (1983, 1985) showed that all \( 1/f^{\beta} \) "noises" are self-affine, and \( \beta \) can be transformatively related to a fractal dimension \( \alpha \) via the Hurst exponent \( H \), such that \( \beta = 2\alpha - H \). Examples of \( 1/f^{\beta} \) noises include white noise (\( 1/f^0 \)) and Brownian noise (\( 1/f^2 \)).

A fractal object's topological dimension is given by \( \beta = \frac{\log N}{\log \frac{1}{\varepsilon}} \). A Euclidean object has a dimension \( \beta \) equal to an integer (Mandelbrot 1983). For example, if \( \beta = 2 \), the object is a square (\( \varepsilon^2 \)), or a disk where \( \varepsilon \) equals \( \pi \times \text{radius} \), and the object's mass \( m \) is equivalent to:

\[
m(\varepsilon) \propto \varepsilon^2
\]

When a portion of the object is removed, its new surface or mass is reduced by the factor \( \delta^{\beta} \), written as:

\[
m(\delta \varepsilon) = \delta^{\beta} m(\varepsilon)
\]

Equation 2

---

#### **Table 1:** Reported fractal dimensions and techniques measuring fractal behavior in plants or forests

| **Author(s) by Date** | **Self-similarity** | **Self-affinity** | **Allometric** | **Review (meta-analysis)** | **Characteristic Measured** | **Fractal Dimension(s)** |
|-----------------------|---------------------|-------------------|----------------|----------------------------|----------------------------|--------------------------|
| **Mandelbrot 1982** | ✓ |  |  | ✓  | Multiple | Multiple |
| **Sernetz et al. 1985**  | ✓ | | ✓ | ✓  | Multiple | Length |
| **Morse et al. 1985** | ✓ | |  | | Canopy | Length |
| **Frontier 1987** | ✓ | | ✓ | ✓  | Multiple | Length |
| **Tatsumi et al. 1989**  | | |  | | Roots  | Box Count |
| **Obert et al. 1990** | ✓ | |  | | Microbial Colony | Box Count Mass |
| **Sugihara and May 1990** | ✓ | | ✓ | ✓  | Multiple | Multiple |
| **Zeide 1991** | ✓ | |  | | Canopy | Length |
| **Zeide and Gresham 1991** | ✓ | |  | | Canopy | Length |
| **Zeide and Pfeifer 1991** | ✓ | |  | | Canopy | Length |
| **Fitter and Strickland 1992**| | |  | | Roots  | Length |
| **Milne 1992** | ✓ | ✓ |  | ✓  | Multiple | Length |
| **Lorimer et al. 1994**  | ✓ | | ✓ | ✓  | Multiple | Length |
| **Solé and Manrubia 1995** | ✓ | |  | | Canopy | Box Count |
| **Loehle and Li 1996** | ✓ | ✓ |  | | Information |  |
| **Halley 1996**  | ✓ | |  | | 1/f noises  | Power Spectral |
| **Plotnick et al. 1996** | | |  | | Canopy | Gliding Box (lacunarity) |
| **Weishampel et al. 1998** | ✓ | |  | | Canopy | Lacunarity  |
| **Zeide 1998** | ✓ | |  | | Canopy | Length |
| **West 1999** | ✓ | | ✓ | | Branching | Box Count |
| **West et al. 1999**  | ✓ | | ✓ | | Branching |  |
| **Brown et al. 2000** | ✓ | | ✓ | ✓  | Multiple |  |
| **Li 2000** | ✓ | ✓ |  | | Patch  | Information, Box Count |
| **Enquist et al. 2002**  | ✓ | |  | | Canopy, Roots  |  |
| **Halley et al. 2004** | | | ✓ | | |  |
| **Drake and Weishampel 2000** | ✓ | |  | | Canopy | Multifractals |
| **Eamus et al. 2002** | | |  | | Roots  | --  |
| **Alados et al. 2003** | ✓ | |  | | Patch  | Information |
| **Zhang et al. 2007** | | |  | | Canopy | Length |
| **Enquist et al. 2010**  | ✓ | |  | | Canopy, Roots  | --  |
| **West et al. 2010**  | | |  | | |  |
| **Savage et al. 2010** | | |  | | |  |
| **Seuront 2011** | ✓ | ✓ | ✓ | ✓  | Multiple | Many |
| **Okie 2013** | ✓ | | ✓ | | Cell surfaces  | Box Count |
| **Bentley et al. 2013**  | ✓ | | ✓ | | Branching | --  |
| **Smith et al. 2014** | ✓ | | ✓ | | Branching | --  |
| **Eghball et al.** | | |  | | Roots  | Box Count |

---

