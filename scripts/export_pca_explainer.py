"""Build a local PC1–PC3 explanation from saved primary PCA tables. No model fitting."""
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "portfolio/web"
SOURCE = ROOT / "data/processed/notebook_05_outputs"
OUTPUT = ROOT / "outputs/frontend-research-support/pca_explainer.json"
PCS = ("PC1", "PC2", "PC3")


def read_rows(path):
    with path.open(encoding="utf8", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(actual, expected, context):
    if not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10):
        raise ValueError(f"{context}: {actual} differs from {expected}")


def build():
    manifest_path = WEB / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    order = manifest["feature_order"]
    if manifest["schema_version"] != "1.1.0" or len(set(order)) != 20 or len(order) != 20:
        raise ValueError("Unexpected website schema or feature order")
    sources = {str(manifest_path.relative_to(ROOT)): digest(manifest_path)}
    tables = {}
    for key in ("coefficients", "feature_correlations", "variance"):
        path = SOURCE / f"pca_primary_{key}.csv"
        sources[str(path.relative_to(ROOT))] = digest(path)
        tables[key] = read_rows(path)
        if key != "variance" and [r["feature"] for r in tables[key]] != order:
            raise ValueError(f"{key}: features differ from manifest order")
    for name in ("spells.csv", "fingerprint.csv"):
        if digest(WEB / name) != manifest["files"][name]["sha256"]:
            raise ValueError(f"{name} differs from website manifest")
    spells = read_rows(WEB / "spells.csv")
    ids = [s["spell_id"] for s in spells]
    profiles = {key: {} for key in ids}
    if len(ids) != len(profiles) or len(ids) != 1396:
        raise ValueError("Unexpected spell identities")
    for row in read_rows(WEB / "fingerprint.csv"):
        profile = profiles[row["spell_id"]]
        feature = row["feature"]
        if feature in profile:
            raise ValueError(f"Duplicate feature {feature} for {row['spell_id']}")
        profile[feature] = float(row["z_score"])
    if any(set(profile) != set(order) for profile in profiles.values()):
        raise ValueError("Incomplete standardized profile")
    columns = [[profiles[key][feature] for key in ids] for feature in order]
    means = [statistics.fmean(values) for values in columns]
    for feature, values, mean in zip(order, columns, means):
        close(mean, 0, feature + " mean")
        close(statistics.pstdev(values), 1, feature + " population SD")
    variances = {r["component"]: r for r in tables["variance"]}
    components = []
    max_error = 0.0
    for pc in PCS:
        scores = [float(s[pc]) for s in spells]
        weights = [float(r[pc]) for r in tables["coefficients"]]
        correlations = [float(r[pc]) for r in tables["feature_correlations"]]
        close(math.fsum(x*x for x in weights), 1, pc + " coefficient norm")
        variance = float(variances[pc]["explained_variance_ratio"])
        close(statistics.pvariance(scores) / len(order), variance, pc + " variance share")
        close(variance, next(r["explained_variance_ratio"] for r in manifest["pca_variance"]
                             if r["component"] == pc), pc + " website variance share")
        for feature, values, correlation in zip(order, columns, correlations):
            close(statistics.correlation(values, scores), correlation, pc + "/" + feature)
        for key, score in zip(ids, scores):
            replay = math.fsum((profiles[key][f] - mean) * w
                               for f, mean, w in zip(order, means, weights))
            close(replay, score, pc + "/" + key)
            max_error = max(max_error, abs(replay - score))
        components.append({"component": pc, "explained_variance_ratio": variance,
                           "coefficients": weights, "feature_score_correlations": correlations})
    print(f"Validated 60 correlations and 4,188 signed scores; max absolute error {max_error:.3g}")
    return {"extension_version": "1.0.0", "base_schema_version": manifest["schema_version"],
            "data_version": manifest["data_version"], "sources_sha256": sources,
            "feature_order": order, "components": components}


def main():
    payload = build()
    encoded = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(encoded, encoding="utf8")
    print(f"{OUTPUT.relative_to(ROOT)} · SHA-256 {digest(OUTPUT)}")


if __name__ == "__main__":
    main()
