# Results

Images of different computer-generated Lindenmayer systems (i.e., fractal trees) were analyzed using the open-source image analysis software **FracLac**. First, the fractal dimension was calculated using regular box-counting, and then with the differential box-count technique. The box-count analysis estimated the objects to have fractal dimensions between \( 1.81 \pm 0.056 < D_B < 1.90 \pm 0.66 \); however, the differential box-count mass dimension was found to be lower on average, with \( D_M = 1.60 \pm 0.10 \) (Table 1).

In Tables 1-X and Figures X-X, the observed mass dimensions of x-ray leaves, branches, and roots are statistically indistinguishable from the MST and fractional Brownian motion (fBm) predictions of \( \alpha = 3/2 \).

From Equation 18, a differential mass dimension for such an image is expected to equal \( 4/3 \) rather than \( 3/2 \) (see Supplementary Information).

---

### Table 1: Fractal mass dimension \( d_m \pm \mu \text{SE} \) and coefficient of variation (CV)

\[
\text{CV} = \frac{\sigma}{\mu}
\]

where \( \sigma \) is the standard deviation over the mean number of pixels per box. The associated lacunarity \( \Lambda \) and CV are also reported.

| **Fractal Type**          | **Pixels** | **\( d_m \pm \mu \text{SE} \)** | **\( \mu r^2 \)** | **\( d_m (\frac{\sigma}{\mu}) \)** | **\( \Lambda \)** | **\( \Lambda (\frac{\sigma}{\mu}) \)** |
|---------------------------|------------|---------------------------------|------------------|------------------------------------|-------------------|---------------------------------------|
| **Peano Curve 1 (square)** | 756,030    | 1.846 ± 0.100                   | 0.9966           | 0.0111                             | 0.0133            | 0.2128                                |
| **Peano Curve 2 (rounded)**| 1,440,000  | 1.803 ± 0.109                   | 0.9959           | 0.0161                             | 0.0713            | 0.1348                                |
| **H-fractal**              | 3,932,289  | 1.760 ± 0.124                   | 0.9945           | 0.0102                             | 0.1142            | 0.0746                                |
| **Pythagoras Tree 1**      | 5,000,000  | 1.607 ± 0.106                   | 0.9953           | 0.0030                             | 0.7003            | 0.0871                                |
| **Pythagoras Tree 2**      | 393,216    | 1.655 ± 0.075                   | 0.9976           | 0.0108                             | 0.2267            | 0.0899                                |
| **Barnsley’s Fern**        | 180,000    | 1.576 ± 0.073                   | 0.9973           | 0.0116                             | 0.3787            | 0.0680                                |
| **Fibonacci Tree**         | 348,140    | 1.470 ± 0.074                   | 0.9969           | 0.0118                             | 0.8680            | 0.0657                                |

---

### Table 2: Observed local mass fractal dimension of five different types of leaves

The results were obtained using the **FracLac** Differential Box Count for a power series with an exponentially increasing box size factor of 0.1.

| **Image**   | **Pixels**  | **\( d_M = \ln(\mu_\varepsilon) / \ln \varepsilon \)** | **\( \mu r^2 \)** | **\( \mu \text{SE} \)** | **\( CV (\frac{\sigma}{\mu}) \)** |
|-------------|-------------|-------------------------------------------------------|--------------------|-------------------------|----------------------------------|
| **Coleus**  | 144,316     | 1.5384                                                | 0.9938             | 0.1008                  | 0.0038                           |
| **Fig**     | 315,495     | 1.4844                                                | 0.9918             | 0.1123                  | 0.0026                           |
| **Nasturtium** | 1,115,114 | 1.5525                                                | 0.9969             | 0.0880                  | 0.0010                           |
| **Ginkgo**  | 1,086,596   | 1.5135                                                | 0.9978             | 0.0705                  | 0.0020                           |
| **Fern**    | 581,196     | 1.5083                                                | 0.9968             | 0.1268                  | 0.0064                           |

---

### Table 3: Observed local mass fractal dimension of three branching networks

Results were obtained using **FracLac** Differential Box Count for a power series with an exponentially increasing box size factor of 0.1.

| **Image**       | **Pixels**  | **\( d_M = \ln(\mu_\varepsilon) / \ln \varepsilon \)** | **\( \mu r^2 \)** | **\( \mu \text{SE} \)** | **\( CV (\frac{\sigma}{\mu}) \)** |
|-----------------|-------------|-------------------------------------------------------|--------------------|-------------------------|----------------------------------|
| **Single branch**| 255,285     | 1.4946                                                | 0.9953             | 0.0850                  | 0.0024                           |
| **Maple branches**| 473,450    | 1.4775                                                | 0.9944             | 0.0920                  | 0.0057                           |
| **Maple root**   | 617,312     | 1.4549                                                | 0.9970             | 0.0668                  | 0.0016                           |

---

### Table 4: Aerial LiDAR Canopy Height Models (CHM) over various forest types

Results were obtained using **FracLac** Differential Box Count for a power series with an exponentially increasing box size factor of 0.1. The predicted mass fractal dimension is \( \frac{3}{2} \) or 1.5.

| **Image**                   | **Pixels**  | **Mass Dimension \( d_M \)** | **\( \mu r^2 \)** | **\( \mu \text{SE} \)** | **\( CV (\frac{\sigma}{\mu}) \)** |
|-----------------------------|-------------|------------------------------|-------------------|-------------------------|----------------------------------|
| **Lowland Rainforest**       | 361,201     | 1.3313                       | 0.9860            | 0.1969                  | 0.0128                           |
| **Pine/Hardwood (South Carolina)** | 362,403 | 1.5223                       | 0.9898            | 0.1919                  | 0.0135                           |
| **Sierra Madre Oaks (Arizona)** | 362,404   | 1.4973                       | 0.9886            | 0.1988                  | 0.0116                           |
| **Western Ponderosa Pine (New Mexico)** | 361,802 | 1.4566                  | 0.9847            | 0.2252                  | 0.0144                           |
| **Southwest Mixed Conifer (New Mexico)** | 361,802 | 1.5319                 | 0.9869            | 0.2190                  | 0.0177                           |
| **Southwest Spruce-Fir (New Mexico)** | 361,802  | 1.5355                  | 0.9862            | 0.2255                  | 0.0139                           |

---
