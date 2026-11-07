# Decoding Winger Playstyles

**How do professional wingers differ in their attacking behaviour, and which historical footballers offer comparable stylistic profiles?**

An independent Python research project examining winger roles across Europe's five major leagues. It describes where players receive and carry the ball, how they progress play, and their passing, crossing and shooting tendencies. It does **not** rank player quality or estimate recruitment success: similar attacking styles can produce very different outcomes.

## Dataset

The final population contains **1,396 player-club-season spells from 665 footballers**, covering **2017–18 through 2023–24** in the Premier League, La Liga, Bundesliga, Serie A and Ligue 1. Each qualifying spell has at least **1,125 minutes**. Winger eligibility uses LW, RW, LM or RM in historical FIFA primary or club positions, supplemented by completed manual verification.

A spell is not a unique footballer or necessarily a complete season. Transfers and repeated seasons remain separate observations. Enrichment preserves the originally selected winger population.

## Representation and findings

Notebook 04 develops **27 candidates → 21 provisional features → 20 final features** across eight behavioural families: Territory, Receiving, Carrying, Dribbling, Passing, Crossing, Shooting and Behavioural Choice. It removes `progressive_distance_per_carry` after redundancy analysis to limit overweighting of carrying behaviour. The [final feature dictionary](docs/feature_dictionary.md) records the implemented formulas and their limitations.

The primary representation globally standardizes all 20 features across the spell population. Saved results show:

- **PCA:** PC1 explains **35.56%** of variance, PC2 **19.32%**, and the first five components **85.23%**. PCA summarizes variation; it is not the primary similarity metric.
- **Historical neighbours:** Euclidean distance in the full standardized 20-dimensional space, excluding every other spell of the target footballer and retaining the closest spell of each distinct candidate footballer. Ten neighbours per spell produce **13,960 records**. Distances are not similarity percentages.
- **Archetypes:** a working K-Means model with K=5 has mean silhouette **0.149**. The weak separation supports cautious descriptive use, not a claim of five naturally distinct player types.
- **Profiles:** **1,396 profiles** and **27,920 feature-level records** combine raw values, z-scores, population percentiles, PCA coordinates, assignments, uncertainty diagnostics and historical neighbours.

| Cluster | Working description | Spells |
|---|---|---:|
| C0 | Penalty-area attacking and shooting | 352 |
| C1 | Crossing-oriented wide play | 291 |
| C2 | Deeper passing progression | 278 |
| C3 | Direct carrying and dribbling | 266 |
| C4 | Advanced creative progression | 209 |

These figures are checked against saved research artifacts, not claimed as a fresh end-to-end reproduction. [Methodology](docs/methodology.md) explains the calculations and sensitivity tests.

## Research notebooks

Run order is 01 through 08, with the inputs and manual staging described in [reproducibility](docs/reproducibility.md).

| Notebook | Purpose |
|---|---|
| [01 — Data audit](notebooks/01_data_audit.ipynb) | Audit seasonal data, correct column meanings and resolve player identities. |
| [02 — Winger population](notebooks/02_winger_population.ipynb) | Apply positional eligibility, completed identity reviews and the playing-time threshold. |
| [03 — Enrichment](notebooks/03_winger_data_enrichment.ipynb) | Add behavioural statistics while preserving the authoritative population. |
| [04 — Feature engineering](notebooks/04_playstyle_feature_engineering.ipynb) | Define, screen and standardize the final behavioural representation. |
| [05 — Playstyle structure](notebooks/05_playstyle_structure.ipynb) | Examine correlations, PCA and representation sensitivity. |
| [06 — Player similarity](notebooks/06_player_style_similarity.ipynb) | Compare distinct footballers using full-dimensional historical neighbours. |
| [07 — Archetypes](notebooks/07_winger_archetype_discovery.ipynb) | Interpret K-Means groupings and assess robustness. |
| [08 — Player profiles](notebooks/08_winger_player_profiles.ipynb) | Assemble fingerprints, assignment diagnostics and population-wide profile exports. |

## Limitations

Season aggregates obscure match-level role changes and tactical context. Historical positional classifications are imperfect and require manual decisions. Repeated footballers contribute unequally to the spell population; minutes thresholds also restrict coverage. Small cross-source discrepancies and uncertain original download versions remain documented. The physical unit of the donor's average shot-distance field is unresolved.

K-Means boundaries overlap and depend on feature representation and population weighting. Robustness tests cover family balancing, equal footballer weights and extreme-observation sensitivity; they do not establish natural categories. Percentiles and centroid margins describe the reference population and model geometry, not effectiveness or membership probabilities. The historical comparison pool spans the full study period, including seasons later than an early target spell; it is not a time-safe scouting backtest.

## Repository and reproducibility

```text
notebooks/        Eight publication copies, with saved outputs removed
docs/             Dictionary, methodology, provenance and handoff design
scripts/          Export, validation and publication checks
portfolio/web/    Eight curated public website files
requirements.txt  Provisional Python 3.12 dependency specification
data/             Local private inputs and saved artifacts (ignored)
.local/           Preserved executed evidence and local checks (ignored)
```

The repository publishes research code, documentation and eight curated website data files under `portfolio/web/`. Original source datasets, full intermediate research artifacts and fitted models remain private. A fresh clone does not contain the inputs needed to reproduce results. The notebooks retain Colab `/content/` paths and require manual staging. Dependency resolution has been checked, but the candidate environment has **not** passed a clean-kernel pipeline run.

Start with [reproducibility instructions](docs/reproducibility.md), [environment status](docs/environment.md) and [source provenance](docs/provenance.md). With the private saved artifacts and a suitable existing pandas/NumPy/PyArrow runtime, run `python3 scripts/validate_research_handoff.py` for read-only checks. This does not fit models or regenerate research exports. Publication safeguards are described in [local workflow](docs/local-workflow.md).

## Sources and portfolio

The statistical data are FBref-derived historical exports. The likely initial Kaggle source is [FBref 2017–2024 for Europe's Top 5 leagues](https://www.kaggle.com/datasets/akshankrithick/fbref-2017-2024-for-europes-top-5-leagues); enrichment uses [Top 5 League Football Player Stats (2017–2025)](https://www.kaggle.com/datasets/emrey3lmaz/top-5-league-football-player-stats-2017-2025). Auxiliary positions come from historical FIFA/SoFIFA data and documented manual decisions. Original download versions and dates are not fully recovered; see [provenance](docs/provenance.md). The MIT license covers this repository's code and documentation, not a grant of rights to redistribute third-party datasets.

A research case study and Winger Style Explorer are planned for [shubhamtanna.in](https://shubhamtanna.in). The project-page route is not yet confirmed. The [portfolio export specification](docs/portfolio_export_architecture.md) and [build/browser workflow](docs/website_export_workflow.md) describe the implemented handoff. The public bundle includes full profiles, fingerprints, neighbours and ten numerical reference comparisons; no frontend is included here.
