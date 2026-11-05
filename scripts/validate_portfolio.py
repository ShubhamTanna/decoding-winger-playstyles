"""Independent reload/semantic checks for website exports against saved research."""
import argparse
import gzip
import hashlib
import subprocess
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd
from portfolio_contract import (ROOT, SOURCES, BUILD_INPUTS, FILES, SCHEMA_VERSION, DATA_VERSION,
    EXPORTER_VERSION, MANIFEST_KEYS, PRECISION, ATOL, RTOL, LABELS, COLORS, KEYS, SPELL_COLUMNS, schemas, read_csv,
    load_sources, feature_metadata, featured_records, comparison_pairs, visualization,
    spell_id, require, canonical, digest)


def exact(a, b, message):
    require(np.array_equal(np.asarray(a), np.asarray(b)), message)


def close(a, b):
    if isinstance(a, dict):
        return isinstance(b, dict) and a.keys() == b.keys() and all(close(v, b[k]) for k, v in a.items())
    if isinstance(a, list):
        return isinstance(b, list) and len(a) == len(b) and all(close(x, y) for x, y in zip(a, b))
    if isinstance(a, (float, int)) and not isinstance(a, bool):
        return isinstance(b, (float, int)) and not isinstance(b, bool) and np.isclose(a, b, atol=ATOL, rtol=RTOL)
    return a == b


def reload_tables(web_root, features):
    return {name: read_csv(Path(web_root) / name, schema) for name, schema in schemas(features).items() if name != "acceptance.csv"}


def compare_tables(d, t):
    """No exporter transform functions are called here."""
    c, f = d["catalog"], d["spec"].feature.tolist()
    ids = [spell_id(row) for row in c[KEYS].itertuples(index=False, name=None)]
    spells, fp, nn, arcs, features = [t[n + ".csv"] for n in ["spells", "fingerprint", "neighbours", "archetypes", "features"]]
    require(len(spells) == 1396 and spells.player_id.nunique() == 665 and spells.spell_id.is_unique, "Spell population or ID uniqueness mismatch")
    exact(spells.spell_id, ids, "Deterministic spell ID/order mismatch")
    for col in SPELL_COLUMNS:
        if col in {"spell_id", "nearest_spell_id"}:
            continue
        exact(spells[col], c[col], f"Original spell values changed: {col}")
    exact(spells.nearest_spell_id, np.array(ids)[c.nearest_candidate_row_idx], "Nearest spell link mismatch")
    require(len(fp) == 27920 and not fp.duplicated(["spell_id", "feature"]).any(), "Fingerprint cardinality mismatch")
    exact(fp.spell_id, np.repeat(ids, 20), "Fingerprint reference/order mismatch")
    for col in fp.columns[1:]:
        exact(fp[col], d["fingerprint"][col], f"Fingerprint values changed: {col}")
    require(len(nn) == 13960, "Neighbour count mismatch")
    exact(nn.target_spell_id, np.array(ids)[d["neighbours"].target_row_idx], "Neighbour target mismatch")
    exact(nn.candidate_spell_id, np.array(ids)[d["neighbours"].candidate_row_idx], "Neighbour candidate mismatch")
    for col in ["rank", "distance"]:
        exact(nn[col], d["neighbours"][col], f"Neighbour {col} changed")
    lookup = spells.set_index("spell_id").player_id
    require(nn.target_spell_id.isin(ids).all() and nn.candidate_spell_id.isin(ids).all(), "Unknown neighbour spell")
    require((nn.target_spell_id.map(lookup) != nn.candidate_spell_id.map(lookup)).all(), "Same-player neighbour")
    require(nn.groupby("target_spell_id").candidate_spell_id.apply(lambda s: s.map(lookup).nunique()).eq(10).all(), "Candidate footballers not distinct")
    exact(arcs.cluster_id, list(range(5)), "Cluster IDs changed")
    exact(arcs.label, LABELS, "Cluster labels changed")
    exact(arcs.color, COLORS, "Cluster colors changed")
    exact(arcs.n_spells, c.k5_cluster.value_counts().sort_index(), "Cluster counts changed")
    exact(arcs[f], d["centroids"][f], "Centroid values changed")
    metadata = feature_metadata(d["spec"])
    for col in metadata:
        exact(features[col], metadata[col], f"Feature metadata changed: {col}")
    # A second arithmetic check uses reloaded web fingerprints, not source vectors.
    X = fp.z_score.to_numpy().reshape(1396, 20)
    distances = np.linalg.norm(X[d["neighbours"].target_row_idx] - X[d["neighbours"].candidate_row_idx], axis=1)
    require(np.allclose(distances, nn.distance, atol=ATOL, rtol=RTOL), "Browser-space neighbour arithmetic mismatch")
    return ids


