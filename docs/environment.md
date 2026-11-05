# Notebook environment and execution boundaries

## Status

`requirements.txt` is a minimal notebook dependency set plus its resolved transitive dependencies, pinned for a **candidate Python 3.12 environment**. Dependency metadata resolution succeeded on macOS arm64 using Python 3.12.14. The complete environment was **not installed or runtime-tested**, and Linux/Colab compatibility has not been validated. This is not a claim to have recovered the original Colab environment.

Evidence recovered from existing artifacts:

| Package | Version | Evidence |
|---|---|---|
| scikit-learn | 1.6.1 | All six saved model/scaler artifacts contain this version; Notebook 07 manifest agrees |
| pandas | 2.2.3 | Metadata in all 15 Parquet exports |
| PyArrow | 23.0.1 | Original writer metadata in all 15 Parquet exports before closeout; enriched Parquet rewritten with 26.0.1 for the provenance-only correction |

NumPy 2.3.5 and openpyxl 3.1.5 were available in the audit runtime. Their original research versions are unknown. Other pins were selected by dependency resolution for the candidate environment, not inferred as historical versions. The authorized isolated inspection used PyArrow 26.0.1; the candidate specification retains the original writer version 23.0.1.

Direct dependencies reflect actual imports and file readers: NumPy, pandas, SciPy, scikit-learn, Matplotlib, RapidFuzz, joblib, openpyxl, PyArrow and IPython. Standard-library modules need no packages. Colab supplies the notebook host and `google.colab`; do not install a replacement `google.colab` package locally. A separate Jupyter UI is optional and is not part of the analytical requirements.

## Future setup (not executed during cleanup)

In a separate environment, after approval:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Record the resulting Python/package versions and validate existing artifacts before executing research cells. For Colab, use a separate session and verify its Python version and platform compatibility before installing these pins. Restart the runtime after changing binary-library versions. Do not treat successful dependency resolution as proof of numerical reproduction.

## Existing notebook workflow

The notebooks were written for manually staged Colab files. Phase 1 deliberately does not refactor their paths:

- Notebook 01 expects seven seasonal CSVs in its working directory.
- Notebook 02 expects the audited CSV, FIFA CSV and both **completed** review CSVs there.
- Notebook 03 explicitly reads the winger CSV and donor XLSX from `/content/`.
- Notebook 04 reads the enriched Parquet from its working directory and writes under `/content/decoding_winger_playstyles/`.
- Notebooks 05–08 expect manually staged upstream artifacts under `/content/`.
- Colab ZIP/download cells are optional convenience steps and should be skipped outside Colab.

Notebook 02's existing RapidFuzz installation cell is a Colab convenience; preinstall the pinned dependency and skip that cell in a managed environment. Blank review templates now have distinct `*_template.csv` names and use exclusive creation. Missing authoritative review files raise an explicit error; templates are never substituted for reviewed decisions.

Do not use Run All merely to test this specification: notebooks 04, 05 and 07 fit models and export results. A path-portability pass and controlled clean-kernel validation remain future work.

## Preserved analytical artifacts and closeout corrections

Phase 1 closeout synchronized the two enriched CSV percentage columns (`Take-Ons_Succ%` and `Take-Ons_Tkld%`) to the existing numeric Parquet values. Their numerical values and missingness did not change. Neither field feeds the final 20 features or the exported supporting descriptors.

Lamine Yamal's existing Barcelona 2023–2024 RW classification now retains `position_source = "Manual override"` in the winger CSV and both enriched exports, matching corrected Notebook 02 logic. No eligibility, position, identity or attacking-statistic value changed. The enriched Parquet was rewritten using the authorized isolated PyArrow 26.0.1 runtime; every other column and schema metadata were verified unchanged. The candidate requirements retain the original writer version 23.0.1.

All Notebook 04–08 analytical artifacts and all manual review input files remain byte-identical to their pre-closeout versions. Saved notebook outputs were not refreshed. Notebook 08 display code uses the export's average-rank percentile convention. Ordinary CSV type inference can still read manual-position boolean text differently from Parquet's string schema; this is not a changed decision.
