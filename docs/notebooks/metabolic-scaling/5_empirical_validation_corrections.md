# Corrections to 5_empirical_validation.ipynb

## Critical Issues Identified

### 1. Category Error: Wrong Dimension Type Measured

**Problem**: The notebook claims to validate MST's prediction of D_m = 3/2, but differential box-counting (DBC) on grayscale images measures **texture dimension**, not the **skeletal mass dimension** that MST predicts.

**What MST Actually Predicts**:
- D = 3 for space-filling exchange surfaces in 3D
- D_mass = 3/2 for how *mass scales with distance from root* in the branching skeleton
- The 3/4 metabolic scaling comes from θ = D/(D+1) = 3/4

**What DBC on Grayscale Images Measures**:
- How box counts scale in (x, y, intensity) space
- Maximum possible dimension: 3 (2D spatial + 1D intensity)
- For space-filling 2D structures: D → 2.0 + intensity contribution

### 2. Observed D ≈ 2.1 is NOT Consistent with D = 1.5

The notebook's conclusion states:
> "Observed mean: D_m = 2.128 ± 0.047"
> "This is statistically consistent with MST prediction"

This is mathematically false. A t-test of 2.128 against 1.5 would yield p << 0.001.

### 3. Why D ≈ 2.1 Emerges Consistently

The ~2.1 value is actually expected because:
1. Structures nearly fill 2D image space → D approaches 2.0
2. Grayscale intensity variation adds ~0.1-0.2
3. All generators produce similar area coverage

---

## Required Corrections

### A. Add Proper Theoretical Framework

Explain the different fractal dimension types:

| Dimension Type | Symbol | What It Measures | MST Prediction |
|----------------|--------|------------------|----------------|
| Hausdorff/Box | D_H | How many boxes cover the set | D = 3 (3D space-filling) |
| Mass (skeleton) | D_m | Mass scaling M(r) ∝ r^D from center | D_m = 3/2 |
| Information | D_I | Shannon entropy scaling | Varies |
| Correlation | D_2 | Point-pair correlations | Varies |
| DBC Texture | D_DBC | Grayscale texture complexity | ~2.0 for 2D images |

### B. Add Skeletal Analysis Method

To measure the true skeletal dimension:

```python
from skimage.morphology import skeletonize
from scipy.ndimage import distance_transform_edt

def skeletal_box_count(image, threshold=10):
    """
    Measure fractal dimension of the binary skeleton.
    This is what MST's D = 3/2 actually refers to.
    """
    # Binarize
    binary = (image > threshold).astype(np.uint8)

    # Skeletonize to 1-pixel wide lines
    skeleton = skeletonize(binary)

    # Standard box-counting on binary skeleton
    sizes = []
    counts = []

    s = 2
    while s < min(skeleton.shape) // 4:
        # Count boxes containing skeleton pixels
        count = 0
        for i in range(0, skeleton.shape[0], s):
            for j in range(0, skeleton.shape[1], s):
                box = skeleton[i:i+s, j:j+s]
                if box.any():
                    count += 1
        sizes.append(s)
        counts.append(count)
        s *= 2

    # Linear regression in log-log space
    log_sizes = np.log(sizes)
    log_counts = np.log(counts)
    slope, intercept, r, _, se = linregress(log_sizes, log_counts)

    return {
        'dimension': -slope,  # D = -d(log N)/d(log s)
        'r_squared': r**2,
        'std_error': se,
        'skeleton': skeleton
    }
```

### C. Add Mass-Radius (Sandbox) Analysis

The true test of MST's D_mass = 3/2:

