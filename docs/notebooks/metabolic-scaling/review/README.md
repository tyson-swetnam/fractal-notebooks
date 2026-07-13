# Reviewer companion notebooks — Part II (Metabolic Scaling)

These notebooks accompany a **critical review** of the Part II manuscript
(`docs/metabolic-scaling/`). Unlike the tutorial notebooks one level up
(`1_introduction` … `5_empirical_validation`), these exist to **test** the
paper's claims section by section. The full referee report is
[`REVIEW_metabolic-scaling.md`](../../../../REVIEW_metabolic-scaling.md) at the
repo root.

| Notebook | Section | What it checks |
|---|---|---|
| `abstract_companion.ipynb` | Abstract | claims → falsifiable hypotheses; reviewer scorecard; CyVerse bootstrap |
| `introduction_companion.ipynb` | Introduction | the missing estimator-bias control (fBm of known `D = 3 − H`, both estimators) |
| `methods_companion.ipynb` | Methods | exact re-derivation; flags broken/missing equations; reconciles 3 vs 3/2 vs 4/3 |
| `results_companion.ipynb` | Results | binary vs grayscale dimension; synthetic controls; TOST equivalence test; empirical pull |
| `discussion_companion.ipynb` | Discussion | DLA/Eden/KPZ vs self-affine; the (un)falsifiable MEP claim; the 3/4-vs-2/3 omission |
| `conclusion_companion.ipynb` | Conclusion | decision table: what each conclusion still needs |
| `references_companion.ipynb` | References | programmatic DOI/citation audit |

## Running them

```bash
# from a conda env with the scientific stack (see environments/fractal-foundations-gpu.yml)
cd docs/notebooks/metabolic-scaling/review
jupyter lab            # or: jupyter notebook
```

Launch Jupyter **from this folder** so `import fractal_review_utils` resolves
(the notebooks add the working directory to `sys.path`). Shared logic —
estimators, the CyVerse pull, the equivalence test — lives in
`fractal_review_utils.py`.

## Data (CyVerse Data Store)

The empirical cells fetch the author's private collection:

```
/iplant/home/tswetnam/fractal-notebooks/data/
```

Authenticate first with your **own** iRODS credentials:

```bash
gocmd init      # or:  iinit
```

The pull uses `gocmd` (preferred) or `iget`. If it fails — no client, not
authenticated, or no read access — the notebooks **fall back to deterministic
synthetic objects and say so**. Nothing is silently presented as "empirical."

> A private iRODS collection is not reachable through a shared MCP connector
> scoped to `/iplant/home/shared`; it is reachable by the data owner (or anyone
> granted access) running these cells locally after authenticating.
