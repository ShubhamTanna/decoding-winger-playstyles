# Website export workflow and browser handoff

The committed `portfolio/web/` bundle is the public research-to-website interface. Claude can use it without private datasets, fitted models or notebooks. Export implementation is separate from frontend work.

## Build prerequisites and commands

Use the canonical workspace with private saved inputs in `data/processed/` and an existing Python environment containing NumPy, pandas and PyArrow. No scikit-learn/model loading is needed. The tested inspection runtime used Python 3.12, NumPy 2.3.5, pandas 2.2.3 and PyArrow 26.0.1; this does not certify the full notebook environment.

```sh
python3 scripts/validate_research_handoff.py
python3 scripts/test_portfolio.py
python3 scripts/export_portfolio.py --output .local/web-release-a
python3 scripts/validate_portfolio.py --web-root .local/web-release-a
python3 scripts/export_portfolio.py --output .local/web-release-b
```

Output paths must not exist. All source/model files are read-only. The exporter builds in a temporary sibling, reloads and validates every file, checks that source hashes stayed constant, then renames the complete directory into place. A failed build cleans only its own temporary directory. It never overwrites an existing release. `--data-root` accepts another explicitly supplied saved-artifact root.

Commit the four build modules and dictionary before release generation. The exporter records the latest commit affecting these build inputs and verifies their exact bytes. This avoids a self-referential commit hash and keeps builds identical after commits that only add generated outputs or validation reports. `--allow-dirty` is solely for development staging; it marks the manifest as nonpublishable and the pre-commit safeguard rejects it.

Compare the two builds byte-for-byte, validate again, then copy the eight files as a complete bundle to a new `portfolio/web/` directory. For a future replacement, preserve the old release outside the tracked output directory and review the release/version diff; the exporter does not silently overwrite it. Stage explicit files, run `python3 scripts/check_publication.py` and `git diff --cached --check`, and use a development PR.

## Source selection and precision

`scripts/portfolio_contract.py` lists every input explicitly. It uses the full Notebook 08 catalogue and fingerprint table, original Notebook 06 neighbours, Notebook 07 centroids/assignments/robustness, Notebook 05 scores/variance and Notebook 04 raw/scaled/specification tables. No compact-catalogue substitution is made. The finalized Markdown dictionary supplies human-readable metadata and exact denominators.

Analytical floats are serialized with **17 significant digits**, which preserves float64 values exactly after round-trip parsing. CSV source files are read with pandas `float_precision="round_trip"`. There is no lossful export rounding. Float comparisons to source use exact equality; independent arithmetic uses `abs(actual − expected) <= 1e-10 + 1e-10 × abs(expected)`. This is also the browser acceptance tolerance.

Use JavaScript `Number` for numeric cells and an RFC-compatible CSV parser, not string splitting on commas: JSON arrays/objects and text fields are quoted. Parse booleans as the literals `true` and `false`, not JavaScript truthiness of strings. Field types/nullability are in the manifest. Ratios remain raw in fingerprints; apply `display_multiplier`, `display_precision` and `display_suffix` only for display. Z-scores and distances may display three decimal places, percentiles one; calculations always use original stored numbers. `avg_shot_distance` has no asserted metres/yards unit.

## How Claude selects and explains profiles

1. Load `manifest.json` and verify `schema_version` 1.1.0. Follow `featured_spells[].spell_id`; public names/club aliases are separate from canonical matching keys. Neymar's public club name is Paris Saint-Germain; its stored key remains `Paris S-G`.
2. Join `spells.csv` by `spell_id`. Join `fingerprint.csv` by `(spell_id, feature)` and order by `manifest.feature_order`, never alphabetical column order. Every spell has all 20 features. `observation_row_idx` is retained for research auditing but is not a public identity.
3. Match `neighbours.csv` on `target_spell_id`, display ranks 1–10 and resolve each `candidate_spell_id` through spells. Keep the saved distance; do not convert it to percentage similarity. All target-footballer seasons are excluded, and candidate footballers are distinct.
4. Use archetype labels/colors exactly; use original PC1/PC2 for the map. Fingerprint centroid coordinates come from `assigned_centroid_z`, with all five centroid vectors also available in `archetypes.csv`. Read the overflow requirement before choosing axis domains.
5. Use `facts.md` for the Stage 1 case study. Its three examples include exact spell IDs, actual archetype, minutes and saved nearest footballer/distance, with traceable sources. Their complete metrics remain in the same public data tables as every other spell.

## Browser reference calculations

Filter `acceptance.csv` to `field == "comparison_20d"` for exactly ten reference pairs. Decode the `expected` JSON object. Resolve its target and candidate IDs to the 20 z-scores in feature order. For each feature compute the squared difference, sum all 20 and take the square root. Sort contributions descending, breaking ties by original feature order, and compare the largest three to `expected.top3`. Compare the distance and each contribution using the documented tolerance; feature IDs must match exactly.

These cases span very close and distant observations, cross-archetype featured comparisons and an extreme Doku observation. They are tests of the existing representation, not another similarity model. Do not compute from rounded tooltips, percentiles, raw values or PCA scores. The ledger also contains count checks, canonical-value integrity hashes and saved featured-profile/percentile expectations; `actual` values were calculated from reopened website files, while `expected` comes from original analytical artifacts.

## Validation scope

The independent validator does not import exporter transformations. It reloads strictly typed CSVs and compares all projected source values, relationships, centroids, assignments, percentiles, coordinates and ranks to authoritative saved inputs. It validates every manifest source/file hash and the recorded code commit. The exporter uses this validator before publication; tests deliberately alter values and recompute file checksums to ensure semantic checks still catch them.

Tests cover deterministic bytes, round trips, missing files, source identity/feature order, output overwrite protection, cleanup after failed validation and corruptions to distances, same-player candidates, ranks, foreign keys, percentiles, PCA values, duplicate IDs, centroids, headers and acceptance expectations. All source files are hashed before and after tests. A public clone can consume the bundle and reference tests without private data, but rerunning the authoritative Python validator requires those original private artifacts.

Gzip sizes in the validation report are estimates at compression level 9 with deterministic gzip headers; HTTP/CDN settings may produce different transfer sizes. Compression artifacts are not committed. No frontend or deployment is included.