```python
def mass_radius_analysis(image, center=None, threshold=10):
    """
    Sandbox method: measure how mass scales with distance from root.

    MST predicts: M(r) ∝ r^(3/2) for branching networks

    This is the correct method to test the 3/2 prediction.
    """
    binary = (image > threshold).astype(np.float64)

    if center is None:
        # Find root (bottom center for trees, top for roots)
        cols_with_mass = np.where(binary.sum(axis=0) > 0)[0]
        center_x = int(np.median(cols_with_mass))
        rows_with_mass = np.where(binary[:, center_x] > 0)[0]
        center_y = rows_with_mass[-1]  # Bottom of trunk
        center = (center_y, center_x)

    # Distance transform from center
    y, x = np.ogrid[:binary.shape[0], :binary.shape[1]]
    distances = np.sqrt((x - center[1])**2 + (y - center[0])**2)

    # Mass within radius r
    radii = np.logspace(1, np.log10(min(binary.shape) / 2), 20)
    masses = []

    for r in radii:
        mask = distances <= r
        mass = (binary * mask).sum()
        masses.append(mass)

    # Fit M(r) = c * r^D
    log_r = np.log(radii)
    log_m = np.log(np.array(masses) + 1)

    # Use middle portion for fit (avoid edge effects)
    mid = len(radii) // 4
    end = 3 * len(radii) // 4

    slope, intercept, r_val, _, se = linregress(
        log_r[mid:end], log_m[mid:end]
    )

    return {
        'mass_dimension': slope,
        'r_squared': r_val**2,
        'std_error': se,
        'radii': radii,
        'masses': np.array(masses),
        'center': center
    }
```

### D. Correct the Conclusions

Replace the current conclusions with:

```python
def print_corrected_conclusions(skeletal_results, mass_radius_results, dbc_results):
    """
    Print accurate conclusions distinguishing dimension types.
    """
    print("="*70)
    print("CORRECTED CONCLUSIONS")
    print("="*70)

    print("\n1. DIFFERENTIAL BOX-COUNTING RESULTS (D_DBC)")
    dbc_dims = [r['dimension'] for r in dbc_results]
    print(f"   Mean D_DBC = {np.mean(dbc_dims):.3f} ± {np.std(dbc_dims):.3f}")
    print(f"   This measures TEXTURE dimension in 2D+intensity space")
    print(f"   Expected range for space-filling 2D: 2.0-2.2 ✓")
    print(f"   This is NOT the dimension MST predicts!")

    print("\n2. SKELETAL BOX-COUNTING RESULTS (D_skeleton)")
    skel_dims = [r['dimension'] for r in skeletal_results]
    print(f"   Mean D_skeleton = {np.mean(skel_dims):.3f} ± {np.std(skel_dims):.3f}")
    print(f"   This measures branching pattern complexity")
    print(f"   Expected for binary trees: D ≈ log(2)/log(γ^-1)")

    print("\n3. MASS-RADIUS ANALYSIS (D_mass) - THE TRUE MST TEST")
    mass_dims = [r['mass_dimension'] for r in mass_radius_results]
    print(f"   Mean D_mass = {np.mean(mass_dims):.3f} ± {np.std(mass_dims):.3f}")
    print(f"   MST predicts: D_mass = 3/2 = 1.500")

    # Proper statistical test
    from scipy.stats import ttest_1samp
    t_stat, p_val = ttest_1samp(mass_dims, 1.5)
    print(f"   t-test vs 1.5: t = {t_stat:.3f}, p = {p_val:.4f}")

    if p_val > 0.05:
        print(f"   → CONSISTENT with MST prediction ✓")
    else:
        diff = np.mean(mass_dims) - 1.5
        print(f"   → Differs from MST by {diff:+.3f}")

    print("\n4. KEY INSIGHT")
    print("   Different methods measure DIFFERENT dimensions!")
    print("   - DBC on grayscale → texture (D ≈ 2.1)")
    print("   - Skeleton box-count → branching pattern (D ≈ 1.3-1.7)")
    print("   - Mass-radius → resource distribution (D ≈ 1.5)")
    print("   Only mass-radius directly tests MST's metabolic prediction.")
```

---

## Summary of Changes Needed

1. **Cell after imports**: Add theoretical framework explaining dimension types
2. **New analysis methods**: Add `skeletal_box_count()` and `mass_radius_analysis()`
3. **Analysis cells**: Apply all three methods to each structure
4. **Results tables**: Show all three dimension types side-by-side
5. **Statistical validation**: Test mass-radius D against 1.5 (not DBC!)
6. **Conclusions**: Accurately describe what each method measures

## Why This Matters

The original notebook perpetuates a common error in the fractal ecology literature: using the wrong dimension measurement to test MST. Many papers report D ≈ 1.7-2.0 from box-counting and claim this validates (or refutes) MST, when they're measuring the wrong quantity entirely.

The mass-radius method is the correct approach because MST specifically predicts how *total branch mass scales with distance from the root*—this is the metabolically relevant quantity that determines how resources flow through the network.
