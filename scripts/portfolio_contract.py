"""Versioned contract and read-only inputs for the curated portfolio release."""
from pathlib import Path
import csv
import hashlib
import json
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1.1.0"
EXPORTER_VERSION = "1.0.0"
DATA_VERSION = "2017-2024.phase1-final.v1"
ATOL = RTOL = 1e-10
COLORS = ["#b5608f", "#d18b00", "#00876a", "#0068a8", "#3d9fd6"]
LABELS = ["Penalty-area attacking and shooting", "Crossing-oriented wide play", "Deeper passing progression", "Direct carrying and dribbling", "Advanced creative progression"]
KEYS = ["player_id", "squad", "season"]
FEATURED = [
    ("Vinícius Júnior", "Real Madrid", "Vinicius Júnior_2000", "Real Madrid", "2022-2023", 3),
    ("Neymar", "Paris Saint-Germain", "Neymar_1992", "Paris S-G", "2021-2022", 4),
    ("Raphinha", "Leeds United", "Raphinha_1996", "Leeds United", "2020-2021", 1),
]
SOURCES = {
    "spec": "notebook_04_outputs/winger_style_feature_specification.csv",
    "raw": "notebook_04_outputs/winger_style_features_raw.parquet",
    "scaled": "notebook_04_outputs/winger_style_features_scaled.parquet",
    "pca": "notebook_05_outputs/pca_primary_scores.parquet",
    "variance": "notebook_05_outputs/pca_primary_variance.csv",
    "neighbours": "notebook_06_outputs/top10_primary_euclidean.parquet",
    "similarity_manifest": "notebook_06_outputs/similarity_manifest.json",
    "assignments": "notebook_07_outputs/winger_k5_profile_assignments.parquet",
    "centroids": "notebook_07_outputs/winger_k5_centroids_standardized.csv",
    "robustness": "notebook_07_outputs/winger_clustering_robustness.csv",
    "clustering_manifest": "notebook_07_outputs/winger_clustering_manifest.json",
    "catalog": "notebook_08_outputs/winger_player_profile_catalog.parquet",
    "fingerprint": "notebook_08_outputs/winger_player_fingerprint_long.parquet",
    "profile_manifest": "notebook_08_outputs/winger_player_profiles_manifest.json",
}
BUILD_INPUTS = ["docs/feature_dictionary.md", "scripts/portfolio_contract.py", "scripts/export_portfolio.py", "scripts/validate_portfolio.py"]
SPELL_COLUMNS = ["spell_id", "observation_row_idx", "player_id", "player", "squad", "comp", "season", "age", "born", "Minutes", "k5_cluster", "archetype_name", "k5_silhouette", "k5_centroid_distance", "k5_second_centroid_distance", "k5_centroid_margin", "PC1", "PC2", "PC3", "PC4", "PC5", "k5_family_balanced_aligned", "k5_equal_player_weight_aligned", "k5_extreme_trimmed_aligned", "k5_label_preserved_all_three_tests"] + [f"distance_to_cluster_{i}" for i in range(5)] + ["alternative_cluster", "alternative_archetype_name", "alternative_centroid_distance", "centroid_distance_pct_within_cluster", "nearest_spell_id", "nearest_distance", "nearest_distance_population_percentile"]
FEATURE_COLUMNS = ["feature_order", "feature", "display_name", "macro_family", "formula", "source_columns", "denominator", "unit", "interpretation", "limitations", "family_weight", "unit_status", "display_precision", "display_multiplier", "display_suffix"]
FINGERPRINT_COLUMNS = ["spell_id", "feature", "macro_family", "raw_value", "z_score", "population_percentile", "assigned_centroid_z"]
NEIGHBOUR_COLUMNS = ["target_spell_id", "rank", "candidate_spell_id", "distance"]
ACCEPTANCE_COLUMNS = ["check_id", "entity_id", "field", "expected", "actual", "atol", "rtol", "passed", "source_ref"]
FILES = {"manifest.json", "features.csv", "archetypes.csv", "spells.csv", "fingerprint.csv", "neighbours.csv", "acceptance.csv", "facts.md"}
STRING_FIELDS = set("spell_id player_id player squad comp season archetype_name alternative_archetype_name nearest_spell_id feature display_name macro_family formula source_columns denominator unit interpretation limitations unit_status display_suffix label color target_spell_id candidate_spell_id check_id entity_id field expected actual source_ref".split())
INT_FIELDS = set("observation_row_idx age born Minutes k5_cluster k5_family_balanced_aligned k5_equal_player_weight_aligned k5_extreme_trimmed_aligned alternative_cluster feature_order display_precision cluster_id n_spells rank".split())
PRECISION = {"storage": "17 significant digits, float64 round-trip; no analytical rounding", "atol": ATOL, "rtol": RTOL, "display": "features.csv display_multiplier/precision/suffix apply only in UI; distance and z-score display 3 decimals, percentiles 1 decimal"}
MANIFEST_KEYS = set("schema_version data_version exporter_version source_commit source_tree_dirty observational_unit n_spells n_players n_features n_clusters n_neighbours n_fingerprint_rows season_bounds leagues minimum_minutes feature_order family_order pca_variance primary_similarity top_k same_player_excluded comparison_scope archetype_colors interaction_color featured_spells visualization precision limitations sources files".split())
BOOL_FIELDS = {"k5_label_preserved_all_three_tests", "passed"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spell_id(key):
    return "spell_" + hashlib.sha256(canonical(list(key)).encode("utf-8")).hexdigest()


def schemas(features):
    columns = {"features.csv": FEATURE_COLUMNS, "archetypes.csv": ["cluster_id", "label", "color", "n_spells"] + features, "spells.csv": SPELL_COLUMNS, "fingerprint.csv": FINGERPRINT_COLUMNS, "neighbours.csv": NEIGHBOUR_COLUMNS, "acceptance.csv": ACCEPTANCE_COLUMNS}
    return {name: [{"name": c, "type": "string" if c in STRING_FIELDS else "integer" if c in INT_FIELDS else "boolean" if c in BOOL_FIELDS else "number", "nullable": False, **({"allow_empty": True} if c == "display_suffix" else {})} for c in cols] for name, cols in columns.items()}


def read_csv(path, schema):
    """Parse explicitly and reject missing/extra fields, nonfinite values and type drift."""
    with Path(path).open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        require(header == [x["name"] for x in schema], f"Schema/header mismatch: {path.name}")
        rows = []
        for lineno, row in enumerate(reader, 2):
            require(len(row) == len(schema), f"Invalid CSV width: {path.name}:{lineno}")
            parsed = []
            for token, field in zip(row, schema):
                require(token != "" or field.get("allow_empty", False), f"Missing {field['name']}: {path.name}:{lineno}")
                kind = field["type"]
                if kind == "integer":
                    require(re.fullmatch(r"-?(0|[1-9][0-9]*)", token) is not None, f"Invalid integer {field['name']}")
                    value = int(token)
                elif kind == "number":
                    value = float(token)
                    require(np.isfinite(value), f"Nonfinite {field['name']}")
                elif kind == "boolean":
                    require(token in {"true", "false"}, f"Invalid boolean {field['name']}")
                    value = token == "true"
                else:
                    value = token
                parsed.append(value)
            rows.append(parsed)
    return pd.DataFrame(rows, columns=header)


def load_sources(data_root):
    data_root = Path(data_root)
    data = {}
    for key, relative in SOURCES.items():
        path = data_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"Required analytical input missing: {relative}")
        if path.suffix == ".json":
            data[key] = json.loads(path.read_text())
        elif path.suffix == ".parquet":
            data[key] = pd.read_parquet(path)
        else:
            data[key] = pd.read_csv(path, float_precision="round_trip")
    validate_sources(data)
    return data


