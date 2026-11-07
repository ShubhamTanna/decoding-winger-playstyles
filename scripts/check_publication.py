"""Validate staged publication files without executing research notebooks."""
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath


def git(*args):
    return subprocess.check_output(["git", *args])


allowed = {".gitignore", "AGENTS.md", "README.md", "LICENSE", "requirements.txt",
           "docs/environment.md", "docs/local-workflow.md",
           "docs/case_study_fact_sheet.md", "docs/explorer_copy_audit.md",
           "docs/frontend_research_support.md", "scripts/export_pca_explainer.py",
           "docs/feature_dictionary.md", "docs/methodology.md",
           "docs/reproducibility.md", "docs/provenance.md",
           "docs/portfolio_export_architecture.md", "docs/phase2a_validation.md",
           "scripts/validate_research_handoff.py",
           "scripts/portfolio_contract.py", "scripts/export_portfolio.py",
           "scripts/validate_portfolio.py", "scripts/test_portfolio.py",
           "docs/website_export_workflow.md", "docs/phase2b_validation.md",
           ".githooks/pre-commit", "scripts/check_publication.py"}
web_files = {"portfolio/web/" + name for name in [
    "manifest.json", "features.csv", "archetypes.csv", "spells.csv",
    "fingerprint.csv", "neighbours.csv", "acceptance.csv", "facts.md"]}
allowed.update(web_files)
# Exact-file exceptions for the approved long tables; all other limits remain 2 MB.
size_limits = {"portfolio/web/fingerprint.csv": 6_000_000,
               "portfolio/web/neighbours.csv": 3_000_000}
secret_patterns = [rb"gh[pousr]_" + rb"[A-Za-z0-9]{30,}",
                   rb"github_pat_" + rb"[A-Za-z0-9_]{30,}",
                   rb"-----BEGIN " + rb"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
                   rb"AKIA" + rb"[A-Z0-9]{16}"]
errors = []
paths = git("ls-files", "-z").decode().strip("\0").split("\0")
for path in filter(None, paths):
    p = PurePosixPath(path)
    notebook = p.parent == PurePosixPath("notebooks") and p.suffix == ".ipynb"
    if path not in allowed and not notebook:
        errors.append(f"Unapproved public path: {path}")
    blob = git("show", ":" + path)
    if len(blob) > size_limits.get(path, 2_000_000):
        errors.append(f"File exceeds approved size limit: {path}")
    if any(re.search(pattern, blob) for pattern in secret_patterns):
        errors.append(f"Possible credential: {path}")
    if notebook:
        n = json.loads(blob)
        if "widgets" in n.get("metadata", {}):
            errors.append(f"Widget state: {path}")
        for i, cell in enumerate(n["cells"]):
            if cell.get("outputs") or cell.get("execution_count") is not None or cell.get("attachments"):
                errors.append(f"Saved output, execution count or attachment: {path}, cell {i}")
present_web = web_files.intersection(paths)
if present_web:
    if present_web != web_files:
        errors.append("Incomplete curated website bundle")
    else:
        import hashlib
        manifest = json.loads(git("show", ":portfolio/web/manifest.json"))
        if manifest.get("source_tree_dirty") is not False:
            errors.append("Website bundle is a development build")
        if set(manifest.get("files", {})) != {p.split("/")[-1] for p in web_files} - {"manifest.json"}:
            errors.append("Website manifest file registry mismatch")
        for relative in web_files - {"portfolio/web/manifest.json"}:
            blob = git("show", ":" + relative)
            info = manifest.get("files", {}).get(relative.split("/")[-1], {})
            if info.get("sha256") != hashlib.sha256(blob).hexdigest() or info.get("bytes") != len(blob):
                errors.append(f"Staged website checksum/size mismatch: {relative}")
        for relative, expected_hash in manifest.get("sources", {}).items():
            if relative.startswith(("scripts/", "docs/")) and relative in paths:
                if hashlib.sha256(git("show", ":" + relative)).hexdigest() != expected_hash:
                    errors.append(f"Website build source drift: {relative}")
if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Publication check passed: {len(paths)} staged files; no research execution.")