def comparison(vector_a, vector_b, features, a_id, b_id):
    squared = np.square(vector_a - vector_b)
    order = sorted(range(len(features)), key=lambda i: (-float(squared[i]), i))[:3]
    return {"target_spell_id": a_id, "candidate_spell_id": b_id,
            "distance": float(np.sqrt(squared.sum())),
            "top3": [{"feature": features[i], "squared_contribution": float(squared[i])} for i in order]}


def acceptance_rows(d, t):
    """Expected values come from source tables; actual values from reopened website files."""
    c, f = d["catalog"], d["spec"].feature.tolist()
    s, fp, nn = t["spells.csv"], t["fingerprint.csv"], t["neighbours.csv"]
    ids = [spell_id(row) for row in c[KEYS].itertuples(index=False, name=None)]
    rows = []
    def add(check, entity, field, expected, actual, source):
        rows.append([check, entity, field, canonical(expected), canonical(actual), ATOL, RTOL, bool(close(expected, actual)), source])
    for key, expected, actual in [("spells", len(c), len(s)), ("players", c.player_id.nunique(), s.player_id.nunique()), ("features", len(f), len(t["features.csv"])), ("fingerprints", len(d["fingerprint"]), len(fp)), ("neighbours", len(d["neighbours"]), len(nn)), ("unique_spell_ids", len(c), s.spell_id.nunique())]:
        add("count_" + key, "population", key, int(expected), int(actual), "saved research population")
    add("feature_order", "population", "feature_order", f, t["features.csv"].feature.tolist(), SOURCES["spec"])
    add("cluster_counts", "population", "cluster_counts", [int((c.k5_cluster == i).sum()) for i in range(5)], t["archetypes.csv"].n_spells.tolist(), SOURCES["assignments"])
    for kind, valid in [("fingerprint", fp.spell_id.isin(ids).all()), ("neighbour", nn.target_spell_id.isin(ids).all() and nn.candidate_spell_id.isin(ids).all())]:
        add("references_" + kind, "population", "valid_references", True, bool(valid), SOURCES["catalog"])
    for label, original, exported, source in [
        ("pca", c[[f"PC{i}" for i in range(1,6)]].to_numpy().tolist(), s[[f"PC{i}" for i in range(1,6)]].to_numpy().tolist(), SOURCES["pca"]),
        ("assignments", c.k5_cluster.tolist(), s.k5_cluster.tolist(), SOURCES["assignments"]),
        ("centroids", d["centroids"][f].to_numpy().tolist(), t["archetypes.csv"][f].to_numpy().tolist(), SOURCES["centroids"]),
        ("neighbour_distances", d["neighbours"].distance.tolist(), nn.distance.tolist(), SOURCES["neighbours"]),
        ("percentiles", d["fingerprint"].population_percentile.tolist(), fp.population_percentile.tolist(), SOURCES["fingerprint"]),
    ]:
        hash_value = lambda value: hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()
        add("integrity_" + label, "population", "sha256_canonical_values", hash_value(original), hash_value(exported), source)
    X = d["scaled"][f].to_numpy(dtype=float)
    web_X = fp.z_score.to_numpy(dtype=float).reshape(1396, 20)
    for label, a, b in comparison_pairs(d):
        add("comparison_" + label, ids[a] + "|" + ids[b], "comparison_20d",
            comparison(X[a], X[b], f, ids[a], ids[b]), comparison(web_X[a], web_X[b], f, ids[a], ids[b]), SOURCES["scaled"])
    for featured in featured_records(d):
        i = ids.index(featured["spell_id"])
        original = c.iloc[i]
        actual = s.iloc[i]
        fields = ["k5_cluster", "PC1", "PC2", "k5_centroid_distance", "k5_centroid_margin", "nearest_distance"]
        expected_values = {col: int(original[col]) if col == "k5_cluster" else float(original[col]) for col in fields}
        actual_values = {col: int(actual[col]) if col == "k5_cluster" else float(actual[col]) for col in fields}
        expected_values["nearest_spell_id"] = ids[int(original.nearest_candidate_row_idx)]
        actual_values["nearest_spell_id"] = actual.nearest_spell_id
        add("featured_profile_" + str(i), ids[i], "profile", expected_values, actual_values, SOURCES["catalog"])
        # All 20 percentiles are compact enough and avoid cherry-picked expectations.
        expected_pct = d["fingerprint"].iloc[i*20:(i+1)*20].population_percentile.tolist()
        actual_pct = fp[fp.spell_id.eq(ids[i])].population_percentile.tolist()
        add("featured_percentiles_" + str(i), ids[i], "population_percentiles_feature_order", expected_pct, actual_pct, SOURCES["fingerprint"])
    return rows


