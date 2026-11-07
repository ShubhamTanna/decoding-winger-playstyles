# Research handoff for Claude · Schema 1.1.0

## Two featured examples to add to editorial copy

Use **Richarlison, Everton 2018–19** for C0 and **Carlos Soler, Valencia 2018–19** for C2. Richarlison combines a larger penalty-area share of attacking-third touches (+0.98 standard deviations), more shots per 100 attacking-third touches (+0.90) and a shorter average shot distance (−1.31). Soler combines more progressive passes per 90 (+0.54), a smaller carry share of progressive actions (−1.57) and a smaller attacking-third touch share (−1.29). Each sentence describes one spell relative to the pooled historical population.

The shortlist uses saved primary assignments and full-precision ascending distance within cluster, then spell ID for ties. Recognizability is an editorial judgment. All six spells retained their primary label in all three saved robustness checks. The rank denominator counts spells. Distances below are the exported decimal values.

| Archetype | Player, club, season | Rank | Centroid distance | Canonical spell ID |
|---|---|---:|---:|---|
| C0 | **Richarlison**, Everton, 2018–19 | 4 / 352 | 1.6050875072759272 | `spell_225fb582e4861300f9a3cadfe6255de04b61f89abdcea60b26cce593433be72f` |
| C0 | Eric Maxim Choupo-Moting, Stoke City, 2017–18 | 2 / 352 | 1.5056032976266764 | `spell_cbd682a180494da5884480d3f189a8a4164263fdd16b0f1c1ee24843a305a962` |
| C0 | Mikel Oyarzabal, Real Sociedad, 2018–19 | 3 / 352 | 1.5764030165773162 | `spell_7097748a3f41baf233e3d6bee56fd6e8564718e4118568fda5f3196de6c1e36d` |
| C2 | **Carlos Soler**, Valencia, 2018–19 | 1 / 278 | 1.3049921707186103 | `spell_ce2703937ee6aa10ba5dde04a39713ffc6cf7ce8efdec98838b40799399e6b9b` |
| C2 | Alex Iwobi, Everton, 2022–23 | 10 / 278 | 1.9449649706036374 | `spell_e04d0e8eb5a6d0c535f54d37d7c3e8eaf4a10295daffea4544dc1fe7edd494e7` |
| C2 | Thomas Lemar, Atlético Madrid, 2020–21 | 13 / 278 | 2.0152533410585574 | `spell_e8c2e96deda7c194757bbbd67d71a65693d6532439d986ed32661b97739a43d1` |

Choupo-Moting is closer than Richarlison and shows particularly frequent shooting per attacking-third touch (+1.02). Oyarzabal shows the box involvement (+0.64) and shorter shot distance (−0.70), with shooting per attacking-third touch nearer the mean (+0.06). Iwobi and Lemar combine above-average progressive passes per 90 (+0.95 and +0.93) with below-average carry shares of progression (−1.28 and −1.25). The existing three featured entries remain in the released manifest. The two additions above are editorial candidates pending selection.

## PCA explanations for the saved map

The primary tables in `data/processed/notebook_05_outputs/` are `pca_primary_coefficients.csv`, `pca_primary_feature_correlations.csv` and `pca_primary_variance.csv`. All three source files match the preserved research snapshot byte for byte and agree with the original SHA-256 inventory. In Notebook 05 (zero-based cells 3–4, 6, 10, 34), X is the globally standardized 20-feature matrix in specification order, with equal weight per feature. Ordinary centred, unwhitened PCA was applied to all 1,396 spells. Each **coefficient** weights a centred standardized input in the score. Each **feature–score correlation** is Pearson r across the spells. Use correlations for axis descriptions. The sign of an eigenvector is mathematically arbitrary, but the sign in these files must agree with the existing map.

| Axis | Variance | Suggested description in the released orientation |
|---|---:|---|
| PC1 | 35.56% | Higher scores go with more carries into the box per 90 (r = +0.85) and a greater carry share of progression (+0.84). Lower scores go with a higher long-pass share (−0.48) and longer average shots (−0.47). |
| PC2 | 19.32% | Higher scores go with more passes into the box (+0.78) and crosses per 90 (+0.73). Lower scores go with a greater penalty-area share of attacking-third touches (−0.51) and more shots per 100 attacking-third touches (−0.41). |
| PC3 | 14.01% | Higher scores go with a greater cross share of passes (+0.79) and more crosses per 90 (+0.56). Lower scores go with a higher progressive-pass share (−0.68) and more progressive passes per 90 (−0.64). |

PC1 and PC2 together show 54.88% of standardized variation. PC3 brings the cumulative total to 68.89%. Axis scores describe combinations of behaviours and have no quality ranking.

**Optional companion export.** From the repository root run `python3 scripts/export_pca_explainer.py` (Python 3.10+). This writes `outputs/frontend-research-support/pca_explainer.json`. It names the compatible base schema and data release, records source hashes, and contains the ordered feature IDs and three named components, each with its variance ratio, 20 coefficients and 20 correlations. The same index always refers to the same feature. The check requires matching source feature order, centred unit-population-SD inputs, agreement on explained variance, and replay of every signed score and correlation against the website fingerprints. Maximum absolute error over 4,188 projected coordinates was 1.78 × 10⁻¹⁵.

