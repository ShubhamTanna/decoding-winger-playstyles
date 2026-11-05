"""Export eight curated website files from saved analytical tables, without fitting models."""
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import numpy as np
import pandas as pd
from portfolio_contract import (ROOT, SOURCES, BUILD_INPUTS, FILES, SCHEMA_VERSION, DATA_VERSION,
    EXPORTER_VERSION, PRECISION, LABELS, COLORS, KEYS, SPELL_COLUMNS, FINGERPRINT_COLUMNS,
    NEIGHBOUR_COLUMNS, ACCEPTANCE_COLUMNS, ATOL, RTOL, schemas, load_sources,
    feature_metadata, featured_records, visualization, spell_id, require, digest)
from validate_portfolio import reload_tables, compare_tables, acceptance_rows, validate


def write_csv(path, frame):
    def token(value):
        if isinstance(value, (bool, np.bool_)):
            return "true" if value else "false"
        if isinstance(value, (float, np.floating)):
            require(np.isfinite(value), f"Cannot export nonfinite number: {path.name}")
            return format(float(value), ".17g")
        if isinstance(value, (int, np.integer)):
            return str(int(value))
        require(isinstance(value, str), f"Unsupported or missing value: {path.name}")
        return value
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(frame.columns)
        for row in frame.itertuples(index=False, name=None):
            writer.writerow([token(v) for v in row])


def facts_text(d, featured):
    c, variance = d["catalog"], d["variance"]
    counts = c.k5_cluster.value_counts().sort_index()
    lines = ["# Decoding Winger Playstyles — verified website facts", "",
        "## Scope and methods", "",
        f"The historical population contains **{len(c):,} player-club-season spells** from **{c.player_id.nunique():,} distinct footballers**, covering 2017–18 through 2023–24 in the Premier League, La Liga, Bundesliga, Serie A and Ligue 1. Source: `notebook_08_outputs/winger_player_profile_catalog.parquet`, identity and season fields.", "",
        "Eligibility requires at least **1,125 minutes per spell** and LW/RW/LM/RM eligibility from historical primary or club positions, supplemented by completed manual verification. Source: Notebook 02, minutes filter and final positional selection (see `docs/methodology.md`). A transferred player can contribute separate club spells; a spell is not a unique footballer.", "",
        "Feature selection follows **27 → 21 → 20**: initial candidates, provisional features, then the final 20 features across eight families. Notebook 04 cell 226 removes `progressive_distance_per_carry` because of overlap with progressive-carry volume and share. Formulas are in `features.csv` and `docs/feature_dictionary.md`; `cross_pass_share` uses donor `Total_Att`. Average shot distance remains source-reported distance with its physical unit unresolved.", "",
        f"PCA variance: PC1 **{variance.explained_variance_pct.iloc[0]:.2f}%**, PC2 **{variance.explained_variance_pct.iloc[1]:.2f}%**; first five PCs **{variance.cumulative_variance_pct.iloc[4]:.2f}%** cumulatively. Source: `notebook_05_outputs/pca_primary_variance.csv`. The map preserves saved coordinates; it is not the primary distance metric.", "",
        f"Primary similarity is Euclidean distance across all 20 globally standardized features. Each spell has ten nearest distinct footballers, excluding all spells of the target footballer: **{len(d['neighbours']):,} neighbour records**. Source: `notebook_06_outputs/top10_primary_euclidean.parquet` and `similarity_manifest.json`. The retrospective pool includes the entire study period; distances are not similarity percentages or time-safe scouting forecasts.", "",
        f"The profile export contains **{len(d['fingerprint']):,} feature-level fingerprint records**. Percentiles use average ranks over all 1,396 spells, not equal weight per footballer. Source: `notebook_08_outputs/winger_player_fingerprint_long.parquet` and the profile manifest.", "",
        "## Working descriptive archetypes", "", "| Cluster | Name | Spells | Color |", "|---|---|---:|---|"]
    for i in range(5):
        lines.append(f"| C{i} | {LABELS[i]} | {counts[i]} | `{COLORS[i]}` |")
    lines += ["", f"Mean saved silhouette: **{c.k5_silhouette.mean():.6f}**. Source: the Notebook 07 assignments and Notebook 08 catalogue; labels and settings: `winger_clustering_manifest.json`. K=5 is a working descriptive model, not an objectively optimal natural classification. Boundaries overlap; centroid margins are geometric diagnostics, not membership probabilities.", "", "## Completed robustness experiments", "", "| K=5 sensitivity test | Adjusted Rand index | Matched agreement |", "|---|---:|---:|"]
    for row in d["robustness"].query("k == 5").itertuples():
        lines.append(f"| {row.test} | {row.adjusted_rand_index:.6f} | {row.matched_agreement_pct:.6f}% |")
    lines += ["", "Source: `notebook_07_outputs/winger_clustering_robustness.csv`. Tests use family-balanced features, equal total weight per footballer and exclusion of observations above the 99th percentile of standardized-vector norm during the alternative fit. Original assignments remain authoritative. These are completed research findings, not models fitted by the website exporter.", "", "## Featured historical profiles", ""]
    for record in featured:
        mask = np.logical_and.reduce([c[k].eq(record[k]) for k in KEYS])
        row = c.loc[mask].iloc[0]
        lines += [f"### {record['display_name']} — {record['display_club']}, {record['season']}", "",
            f"Spell: `{record['spell_id']}`. Canonical key: `{row.player_id}` / `{row.squad}` / `{row.season}`.", "",
            f"Primary archetype: **C{row.k5_cluster} — {row.archetype_name}**. Recorded minutes: **{row.Minutes:,}**. Closest historical footballer: **{row.nearest_player}**, {row.nearest_squad}, {row.nearest_season}; Euclidean distance **{row.nearest_distance:.6f}**. Source: `notebook_08_outputs/winger_player_profile_catalog.parquet` and the primary neighbour export. Join this spell ID to `spells.csv`, all 20 rows in `fingerprint.csv` and its ten rows in `neighbours.csv`; do not hardcode an observation index.", ""]
    lines += ["## Interpretation and sources", "",
        "These measurements describe attacking style, not player quality, finishing ability, team fit or recruitment success. Team context, source definitions and repeated seasons affect the population. Feature values are not clipped; display formatting must not alter stored data. Selection uses red `#ff0000`, never a sixth archetype color.", "",
        "Statistical attribution: [likely initial Kaggle distribution](https://www.kaggle.com/datasets/akshankrithick/fbref-2017-2024-for-europes-top-5-leagues) and [enrichment distribution](https://www.kaggle.com/datasets/emrey3lmaz/top-5-league-football-player-stats-2017-2025), both FBref-derived. Auxiliary positions use historical FIFA/SoFIFA and completed manual decisions. Original download versions/dates are not fully established; see `docs/provenance.md`. Relative research source paths in this fact sheet refer to private artifacts whose hashes are recorded in `manifest.json`; consuming these website files does not require access to those private sources.", ""]
    return "\n".join(lines)


