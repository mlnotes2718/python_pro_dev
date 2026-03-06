# pre-commit — Git Hook Orchestrator

## What It Does

`pre-commit` installs and manages git hooks that run automatically before commits and pushes. It ensures quality checks pass before code enters the repository, catching issues at the earliest possible moment — before review, before CI, before deployment.

Without pre-commit, developers must remember to run linters and tests manually. With pre-commit, enforcement is automatic and consistent across the whole team.

---

## Setup

```bash
just setup          # Installs hooks during project setup
```

Or manually:

```bash
uv run pre-commit install                                     # Install pre-commit hook
uv run pre-commit install --hook-type pre-push               # Also install pre-push hook
```

---

## Running Hooks Manually

```bash
just precommit                               # Run all hooks against all files
uv run pre-commit run --all-files            # Same, direct
uv run pre-commit run ruff --all-files       # Run a single hook
uv run pre-commit run --from-ref HEAD~1 --to-ref HEAD  # Run only on changed files
```

---

## Hook Stages in This Project

### Pre-commit (runs on every `git commit`)

| Hook | Purpose |
|---|---|
| `check-merge-conflict` | Block commits with unresolved merge markers |
| `check-added-large-files` | Block files over 500KB |
| `check-toml` | Validate `pyproject.toml` syntax |
| `check-yaml` | Validate YAML file syntax |
| `check-json` | Validate JSON file syntax |
| `end-of-file-fixer` | Ensure every file ends with a newline |
| `trailing-whitespace` | Remove trailing whitespace |
| `debug-statements` | Catch forgotten `pdb` / `breakpoint()` calls |
| `detect-private-key` | Catch accidentally committed private keys |
| `ruff` | Lint and auto-fix Python code |
| `ruff-format` | Format Python code |
| `bandit` | Security scan Python code |
| `gitleaks` | Scan for secrets and credentials |

### Pre-push (runs on every `git push`)

| Hook | Purpose |
|---|---|
| `mypy` | Static type checking |
| `pytest` | Full test suite with coverage |
| `pip-audit` | Dependency CVE scan (only when lockfile changes) |
| `gitleaks` | Secret scan (also runs on push) |

The split between commit and push stages is intentional:
- **Fast checks** (linting, formatting, secret scanning) run on every commit — seconds of overhead
- **Slow checks** (type checking, tests, CVE scanning) run on push — acceptable for the full gate

---

## Configuration File

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-merge-conflict
        stages: [pre-commit]
      # ...

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.4
    hooks:
      - id: ruff
        args: [--fix]
        stages: [pre-commit]
      - id: ruff-format
        stages: [pre-commit]
```

Remote hooks are versioned (e.g. `rev: v6.0.0`) and cached locally — they don't require network access after first install.

Local hooks (mypy, pytest, pip-audit) use `entry: just <recipe>` to delegate to the justfile, keeping configuration in one place.

---

## Bypassing Hooks (Use Sparingly)

```bash
git commit --no-verify    # Skip pre-commit hooks
git push --no-verify      # Skip pre-push hooks
```

Only use `--no-verify` in genuine emergencies (e.g. hotfixing a production outage). Never use it routinely — it defeats the purpose of having hooks.

---

## Updating Hook Versions

```bash
uv run pre-commit autoupdate    # Update all hooks to their latest tagged versions
```

Run this periodically (e.g. monthly) and commit the updated `.pre-commit-config.yaml`.

---

## Troubleshooting

### Hooks not running

```bash
uv run pre-commit install   # Re-install hooks
ls .git/hooks/              # Verify hook files exist
```

### A hook is failing on unrelated files

```bash
just precommit              # Run manually to see full output
uv run pre-commit run ruff --all-files --verbose
```

### Clearing the hook cache

```bash
uv run pre-commit clean     # Remove cached environments
uv run pre-commit install   # Reinstall from scratch
```