def validate_sources(d):
    f = d["spec"].feature.tolist()
    require(len(f) == len(set(f)) == 20 and d["spec"].macro_family.nunique() == 8, "Expected 20 ordered features / eight families")
    for manifest, field in [("similarity_manifest", "features"), ("clustering_manifest", "feature_order"), ("profile_manifest", "feature_order")]:
        require(d[manifest][field] == f, f"Feature order mismatch: {manifest}")
    require(d["clustering_manifest"]["provisional_cluster_names"] == {str(i): s for i, s in enumerate(LABELS)}, "Archetype names changed")
    base = d["raw"]
    for key in ["raw", "scaled", "pca", "assignments", "catalog"]:
        t = d[key]
        require(len(t) == 1396 and t.player_id.nunique() == 665, f"Population mismatch: {key}")
        require(not t[KEYS].isna().any().any() and not t.duplicated(KEYS).any(), f"Missing/duplicate identity: {key}")
        require(t[KEYS].reset_index(drop=True).equals(base[KEYS].reset_index(drop=True)), f"Ordered identity mismatch: {key}")
    for key in ["raw", "scaled"]:
        require([c for c in d[key].columns if c in f] == f, f"Matrix order mismatch: {key}")
        require(np.isfinite(d[key][f].to_numpy(dtype=float)).all(), f"Nonfinite matrix: {key}")
    c = d["catalog"]
    for key in ["assignments", "catalog"]:
        require(np.array_equal(d[key].observation_row_idx, np.arange(1396)), f"Observation indices mismatch: {key}")
    require(c.Minutes.ge(1125).all(), "Minutes eligibility mismatch")
    require(sorted(c.season.unique()) == [f"{y}-{y+1}" for y in range(2017, 2024)] and c.comp.nunique() == 5, "Historical coverage mismatch")
    for col in d["assignments"]:
        require(np.array_equal(c[col], d["assignments"][col]), f"Profile assignment drift: {col}")
    for col in [f"PC{i}" for i in range(1, 6)]:
        require(np.array_equal(c[col], d["pca"][col]), f"Saved PCA drift: {col}")
    require(sorted(c.k5_cluster.unique()) == list(range(5)), "Expected original five clusters")
    require(c.archetype_name.tolist() == [LABELS[i] for i in c.k5_cluster], "Profile archetype label mismatch")
    centers = d["centroids"]
    require(centers.columns.tolist() == ["cluster"] + f and centers.cluster.tolist() == list(range(5)), "Centroid schema/order mismatch")
    X = d["scaled"][f].to_numpy(dtype=float)
    dist = np.linalg.norm(X[:, None, :] - centers[f].to_numpy()[None, :, :], axis=2)
    require(np.array_equal(dist.argmin(axis=1), c.k5_cluster), "Centroid assignments mismatch")
    require(np.allclose(dist, c[[f"distance_to_cluster_{i}" for i in range(5)]], atol=ATOL, rtol=RTOL), "Centroid distances mismatch")
    nearest = d["neighbours"]
    require(len(nearest) == 13960, "Neighbour count mismatch")
    for role in ["target", "candidate"]:
        index = nearest[f"{role}_row_idx"].to_numpy()
        require(np.issubdtype(index.dtype, np.integer) and ((index >= 0) & (index < 1396)).all(), "Invalid neighbour index")
        for field in KEYS:
            require(np.array_equal(nearest[f"{role}_{field}"], c[field].to_numpy()[index]), "Neighbour identity mismatch")
    require((nearest.target_player_id != nearest.candidate_player_id).all(), "Same-footballer neighbour")
    require(nearest.groupby("target_row_idx").candidate_player_id.nunique().eq(10).all(), "Nonunique neighbour footballers")
    require(nearest.target_row_idx.tolist() == np.repeat(np.arange(1396), 10).tolist() and nearest['rank'].tolist() == list(range(1, 11)) * 1396, "Neighbour ordering/ranks changed")
    require(nearest.groupby("target_row_idx").distance.apply(lambda x: x.is_monotonic_increasing).all(), "Neighbour distances not ranked")
    require(np.allclose(np.linalg.norm(X[nearest.target_row_idx] - X[nearest.candidate_row_idx], axis=1), nearest.distance, atol=ATOL, rtol=RTOL), "Saved neighbour distance mismatch")
    first = nearest[nearest["rank"].eq(1)]
    require(np.array_equal(first.candidate_row_idx, c.nearest_candidate_row_idx) and np.array_equal(first.distance, c.nearest_distance), "Catalogue first neighbour mismatch")
    sorted_dist = np.sort(dist, axis=1)
    require(np.allclose((sorted_dist[:,1]-sorted_dist[:,0])/sorted_dist[:,1], c.k5_centroid_margin, atol=ATOL, rtol=RTOL), "Centroid margins mismatch")
    require(np.allclose(c.centroid_distance_pct_within_cluster, c.groupby("k5_cluster").k5_centroid_distance.rank(method="average", pct=True)*100, atol=ATOL, rtol=RTOL), "Centroid percentiles changed")
    require(np.allclose(c.nearest_distance_population_percentile, c.nearest_distance.rank(method="average", pct=True)*100, atol=ATOL, rtol=RTOL), "Neighbour percentiles changed")
    fp = d["fingerprint"]
    require(len(fp) == 27920 and fp.feature.tolist() == f * 1396 and np.array_equal(fp.observation_row_idx, np.repeat(np.arange(1396), 20)), "Fingerprint shape/order mismatch")
    for col, values in [("raw_value", d["raw"][f].to_numpy().ravel()), ("z_score", X.ravel())]:
        require(np.array_equal(fp[col], values), f"Fingerprint mismatch: {col}")
    require(np.allclose(fp.population_percentile, d["raw"][f].rank(method="average", pct=True).to_numpy().ravel()*100, atol=ATOL, rtol=RTOL), "Population percentiles changed")
    require(fp.macro_family.tolist() == d["spec"].macro_family.tolist() * 1396, "Fingerprint family mismatch")
    require(np.allclose(fp.assigned_centroid_z, centers[f].to_numpy()[c.k5_cluster].ravel(), atol=ATOL, rtol=RTOL), "Fingerprint centroid mismatch")


