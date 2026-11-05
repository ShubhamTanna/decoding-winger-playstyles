# Decoding Winger Playstyles — verified website facts

## Scope and methods

The historical population contains **1,396 player-club-season spells** from **665 distinct footballers**, covering 2017–18 through 2023–24 in the Premier League, La Liga, Bundesliga, Serie A and Ligue 1. Source: `notebook_08_outputs/winger_player_profile_catalog.parquet`, identity and season fields.

Eligibility requires at least **1,125 minutes per spell** and LW/RW/LM/RM eligibility from historical primary or club positions, supplemented by completed manual verification. Source: Notebook 02, minutes filter and final positional selection (see `docs/methodology.md`). A transferred player can contribute separate club spells; a spell is not a unique footballer.

Feature selection follows **27 → 21 → 20**: initial candidates, provisional features, then the final 20 features across eight families. Notebook 04 cell 226 removes `progressive_distance_per_carry` because of overlap with progressive-carry volume and share. Formulas are in `features.csv` and `docs/feature_dictionary.md`; `cross_pass_share` uses donor `Total_Att`. Average shot distance remains source-reported distance with its physical unit unresolved.

PCA variance: PC1 **35.56%**, PC2 **19.32%**; first five PCs **85.23%** cumulatively. Source: `notebook_05_outputs/pca_primary_variance.csv`. The map preserves saved coordinates; it is not the primary distance metric.

Primary similarity is Euclidean distance across all 20 globally standardized features. Each spell has ten nearest distinct footballers, excluding all spells of the target footballer: **13,960 neighbour records**. Source: `notebook_06_outputs/top10_primary_euclidean.parquet` and `similarity_manifest.json`. The retrospective pool includes the entire study period; distances are not similarity percentages or time-safe scouting forecasts.

The profile export contains **27,920 feature-level fingerprint records**. Percentiles use average ranks over all 1,396 spells, not equal weight per footballer. Source: `notebook_08_outputs/winger_player_fingerprint_long.parquet` and the profile manifest.

## Working descriptive archetypes

| Cluster | Name | Spells | Color |
|---|---|---:|---|
| C0 | Penalty-area attacking and shooting | 352 | `#b5608f` |
| C1 | Crossing-oriented wide play | 291 | `#d18b00` |
| C2 | Deeper passing progression | 278 | `#00876a` |
| C3 | Direct carrying and dribbling | 266 | `#0068a8` |
| C4 | Advanced creative progression | 209 | `#3d9fd6` |

Mean saved silhouette: **0.149190**. Source: the Notebook 07 assignments and Notebook 08 catalogue; labels and settings: `winger_clustering_manifest.json`. K=5 is a working descriptive model, not an objectively optimal natural classification. Boundaries overlap; centroid margins are geometric diagnostics, not membership probabilities.

## Completed robustness experiments

| K=5 sensitivity test | Adjusted Rand index | Matched agreement |
|---|---:|---:|
| family_balanced | 0.831241 | 92.406877% |
| equal_player_weight | 0.708791 | 87.320917% |
| extreme_trimmed | 0.911529 | 96.060172% |

Source: `notebook_07_outputs/winger_clustering_robustness.csv`. Tests use family-balanced features, equal total weight per footballer and exclusion of observations above the 99th percentile of standardized-vector norm during the alternative fit. Original assignments remain authoritative. These are completed research findings, not models fitted by the website exporter.

## Featured historical profiles

### Vinícius Júnior — Real Madrid, 2022-2023

Spell: `spell_5143b9463bb9693f1e7cd49451fa3bc3df4cb506479ea119f6247406dbf5cb9c`. Canonical key: `Vinicius Júnior_2000` / `Real Madrid` / `2022-2023`.

Primary archetype: **C3 — Direct carrying and dribbling**. Recorded minutes: **2,823**. Closest historical footballer: **Samuel Chukwueze**, Villarreal, 2021-2022; Euclidean distance **3.406777**. Source: `notebook_08_outputs/winger_player_profile_catalog.parquet` and the primary neighbour export. Join this spell ID to `spells.csv`, all 20 rows in `fingerprint.csv` and its ten rows in `neighbours.csv`; do not hardcode an observation index.

### Neymar — Paris Saint-Germain, 2021-2022

Spell: `spell_8f1bd18729e941a5a3b6e8e434c221d40faf98b740eff059b4d4b86ee42fce00`. Canonical key: `Neymar_1992` / `Paris S-G` / `2021-2022`.

Primary archetype: **C4 — Advanced creative progression**. Recorded minutes: **1,851**. Closest historical footballer: **Philippe Coutinho**, Barcelona, 2017-2018; Euclidean distance **1.589447**. Source: `notebook_08_outputs/winger_player_profile_catalog.parquet` and the primary neighbour export. Join this spell ID to `spells.csv`, all 20 rows in `fingerprint.csv` and its ten rows in `neighbours.csv`; do not hardcode an observation index.

### Raphinha — Leeds United, 2020-2021

Spell: `spell_af120efe7bfdf9052622057e5dd0d673725a3cd20a45666797aa2c7bf7136542`. Canonical key: `Raphinha_1996` / `Leeds United` / `2020-2021`.

Primary archetype: **C1 — Crossing-oriented wide play**. Recorded minutes: **2,360**. Closest historical footballer: **Samu Castillejo**, Milan, 2019-2020; Euclidean distance **2.081936**. Source: `notebook_08_outputs/winger_player_profile_catalog.parquet` and the primary neighbour export. Join this spell ID to `spells.csv`, all 20 rows in `fingerprint.csv` and its ten rows in `neighbours.csv`; do not hardcode an observation index.

## Interpretation and sources

These measurements describe attacking style, not player quality, finishing ability, team fit or recruitment success. Team context, source definitions and repeated seasons affect the population. Feature values are not clipped; display formatting must not alter stored data. Selection uses red `#ff0000`, never a sixth archetype color.

Statistical attribution: [likely initial Kaggle distribution](https://www.kaggle.com/datasets/akshankrithick/fbref-2017-2024-for-europes-top-5-leagues) and [enrichment distribution](https://www.kaggle.com/datasets/emrey3lmaz/top-5-league-football-player-stats-2017-2025), both FBref-derived. Auxiliary positions use historical FIFA/SoFIFA and completed manual decisions. Original download versions/dates are not fully established; see `docs/provenance.md`. Relative research source paths in this fact sheet refer to private artifacts whose hashes are recorded in `manifest.json`; consuming these website files does not require access to those private sources.