**Release proposal.** Keep the companion local for review. For formal adoption, publish an optional `pca_explainer.json` in a separately versioned additive release (proposed 1.2.0). Register its checksum, size and base-data identity, validate feature order, dimensions, scores and correlations before publication, and test the consumer's version handling. The existing eight-file 1.1.0 contract stays usable as released. If the two editorial picks are approved, append their spell IDs to the featured list in a future release and review any consumer assumptions that the list has exactly three entries.

## Wording rules

For a single feature, z = (spell value − pooled spell mean) / pooled population standard deviation. Positive means more of the measured quantity than the mean, negative means less, and zero means equal to the mean. Write “crossed more often,” “crosses accounted for a larger share of passes,” or “shot from farther away,” according to the feature’s denominator and unit. Use the same comparison population for every season.

| When showing | Use |
|---|---|
| One spell, one feature | Lead with the measured value and denominator. “Raphinha crossed 7.47 times per 90 at Barcelona in 2022–23, around the 96th percentile among qualifying spells.” The saved z-score (+2.10) expresses distance above the pooled **mean** in population standard deviations. For a share, name the denominator. For a distance, say shorter or longer. |
| Percentiles | Use the saved raw-feature rank across all 1,396 spells, including repeated footballers. Notebook 08 cell 12 uses ascending, one-based average ranks for ties, divided by 1,396 and multiplied by 100. “Around the 90th percentile” is safe. A percentile is a rank, not an event rate, a percent increase, a probability or the exact fraction strictly below when observations tie. Percentile changes are percentile points. |
| Mean versus median | Zero z is the arithmetic mean. The 50th percentile denotes the middle of the ranked distribution, which can differ from the mean. For crosses per 90, Leonardo Bittencourt at Köln in 2017–18 recorded 3.18, **55.6th percentile and z = −0.042**. “Above the middle” and “below average” are both accurate here. Avoid turning a positive z into a percentile using a normal curve. |
| Archetype tendencies | “Crosses make up a larger share of pass attempts in C1; its centre sits 1.24 standard deviations above the historical mean.” A centroid coordinate is the cluster mean of standardized spell values. It has no saved individual-spell percentile. The mean of member percentiles, or the empirical rank of the centroid value, answers a different question. Keep archetype copy on the centroid scale. |
| Representativeness | “Fourth closest to the C0 centre across all 20 behaviours.” Smaller Euclidean distance means closer. A high within-cluster **distance** percentile means farther away. This rank, the distance margin, and the silhouette measure different things. None is a membership probability or an ability rating. |
| Spell similarity and overlap | Compute Euclidean distance across all 20 global z-scores. Smaller distances mean more similar measured tendencies. Avoid “percentage similar.” The five labels summarize overlapping groups (overall silhouette about 0.149). The nearest-centre assignment is definite in this model, but a small runner-up margin can place a spell near the boundary. |

Use percentile-first language for **individual measured features**. For rate and share metrics, keep raw values visible so a visitor can distinguish “15% of pass attempts” from “89th percentile.” For average shot distance keep the physical unit unspecified. For a change across seasons, identify the measured change without inferring improved performance.

## Historical evolution from 1.1.0

Group `spells.csv` by `player_id`, keep `spell_id` as the observation key, and sort by numeric season start. Of 665 footballers, 329 have qualifying spells in multiple seasons. One player-season has two qualifying club spells: Dango Ouattara at Lorient and Bournemouth in 2022–23. Show these side by side or tied on the time axis. Season labels alone do not establish their within-season chronology.

- Each spell carries its cluster, PC1–PC5, distance to its assigned centroid, all five fixed-centroid distances and the runner-up margin. The same fitted axes and centres apply across years. If the label changes, use `distance_to_cluster_k` on both spells to measure a change relative to one fixed centre.
- Join `fingerprint.csv` on `(spell_id, feature)` for all 20 raw values, z-scores and pooled percentiles. Subtract like from like. For direct distance, join both vectors in manifest order, then take the square root of the sum of squared differences. The precomputed top-ten neighbours deliberately exclude the same footballer. Their absence does not prevent this comparison.
- Replay example: Raphinha, Leeds 2021–22 → Barcelona 2022–23. His assignment changes C1 → C4 and PC1 changes −0.485736 → +1.968533. Crosses per 90 rise from 5.001715 to 7.471042. The complete 20-feature distance is **5.040998865549299**. The two assigned-centroid distances (2.585540 and 4.912960) refer to **different centres**.
- These are qualifying historical spells, with a 1,125-minute minimum. Gaps do not establish inactivity. Club, league, teammates and role can change. The files support descriptive change, not a continuous career trajectory, a causal explanation, within-season timing or a performance trend.

Evidence for the shortlist and evolution checks: released `portfolio/web/{manifest.json,spells.csv,fingerprint.csv,archetypes.csv,neighbours.csv}`. The ten JavaScript acceptance replays are Claude's reported integration result; the PCA replay above is a separate research-side check.