def validate(web_root, data_root, allow_dirty=False):
    web_root, data_root = Path(web_root), Path(data_root)
    require(web_root.is_dir(), f"Missing web directory: {web_root}")
    require({p.name for p in web_root.iterdir()} == FILES, "Expected exactly the eight contract files")
    def reject_constant(x):
        raise ValueError(f"Nonfinite JSON constant: {x}")
    m = json.loads((web_root / "manifest.json").read_text(), parse_constant=reject_constant)
    require(set(m) == MANIFEST_KEYS, "Manifest top-level schema mismatch")
    require(type(m["source_tree_dirty"]) is bool, "Invalid dirty marker")
    require(m["precision"] == PRECISION, "Precision policy changed")
    require(m["schema_version"] == SCHEMA_VERSION and m["data_version"] == DATA_VERSION and m["exporter_version"] == EXPORTER_VERSION, "Unsupported release version")
    require(re.fullmatch(r"[0-9a-f]{40}", m["source_commit"]) is not None, "Invalid source commit")
    require(allow_dirty or not m["source_tree_dirty"], "Development build is not publishable")
    d = load_sources(data_root)
    f = d["spec"].feature.tolist()
    require(m["season_bounds"] == ["2017-2018", "2023-2024"] and m["leagues"] == sorted(d["catalog"].comp.unique()), "Manifest coverage mismatch")
    require(m["comparison_scope"] == "retrospective full study period" and m["limitations"] == d["profile_manifest"]["interpretation_limitations"], "Manifest caveats changed")
    require(m["feature_order"] == f and m["family_order"] == list(dict.fromkeys(d["spec"].macro_family)), "Manifest feature/family order changed")
    require(m["archetype_colors"] == {f"C{i}": color for i, color in enumerate(COLORS)} and m["interaction_color"] == "#ff0000", "Manifest colors changed")
    require(m["featured_spells"] == featured_records(d), "Featured manifest references changed")
    require(m["visualization"] == visualization(d), "Visualization bounds/requirements changed")
    require(m["pca_variance"] == d["variance"].to_dict(orient="records"), "PCA variance metadata changed")
    for key, value in {"n_spells":1396,"n_players":665,"n_features":20,"n_clusters":5,"n_neighbours":13960,"n_fingerprint_rows":27920,"top_k":10,"minimum_minutes":1125}.items():
        require(m[key] == value, f"Manifest count changed: {key}")
    require(m["observational_unit"] == "player-club-season spell" and m["primary_similarity"] == "standardized_20d_euclidean" and m["same_player_excluded"] is True, "Manifest method changed")
    expected_sources = {"data/processed/" + rel: digest(data_root / rel) for rel in SOURCES.values()}
    expected_sources.update({rel: digest(ROOT / rel) for rel in BUILD_INPUTS})
    require(m["sources"] == expected_sources, "Source/build provenance hashes changed")
    if not m["source_tree_dirty"]:
        for relative in BUILD_INPUTS:
            result = subprocess.run(["git", "show", f"{m['source_commit']}:{relative}"], cwd=ROOT, capture_output=True)
            require(result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == m["sources"][relative], f"Source commit does not contain build input: {relative}")
    contract = schemas(f)
    require(set(m["files"]) == FILES - {"manifest.json"}, "Manifest file registry changed")
    for name, info in m["files"].items():
        require(info["sha256"] == digest(web_root / name), f"Checksum mismatch: {name}")
        require(info["bytes"] == (web_root / name).stat().st_size, f"Byte size mismatch: {name}")
        if name in contract:
            require(info["schema"] == contract[name], f"Manifest schema mismatch: {name}")
    t = reload_tables(web_root, f)
    compare_tables(d, t)
    acceptance = read_csv(web_root / "acceptance.csv", contract["acceptance.csv"])
    expected = pd.DataFrame(acceptance_rows(d, t), columns=acceptance.columns)
    for col in expected:
        exact(acceptance[col], expected[col], f"Acceptance evidence changed: {col}")
    require(acceptance.passed.all() and acceptance.field.eq("comparison_20d").sum() == 10, "Acceptance cases failed or incomplete")
    for name, table in {**t, "acceptance.csv": acceptance}.items():
        require(m["files"][name]["rows"] == len(table), f"Manifest row count: {name}")
    # Check generated facts against independent saved evidence (not an exporter import).
    facts = (web_root / "facts.md").read_text()
    for value in ["1,396", "665", "1,125", "27 → 21 → 20", "35.56%", "19.32%", "85.23%", "0.149190", "13,960", "27,920"]:
        require(value in facts, f"Missing verified fact: {value}")
    for row in d["robustness"].query("k == 5").itertuples():
        require(f"{row.adjusted_rand_index:.6f}" in facts and f"{row.matched_agreement_pct:.6f}%" in facts, "Robustness fact mismatch")
    for item in featured_records(d):
        require(item["spell_id"] in facts and item["display_name"] in facts, "Featured facts missing")
    sizes = {name: {"bytes": (web_root/name).stat().st_size, "gzip_bytes": len(gzip.compress((web_root/name).read_bytes(), compresslevel=9, mtime=0))} for name in sorted(FILES)}
    return {"status": "passed", "schema_version": SCHEMA_VERSION, "counts": {"spells": 1396, "footballers": 665, "features": 20, "fingerprints": 27920, "neighbours": 13960, "comparison_cases": 10, "acceptance_rows": len(acceptance)}, "exact_source_value_roundtrip": True, "arithmetic_tolerance": {"atol": ATOL, "rtol": RTOL}, "sizes": sizes, "total_bytes": sum(v["bytes"] for v in sizes.values()), "total_gzip_bytes": sum(v["gzip_bytes"] for v in sizes.values()), "visualization": m["visualization"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=ROOT/"data/processed")
    parser.add_argument("--web-root", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true", help="Accept explicitly marked development builds only")
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.web_root, args.data_root, args.allow_dirty), indent=2, ensure_ascii=False))
    except (ValueError, KeyError, FileNotFoundError) as error:
        parser.exit(1, f"Validation failed: {error}\n")


if __name__ == "__main__":
    main()
