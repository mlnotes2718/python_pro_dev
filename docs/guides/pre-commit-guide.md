# Pre-commit Guide (uv + ruff + mypy + pytest)

## What is pre-commit?

Pre-commit is a framework for managing git hooks. It runs checks automatically **before every commit**, catching issues early before they reach your repo or CI/CD pipeline.

```
git commit → pre-commit hooks run → (pass) commit saved / (fail) commit aborted
```

---

## Installation

```bash
# Install as a dev dependency (recommended)
uv add pre-commit --dev

# Activate the hook in your repo (run once after cloning)
uv run pre-commit install
```

> ⚠️ Every developer needs to run `pre-commit install` once after cloning. Without this, hooks won't trigger.

---

## Configuration

Create `.pre-commit-config.yaml` in your project root (same level as `pyproject.toml`):

```yaml
# .pre-commit-config.yaml
repos:
  # Ruff - lint and format (remote is fine, auto-discovers pyproject.toml)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10
    hooks:
      - id: ruff              # linter (replaces flake8, isort, etc.)
        args: [--fix]         # auto-fix fixable issues
      - id: ruff-format       # formatter (replaces black)

  # Mypy and pytest as local - they need your project's virtualenv
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy src  # replace 'src' with your source folder, or use '.' for flat layout
        language: system
        types: [python]
        pass_filenames: false  # let mypy use your pyproject.toml config

      - id: pytest
        name: pytest
        entry: uv run pytest --cov --cov-report=term-missing
        language: system
        pass_filenames: false
        always_run: true
```

### Remote vs Local — When to use each

| Tool | Use | Reason |
|---|---|---|
| `ruff` | Remote ✅ | Self-contained, auto-discovers `pyproject.toml` |
| `mypy` | Local ✅ | Needs your venv, stubs, and `pyproject.toml` overrides |
| `pytest` | Local ✅ | Needs your venv, source files, and test files |

> **Why does mypy need to be local?** The `mirrors-mypy` remote hook runs in an isolated environment and **ignores your `pyproject.toml` overrides** (like `[[tool.mypy.overrides]]`). Using `repo: local` with `uv run mypy` ensures it reads your full config.

> **Why specify `src` in the entry?** With `pass_filenames: false`, mypy receives no files from pre-commit and needs an explicit target. Use `uv run mypy src` for `src/` layout, or `uv run mypy .` for a flat layout.

---

## Sample pyproject.toml

```toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.11"

[tool.uv]
dev-dependencies = [
    "pre-commit",
    "pytest",
    "pytest-cov",
    "mypy",
    "ruff",
]

# Ruff config
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
# E: pycodestyle, F: Pyflakes, I: isort, B: flake8-bugbear, UP: pyupgrade, N: pep8-naming
select = ["E", "F", "I", "B", "UP", "N"]
ignore = ["T201"]  # ignore print statements

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# Mypy config
[tool.mypy]
python_version = "3.11"
strict = true
show_error_codes = true
warn_unused_configs = true
ignore_missing_imports = true  # useful for libs without stubs (e.g. ML libs)

# Relax strict typing in tests
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# Pytest config
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing"

# Coverage config
[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]
```

---

## Project Structure

```
your-project/
├── .pre-commit-config.yaml   ← committed to repo
├── pyproject.toml
├── src/
│   └── your_package/
│       └── __init__.py
└── tests/
    └── test_example.py
```

---

## Common Commands

| Command | What it does |
|---|---|
| `uv run pre-commit install` | Activate hooks (run once after clone) |
| `uv run pre-commit run --all-files` | Run all hooks manually |
| `uv run pre-commit run ruff` | Run a specific hook only |
| `uv run pre-commit autoupdate` | Update hook versions to latest |
| `git commit --no-verify` | Skip hooks for one commit |

---

## Workflow

```
Developer clones repo
        ↓
uv sync
uv run pre-commit install   ← must do this once!
        ↓
Write code → git commit
        ↓
  [ruff lint]     → fix or abort
  [ruff format]   → fix or abort
  [mypy]          → abort if type errors
  [pytest --cov]  → abort if tests fail
        ↓
Commit saved ✅
```

---

## Moving Pytest to Pre-push (Optional)

Pytest can be slow. If it's slowing down your commits, move it to run only on `git push`:

```bash
# Install hook for both commit and push stages
uv run pre-commit install --hook-type pre-push
```

Then update `.pre-commit-config.yaml`:

```yaml
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest --cov --cov-report=term-missing
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]   # ← only runs on git push
```

---

## CI/CD Safety Net (GitHub Actions)

Local hooks can be skipped (`--no-verify`) or forgotten. Always enforce with CI:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: Run pre-commit
        run: uv run pre-commit run --all-files
```

---

## Logs & Debugging

If something goes wrong, check the pre-commit log:

```bash
cat ~/.cache/pre-commit/pre-commit.log

# Or follow in real time
tail -f ~/.cache/pre-commit/pre-commit.log
```

---

## Onboarding New Developers

Since `.pre-commit-config.yaml` is committed to the repo, new developers just need:

```bash
git clone <repo>
cd <repo>
uv sync                        # install dependencies
uv run pre-commit install      # activate hooks
```

Add this to your `README.md` or a `Makefile`:

```makefile
# Makefile
setup:
	uv sync
	uv run pre-commit install
```

```bash
make setup
```


---

## Hook Stages

By default all hooks run on `git commit`. You can control **when** each hook runs using `stages`.

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10
    hooks:
      - id: ruff
        args: [--fix]
        stages: [pre-commit]      # fast checks on commit
      - id: ruff-format
        stages: [pre-commit]

  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: uv run mypy src
        language: system
        types: [python]
        pass_filenames: false
        stages: [pre-commit]      # fast checks on commit

      - id: pytest
        name: pytest
        entry: uv run pytest --cov --cov-report=term-missing
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]        # slow checks on push only
```

Install both hook types:

```bash
uv run pre-commit install                        # pre-commit hooks
uv run pre-commit install --hook-type pre-push   # pre-push hooks
```

Result:
```
git commit  → ruff, ruff-format, mypy   (fast)
git push    → pytest                    (thorough)
```

> **Rule of thumb:** fast checks on commit, slow checks on push.

---

## Summary

| Tool | Role | Source |
|---|---|---|
| `ruff` | Lint + format | Remote (auto-discovers config) |
| `mypy` | Type checking | Local (needs venv + config overrides) |
| `pytest --cov` | Tests + coverage | Local (needs venv) |
| GitHub Actions | CI enforcer | Always runs on push |
