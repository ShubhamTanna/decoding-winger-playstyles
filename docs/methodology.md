# Research methodology

This describes the completed research in notebooks 01–08. It separates implemented methods from claims that require a new run. Cell references are zero-based. [Reproducibility](reproducibility.md) lists input and execution requirements; [provenance](provenance.md) identifies authoritative artifacts.

## Population and preprocessing — notebooks 01–03

Notebook 01 concatenates seven seasonal statistical files, corrects misleading names (including total minutes), checks arithmetic/duplicate columns and removes redundant fields. Footballer identity begins with name plus birth year, with a documented correction for two different Vitinhas born in 2000. Club-season spells remain separate; apparent repeated player-season rows are not automatically duplicates.

Notebook 02's final identity matcher pools FIFA editions 18–24 by footballer, restricts candidates by birth year and compares normalized name aliases. Club-history similarity breaks ties. A unique best name score of 100 is accepted automatically; other eligible identities use the completed review table. The earlier season-specific matcher is exploratory, not the final identity procedure (cell 14). Resolved identities receive season-to-edition positional information. LW/RW/LM/RM in either primary or club position qualifies; missing classifications use completed manual decisions. The minimum is 1,125 minutes **per spell**. The explicit Lamine Yamal 2023–24 RW override retains `Manual override` provenance (cells 56–57, 63).

Notebook 03 normalizes donor identity keys, filters relevant coverage, resolves Bobby Reid/De Cordova-Reid and Mohammed/Mohamed Daramy aliases, and uses a validated one-to-one left join on normalized player, birth year, season and club. The original 1,396-spell population is authoritative, with complete donor match coverage. Overlapping statistics are audited rather than indiscriminately replaced. The documented Douglas Costa Juventus 2017–18 assist correction also updates its derived totals/rate (cells 86–88); it is an existing decision, not a new Phase 2 inference. Decimal commas and numeric types are normalized. Enriched Parquet is the downstream input; small remaining cross-source disagreements are retained.

## Features and standardization — notebook 04

The [dictionary](feature_dictionary.md) specifies every retained source column and denominator. Per-90 rates use spell minutes; shares and per-100 rates use positive denominators, otherwise missing. The final saved matrices are finite. Source alignment matters: crossing and long-pass shares divide donor numerators by donor `Total_Att`.

The documented selection is **27 candidates → 21 provisional → 20 final features**. Screening considers interpretation, sparsity, denominator reliability, temporal patterns and correlations. Cell 226 excludes `progressive_distance_per_carry` because it overlaps strongly with progressive-carry volume and share. Related volume/propensity pairs remain when they express different aspects of behaviour. Quality/output descriptors remain outside the style matrix.

Primary scaling uses `StandardScaler()` on the full spell population (cell 246): z = (x − population mean) / population standard deviation, with ddof=0. There is no train/test split or predictive generalization claim. Family-balanced sensitivity values multiply each z-score by 1/sqrt(m), where m is its retained macro-family feature count (cells 252–253). Repeated footballers affect both the primary scaling distribution and empirical percentiles.

## PCA — notebook 05

PCA is applied to the globally standardized 20-feature matrix, with a separate family-balanced comparison. `PCA()` retains all components; the primary saved variance is PC1 35.56%, PC2 19.32%, first five cumulatively 85.23%. The saved coefficients and scores define the historical projection and sign convention. PCA is a descriptive view, not the distance space for primary neighbours or a replacement for the 20-dimensional cluster input. Preserve existing coordinates rather than refitting for a website map.

## Similarity — notebook 06

For spells i and j, distance is sqrt(sum over the 20 features of (z_i − z_j)^2). All spells with the target's `player_id` are excluded. Candidates are ordered by distance with stable mergesort; only the closest spell of each distinct candidate footballer survives, then the first ten are retained (cell 13; population export uses the same principle). The output has 13,960 neighbour rows. Equal-distance ordering inherits original candidate order; do not silently rerank exports.

The pool is retrospective across all seven seasons, without a target-date restriction. Historical neighbours therefore do not imply that the candidate spell would have been available when the target played. Distance is neither a probability nor a percentage. Squared feature differences explain additive contributions to squared distance, not contributions to effectiveness. Family-balanced Euclidean and standardized Manhattan comparisons are sensitivity analyses; the primary product uses standardized Euclidean distances.

## Archetypes and robustness — notebook 07

K-Means diagnostics evaluate K=2 through K=10. The descriptive handoff retains K=5 in the original standardized space with `random_state=42`, `n_init=30`, `max_iter=500` (cell 14 and saved manifest). Its mean saved silhouette is 0.1491902281; clusters overlap substantially. Labels are working interpretations, not discovered natural types, positions or player rankings.

| ID | Working label | Count |
|---|---|---:|
| C0 | Penalty-area attacking and shooting | 352 |
| C1 | Crossing-oriented wide play | 291 |
| C2 | Deeper passing progression | 278 |
| C3 | Direct carrying and dribbling | 266 |
| C4 | Advanced creative progression | 209 |

The saved robustness table compares partitions using adjusted Rand index and Hungarian-aligned label agreement. Alternative cluster labels are aligned for comparison, not used to replace the original five IDs.

| K=5 sensitivity test | ARI | Matched agreement |
|---|---:|---:|
| Family-balanced features | 0.831241 | 92.406877% |
| Equal total weight per footballer | 0.708791 | 87.320917% |
| Extreme-observation sensitivity | 0.911529 | 96.060172% |

Equal-footballer weights are 1 / number of spells for that footballer. The extreme test fits after excluding observations above the 99th percentile of Euclidean norm from the standardized origin, then compares assignments on the complete population (cells 33–34). These completed experiments are reported from saved evidence; none was rerun for this handoff. The primary model continues to include all 1,396 observations.

Centroid margin is (second-nearest distance − assigned distance) / second-nearest distance. A smaller margin means less geometric separation from the nearest alternative, not a calibrated probability of membership. Silhouette and robustness flags provide additional context; a player can plausibly sit between working archetypes.

## Profiles — notebook 08

The catalogue retains assignments, PCA coordinates, five centroid distances, alternative assignments, margins, silhouettes, aligned robustness outcomes and nearest distinct footballer. The long fingerprint table has 1,396 × 20 = 27,920 rows containing raw value, z-score, population percentile and assigned centroid z-score.

Feature percentiles use pandas average ranks divided by the full population count and multiplied by 100. Centroid-distance percentiles rank within the assigned cluster; nearest-neighbour distance percentiles rank first-neighbour distances across all spells. The corrected profile display and export use average-rank tie handling; older Notebook 06 diagnostic ECDF displays should not define the website percentile contract. Low distance percentiles mean relatively close neighbours or centroids, not low player quality.

## Evidence boundary

The Phase 2A validator checks saved identities/order, feature formulas, standardization arithmetic, PCA coefficient consistency, original assignments, stored-pair distances, fingerprints, featured spells and documentation claims. It does not refit a model, rebuild positional matching, recompute every silhouette, rerank the entire population or execute the notebooks end to end. Clean-environment reproduction, upstream matching reproducibility and model-fit repeatability still require an authorized controlled run. No new statistical experiment is part of this handoff.
