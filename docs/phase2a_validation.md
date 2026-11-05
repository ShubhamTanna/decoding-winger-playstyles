# Phase 2A validation record

Validated 5 November 2026 against the saved artifacts in the canonical workspace. These are consistency checks, not a fresh execution of the research pipeline.

## Setup review

[PR #1](https://github.com/ShubhamTanna/decoding-winger-playstyles/pull/1) was reviewed at head `b517a78d1c0ee53aa88857358def41db4609a0de`. GitHub reported it mergeable with no reviews or automated status checks. Local publication checks passed, all eight published notebook cell sources matched the approved executed snapshot, and all local data matched the preserved snapshot. The PR was marked ready and merged through GitHub at `37821712e557be0ff5c5e2c4e5b7c7e88457fa17`; Phase 2 work starts on `codex/phase2-research-handoff` from that merge. No direct push to main or history rewrite was used.

The safeguards exclude data, snapshots, models, backups and generated exports, strip public notebook output state, and inspect indexed files for unexpected paths, size and common credential patterns. They are practical checks, not a complete secret scanner. Existing historical notebook outputs remain in earlier Git history. The Phase 2 allowlist adds only six documentation files and one read-only validation script.

## Saved-artifact checks

| Check | Result |
|---|---|
| Population and identities | 1,396 unique player-club-season keys; 665 footballers; seven seasons/five leagues; all qualifying minutes at least 1,125; ordered keys agree across representations and profiles |
| Feature dictionary | All 20 names, families, formulas, source columns and denominators match implemented Notebook 04 expressions and final feature order |
| Feature arithmetic | All 20 raw columns agree with formulas evaluated in memory; primary standardization and family balancing agree with saved matrices |
| PCA | Saved coefficient arithmetic agrees with scores; profile PC1–PC5 agree; documented 35.56%, 19.32% and cumulative 85.23% checked |
| Clusters | Five original labels agree with saved nearest centroids; centroid distances/margins and assignment fields agree with catalogue; counts 352/291/278/266/209; mean saved silhouette 0.1491902281 |
| Robustness | Documented ARI and matched-agreement figures agree with the saved K=5 robustness table |
| Neighbours | 13,960 rows; ranks 1–10 per target; ten distinct candidate footballers; same-player exclusion; stored distances agree with 20-dimensional pair arithmetic |
| Profiles/fingerprints | 1,396 profiles; 27,920 feature rows; raw values, z-scores, centroid fingerprints and average-rank percentiles agree |
| Featured spells | Exact keys resolve uniquely for Vinícius Júnior / Real Madrid / 2022–23, Neymar / Paris S-G / 2021–22 and Raphinha / Leeds United / 2020–21; labels and neighbour examples agree |
| Preservation | Local data remains byte-identical to the preserved snapshot, including source files, manual decisions, model binaries and analytical exports; public notebooks remain unchanged from merged setup |

The validator prints consumed source SHA-256 values and a summary. It uses NumPy/pandas/PyArrow in an existing inspection runtime; no dependency installation or environment certification is implied. It does not deserialize fitted models. Floating-point arithmetic checks use explicit 1e-10 absolute and relative tolerances; source preservation is additionally checked by byte comparison against the private snapshot.

Negative checks confirmed rejection of reversed standardized-observation order, an altered neighbour distance and an incorrect documented crossing-share denominator. Formula helper checks confirmed missing values for zero/negative denominators and rejection of unrecognized formula calls. Documentation-formula checks and local Markdown link checks form part of the handoff review. No new statistical experiment was performed.

## Not established by this validation

- Full fresh-kernel reproduction of raw preprocessing, identity matching, model fitting or every notebook display.
- Independent reconstruction of all historical manual verification evidence or original download dates/versions.
- A physical unit for donor `Standard_Dist`; it remains source-reported distance with an unresolved unit.
- Website serialization round trips or two-build determinism: these are specified Phase 2B gates, not completed tests of an exporter that does not yet exist.
- A final portfolio project route; the README links to the supplied portfolio domain and labels the project page as planned.

## Recommended Phase 2B scope

Review the proposed schema, implement the small saved-artifact exporter and independent round-trip validator in isolated ignored output directories, validate featured spell acceptance cases and deterministic builds, then review publication before promoting generated data into `portfolio/web/`. Keep source inputs, analytical outputs and models unchanged. Frontend implementation remains separate.
