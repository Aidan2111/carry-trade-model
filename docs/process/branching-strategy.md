# Branching Strategy

This repository uses a simple mainline workflow based on Microsoft Learn and Azure Well-Architected Framework operational excellence guidance.

References:

- Microsoft Learn, Azure Repos branching guidance: https://learn.microsoft.com/en-us/azure/devops/repos/git/git-branching-guidance
- Microsoft Learn, Azure Well-Architected Framework standardizing tools and processes: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/tools-processes
- Microsoft Learn, Azure Well-Architected Framework formalizing development practices: https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/formalize-development-practices

## Rules

`main` is the only always-current branch. It should build, pass tests, and be safe to branch from.

Use short-lived topic branches for all changes:

- `feature/<short-name>` for new user-visible behavior, docs structure, or repo organization.
- `bugfix/<short-name>` for non-urgent fixes.
- `hotfix/<short-name>` for urgent fixes that need a focused review.
- `docs/<short-name>` for documentation-only updates.

Use `release/<version-or-date>` only when a public release needs stabilization after `main` has moved on. Fixes should land through PRs and be ported intentionally, not merged back casually.

Avoid long-lived work branches. If a change becomes too large to review cleanly, split it into smaller PRs that each leave `main` in a healthy state.

## Pull Request Quality Gate

Every pull request should include:

- A concise summary of what changed and why.
- The commands run for testing or a clear reason a command was not run.
- Risk notes for data provenance, public-facing claims, API behavior, and dashboard behavior.
- Documentation updates when commands, paths, branch policy, runtime behavior, or public positioning changed.

Expected local verification before merge:

```bash
.venv/bin/python -m unittest discover -s tests -v
find . -path './.venv' -prune -o -path './frontend/node_modules' -prune -o -path './frontend/dist' -prune -o -path './frontend/build' -prune -o -name '*.py' -print0 | xargs -0 .venv/bin/python -m py_compile
.venv/bin/python scripts/system_evaluation.py
cd frontend && npm run build
```

Run `npm audit --omit=dev` from `frontend/` before public-release or dependency-security changes.

## Branch Protection Settings

When this repo is managed through GitHub or Azure Repos policies, protect `main` with:

- Pull request required before merge.
- Successful tests/build required before merge.
- Direct pushes disabled for routine work.
- Required review for non-trivial code, data, or public-facing docs changes.

These settings follow the same intent as the Well-Architected Framework: standardized practices, peer review, quality gates, and an audit trail.
