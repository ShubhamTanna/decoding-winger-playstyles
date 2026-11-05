# Portfolio research-data handoff — implemented schema 1.1.0

**Implemented in Phase 2B.** The curated release directory is `portfolio/web/`. A small Python exporter reads saved tables and an independent round-trip validator checks the result. It must not import notebook execution code, deserialize `.joblib` models, refit statistics or hand-transcribe numerical tables. The read-only preflight is implemented now in `scripts/validate_research_handoff.py`.

## Build and publication boundary

Implemented command interface (choose a new staging directory for each build):

```sh
python3 scripts/export_portfolio.py --data-root data/processed --output .local/web-build
python3 scripts/validate_portfolio.py --data-root data/processed --web-root .local/web-build
```

The exporter requires a nonexistent output directory, validate sources first, build in a temporary sibling directory, validate round trips, then rename the complete build into place. Failure must leave existing builds and research artifacts untouched. Use an explicit source registry, not recursive first-match filename discovery. Produce all eight agreed files in one build, without partial publication.

The user authorized publication of these eight curated outputs in Phase 2B. Safeguards now allow only those exact generated paths, with 6 MB and 3 MB caps for fingerprint and neighbour tables respectively; other files retain the 2 MB cap. Do not add generated CSVs with `git add -f`. The portfolio frontend belongs to a separate collaborator and is outside this repository task.

## Identifiers, ordering and serialization

- The observational key is the exact ordered triple `[player_id, squad, season]`. Require it to be unique and non-null. Preserve `player_id` as the footballer identifier; do not make a footballer ID from spell ID, name alone or row position.
- Define `spell_id = "spell_" + sha256(UTF-8(json.dumps([player_id, squad, season], ensure_ascii=False, separators=(",", ":")))).hexdigest()`. Use all 64 lowercase hex digits. Do not case-fold, strip accents, normalize club aliases or alter canonical strings before hashing. Validate uniqueness. Human display aliases are separate.
- Preserve `observation_row_idx` as the original 0-based research index for audits, never as the only join key. Before resolving index-based neighbours, require exact ordered equality of player/club/season keys across raw/scaled features, assignments, PCA scores and profiles. Resolve indices to spell IDs only after this check.
- Keep `spells.csv` in original observation order; fingerprints in observation order then final feature order; neighbours in target observation order then original rank; archetypes in C0–C4 order. Do not rerank ties or renumber clusters.
- UTF-8 CSV, comma separator, header, RFC-compatible quoting, LF line endings, no implicit dataframe index. Canonical identity strings are retained. Booleans serialize as `true`/`false`; numeric nulls as empty fields; required keys may never be null. Empty text and absent text must not be conflated in fields where that distinction matters; omit such optional free-text fields from v1.
- Use enough numeric precision for float64 round trips (for example 17 significant digits), never display-rounded values. Parse round trips explicitly with the schema. JSON uses finite numbers and `null`, never NaN/Infinity; disallow non-finite required numeric research values. Display rounding belongs to the UI.
- Deterministic builds must yield identical bytes for identical source/configuration. Do not inject wall-clock build timestamps; use source hashes, build version and commit identity. A timestamp, if later required, must be explicit and reproducible.

## Agreed files and field contracts

The paths abbreviated N04–N08 below are `data/processed/notebook_04_outputs/` through `notebook_08_outputs/`.

### `manifest.json`

An object containing:

- `schema_version` (`1.1.0`; the Phase 2A draft was `1.0.0`), `data_version` (explicit research release), `exporter_version` and `source_commit` (the latest full Git commit affecting the recorded build-input files, verified against their bytes; unrelated documentation/output commits do not change it), and `source_tree_dirty` (must be false for publication).
- `observational_unit = "player-club-season spell"`, `n_spells = 1396`, `n_players = 665`, `n_features = 20`, `n_clusters = 5`, `n_neighbours = 13960`, `n_fingerprint_rows = 27920`; season bounds and the five leagues.
- `feature_order`, `family_order`, method identifiers, minutes threshold and interpretation limitations, consolidated from the N06, N07 and N08 manifests and documented eligibility.
- `pca_variance`: original N05 variance rows, not recomputed PCA. `primary_similarity = "standardized_20d_euclidean"`, `top_k = 10`, `same_player_excluded = true`, retrospective full-period comparison scope.
- `archetype_colors` and `interaction_color` from the approved constants below; `featured_spells` with canonical keys, deterministic IDs and public display names.
- `sources`: repository-relative input names and SHA-256 hashes, never absolute local paths or private review contents. Hash all consumed manifests, feature specification, tables, dictionary/metadata configuration and validation expectations.
- `files`: schema/type/nullability specification, row counts and SHA-256 for the other seven files. Avoid a self-referential manifest hash; an external release checksum may cover the finished manifest.

Schema versions track field/meaning changes; data versions track source-artifact changes; exporter versions track transformation code. Do not silently change any of these under a published release ID.

### `features.csv` — 20 rows

Columns: `feature_order` (0-based integer), `feature`, `display_name`, `macro_family`, `formula`, `source_columns` (JSON array encoded as a CSV string), `denominator`, `unit`, `interpretation`, `limitations`, `family_weight` (float), `unit_status` (`verified_definition` or `unresolved_physical_unit`), `display_precision` (integer decimal places), `display_multiplier` (float) and `display_suffix` (string, possibly empty).

Order/family/weight come from N04 `winger_style_feature_specification.csv`; definitions come from [feature_dictionary.md](feature_dictionary.md), checked against Notebook 04. The exporter parses the reviewed Markdown dictionary as the single human-authored definition source. `interpretation` is the readable feature definition. Display metadata is derived by explicit rules: raw ratio shares multiply by 100 and display one decimal with `%`; distance displays one decimal without an assumed physical unit; other rates display two decimals. Stored raw values never use those display transformations. Formula units can be verified from code without proving a donor physical distance unit. `avg_shot_distance` must keep the unresolved-unit flag.

### `archetypes.csv` — 5 rows

Columns: `cluster_id` (integer 0–4), `label`, `color`, `n_spells` (integer), followed by the 20 feature columns in manifest order. Those numerical columns contain the original standardized centroid coordinates from N07 `winger_k5_centroids_standardized.csv`; labels come from the clustering manifest, counts from original assignments. No cluster-label alignment or remapping is applied to the primary model.

| ID | Color |
|---|---|
| C0 | `#b5608f` |
| C1 | `#d18b00` |
| C2 | `#00876a` |
| C3 | `#0068a8` |
| C4 | `#3d9fd6` |

`#ff0000` is reserved for selected observations and interaction. It is not an archetype color.

### `spells.csv` — 1,396 rows

Source: N08 `winger_player_profile_catalog.parquet`, checked against N07 assignments and N05 scores. Begin with `spell_id`, then these original fields in the listed order:

- Identity/context: `observation_row_idx`, `player_id`, `player`, `squad`, `comp`, `season`, `age`, `born`, `Minutes`.
- Primary assignment: `k5_cluster`, `archetype_name`, `k5_silhouette`, `k5_centroid_distance`, `k5_second_centroid_distance`, `k5_centroid_margin`.
- Projection: `PC1`, `PC2`, `PC3`, `PC4`, `PC5` (original primary coordinates).
- Robustness: `k5_family_balanced_aligned`, `k5_equal_player_weight_aligned`, `k5_extreme_trimmed_aligned`, `k5_label_preserved_all_three_tests`.
- Comparisons: `distance_to_cluster_0` through `distance_to_cluster_4`, `alternative_cluster`, `alternative_archetype_name`, `alternative_centroid_distance`, `centroid_distance_pct_within_cluster`.
- Nearest neighbour: generated `nearest_spell_id` (resolve `nearest_candidate_row_idx`), plus original `nearest_distance`, `nearest_distance_population_percentile`.

