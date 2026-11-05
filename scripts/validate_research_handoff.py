"""Read-only validation of saved research and Phase 2 documentation; no model loading."""
import ast
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
KEYS = ["player_id", "squad", "season"]
checks = []
consumed = {}


def source(folder, name):
    path = DATA / folder / name
    if not path.is_file():
        raise FileNotFoundError(f"Required private artifact missing: {path.relative_to(ROOT)}")
    consumed[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def table(folder, name):
    path = source(folder, name)
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)


def equal(a, b):
    np.testing.assert_allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float),
                               atol=1e-10, rtol=1e-10)


def pretty(node):
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "df":
        return node.slice.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return pretty(node.left) + " + " + pretty(node.right)
    if isinstance(node, ast.Call) and node.func.id in {"per90", "per_100", "safe_ratio"}:
        return node.func.id + "(" + ", ".join(pretty(a) for a in node.args) + ")"
    raise ValueError("Unexpected feature expression")


def evaluate(node, enriched):
    if isinstance(node, ast.Subscript):
        pretty(node)  # Validate allowed source expression.
        return enriched[node.slice.value].to_numpy(dtype=float)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return evaluate(node.left, enriched) + evaluate(node.right, enriched)
    if isinstance(node, ast.Call):
        pretty(node)
        a, b = [evaluate(arg, enriched) for arg in node.args]
        result = np.divide(a, b, out=np.full_like(a, np.nan), where=b > 0)
        return result * {"per90": 90, "per_100": 100, "safe_ratio": 1}[node.func.id]
    raise ValueError("Unexpected feature expression")


