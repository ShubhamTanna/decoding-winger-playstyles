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
           ".githooks/pre-commit", "scripts/check_publication.py"}
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
    if len(blob) > 2_000_000:
        errors.append(f"File exceeds 2 MB: {path}")
    if any(re.search(pattern, blob) for pattern in secret_patterns):
        errors.append(f"Possible credential: {path}")
    if notebook:
        n = json.loads(blob)
        if "widgets" in n.get("metadata", {}):
            errors.append(f"Widget state: {path}")
        for i, cell in enumerate(n["cells"]):
            if cell.get("outputs") or cell.get("execution_count") is not None or cell.get("attachments"):
                errors.append(f"Saved output, execution count or attachment: {path}, cell {i}")
if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Publication check passed: {len(paths)} staged files; no research execution.")