Identity/name/club/competition/season/archetype fields and generated IDs are strings; row indices, age, birth year, minutes and cluster IDs are integers; the stability flag is boolean; distances, margins, silhouette, PCA and percentile fields are floats. The saved `age` column is integer-valued with no missing entries; retain the source age convention without deriving a new age from dates. Require age/birth metadata and identity/model fields to be complete for this version; a future nullable variant requires an explicit schema change. Neighbour descriptive fields can be resolved through `nearest_spell_id`, avoiding redundant display aliases. K=2 assignments remain research diagnostics outside the v1 public spell schema.

### `fingerprint.csv` — 27,920 rows

Columns: `spell_id`, `feature`, `macro_family`, `raw_value`, `z_score`, `population_percentile`, `assigned_centroid_z`. Map N08 `winger_player_fingerprint_long.parquet` without recalculating exported values. Enforce one row per (spell, feature), exactly 20 per spell. All four measurements are finite floats. Percentiles are on a 0–100 scale using average ranks, not effectiveness scores.

### `neighbours.csv` — 13,960 rows

Columns: `target_spell_id`, `rank` (integer 1–10), `candidate_spell_id`, `distance` (float). Map N06 `top10_primary_euclidean.parquet` and preserve original distance values and rank. Require ten distinct candidate footballers per target and exclude every spell of the target footballer. Do not substitute PCA proximity, cosine distance, similarity percentages or sensitivity neighbours. For feature explanations the frontend can use the published z-score fingerprints; percentage contributions refer to squared distance, not similarity.

### `acceptance.csv`

A machine-readable validation ledger: `check_id`, `entity_id`, `field`, `expected` (canonical JSON scalar/array as a CSV string), `actual` (same encoding), `atol`, `rtol`, `passed` (boolean), `source_ref`. `entity_id` is a deterministic spell ID or named population invariant; `source_ref` is relative artifact/column evidence, not a machine path.

Include counts, identity uniqueness, feature order, cluster counts/labels, preserved PCA/distances, referential integrity, every featured spell's assignment and nearest neighbour, and representative fingerprint/percentile values for all three featured spells. Generate numerical expectations from the saved authoritative sources and compare them to independently reloaded website CSVs. Do not set expected and actual from the same in-memory output object. Require exact keys/ranks/labels and exact round-trip source floats where possible; use explicit `atol=1e-10`, `rtol=1e-10` only for independently recomputed arithmetic. Tolerances must never excuse changed serialized source values.

### `facts.md`

Generate a short public fact sheet from validated counts, PCA variance, mean saved silhouette and manifest limitations. Include historical scope, style-versus-quality warning, overlapping archetypes, retrospective neighbour scope and source attributions. Format display values only here; full-precision data stay in tables. Avoid manually copying large numerical tables into prose.

## Featured spells: actual saved profiles

The following exact keys uniquely resolve in the Notebook 08 catalogue. Public aliases must not alter these keys. Rounded distances below are orientation examples only; export full-precision saved values.

| Public name | Canonical player ID / club / season | Original index | Cluster | Nearest historical footballer | Distance |
|---|---|---:|---|---|---:|
| Vinícius Júnior | `Vinicius Júnior_2000` / `Real Madrid` / `2022-2023` | 1087 | C3 | Samuel Chukwueze, Villarreal, 2021–22 | 3.406777 |
| Neymar | `Neymar_1992` / `Paris S-G` / `2021-2022` | 930 | C4 | Philippe Coutinho, Barcelona, 2017–18 | 1.589447 |
| Raphinha | `Raphinha_1996` / `Leeds United` / `2020-2021` | 751 | C1 | Samu Castillejo, Milan, 2019–20 | 2.081936 |

Use all 20 saved fingerprint rows, primary neighbour rows, original PCA coordinates and assignment diagnostics for these profiles. Do not invent qualitative explanations from the selected names alone. A narrative should cite the actual high/low features and centroid comparisons from those records.

