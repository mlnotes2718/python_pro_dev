# Python Pro Dev

A professional-grade Python project template demonstrating a complete development toolchain for production-quality code. Built with safety, correctness, and automation at every layer.

---

## Toolchain Overview

| Tool | Category | When It Runs |
|---|---|---|
| [uv](https://docs.astral.sh/uv/) / conda | Package & env management | Manual |
| [just](https://just.systems/) | Task runner | Manual |
| [Ruff](https://docs.astral.sh/ruff/) | Linter + formatter | Pre-commit |
| [mypy](https://mypy.readthedocs.io/) | Static type checker | Pre-push |
| [pytest](https://docs.pytest.org/) + [pytest-cov](https://pytest-cov.readthedocs.io/) | Testing + coverage | Pre-push |
| [Hypothesis](https://hypothesis.readthedocs.io/) | Property-based testing | Pre-push (via pytest) |
| [Bandit](https://bandit.readthedocs.io/) | Security linter | Pre-commit |
| [pip-audit](https://pypi.org/project/pip-audit/) | Dependency vulnerability scan | Pre-push |
| [pre-commit](https://pre-commit.com/) | Git hook orchestrator | On commit / push |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanning | Pre-commit + pre-push |

> **Upgrade path:** When moving to conda environments or containers, replace `pip-audit` with [Grype](https://github.com/anchore/grype) for deeper filesystem-level vulnerability scanning.

---

## Quick Start

### With uv (preferred)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and set up the project
git clone <your-repo>
cd python-pro-dev
just setup
```

### With conda

```bash
# just setup auto-detects uv or conda
just setup
```

`just setup` installs all dependencies and registers pre-commit hooks in one step.

---

## Project Structure

```
python-pro-dev/
├── src/
│   └── main.py          # Application source
├── tests/
│   └── test_main.py     # Pytest + Hypothesis tests
├── log/                 # App and audit logs (gitignored)
├── docs/                # Detailed tool guides
│   ├── uv.md
│   ├── just.md
│   ├── ruff.md
│   ├── mypy.md
│   ├── pytest.md
│   ├── hypothesis.md
│   ├── bandit.md
│   ├── pip-audit.md
│   ├── pre-commit.md
│   └── gitleaks.md
├── justfile             # Task runner commands
├── pyproject.toml       # All tool configuration
├── .pre-commit-config.yaml
└── .env                 # Local secrets (gitignored)
```

---

## Daily Workflow

```bash
just lint          # Fix style and lint issues (Ruff)
just typecheck     # Check types (mypy)
just test          # Run tests with coverage (pytest)
just sec           # Security scan (Bandit)
just audit         # Dependency CVE scan (pip-audit)
just health        # Check environment consistency
just precommit     # Run all pre-commit hooks manually
just run           # Run everything: lint → typecheck → health → audit → sec → test → clean
just clean         # Remove all cache and build artifacts
```

Git automation handles the rest:

- **On `git commit`** → Ruff, Bandit, Gitleaks, and standard file checks run automatically.
- **On `git push`** → mypy, pytest, pip-audit, and Gitleaks run automatically.

---

## Configuration

All tool configuration lives in `pyproject.toml`. No scattered config files.

```toml
[tool.ruff]        # Linting and formatting rules
[tool.mypy]        # Type checking strictness
[tool.pytest.ini_options]  # Test discovery and coverage
[tool.bandit]      # Security scan exclusions
[tool.coverage.report]     # Coverage reporting
```

See the `docs/` folder for a detailed guide on each tool's configuration and usage.

---

## Environment Strategy

This project uses **uv by default** and falls back to **conda** when uv is not available. The `justfile` detects the environment automatically:

```just
env_type := `[ -n "$CONDA_PREFIX" ] && echo "conda" || echo "uv"`
```

Every `just` command runs the correct tool transparently — you never need to think about which environment manager is active.

**Use conda when:**
- Working with packages that require compiled C/CUDA extensions (e.g. PyTorch, NumPy with MKL)
- Managing non-Python dependencies in the same environment

**Upgrade to Grype when:**
- Running containerised workloads (Docker, OCI images)
- Using conda environments where pip-audit has incomplete visibility
- You need OS-level package scanning, not just Python package scanning

---

## Detailed Docs

Each tool has its own guide in the `docs/` folder:

- [`docs/uv.md`](docs/uv.md) — Package and environment management
- [`docs/just.md`](docs/just.md) — Task runner commands
- [`docs/ruff.md`](docs/ruff.md) — Linting and formatting
- [`docs/mypy.md`](docs/mypy.md) — Static type checking
- [`docs/pytest.md`](docs/pytest.md) — Testing and coverage
- [`docs/hypothesis.md`](docs/hypothesis.md) — Property-based testing
- [`docs/bandit.md`](docs/bandit.md) — Security linting
- [`docs/pip-audit.md`](docs/pip-audit.md) — Dependency CVE scanning
- [`docs/pre-commit.md`](docs/pre-commit.md) — Git hook automation
- [`docs/gitleaks.md`](docs/gitleaks.md) — Secret scanning