def feature_metadata(spec):
    """The reviewed Markdown table is the single human-authored definition source."""
    rows = []
    for line in (ROOT / "docs/feature_dictionary.md").read_text().splitlines():
        if not line.startswith("| `"):
            continue
        cells = [x.strip().strip('`') for x in line.strip().strip('|').split('|')]
        require(len(cells) == 9, "Dictionary schema changed")
        name, label, family, formula, sources, denominator, unit, interpretation, limits = cells
        share = formula.startswith("safe_ratio(")
        rows.append([len(rows), name, label, family, formula, canonical(re.findall(r'`([^`]+)`', line.split(' | ')[4])), denominator, unit, interpretation, limits, float(spec.iloc[len(rows)].family_weight), "unresolved_physical_unit" if name == "avg_shot_distance" else "verified_definition", 1 if share or name == "avg_shot_distance" else 2, 100.0 if share else 1.0, "%" if share else ""])
    result = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    require(result.feature.tolist() == spec.feature.tolist() and result.macro_family.tolist() == spec.macro_family.tolist(), "Dictionary order/families changed")
    require(result.loc[result.feature.eq("cross_pass_share"), "denominator"].iloc[0] == "Total_Att", "Crossing denominator changed")
    return result


def resolve(catalog, key):
    mask = np.ones(len(catalog), dtype=bool)
    for field, value in zip(KEYS, key):
        mask &= catalog[field].eq(value).to_numpy()
    indices = np.flatnonzero(mask)
    require(len(indices) == 1, f"Expected exactly one featured/reference spell: {key}")
    return int(indices[0])


