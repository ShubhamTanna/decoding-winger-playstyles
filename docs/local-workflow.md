# Local research workspace

This repository carries the eight approved Phase 1 notebook sources, the candidate environment, and publication safeguards. Public notebook copies have outputs and execution metadata removed. No research code was executed and no model was refitted during setup.

## Local layout

- `notebooks/`: source publication copies; all cell sources match the approved research notebooks.
- `data/`: ignored, byte-identical working copy of all original local datasets and saved outputs.
- `.local/research-snapshot/`: ignored, complete byte-identical snapshot of the original research folder, including executed notebooks, private documents, and OS metadata.
- `.local/research-sha256.json`: SHA-256 manifest of every original research file.
- `.local/previous-checkout-sha256.json`: manifest of the earlier checkout's working files, excluding Git internals.

The canonical machine path is `/Users/shubham/Documents/Codex/Projects/decoding-winger-playstyles`. The Desktop research folder and the earlier dated Codex checkout remain untouched. Make ongoing edits here. Use this folder as the project location in local agent sessions. Remote sessions and fresh clones do not automatically have the ignored data or local snapshot; confirm access before work and supply private inputs through an appropriate private channel when needed.

## Source workflow

Use a `codex/` feature branch. Review source changes, stage explicit files, then run:

```sh
python3 scripts/check_publication.py
git diff --cached --check
git diff --cached --stat
```

The publication check reads the staged Git blobs, rejects unapproved paths, files over 2 MB, common credential patterns, and notebooks containing outputs, attachments or execution state. It is a practical guard, not a guarantee that every secret or sensitive statement will be detected: review the actual diff as well. This clone enables the tracked pre-commit hook via `git config core.hooksPath .githooks`. Fresh clones must run that command to enable it. Amend the explicit path allowlist deliberately when adding source files.

Push to the feature branch and open a PR against `main`; do not force push. GitHub authentication is held by GitHub CLI in the system credential manager. It is not included in this repository. Check `gh auth status` when access fails and distinguish network restrictions from expired credentials.

## Research execution

Read environment.md before installing or running anything. The candidate environment is not a tested local runtime. The notebooks retain their original Colab-oriented paths; a fresh clone is not a turnkey execution environment. Preserve completed manual decisions and use isolated outputs for any authorized rerun.

The repository's earlier history already contains executed notebook outputs. This setup removes them from the new branch tip; it does not rewrite or erase historical commits.

## Curated website publication (Phase 2B)

The user's Phase 2B instruction authorizes only the eight reviewed files in `portfolio/web/`. Data, snapshots and model binaries remain private. Exact-path `.gitignore` exceptions and the publication allowlist permit those files, with explicit 6 MB/3 MB limits for fingerprint/neighbour CSVs. The hook verifies staged bundle hashes and source-code consistency; the independent website validator supplies semantic checks before staging. See [website export workflow](website_export_workflow.md).