def main():
    n04, n05, n06, n07, n08 = [f"notebook_{i:02}_outputs" for i in range(4, 9)]
    spec = table(n04, "winger_style_feature_specification.csv")
    features = spec.feature.tolist()
    raw = table(n04, "winger_style_features_raw.parquet")
    scaled = table(n04, "winger_style_features_scaled.parquet")
    balanced = table(n04, "winger_style_features_family_balanced.parquet")
    enriched = table("notebook_01_-_03_outputs", "fbref_2017_2024_wingers_enriched.parquet")
    scores = table(n05, "pca_primary_scores.parquet")
    assignments = table(n07, "winger_k5_profile_assignments.parquet")
    catalog = table(n08, "winger_player_profile_catalog.parquet")
    fingerprints = table(n08, "winger_player_fingerprint_long.parquet")
    neighbours = table(n06, "top10_primary_euclidean.parquet")
    assert len(features) == 20 and len(set(features)) == 20
    assert spec.macro_family.nunique() == 8
    assert "progressive_distance_per_carry" not in features
    for df in [enriched, raw, scaled, balanced, scores, assignments, catalog]:
        assert len(df) == 1396 and df.player_id.nunique() == 665
        assert not df[KEYS].isna().any().any() and not df.duplicated(KEYS).any()
        pd.testing.assert_frame_equal(df[KEYS].reset_index(drop=True), raw[KEYS].reset_index(drop=True), check_dtype=False)
    for df in [raw, scaled, balanced]:
        assert [c for c in df.columns if c in features] == features
    for df in [assignments, catalog]:
        assert np.array_equal(df.observation_row_idx, np.arange(1396))
    assert enriched.Minutes.ge(1125).all()
    assert enriched.season.nunique() == 7 and enriched.comp.nunique() == 5
    assert sorted(enriched.season.unique()) == [f"{y}-{y+1}" for y in range(2017, 2024)]
    for folder, name, key in [(n06, "similarity_manifest.json", "features"),
                               (n07, "winger_clustering_manifest.json", "feature_order"),
                               (n08, "winger_player_profiles_manifest.json", "feature_order")]:
        manifest = json.loads(source(folder, name).read_text())
        assert manifest[key] == features
    checks.append("Population, feature order, manifests and ordered identities agree")

    notebook = json.loads((ROOT / "notebooks/04_playstyle_feature_engineering.ipynb").read_text())
    expressions = {}
    for idx in [11, 23, 37, 62, 82, 98]:
        for node in ast.parse("".join(notebook["cells"][idx]["source"])).body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript):
                expressions[node.targets[0].slice.value] = node.value
    dictionary = (ROOT / "docs/feature_dictionary.md").read_text()
    rows = [line.split(" | ") for line in dictionary.splitlines() if line.startswith("| `")]
    assert [row[0].removeprefix("| `").removesuffix("`") for row in rows] == features
    for feature, family, row in zip(features, spec.macro_family, rows):
        expression = expressions[feature]
        assert row[2] == family and row[3] == f"`{pretty(expression)}`"
        sources = list(dict.fromkeys(node.slice.value for node in ast.walk(expression) if isinstance(node, ast.Subscript)))
        assert row[4] == ", ".join(f"`{column}`" for column in sources)
        denominator = pretty(expression.args[1]) if isinstance(expression, ast.Call) else "None (source aggregate)"
        assert row[5] == f"`{denominator}`"
        equal(evaluate(expressions[feature], enriched), raw[feature])
    decisions = table(n04, "winger_style_feature_decisions.csv")
    assert len(decisions) == 27 and decisions.decision.eq("Retain").sum() == 20
    assert decisions.loc[decisions.feature.eq("progressive_distance_per_carry"), "decision"].iloc[0] == "Drop"
    assert "Total_Att" in pretty(expressions["cross_pass_share"])
    X = scaled[features].to_numpy(dtype=float)
    R = raw[features].to_numpy(dtype=float)
    assert np.isfinite(X).all() and np.isfinite(R).all()
    equal((R - R.mean(axis=0)) / R.std(axis=0, ddof=0), X)
    equal(balanced[features], X * spec.family_weight.to_numpy())
    checks.append("All 20 dictionary formulas reproduce saved values; scaling and family weights agree")

    coefficients = pd.read_csv(source(n05, "pca_primary_coefficients.csv"), index_col=0).loc[features]
    equal((X - X.mean(axis=0)) @ coefficients.to_numpy(), scores[[f"PC{i}" for i in range(1, 21)]])
    equal(catalog[[f"PC{i}" for i in range(1, 6)]], scores[[f"PC{i}" for i in range(1, 6)]])
    variance = table(n05, "pca_primary_variance.csv")
    assert [round(variance.explained_variance_pct.iloc[i], 2) for i in [0, 1]] == [35.56, 19.32]
    assert round(variance.cumulative_variance_pct.iloc[4], 2) == 85.23
    centroids = table(n07, "winger_k5_centroids_standardized.csv").sort_values("cluster")
    assert centroids.cluster.tolist() == list(range(5))
    distances = np.linalg.norm(X[:, None, :] - centroids[features].to_numpy()[None, :, :], axis=2)
    assert np.array_equal(distances.argmin(axis=1), catalog.k5_cluster)
    assert np.array_equal(assignments.k5_cluster, catalog.k5_cluster)
    for column in assignments.columns:
        pd.testing.assert_series_equal(assignments[column], catalog[column], check_dtype=False)
    equal(distances, catalog[[f"distance_to_cluster_{i}" for i in range(5)]])
    sorted_distances = np.sort(distances, axis=1)
    equal((sorted_distances[:, 1] - sorted_distances[:, 0]) / sorted_distances[:, 1], catalog.k5_centroid_margin)
    counts = catalog.k5_cluster.value_counts().sort_index().to_dict()
    assert counts == {0: 352, 1: 291, 2: 278, 3: 266, 4: 209}
    assert round(catalog.k5_silhouette.mean(), 10) == 0.1491902281
    robust = table(n07, "winger_clustering_robustness.csv").query("k == 5")
    expected = {"family_balanced": (0.831241, 92.406877), "equal_player_weight": (0.708791, 87.320917), "extreme_trimmed": (0.911529, 96.060172)}
    for row in robust.itertuples():
        assert (round(row.adjusted_rand_index, 6), round(row.matched_agreement_pct, 6)) == expected[row.test]
    checks.append("PCA, five original assignments, centroid margins and documented robustness figures agree")

    assert len(neighbours) == 13960
    target = neighbours.target_row_idx.to_numpy(dtype=int)
    candidate = neighbours.candidate_row_idx.to_numpy(dtype=int)
    assert ((target >= 0) & (target < 1396) & (candidate >= 0) & (candidate < 1396)).all()
    for role, indices in [("target", target), ("candidate", candidate)]:
        for column in ["player_id", "player", "squad", "season"]:
            assert np.array_equal(neighbours[f"{role}_{column}"], raw[column].to_numpy()[indices])
    assert (neighbours.target_player_id != neighbours.candidate_player_id).all()
    assert neighbours.groupby("target_row_idx").candidate_player_id.nunique().eq(10).all()
    for _, group in neighbours.groupby("target_row_idx"):
        assert group.sort_values("rank")["rank"].tolist() == list(range(1, 11))
        assert group.sort_values("rank").distance.is_monotonic_increasing
    equal(np.linalg.norm(X[target] - X[candidate], axis=1), neighbours.distance)
    first = neighbours.query("rank == 1").sort_values("target_row_idx")
    equal(first.distance, catalog.nearest_distance)
    assert np.array_equal(first.candidate_row_idx, catalog.nearest_candidate_row_idx)
    assert len(fingerprints) == 27920 and not fingerprints.duplicated(["observation_row_idx", "feature"]).any()
    assert np.array_equal(fingerprints.observation_row_idx, np.repeat(np.arange(1396), 20))
    assert fingerprints.feature.tolist() == features * 1396
    equal(fingerprints.raw_value, R.reshape(-1))
    equal(fingerprints.z_score, X.reshape(-1))
    equal(fingerprints.population_percentile, raw[features].rank(method="average", pct=True).to_numpy().reshape(-1) * 100)
    equal(fingerprints.assigned_centroid_z, centroids[features].to_numpy()[catalog.k5_cluster].reshape(-1))
    equal(catalog.nearest_distance_population_percentile, catalog.nearest_distance.rank(method="average", pct=True) * 100)
    equal(catalog.centroid_distance_pct_within_cluster, catalog.groupby("k5_cluster").k5_centroid_distance.rank(method="average", pct=True) * 100)
    checks.append("Original neighbour distances/ranks and complete fingerprints/profile percentiles agree")

    featured = []
    for pid, club, season, idx, cluster, distance in [
        ("Vinicius Júnior_2000", "Real Madrid", "2022-2023", 1087, 3, 3.406777),
        ("Neymar_1992", "Paris S-G", "2021-2022", 930, 4, 1.589447),
        ("Raphinha_1996", "Leeds United", "2020-2021", 751, 1, 2.081936),
    ]:
        matches = catalog[catalog.player_id.eq(pid) & catalog.squad.eq(club) & catalog.season.eq(season)]
        assert len(matches) == 1
        row = matches.iloc[0]
        assert row.observation_row_idx == idx and row.k5_cluster == cluster
        assert round(row.nearest_distance, 6) == distance
        featured.append({"player_id": pid, "squad": club, "season": season, "row": idx, "cluster": cluster,
                         "nearest_player": row.nearest_player, "nearest_distance": float(row.nearest_distance)})
    # Check documented numerical tokens, not just independently computed expectations.
    readme = (ROOT / "README.md").read_text()
    methodology = (ROOT / "docs/methodology.md").read_text()
    architecture = (ROOT / "docs/portfolio_export_architecture.md").read_text()
    for value in ["1,396", "665", "1,125", "35.56%", "19.32%", "85.23%", "13,960", "0.149", "27,920"]:
        assert value in readme
    for _, (ari, agreement) in expected.items():
        assert f"{ari:.6f}" in methodology and f"{agreement:.6f}%" in methodology
    for row in featured:
        assert row["player_id"] in architecture and f"{row['nearest_distance']:.6f}" in architecture
        assert row["nearest_player"] in architecture
    for color in ["#b5608f", "#d18b00", "#00876a", "#0068a8", "#3d9fd6", "#ff0000"]:
        assert color in architecture
    checks.append("Featured spells and numerical documentation claims match saved evidence")
    print(json.dumps({"checks": checks, "counts": {"spells": 1396, "players": 665, "features": 20,
          "fingerprints": len(fingerprints), "neighbours": len(neighbours)}, "cluster_counts": counts,
          "mean_saved_silhouette": float(catalog.k5_silhouette.mean()), "featured": featured,
          "source_sha256": consumed, "not_run": ["model fitting", "full notebook execution", "full neighbour reranking", "website export"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