def build(output, data_root, allow_dirty=False):
    output, data_root = Path(output).resolve(), Path(data_root).resolve()
    require(output != ROOT, "Cannot replace repository root")
    protected = [data_root, ROOT/"data", ROOT/".local/research-snapshot", ROOT/"notebooks", ROOT/"scripts", ROOT/"docs", ROOT/".git"]
    require(not any(output == p or p in output.parents for p in protected), "Output overlaps protected research/source directory")
    require(not output.exists(), "Output already exists; choose a new staging directory (no overwrites)")
    d = load_sources(data_root)
    commit = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", *BUILD_INPUTS], cwd=ROOT, text=True).strip()
    dirty = False
    for relative in BUILD_INPUTS:
        tracked = subprocess.run(["git", "show", f"{commit}:{relative}"], cwd=ROOT, capture_output=True)
        dirty |= tracked.returncode != 0 or tracked.stdout != (ROOT/relative).read_bytes()
    require(allow_dirty or not dirty, "Commit exporter inputs before release build; --allow-dirty is development-only")
    source_hashes = {"data/processed/"+rel: digest(data_root/rel) for rel in SOURCES.values()}
    source_hashes.update({rel: digest(ROOT/rel) for rel in BUILD_INPUTS})
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".web-build-", dir=output.parent))
    try:
        f, c = d["spec"].feature.tolist(), d["catalog"]
        ids = [spell_id(row) for row in c[KEYS].itertuples(index=False, name=None)]
        require(len(ids) == len(set(ids)), "Spell ID collision")
        spells = c.copy()
        spells.insert(0, "spell_id", ids)
        spells["nearest_spell_id"] = np.array(ids)[c.nearest_candidate_row_idx]
        fp = d["fingerprint"].copy()
        fp["spell_id"] = np.array(ids)[fp.observation_row_idx]
        nn = d["neighbours"].copy()
        nn["target_spell_id"] = np.array(ids)[nn.target_row_idx]
        nn["candidate_spell_id"] = np.array(ids)[nn.candidate_row_idx]
        arcs = d["centroids"].rename(columns={"cluster":"cluster_id"}).copy()
        arcs.insert(1, "label", LABELS)
        arcs.insert(2, "color", COLORS)
        arcs.insert(3, "n_spells", c.k5_cluster.value_counts().sort_index().to_numpy())
        tables = {"features.csv": feature_metadata(d["spec"]), "spells.csv": spells[SPELL_COLUMNS], "fingerprint.csv": fp[FINGERPRINT_COLUMNS], "neighbours.csv": nn[NEIGHBOUR_COLUMNS], "archetypes.csv": arcs}
        for name, frame in tables.items():
            write_csv(stage/name, frame)
        # Independent parser/semantic comparison is deliberately before acceptance generation.
        reopened = reload_tables(stage, f)
        compare_tables(d, reopened)
        acceptance = pd.DataFrame(acceptance_rows(d, reopened), columns=ACCEPTANCE_COLUMNS)
        require(acceptance.passed.all(), "Acceptance calculation failed")
        write_csv(stage/"acceptance.csv", acceptance)
        tables["acceptance.csv"] = acceptance
        featured = featured_records(d)
        (stage/"facts.md").write_text(facts_text(d, featured), encoding="utf-8")
        contract = schemas(f)
        file_info = {name: {"sha256": digest(stage/name), "bytes": (stage/name).stat().st_size,
                     **({"rows": len(tables[name]), "schema": contract[name]} if name in tables else {"media_type":"text/markdown"})} for name in sorted(FILES-{"manifest.json"})}
        m = {"schema_version":SCHEMA_VERSION,"data_version":DATA_VERSION,"exporter_version":EXPORTER_VERSION,
             "source_commit":commit,"source_tree_dirty":bool(dirty),"observational_unit":"player-club-season spell",
             "n_spells":1396,"n_players":665,"n_features":20,"n_clusters":5,"n_neighbours":13960,"n_fingerprint_rows":27920,
             "season_bounds":["2017-2018","2023-2024"],"leagues":sorted(c.comp.unique()),"minimum_minutes":1125,
             "feature_order":f,"family_order":list(dict.fromkeys(d["spec"].macro_family)),
             "pca_variance":d["variance"].to_dict(orient="records"),"primary_similarity":"standardized_20d_euclidean",
             "top_k":10,"same_player_excluded":True,"comparison_scope":"retrospective full study period",
             "archetype_colors":{f"C{i}":color for i,color in enumerate(COLORS)},"interaction_color":"#ff0000",
             "featured_spells":featured,"visualization":visualization(d),
             "precision": PRECISION,
             "limitations":d["profile_manifest"]["interpretation_limitations"],
             "sources":source_hashes,"files":file_info}
        (stage/"manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)+"\n", encoding="utf-8")
        report = validate(stage, data_root, allow_dirty)
        # Refuse sources changed while the build was running.
        for relative, before in source_hashes.items():
            path = data_root/relative.removeprefix("data/processed/") if relative.startswith("data/processed/") else ROOT/relative
            require(digest(path) == before, f"Source changed during build: {relative}")
        require(not output.exists(), "Output appeared during build; refusing replacement")
        os.rename(stage, output)
        return report
    except BaseException:
        shutil.rmtree(stage)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=ROOT/"data/processed")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true", help="Mark a staging build as development-only")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output, args.data_root, args.allow_dirty), indent=2, ensure_ascii=False))
    except (ValueError, KeyError, FileNotFoundError) as error:
        parser.exit(1, f"Export failed: {error}\n")


if __name__ == "__main__":
    main()
