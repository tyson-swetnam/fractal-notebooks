"""
fractal_review_utils.py
=======================
Shared utilities for the *reviewer companion* notebooks that accompany
Part II (Metabolic Scaling Theory and Biological Fractals).

These notebooks were written as a **critical-review apparatus**: they exist to
*test*, not merely illustrate, the paper's claims. The functions below therefore
try to make three things reproducible:

1. Pulling the empirical images/data from CyVerse (the author's private
   Data Store collection) using the *reader's own* iRODS credentials, with a
   deterministic synthetic fallback so the notebooks run before/without data.
2. Measuring fractal dimension two different ways -- binary box-counting
   (range 1..2) and Sarkar-Chaudhuri differential/grayscale box-counting
   (range 2..3) -- because the paper compares a value (~1.5) that is only
   coherent under the *binary* interpretation.
3. Stating the competing theoretical targets (3, 3/2, 4/3) explicitly so a
   notebook can show which prediction a measurement is actually being
   compared against.

Dependencies: numpy, scipy, matplotlib (the `fractal-foundations-gpu` conda env
in environments/ already has these). CyVerse pull additionally needs a working
`gocmd` or iRODS iCommands (`iget`) on PATH plus an authenticated session
(`iinit` / `gocmd init`).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Iterable

import numpy as np

# --------------------------------------------------------------------------- #
#  1.  CyVerse Data Store access
# --------------------------------------------------------------------------- #
# The paper's empirical inputs (x-ray leaves, branch/root scans, LiDAR canopy
# height models) live in the author's *private* collection:
DEFAULT_REMOTE = "/iplant/home/tswetnam/fractal-notebooks/data"

# NOTE FOR REVIEWERS / READERS:
#   A private iRODS collection is NOT reachable through a shared MCP connector
#   scoped to /iplant/home/shared.  It IS reachable by the data owner (or anyone
#   granted read access) running these cells locally after authenticating, e.g.
#       gocmd init          # or:  iinit
#   The helper below shells out to whichever client is installed and falls back
#   to synthetic data if the pull fails, so nothing here silently fabricates a
#   result and calls it "empirical".


def cyverse_pull(remote: str = DEFAULT_REMOTE,
                 local: str = "./data",
                 verbose: bool = True) -> tuple[str | None, str]:
    """Recursively fetch `remote` from the CyVerse Data Store into `local`.

    Returns (local_path_or_None, status_string).  Never raises: on any failure
    it returns (None, reason) so a notebook can branch to synthetic data.
    """
    os.makedirs(local, exist_ok=True)

    def _run(cmd: list[str]) -> tuple[bool, str]:
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            return p.returncode == 0, (p.stdout + p.stderr).strip()
        except FileNotFoundError:
            return False, f"{cmd[0]}: not installed"
        except subprocess.TimeoutExpired:
            return False, f"{cmd[0]}: timed out"

    # Prefer gocmd (the client this repo standardizes on), then iget.
    attempts: list[tuple[str, list[str]]] = []
    if shutil.which("gocmd"):
        attempts.append(("gocmd", ["gocmd", "get", "-f", remote, local]))
    if shutil.which("iget"):
        attempts.append(("iget", ["iget", "-rf", remote, local]))

    if not attempts:
        msg = ("No iRODS client found (looked for `gocmd` and `iget`). "
               "Install iCommands or gocmd and authenticate, then re-run.")
        if verbose:
            print("[cyverse_pull] " + msg)
        return None, msg

    for name, cmd in attempts:
        ok, out = _run(cmd)
        if ok:
            dest = os.path.join(local, os.path.basename(remote.rstrip("/")))
            dest = dest if os.path.exists(dest) else local
            if verbose:
                print(f"[cyverse_pull] OK via {name}: {remote} -> {dest}")
            return dest, f"pulled via {name}"
        if verbose:
            print(f"[cyverse_pull] {name} failed: {out.splitlines()[-1] if out else '?'}")

    return None, ("Pull failed with every available client. Most likely you are "
                  "not authenticated (`gocmd init` / `iinit`) or lack read "
                  "access to the collection.")


# --------------------------------------------------------------------------- #
#  2.  Synthetic fractals with *analytically known* dimension
#      (these are the controls the paper is missing)
# --------------------------------------------------------------------------- #
def fbm_surface(size: int = 512, H: float = 0.7, seed: int = 0) -> np.ndarray:
    """Fractional Brownian *surface* via spectral synthesis.

    A 2-D fBm surface embedded in 3-D has box/Hausdorff dimension

        D = 3 - H            (0 < H < 1  ->  2 < D < 3)

    so this is the ground truth for validating a *grayscale* estimator.
    Returns a float array in [0, 1].
    """
    rng = np.random.default_rng(seed)
    k = np.fft.fftfreq(size)
    kx, ky = np.meshgrid(k, k)
    kr = np.sqrt(kx ** 2 + ky ** 2)
    kr[0, 0] = 1.0
    # radial power spectrum P(k) ~ k^-(2H + E), E = 2 for a surface
    beta = 2 * H + 2
    amplitude = kr ** (-beta / 2.0)
    amplitude[0, 0] = 0.0
    phases = rng.uniform(0, 2 * np.pi, size=(size, size))
    spectrum = amplitude * np.exp(1j * phases)
    field = np.fft.ifft2(spectrum).real
    field -= field.min()
    if field.max() > 0:
        field /= field.max()
    return field


def fbm_surface_dimension(H: float) -> float:
    """Analytic box dimension of an fBm surface: D = 3 - H."""
    return 3.0 - H


def sierpinski_carpet(order: int = 5) -> np.ndarray:
    """Binary Sierpinski carpet; exact box dimension = ln 8 / ln 3 ~ 1.8928."""
    img = np.ones((1, 1), dtype=np.uint8)
    for _ in range(order):
        img = np.kron(img, np.ones((3, 3), dtype=np.uint8))
        img[1::3, 1::3] = 0
    return img


SIERPINSKI_CARPET_DIM = np.log(8) / np.log(3)  # ~1.8928


# --------------------------------------------------------------------------- #
#  3.  Estimators
# --------------------------------------------------------------------------- #
def _regress_loglog(sizes: np.ndarray, counts: np.ndarray) -> tuple[float, float]:
    """Return (dimension, r2) from N(s) ~ s^-D  ->  slope of log N vs log(1/s)."""
    x = np.log(1.0 / sizes)
    y = np.log(counts)
    A = np.vstack([x, np.ones_like(x)]).T
    slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    yhat = A @ np.linalg.lstsq(A, y, rcond=None)[0]
    ss_res = np.sum((y - yhat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(slope), float(r2)


def box_sizes(n: int, min_size: int = 2, factor: float = 2.0) -> np.ndarray:
    """Geometric ladder of box sizes up to ~n/2."""
    sizes, s = [], min_size
    while s <= n // 2:
        sizes.append(int(round(s)))
        s *= factor
    return np.unique(np.array(sizes, dtype=int))


def binary_box_count(binary: np.ndarray,
                     min_size: int = 2, factor: float = 2.0,
                     sizes: np.ndarray | None = None) -> dict:
    """Classic Minkowski-Bouligand box-count on a binary image.

    Dimension lives in [1, 2] for a plane-embedded set; this is the
    interpretation under which the paper's ~1.5 target is meaningful.

    Pass explicit `sizes` to align the box ladder with an object's natural
    scales (e.g. powers of 3 for a Sierpinski carpet); a *mismatched* ladder
    biases the estimate toward the embedding dimension -- itself a live
    illustration of why measurement choices matter for this paper's thesis.
    """
    b = (np.asarray(binary) > 0).astype(np.uint8)
    n = min(b.shape)
    if sizes is None:
        sizes = box_sizes(n, min_size, factor)
    sizes = np.asarray(sizes, dtype=int)
    sizes = sizes[(sizes >= 1) & (sizes <= n // 2)]
    counts = []
    for s in sizes:
        trimmed = b[: (b.shape[0] // s) * s, : (b.shape[1] // s) * s]
        blocks = trimmed.reshape(trimmed.shape[0] // s, s,
                                 trimmed.shape[1] // s, s)
        occupied = blocks.any(axis=(1, 3)).sum()
        counts.append(max(occupied, 1))
    D, r2 = _regress_loglog(sizes.astype(float), np.array(counts, float))
    return {"dimension": D, "r2": r2, "sizes": sizes, "counts": np.array(counts),
            "method": "binary box-count (range 1..2)"}


def differential_box_count(gray: np.ndarray,
                           min_size: int = 2, factor: float = 2.0,
                           levels: int = 256,
                           sizes: np.ndarray | None = None) -> dict:
    """Sarkar-Chaudhuri differential (grayscale) box-count.

    Treats intensity as a height surface; dimension lives in [2, 3].
    This is the "differential box count" named in the paper's Methods.
    """
    g = np.asarray(gray, dtype=float)
    g = g - g.min()
    if g.max() > 0:
        g = g / g.max() * (levels - 1)
    G = levels - 1
    L = min(g.shape)
    if sizes is None:
        sizes = box_sizes(L, min_size, factor)
    sizes = np.asarray(sizes, dtype=int)
    sizes = sizes[(sizes >= 1) & (sizes <= L // 2)]
    Ns = []
    for s in sizes:
        h = G * s / L                       # gray-box height (Sarkar-Chaudhuri)
        h = max(h, 1e-9)
        trimmed = g[: (g.shape[0] // s) * s, : (g.shape[1] // s) * s]
        blocks = trimmed.reshape(trimmed.shape[0] // s, s,
                                 trimmed.shape[1] // s, s)
        gmin = blocks.min(axis=(1, 3))
        gmax = blocks.max(axis=(1, 3))
        nr = np.floor(gmax / h) - np.floor(gmin / h) + 1.0
        Ns.append(max(nr.sum(), 1.0))
    D, r2 = _regress_loglog(sizes.astype(float), np.array(Ns, float))
    return {"dimension": D, "r2": r2, "sizes": sizes, "counts": np.array(Ns),
            "method": "differential/grayscale box-count (range 2..3)"}


# --------------------------------------------------------------------------- #
#  4.  The equivalence test the Results section asserts but never runs
# --------------------------------------------------------------------------- #
def tost_equivalence(sample: Iterable[float], target: float,
                     margin: float = 0.10, alpha: float = 0.05) -> dict:
    """Two one-sided tests (TOST) for *equivalence* to `target`.

    "Statistically indistinguishable from 3/2" is an equivalence claim and
    CANNOT be supported by a failure to reject a point null.  TOST is the
    correct test: reject non-equivalence only if the whole (1-2*alpha) CI of
    the mean falls inside [target - margin, target + margin].
    """
    from scipy import stats  # local import keeps module import cheap

    x = np.asarray(list(sample), dtype=float)
    n = len(x)
    mean, sd = x.mean(), x.std(ddof=1)
    se = sd / np.sqrt(n)
    df = n - 1
    low, high = target - margin, target + margin
    t_low = (mean - low) / se
    t_high = (mean - high) / se
    p_low = 1 - stats.t.cdf(t_low, df)       # H0: mean <= low
    p_high = stats.t.cdf(t_high, df)         # H0: mean >= high
    p_tost = max(p_low, p_high)
    tcrit = stats.t.ppf(1 - alpha, df)
    ci = (mean - tcrit * se, mean + tcrit * se)
    return {"n": n, "mean": mean, "sd": sd, "se": se,
            "target": target, "margin": margin,
            "ci_90": ci, "p_tost": p_tost,
            "equivalent": bool(p_tost < alpha and low <= ci[0] and ci[1] <= high)}


# --------------------------------------------------------------------------- #
#  5.  The competing theoretical targets, stated explicitly
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DimTarget:
    value: float
    where_from: str
    object_measured: str
    range_valid: str


THEORY_TARGETS = {
    "D=3 (space-filling network)": DimTarget(
        3.0,
        "WBE space-filling constraint N_k * l_k^3 = const  =>  D_H = ln n / ln(1/gamma) = 3",
        "the full 3-D branching network / exchange surface",
        "Hausdorff dim of the 3-D object, range 2..3"),
    "D=3/2 (projected silhouette)": DimTarget(
        1.5,
        "Methods eqns 15-17 as written: N(eps) ~ eps^(3/2) for a 2-D projection",
        "binary silhouette of the network projected to 2-D",
        "binary box-count, range 1..2"),
    "D=4/3 (Results, eqn '18')": DimTarget(
        4.0 / 3.0,
        "Results section: 'a differential mass dimension for such an image is "
        "expected to equal 4/3 rather than 3/2' -- source eqn not shown",
        "same projected image (contradicts the 3/2 target)",
        "binary box-count, range 1..2"),
}


def print_theory_targets() -> None:
    print("Competing theoretical targets the paper compares data against:\n")
    for name, t in THEORY_TARGETS.items():
        print(f"  {name:32s} value={t.value:0.4f}")
        print(f"      object : {t.object_measured}")
        print(f"      from   : {t.where_from}")
        print(f"      range  : {t.range_valid}\n")


# --------------------------------------------------------------------------- #
#  6.  Citation / DOI hygiene audit  (for the references companion)
# --------------------------------------------------------------------------- #
def audit_citations(rows: list[dict]) -> list[dict]:
    """Flag missing/placeholder/duplicate DOIs in a list of citation dicts.

    Each row: {"cite": str, "doi": str}.  Returns rows augmented with a
    "flags" list.  Pure string checks -- does not hit the network.
    """
    seen: dict[str, str] = {}
    out = []
    for r in rows:
        doi = (r.get("doi") or "").strip()
        flags = []
        if doi == "" or doi.lower() in {"xx", "doi:", "doi: "}:
            flags.append("missing/placeholder DOI")
        if "xx" in doi.lower():
            flags.append("placeholder token 'xx' in DOI")
        norm = doi.lower().replace("doi:", "").strip()
        if norm and norm in seen:
            flags.append(f"duplicate DOI shared with '{seen[norm]}'")
        elif norm:
            seen[norm] = r.get("cite", "?")
        out.append({**r, "flags": flags})
    return out