def featured_records(d):
    c = d["catalog"]
    result = []
    for display, display_club, pid, club, season, cluster in FEATURED:
        i = resolve(c, (pid, club, season))
        require(int(c.iloc[i].k5_cluster) == cluster, "Featured archetype mismatch")
        result.append({"display_name": display, "display_club": display_club, "player_id": pid, "squad": club, "season": season, "spell_id": spell_id((pid, club, season)), "cluster_id": cluster})
    return result


def comparison_pairs(d):
    """Ten deterministic reference cases, selected without fitting/reranking a model."""
    c = d["catalog"]
    ids = [resolve(c, (x[2], x[3], x[4])) for x in FEATURED]
    pairs = [(f"featured_nearest_{k+1}", i, int(c.iloc[i].nearest_candidate_row_idx)) for k, i in enumerate(ids)]
    pairs += [("featured_vinicius_neymar", ids[0], ids[1]), ("featured_vinicius_raphinha", ids[0], ids[2]), ("featured_neymar_raphinha", ids[1], ids[2])]
    first = d["neighbours"].query("rank == 1").sort_values(["distance", "target_row_idx"], kind="stable").iloc[0]
    pairs.append(("closest_saved_neighbour", int(first.target_row_idx), int(first.candidate_row_idx)))
    doku = resolve(c, ("Jeremy Doku_2002", "Manchester City", "2023-2024"))
    messi = resolve(c, ("Lionel Messi_1987", "Barcelona", "2018-2019"))
    pairs += [("extreme_doku_vinicius", doku, ids[0]), ("messi_neymar", messi, ids[1])]
    X = d["scaled"][d["spec"].feature].to_numpy(dtype=float)
    distances = np.linalg.norm(X - X[doku], axis=1)
    distances[c.player_id.eq(c.iloc[doku].player_id)] = -np.inf
    pairs.append(("distant_from_doku", doku, int(np.argmax(distances))))
    require(len({tuple(sorted((a, b))) for _, a, b in pairs}) == 10, "Duplicate comparison pairs")
    return pairs


def visualization(d):
    c, fp = d["catalog"], d["fingerprint"]
    return {"pca": {"prototype_pc1": [-8.5, 12.5], "prototype_pc2": [-6.5, 7.0], "observed_pc1": [float(c.PC1.min()), float(c.PC1.max())], "observed_pc2": [float(c.PC2.min()), float(c.PC2.max())], "outside_prototype": int(((c.PC1 < -8.5) | (c.PC1 > 12.5) | (c.PC2 < -6.5) | (c.PC2 > 7)).sum())}, "fingerprint": {"prototype_z": [-3.0, 5.0], "observed_z": [float(fp.z_score.min()), float(fp.z_score.max())], "outside_prototype_feature_rows": int(((fp.z_score < -3) | (fp.z_score > 5)).sum()), "overflow_policy": "Expand the displayed domain to include every selected player and centroid value; never clamp or silently clip. Show the true value in the tooltip.", "player_marker": "archetype-colored dot", "centroid_marker": "open diamond", "reference_band": "grey -1 to +1", "population_mean": 0, "selected_feature_color": "#ff0000"}}