## Validation gates and release process

1. Run the read-only handoff validator and pin source hashes. The integer `age` field and Markdown definition source are resolved.
2. Run the isolated exporter and independent CSV/JSON schema validator. Do not deserialize models. Verify all source indices against identity keys before mapping IDs.
3. Check exact counts (1,396/665/20/5), feature order, five original assignments and centroid IDs, 27,920 fingerprints, 13,960 neighbours, unique spell keys, complete foreign keys and saved PCA/distance preservation. Recompute stored-pair distances as a separate diagnostic without reranking.
4. Verify percentiles against their correct reference populations; compare original centroid margins/robustness flags; resolve all three featured spells by exact key. Assert no infinite/NaN required values or accidental index columns.
5. Read the generated files back and compare to authoritative sources. Build twice in separate temporary directories and require byte-identical files. Add meaningful negative tests for reordered input identities, changed feature order, same-player neighbours, altered distances, duplicate IDs and missing source files.
6. Promote only the validated eight-file bundle to the authorized `portfolio/web/` directory and submit a development PR. Phase 2B must not be merged before review; no direct main write or frontend implementation is implied.


## Explicit Phase 2B contract resolutions

Schema 1.1.0 adds display precision/multiplier/suffix fields to the draft feature schema. It retains the acceptance ledger columns and extends their contents with ten `comparison_20d` rows plus population, integrity and featured-profile checks. It publishes no rounded analytical values: 17-significant-digit CSV serialization round-trips exactly; browser arithmetic uses absolute and relative tolerance 1e-10. Display precision is a UI recommendation, not an export-rounding operation.

Each comparison's `expected` and `actual` cells contain JSON objects with `target_spell_id`, `candidate_spell_id`, `distance` and `top3` (ordered `{feature, squared_contribution}` objects). Contributions are `(z_target - z_candidate)^2`; ties follow final feature order. Expected uses original saved standardized values; actual uses reopened website fingerprint rows. The ten pairs comprise the three featured players and their saved nearest neighbours, the three featured-to-featured combinations, the globally closest saved first-neighbour pair, Doku 2023–24 versus Vinícius 2022–23, Messi 2018–19 versus Neymar 2021–22, and Doku versus his most distant distinct footballer's spell. The final case uses one reference vector against the saved matrix; it neither refits a model nor alters any neighbour ranking. Case IDs and pair spell IDs are explicit in the ledger. The extra integrity rows hash canonical JSON numeric values with SHA-256; they are not browser distance cases.

The manifest's embedded CSV schemas define names, types, order and nullability; all v1.1 analytical fields are required and finite. Only `display_suffix` permits empty strings. `facts.md` is Markdown rather than a typed table. JSON is UTF-8, sorted keys, finite numeric values and no timestamps. Data release is `2017-2024.phase1-final.v1`; exporter version is `1.0.0`. Source/build hashes and the verified source commit distinguish exact releases. See [workflow and browser handoff](website_export_workflow.md).

## Visualization requirements verified on the full population

PCA bounds PC1 [-8.5, 12.5] and PC2 [-6.5, 7] contain all 1,396 spells. Observed ranges are PC1 [-7.810943, 11.998927] and PC2 [-5.948929, 6.688816]. The manifest records unrounded extrema and a zero overflow count. Five archetype colors must be visible immediately; selection uses the separate red indicator.

The prototype fingerprint axis [-3, 5] excludes 16 feature records. The observed player z-score range is [-4.229951, 9.426019]. The frontend must expand its domain to include every displayed player and centroid value, retaining true values in tooltips; it must not clamp or silently clip. Use archetype-colored player dots, open-diamond centroids, a grey ±1 standard-deviation band, the population mean at z=0 and red selected features. The exact bounds/counts are generated into `manifest.json`; this specification does not implement charts.
