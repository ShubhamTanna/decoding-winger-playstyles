# Case-study fact sheet: Decoding Winger Playstyles

**Question:** How do wingers differ in what they do in attack, and which patterns recur across leagues and seasons? The evidence describes attacking **style**: where touches occur, how the ball progresses, and how often particular actions are attempted. It does not measure how well a player performs them.

## Scope and evidence

The population covers 2017–18 through 2023–24 in the Premier League, La Liga, Bundesliga, Serie A and Ligue 1. One observation is a **footballer at one club in one season**. The 1,396 qualifying spells describe 665 distinct footballers; a returning player contributes repeatedly, and two clubs in one season can produce two observations. Each spell needed at least 1,125 minutes and LW, RW, LM or RM positional eligibility. These are position classifications, not observed minutes spent on the wing.

Start with the [released facts](../portfolio/web/facts.md), [feature dictionary](feature_dictionary.md), [methodology](methodology.md), [source provenance](provenance.md) and [research handoff](frontend_research_support.md). In references below, “N05 / filename” means the private saved artifact under `data/processed/notebook_05_outputs/`; the same convention applies to the other notebook numbers. Notebook cell indices are zero-based. Public website tables are linked in the fact-check section. This is a reading of completed analyses, not a new fit.

## How a spell became a profile

