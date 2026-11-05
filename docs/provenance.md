# Source and artifact provenance

This record identifies local evidence and uncertainty. It does not reconstruct missing download history or authorize redistribution. Data and executed notebooks are private local inputs, excluded from Git; the MIT license does not replace third-party source terms.

## Source inputs

All filenames below are relative to ignored `data/raw/`.

| Source | Local files and coverage | Attribution and uncertainty |
|---|---|---|
| Initial FBref-derived statistical data | `2017-18.csv`, `2018-19.csv`, `2019-20.csv`, `2020-21.csv`, `2021-22.csv`, `2022-23.csv`, `2023-24.csv`; five major European leagues | Likely original distribution: [Akshan Krithick's Kaggle dataset](https://www.kaggle.com/datasets/akshankrithick/fbref-2017-2024-for-europes-top-5-leagues). The original download date/version and exact file-to-version link are not recovered. Notebook 01 documents the audit and column renames. |
| Additional FBref-derived statistics | `Top5_League_Players_2017to2024_dataset.xlsx` (Notebook 03 input), plus a local `.csv` counterpart | [Emre Yılmaz's Kaggle dataset](https://www.kaggle.com/datasets/emrey3lmaz/top-5-league-football-player-stats-2017-2025) is the supplied enrichment source. Its current title spans 2017–2025; the project selects 2017–18 through 2023–24. A filename is not proof of the complete donor coverage or exact download version. Original date/version is unknown. |
| Historical FIFA/SoFIFA positions | `male_players.csv`; Notebook 02 uses FIFA editions 18–24 | Fields include FIFA player ID, names, date of birth, edition, club, primary player position and club position. The precise distribution URL, edition snapshots and download date are not established locally. FIFA classification is auxiliary positional evidence, not the footballer's statistical performance source. |
| Completed identity decisions | `identity_matches_for_review.csv` | Authoritative reviewed identities, not an automatically generated result. Blank `*_template.csv` files are not substitutes. Do not publish or overwrite the completed review table. |
| Completed positional decisions | `manual_position_overrides.csv`, plus the explicit Notebook 02 Yamal override | Preserve existing classifications and recorded evidence. Missing notes/links are provenance limitations; do not invent historical verification sources or infer extra evidence from a current webpage. |

Source pages were checked on 5 November 2026. Kaggle pages exposed no readable field dictionary through the research tool; FBref's shooting table returned HTTP 403. The local `Standard_Dist` physical unit remains unresolved. See [feature dictionary](feature_dictionary.md). These access results do not prove that source documentation does not exist.

## Authoritative processed artifacts

Paths are under ignored `data/processed/`. The folders identify their producing notebooks; current copies are preserved research results, not new Phase 2 exports.

| Folder | Artifact(s) | Authority and downstream use |
|---|---|---|
| `notebook_01_-_03_outputs/` | `fbref_2017_2024_audited.csv` / `.parquet` | Audited source statistics and corrected footballer identifiers; input to population construction. |
| Same | `fbref_2017_2024_wingers.csv` | Authoritative selected population. Enrichment must not redefine eligibility. |
| Same | `fbref_2017_2024_wingers_enriched.parquet` | Preferred typed input to Notebook 04. Matching CSV is a convenience representation with synchronized percentages/provenance. |
| `notebook_04_outputs/` | `winger_style_feature_specification.csv`, `winger_style_feature_decisions.csv` | Final feature order/families/weights and decisions; formulas remain in Notebook 04. |
| Same | `winger_style_features_raw.parquet`, `winger_style_features_scaled.parquet`, `winger_style_features_family_balanced.parquet` | Raw final features, primary standardized space and sensitivity space. CSV counterparts exist. Supporting descriptors are separate from modelling features. |
| `notebook_05_outputs/` | `pca_primary_scores.parquet`, `pca_primary_coefficients.csv`, `pca_primary_variance.csv` | Original primary projection, coefficient matrix and explained variance. Balanced exports and diagnostics are sensitivity evidence. |
| `notebook_06_outputs/` | `top10_primary_euclidean.parquet`, `similarity_manifest.json` | Original ten distinct-footballer neighbours per spell and primary metric/rules. Balanced Euclidean and standardized Manhattan tables are alternatives, not replacements. |
| `notebook_07_outputs/` | `winger_k5_profile_assignments.parquet`, `winger_k5_centroids_standardized.csv`, `winger_clustering_manifest.json`, `winger_clustering_robustness.csv` | Original K=5 assignment IDs, centroids, labels, fit settings and completed sensitivity comparisons. |
| `notebook_08_outputs/` | `winger_player_profile_catalog.parquet`, `winger_player_fingerprint_long.parquet`, `winger_player_profiles_manifest.json` | Authoritative full player profiles, 20-feature fingerprints and interpretation metadata. `winger_player_profile_catalog_compact.csv` is a reduced convenience view. |

Fitted `.joblib` objects remain private historical evidence. The proposed website process need not deserialize them: saved coordinates, centroids, assignments and distances are already available. Preserve original IDs and coordinates; do not relabel clusters or fit replacements during export.

## Known corrections and evidence preservation

Notebook 01 documents player-ID collision handling. Notebook 03 documents the donor name aliases and Douglas Costa assist correction. Phase 1 fixed implementation/documentation issues and synchronized enriched CSV percentage encodings without changing values; it also propagated Yamal's existing RW provenance into the winger CSV and both enriched files. None of these closeout changes altered the final 20 features or downstream analytical outputs.

The canonical local workspace holds `.local/research-snapshot/` with executed evidence and `.local/research-sha256.json` with original file hashes. Publication notebooks preserve approved source while removing outputs, execution counts and embedded state. Existing older Git history may still contain executed outputs; setup did not rewrite that history. Never treat a cleaned public notebook's lack of outputs as evidence that the research was not executed.

## Future export provenance

Each export build should record schema/data/build versions, source commit, source artifact SHA-256 hashes, ordered feature list, population scope, method identifiers, approved colors and featured spell keys. Do not include absolute machine paths, private review contents or invented original download dates. Preserve the source spell key (`player_id`, `squad`, `season`) alongside deterministic web IDs and original observation indices; hashes identify the exact local artifact consumed, not its licensing status or original download provenance.
