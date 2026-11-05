# Phase 2B release validation

Completed 5 November 2026. Setup/documentation PR #2 was reviewed and merged at `f762ffc`; the website release is on `codex/phase2b-website-data-exports`, separate from main. No research models were fitted, notebook pipelines executed or historical analytical outputs regenerated.

## Release

- Schema: **1.1.0**; data: **2017-2024.phase1-final.v1**; exporter: **1.0.0**.
- Export-code source commit: `49ffbac379e98d7ffd7fb6a57b687c977cfacb95`. The release manifest verifies exact committed build inputs and has `source_tree_dirty: false`.
- Final directory: `portfolio/web/`, containing exactly the eight agreed files.
- Full saved Notebook 08 catalogue used; no compact-catalogue substitution or handcrafted numerical tables.
- Public IDs derive from SHA-256 of canonical `[player_id, squad, season]` JSON, not row numbers. Original indices remain in `spells.csv`.

## Results

| Check | Result |
|---|---|
| Population | 1,396 unique spell IDs and canonical keys; 665 footballers |
| Representation | 20 ordered features across eight families; five original cluster IDs/names/colors |
| Fingerprints | 27,920 rows; exact raw values, z-scores, saved average-rank percentiles and centroid values |
| Neighbours | 13,960 original records; complete ranks 1–10; valid spell references; ten distinct candidate footballers; target-footballer exclusion |
| Saved analytical values | Original assignments, PC1–PC5, centroid distances/margins, alternative assignments and robustness flags match exactly after CSV reload |
| Centroids | All five original 20-feature vectors preserved |
| Featured observations | Vinícius Júnior / Real Madrid / 2022–23 → C3; Neymar / Paris S-G / 2021–22 → C4; Raphinha / Leeds United / 2020–21 → C1; resolved by exact key and exposed by public spell ID |
| Acceptance ledger | 31 rows, including exactly ten meaningful 20D comparisons with top-three squared contributions, population/integrity checks and all three featured profile/percentile cases |
| Numerical precision | 17-significant-digit CSV serialization; exact float64 source round trips, no premature rounding; independent arithmetic atol=rtol=1e-10 |
| JavaScript replay | All ten cases passed using Number arithmetic; maximum observed absolute discrepancy 8.881784197001252e-16 for distance/contribution checks |
| Determinism | Two clean exports of the same committed inputs produced byte-identical contents for all eight files, including manifest and facts |
| Preservation | Every local file under data/ remains byte-identical to the preserved research snapshot, including raw inputs, completed manual decisions, model binaries and processed outputs; notebooks, MIT license and requirements are unchanged |

The independent validator reopens files with explicit types, compares them to saved sources, validates all provenance/file hashes, and checks the recorded source commit. Its `expected` acceptance values come from original standardized data; `actual` values come from reloaded public fingerprints. Browser replay used only public fingerprint/acceptance contents, without notebooks or private research data. It verifies JavaScript arithmetic, not any frontend UI or CSV library implementation.

Nine integration tests passed, including ten semantic-corruption subcases. They cover exact build determinism/round trips, missing inputs/outputs, refusal to overwrite releases, reordered source identities/features and cleanup after validation failure. Corruptions to distances, same-player neighbours, ranks, foreign keys, percentiles, PCA, duplicate spell IDs, centroids, CSV headers and acceptance expectations were rejected even after checksums were recomputed. Source hashes before and after tests agree.

## Payload sizes

Bytes are exact for this release. Gzip estimates use level 9 and deterministic headers, calculated separately for each file; actual CDN transfer sizes can differ. No compressed duplicates are committed.

| File | Bytes | Estimated gzip bytes |
|---|---:|---:|
| `acceptance.csv` | 21,078 | 3,221 |
| `archetypes.csv` | 2,727 | 1,432 |
| `facts.md` | 6,439 | 2,875 |
| `features.csv` | 7,956 | 2,139 |
| `fingerprint.csv` | 5,068,111 | 1,011,610 |
| `manifest.json` | 22,827 | 4,729 |
| `neighbours.csv` | 2,275,340 | 702,890 |
| `spells.csv` | 903,010 | 388,285 |
| **Total** | **8,307,488** | **2,117,181** |

The fingerprint and neighbour tables dominate the payload. Consumers can load them only when needed after the manifest, facts and spell catalogue; this is a frontend consideration, not an implementation in this repository.

## Visualization validation

Prototype PCA limits PC1 [-8.5, 12.5], PC2 [-6.5, 7] contain every spell. Actual ranges are PC1 [-7.810943, 11.998927], PC2 [-5.948929, 6.688816].

There are **16 feature records** outside the prototype fingerprint interval [-3, 5]; full observed z-score range is [-4.229951, 9.426019]. The contract requires axis expansion to include all displayed player/centroid values, never silent clipping. Dots use archetype colors, centroids open diamonds, reference band grey ±1, population mean zero and selected features red. Full-precision bounds are in the manifest.

## Publication safeguards and limits

The user authorized these exact eight curated outputs. `.gitignore`, `AGENTS.md` and the publication allowlist reflect that narrow exception; arbitrary raw/intermediate files and generated extras remain prohibited. The only size-limit exceptions are 6 MB for `portfolio/web/fingerprint.csv` and 3 MB for `portfolio/web/neighbours.csv`; other paths keep the 2 MB cap. Staged release checks verify the complete bundle, hashes, byte sizes, clean-build marker and code-source consistency, alongside existing credential/notebook checks.

The physical unit of `avg_shot_distance` remains unresolved and is labeled accordingly. Original download dates/versions and clean-environment notebook reproduction remain historical limitations. These do not prevent consuming the versioned public bundle. No new model claim, new statistical experiment, frontend implementation or deployment is included. Phase 2B is not merged into main; its files and results await review.

## Release file integrity

The manifest contains these hashes and each CSV's ordered field/type/nullability schema. It intentionally excludes a self-hash; byte-identical build comparison includes the manifest itself.

| File | SHA-256 |
|---|---|
| `acceptance.csv` | `6841b49924cc0bf8881e9ba1793e508d6c81bebaa2d2e022236b84b802176b9d` |
| `archetypes.csv` | `9123c8cc0a1df31935c456cbcc19772c2e654e111a3caf7a65189b7514a4a1d6` |
| `facts.md` | `0046b14d55ab93899f3ae73a77d02418e1d816bf9f972368d1e90e9ca8f8d5a9` |
| `features.csv` | `e0f5f15e770e09f3714924f3684868d972d19dd1a4e942329af332591d962d76` |
| `fingerprint.csv` | `f7ac11b4d731304d3ac790e6c898f3b760bc95c8191038a7b4bc8c75db90bbd1` |
| `neighbours.csv` | `485ae88f1ce260c470da4ebccaeec68537f3c8b58a7fe9b73bf476a7034368d1` |
| `spells.csv` | `1b0c8344345ee5f6e00cf92e6f5b9970b108d3aa1fcc016581b62930183eb291` |

See [build and browser workflow](website_export_workflow.md) and [schema specification](portfolio_export_architecture.md) for reproduction and consumption instructions.
