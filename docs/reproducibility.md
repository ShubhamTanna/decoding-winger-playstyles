# Reproducibility and execution boundaries

The research is complete through Notebook 08. A fresh clone contains publication notebook sources and a **provisional** Python 3.12 requirements file, not the private inputs, fitted models or executed outputs. Dependency metadata resolution passed; a full clean-environment run has not. See [environment](environment.md) for recovered version evidence and the remaining Colab path requirements.

## Read-only validation of saved research

With an existing environment containing NumPy, pandas and a pandas-compatible Parquet reader (PyArrow was used for this handoff), from the repository root run:

```sh
python3 scripts/validate_research_handoff.py
```

The command requires the ignored local `data/processed/` artifacts and public notebooks/docs. Missing dependencies or files are reported; nothing is downloaded or reconstructed. It prints a JSON validation summary, writes no artifacts, loads no model binaries and fits no models. Optional private logging can redirect stdout to `.local/` after creating that directory. Do not commit the log or underlying datasets.

Checks establish consistency of saved artifacts and documented claims, not a fresh execution of identity matching, source cleaning or model fitting. The current handoff validation used an already available inspection runtime; it does not validate every package in `requirements.txt` or certify Colab compatibility.

## Controlled pipeline execution (not performed for Phase 2A)

1. Obtain authorized copies of the sources in [provenance](provenance.md), including the **completed** identity and positional review tables. A public clone alone is insufficient.
2. Use an isolated environment/output location. Consult `docs/environment.md` before dependency installation. Record Python/platform/package versions; test the provisional requirements on the intended platform rather than claiming the original Colab environment was recovered.
3. Stage each notebook's inputs at its actual working-directory or `/content/` paths. The table below is an input map, not a portability refactor. Do not point output cells at preserved research artifacts.
4. Run notebooks in sequence only as an explicitly authorized reproduction task. Review manual-input gates; never substitute blank templates or overwrite completed decisions. Colab-only download cells are optional outside Colab.
5. Compare new outputs against preserved artifacts: ordered identity keys, population, exact feature definitions/order, numeric tolerances and model diagnostics. PCA sign choices and cluster-label permutations may differ in a new fit; they must not silently replace the historical website semantics.

| Order | Required inputs | Main outputs |
|---|---|---|
| 01 | Seven seasonal CSVs, `2017-18.csv` through `2023-24.csv`, in working directory | Audited CSV and Parquet |
| 02 | Audited CSV, `male_players.csv`, completed `identity_matches_for_review.csv` and `manual_position_overrides.csv` | Selected winger CSV; separately named review templates |
| 03 | Winger CSV and `Top5_League_Players_2017to2024_dataset.xlsx` under `/content/` | Enriched CSV and typed Parquet |
| 04 | Enriched Parquet in working directory | Final raw/scaled/balanced features, specification, decisions, supporting descriptors and scaler under `/content/decoding_winger_playstyles/` |
| 05 | Notebook 04 artifacts manually staged under `/content/` | Primary/balanced PCA scores, coefficients, variance, diagnostics and fitted PCA objects |
| 06 | Notebook 04 feature/specification artifacts staged under `/content/` | Primary and sensitivity neighbour tables, explanation diagnostics and manifest |
| 07 | Notebook 04 representations/specification, Notebook 05 PCA scores plus `pca_primary.joblib`, and Notebook 06 neighbours under `/content/` | Assignments, centroids, robustness, model objects and manifest |
| 08 | Notebook 04 features/specification, Notebook 06 primary neighbours, Notebook 07 assignments/centroids/model/manifest under `/content/` | Full/compact profile catalogues, fingerprints and manifest |

The final pipeline depends on manually staged intermediates as well as the raw data. The saved artifact hierarchy in `data/processed/` organizes evidence locally; notebooks do not automatically discover that hierarchy. The planned website exporter should consume saved tables directly and avoid notebook execution altogether.

## Determinism and limits

The primary K-Means fit records seed 42, 30 initializations and 500 maximum iterations. Exploratory displays can sample rows without a fixed seed; their visual order is not an analytical output contract. PCA uses `PCA()` without an explicit solver/seed, so retain saved coordinates and record the actual environment before any future fit. Floating-point/library differences and historical source revisions are additional reproducibility limits.

Feature scaling and percentiles use all spell observations, with repeated footballers retained. The saved nearest-neighbour order is part of the handoff contract. A deterministic web identifier should derive from exact canonical identity strings, not transient row positions or translated display names.

## Publication workflow

Follow [local workflow](local-workflow.md). After staging explicit approved source paths:

```sh
python3 scripts/check_publication.py
git diff --cached --check
git diff --cached --stat
```

The path allowlist is extended only for the new documentation and read-only validation script. Datasets, raw sources, generated website exports, models, private snapshots, backups and credentials remain excluded. Public notebook sources and existing model outputs are not modified by Phase 2A.
