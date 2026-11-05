# Decoding Winger Playstyles

## Working agreement
- Use this repository as the canonical working project. Read docs/local-workflow.md and docs/environment.md before changing research files.
- Preserve the original Desktop research folder, the previous Codex checkout, and .local/research-snapshot. Treat them as read-only historical evidence. Never delete, overwrite, or force-reset them.
- All eight current research notebooks are represented in notebooks/. Full executed originals, private planning documents, and original hashes are retained under ignored .local/. Local data/ contains the original datasets and analytical exports.
- Work on codex/* feature branches. Review the diff and run python3 scripts/check_publication.py after staging explicit paths. Commit and push authorized source changes; prepare a PR against main. Never force push or merge to main without an explicit request.
- Never commit data/, .local/, scraped datasets, completed manual review tables, secrets, model binaries, backups, or generated exports. Do not bypass .gitignore using git add -f. New public data needs a separate publication decision.
- Public notebooks must have empty outputs, null execution counts, no attachments, and no embedded widget state. Preserve cell source when preparing publication copies. Keep executed evidence locally before cleaning outputs.
- Do not run all notebooks, fit models, regenerate analytical exports, change feature definitions, or overwrite completed manual reviews as a setup or documentation check. Those require an explicit research task and an isolated output location.
- Preserve population identities, observation order, 20-feature ordering, and saved model semantics. Known research baseline: 1,396 spells and 665 footballers. Explain any deliberate analytical change and validate it against preserved evidence.
- The environment is provisional: dependency resolution passed, but full fresh-kernel reproduction has not. Colab /content paths still require manual staging. Do not claim local execution is ready or results were reproduced without testing.
- Never print credentials. Authentication belongs in the user's credential manager, not repository files. Report permission/network limitations accurately; connector access and local Git authentication are separate.
- Do not deploy or modify the portfolio website as part of research housekeeping.