1. **N01 — audit.** Stack seven seasonal FBref-derived CSVs; correct misleading columns, check duplicate/redundant statistics and distinguish footballers by name plus birth year, with a documented collision correction for the two Vitinhas. Club spells remain separate. Likely distribution: [Akshan Krithick on Kaggle](https://www.kaggle.com/datasets/akshankrithick/fbref-2017-2024-for-europes-top-5-leagues); the exact original download is not verified.
2. **N02 — population.** Match statistical identities to the FIFA/SoFIFA positional data (`male_players.csv`, FIFA 18–24) using birth year, name aliases, club history and completed manual identity decisions. Use the appropriate edition's primary or club position, with documented manual resolutions where necessary, and apply the per-spell minutes cutoff. Neither the positional source nor a manual decision measures the player's match-by-match deployment.
3. **N03 — enrichment.** Join additional FBref-derived statistics from [Emre Yılmaz's dataset](https://www.kaggle.com/datasets/emrey3lmaz/top-5-league-football-player-stats-2017-2025) (`Top5_League_Players_2017to2024_dataset.xlsx`) by normalized player, birth year, club and season. The one-to-one left join matched the entire existing population; the donor did not select new wingers. Retain documented corrections and cross-source reconciliation decisions. Exact download dates/versions are unknown.
4. **N04 — engineer and scale.** Screen 27 candidates for interpretability, denominator reliability, sparsity, temporal behaviour and redundancy. Engineer 21 provisional measures; cell 226 removes `progressive_distance_per_carry` because it overlaps strongly with progressive-carry frequency and share. Keep rate/share pairs where they answer different questions. Standardize the final 20 over all qualifying spells: subtract the pooled arithmetic mean and divide by the pooled population SD (ddof=0; cell 246). Equal weight per feature and spell is the primary specification, not equal weight per family or footballer.
5. **N05–07 — describe structure.** Use PCA to display variation; use all 20 standardized values for historical neighbours and for K-Means. The three operations answer different questions: what varies together, which individual spells are alike, and which group average is nearest.
6. **N08 — profile.** Join by observation identity, retaining raw values, global z-scores, feature percentiles, PCA coordinates, primary/alternative assignments, fixed-centre distances, runner-up margin, silhouette, sensitivity flags and nearest historical footballers. A spell's feature percentile is its ascending rank (ties averaged) divided by 1,396, times 100. The 50th percentile is a rank near the middle, not necessarily the arithmetic mean. A centroid is a mean of standardized values, not an individual percentile.

## What the 20 features measure

Family grouping below is for reading; retain [features.csv](../portfolio/web/features.csv) order for calculations. The linked dictionary gives exact formulas, source columns and limitations.

| Family | Final internal features |
|---|---|
| Territory | `attacking_third_touch_share`, `box_penetration_touch_share` |
| Receiving | `progressive_receptions_p90`, `progressive_reception_share` |
| Carrying | `progressive_carries_p90`, `progressive_carry_share`, `carries_into_box_p90` |
| Dribbling | `take_ons_p90`, `take_ons_per_100_live_touches` |
| Passing | `progressive_passes_p90`, `progressive_pass_share`, `passes_into_box_p90`, `long_pass_share` |
| Crossing | `crosses_p90`, `cross_pass_share` |
| Shooting | `shots_p90`, `shots_per_100_att3rd_touches`, `avg_shot_distance` |
| Behavioural Choice | `carry_progression_share`, `carry_box_entry_share` |

Per 90 uses spell minutes. Attacking-third touch share divides by **all touches**; penalty-area penetration touch share divides by **attacking-third touches**. Take-ons per 100 use **live touches**; shots per 100 use **attacking-third touches**. Neither denominator says where an individual take-on or shot began. Progressive reception and carry shares divide by all receptions and carries respectively. Progressive pass share divides by canonical **Passes Attempted**; cross and long-pass shares divide donor crosses and long attempts by donor **Total_Att**. Carry share of progression divides progressive carries by progressive carries **plus progressive passes**; carry share of box entries divides box carries by box carries **plus box passes**. Those are choices between counted actions, not shares of metres gained or successful attacks. Ratios require a positive denominator; the final matrix is finite. Average shot distance uses source field **Standard_Dist**: “shorter/longer” is supported; metres or yards are not verified.

## PCA: what the axes mean

The primary PCA uses the 20 global z-scores, centred and unwhitened. A **coefficient** weights an input in the linear combination that produces a score. A **feature–score correlation** is the Pearson correlation of that feature with that component across the observed spells. Use correlations to explain the published orientation, not coefficients as if they were correlations. Signs are arbitrary in theory; these signs match the released map. N05 cells 6, 10 and 34; `pca_primary_coefficients.csv`, `pca_primary_feature_correlations.csv`, `pca_primary_variance.csv`.

| Component | Explained variance (%) | Cumulative (%) |
|---|---:|---:|
| PC1 | 35.55904607449477 | 35.55904607449477 |
| PC2 | 19.32465096529335 | 54.883697039788125 |
| PC3 | 14.006829877281016 | 68.89052691706914 |
| PC4 | 8.506178969278583 | 77.39670588634772 |
| PC5 | 7.833534339188369 | 85.2302402255361 |

- **PC1:** Higher scores go with more carries into the box per 90 and a larger carry share of progression; lower scores go with a higher long-pass share and longer average shots.
- **PC2:** Higher scores go with more passes into the box and crosses per 90; lower scores go with a greater penalty-area share of attacking-third touches and more shots per 100 attacking-third touches.
- **PC3:** Higher scores go with crosses accounting for more passes and more crosses per 90; lower scores go with higher progressive-pass share and more progressive passes per 90.

Directions blend multiple behaviours. Projected neighbours can differ on omitted axes. N05 cell 31 compares ten neighbouring **spells** after excluding the target footballer: even the five-component projection retained only about 54% of the original ten on average. That diagnostic allows repeated candidate footballers; it is distinct from N06's ten different people.

## Five descriptive archetypes

Read each row as a **group tendency relative to the pooled spell mean**, not a requirement for membership. The featured spell illustrates a group; a famous example need not be its closest member.

| Archetype | Spells | Measured tendencies and contrast | Approved editorial example |
|---|---:|---|---|
| C0 · Penalty-area attacking and shooting | 352 | A larger share of attacking-third touches in the box, shorter average shots and more shots per 100 attacking-third touches. Fewer crosses and progressive passes per 90. Shots per 90 are near the overall mean: the name does not imply high shot volume or conversion. | Richarlison · Everton · 2018–19 |
| C1 · Crossing-oriented wide play | 291 | More crosses per 90; crosses and long passes account for larger shares of attempts. A smaller share of attacking-third touches in the box and longer average shots. This is delivery behaviour, not evidence of a player's touchline position. | Raphinha · Leeds United · 2020–21 |
| C2 · Deeper passing progression | 278 | Smaller attacking-third share of touches, progressive share of receptions and carry share of progression. Progressive pass frequency and share are above the pooled mean; **all six largest deviations are negative**. There is no need to invent a dominant positive trait. | Carlos Soler · Valencia · 2018–19 |
| C3 · Direct carrying and dribbling | 266 | More carries into the box, more progressive carries per 90 and a larger progressive share of carries; more take-on attempts per 100 live touches. A smaller long-pass share. Attempt frequency does not measure dribbling success. | Vinícius Júnior · Real Madrid · 2022–23 |
| C4 · Advanced creative progression | 209 | More passes into the box, progressive passes, progressive carries and shots per 90. A smaller carry share of progression can coexist with high carry volume. These measures do not establish chances created or the starting locations of passes. | Neymar · Paris Saint-Germain · 2021–22 |

**How reliable are the groups?** N07 explored K=2–10 and retained K=5 as an interpretable description of continuous variation. The original mean silhouette was about 0.149: there is substantial overlap, not five independently established natural player types. The nearest centroid determines assignment. The runner-up margin, (second distance − assigned distance) / second distance, measures geometric separation, not membership probability. A smaller distance to one's centre means a more representative *profile*, not better performance.

N07 compared the original partition with three saved alternatives. Family balancing multiplies each z-score by 1/√(features in family); player balancing gives each footballer equal total weight across their spells; extreme trimming omits spells above the 99th percentile of standardized vector length during the alternative fit and assesses assignments on the complete population. Adjusted Rand index (ARI) compares partitions; matched agreement counts spells retaining a label after aligning the alternative IDs. The broad patterns often recur, but equal-footballer weighting changes more assignments than the other two checks. Agreement across tests is not proof of out-of-sample stability.

## Which historical spells are most alike?

For two spells use the square root of the sum of the 20 squared z-score differences. N06 excludes **every spell of the target footballer**, sorts eligible spells by ascending distance (stable original order for ties), keeps only the nearest spell for each different footballer, then takes ten. The release has 13,960 relationships. Retrieval is retrospective across the whole period, not “who was available then.” There is no universal threshold for a good match. Feature contributions divide each squared difference by the sum of squared differences; when the profiles coincide there is no difference to apportion.

N06 compared family-balanced Euclidean and standardized Manhattan distance with the primary lists. On average about 86% and 79% of the ten **footballer identities**, respectively, were retained. The nearest identity did not always survive. Those are agreements between lists, never scores for how similar two people are.

**An unusual spell within C3.** Jérémy Doku (Manchester City, 2023–24) recorded 8.29 carries into the box per 90 (+9.43 SD) and 12.30 progressive carries per 90 (+6.47 SD). Across all 20 features, his distance from the pooled mean was 14.48, the largest among the 1,396 spells (next: 9.99). His distance from the C3 centre was 11.36 (next within C3: 8.37). His nearest spell by another footballer was Vinícius Júnior at Real Madrid in 2022–23, 7.15 units away. Doku retained C3 in all three sensitivity checks: he was an unusual member of the group, and the distances say nothing about his ability.

Sources: N04 / `winger_style_features_raw.parquet`, `winger_style_features_scaled.parquet`; N07 / `winger_k5_centroids_standardized.csv`, `winger_k5_profile_assignments.parquet`; N06 / `top10_primary_euclidean.parquet`. Spell: `spell_c601a57ea8614558a13c03445c97d6b2310e7bd5953158b40fe0f0b73d9b7e53`.

## Two historical comparisons

Each pair below uses fingerprints joined by spell ID and feature in model order. Distances are direct comparisons of the original global z-scores, not lookups in the other-footballer neighbour list. Raw rates and shares are displayed rounded here; exact inputs appear in the ledger.

**Raphinha — a different nearest centre.** Player ID `Raphinha_1996`. Leeds United 2021–22, C1 (`spell_5f0bd70a011e45f238f411db9bfdcb8e75e5fecb1e3e1dd4741956e943b2d9a9`) → Barcelona 2022–23, C4 (`spell_4939341e781c443314a24c988916302bc6d693117a6faa2cded7f496630aec3c`). Crosses rose from **5.00 to 7.47 per 90** and passes into the penalty area from **1.51 to 3.21 per 90**. The complete profiles were **5.04** units apart. He crossed *more*, even though the second spell did not receive the crossing-oriented label. The assignment reflects the full profile, not a single defining action. These figures do not explain why his behaviour changed.

**Carlos Soler — meaningful movement within the same group.** Player ID `Carlos Soler_1997`. Valencia 2018–19, C2 (`spell_ce2703937ee6aa10ba5dde04a39713ffc6cf7ce8efdec98838b40799399e6b9b`) and Valencia 2020–21, C2 (`spell_66e1056814f3eb6cb7724e7b4c7d0dc68d64453de32a163049effdc70bd7a29d`). The attacking-third share of touches fell from **36.02% to 24.67%**, while progressive passes rose from **4.50 to 5.03 per 90**. His two profiles were **5.15** units apart despite retaining the same label. These are selected, nonconsecutive seasons at the same club, not a continuous trajectory or evidence of improvement or decline.

## Boundaries for public copy

There are no tracking coordinates, tactical instructions, opponent adjustments or controlled teammate/possession effects here. Event totals and ratios describe behaviour in context, not finishing quality, efficiency, causality or future recruitment success. Coverage excludes other leagues, seasons, nonqualifying positions and lower-minute spells; absent years do not imply inactivity. Some footballers contribute more observations. Of the 665, 329 qualify in multiple seasons. Dango Ouattara has two club spells in 2022–23; season alone does not order them. Do not infer a permanent player type or a causal role change from a label switch. The source downloads are incompletely versioned, some cross-source discrepancies remain, shot-distance units are unresolved, and [clean-environment reproduction](reproducibility.md) has not been demonstrated. This handoff verifies saved evidence; it does not claim an independent rerun.

## Fact-check ledger

Exact values below refer to the saved precision, except where explicitly labelled a display rounding. Supporting tables: [spells](../portfolio/web/spells.csv), [features](../portfolio/web/features.csv), [centroids](../portfolio/web/archetypes.csv), [fingerprints](../portfolio/web/fingerprint.csv), [neighbours](../portfolio/web/neighbours.csv).

| Claim | Exact value | Suggested public wording | Source and guardrail |
|---|---|---|---|
| Coverage | 2017–18 to 2023–24 inclusive; 7 seasons, 5 leagues | Seven seasons across Europe's five major leagues | N01 inputs; spells season/competition. Historical, not current. |
| Eligibility and population | ≥1,125 minutes; 1,396 spells; 665 footballers | 1,396 qualifying player–club–season observations from 665 players | N02 final selection; N08 catalogue; spells. Threshold is per club spell. |
| Representation | 27 → 21 → 20; 8 families | Twenty features remain after screening and removing a redundant carry measure | N04 cell 226; features.csv. Twenty standardized measures, not outcomes. |
| PCA | PC1–5 and cumulative percentages: exact table above | The first two axes show 54.88% of variation; the first five show 85.23% | N05 / pca_primary_variance.csv. Explained variance, not accuracy. |
| Map neighbourhood diagnostic | 0.5421203438395416 mean overlap | Even five PCs retained only about 54% of the ten neighbouring spells on average | N05 cell 31 / pca_neighbour_preservation.csv. Same-player exclusion; no candidate deduplication. |
| Neighbours and fingerprints | 10 per spell; 13,960 pairs; 27,920 spell–feature rows | Ten distinct historical footballers per spell; 20 feature records per spell | N06 primary top-ten export; N08 long fingerprint; website tables. Directional records, not unique pairs. |
| Alternative neighbour lists | Mean top-ten overlap: 0.8615329512893983 / 0.7900429799426935; same top-one player: 78.00859598853869% / 69.34097421203438% | Family-balanced Euclidean and Manhattan retained about 8.6 and 7.9 of ten identities on average | N06 / distance_metric_comparison.csv. Order of alternatives as stated; not pairwise similarity. |
| Clusters | K tested 2–10; K=5 counts C0–C4: 352, 291, 278, 266, 209 | Five overlapping summaries of style | N07 manifest, diagnostics and website centroids. Counts are spells. |
| C0 centre (z) | `box_penetration_touch_share`: 0.77846210279407457; `shots_per_100_att3rd_touches`: 0.57069538542533937; `shots_p90`: 0.0039261887209053768 | More shooting per attacking-third touch; shots per 90 near the mean | archetypes.csv, cluster 0. Group means, not individual ranks. |
| C1 centre (z) | `cross_pass_share`: 1.235522790621441; `box_penetration_touch_share`: -0.70026716171628056 | Greater cross share; smaller penalty-area share of attacking-third touches | archetypes.csv, cluster 1. Group means, not individual ranks. |
| C2 centre (z) | `carry_progression_share`: -1.2841512428831603; `progressive_passes_p90`: 0.62817109246158076 | Less progression by carrying; more progressive passes per 90 | archetypes.csv, cluster 2. Group means, not individual ranks. |
| C3 centre (z) | `carries_into_box_p90`: 1.3804465712667267; `take_ons_per_100_live_touches`: 1.0828058780568814; `long_pass_share`: -0.56016176615417501 | More carries into the box and more attempted take-ons per live touch; smaller long-pass share | archetypes.csv, cluster 3. Group means, not individual ranks. |
| C4 centre (z) | `passes_into_box_p90`: 1.3153949343095994; `carry_progression_share`: -0.3546401788175092 | More passes into the box, but a smaller share of progression by carrying | archetypes.csv, cluster 4. Group means, not individual ranks. |
| Mean silhouette | 0.14919022811913307 | Overall separation is modest (silhouette ≈0.149) | Mean saved k5_silhouette across spells; not a percentage or confidence score. |
| Family-balanced K=5 | ARI 0.8312411010982386; matched 92.40687679083095% | About 92% retained their aligned assignment | N07 / winger_clustering_robustness.csv; agreement with primary, not accuracy. |
| Equal-player-weight K=5 | ARI 0.7087913231876931; matched 87.32091690544412% | About 87% retained their aligned assignment | Same artifact; repeated-player weighting matters. |
| Extreme-trimmed K=5 | ARI 0.9115294205909105; matched 96.06017191977078% | About 96% retained their aligned assignment | Same artifact; 99th-percentile norm cutoff applies to alternative fit only. |
| Longitudinal coverage | 329 of 665 distinct players in multiple seasons; 1 player-season with two qualifying clubs | Follow qualifying club spells, not an uninterrupted career | spells by player_id and distinct season; two club spells are not a timeline within that season. |
| Raphinha, rates and distance | Crosses/90: 5.0017152658662098 → 7.4710424710424714; box passes/90: 1.5128644939965694 → 3.214285714285714; distance 5.040998865549299 | More crosses and passes into the area; C1 → C4 | Fingerprints for the two IDs above; Euclidean distance over all 20 z-scores. Not a reason for the change. |
| Carlos Soler, shares, rates and distance | Attacking-third touch share: 0.36021505376344087 → 0.24672489082969432; progressive passes/90: 4.5 → 5.0347349177330898; distance 5.154391554664018 | A smaller attacking-third touch share and more progressive passes; C2 in both spells | Same method; shares in raw fraction units, not percentile ranks. |
