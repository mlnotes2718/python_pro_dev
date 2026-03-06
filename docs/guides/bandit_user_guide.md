# Bandit User Guide
> Python Security Linter — Practical Reference

---

## What is Bandit?

Bandit is a **static analysis security tool (SAST)** for Python, maintained by the Python Code Quality Authority (PyCQA). It scans your source code for common security vulnerabilities and insecure patterns — it does **not** protect your app at runtime.

---

## Installation

```bash
# Dev only — bandit has no purpose in production
uv add --dev bandit
```

---

## Basic Usage

```bash
# Scan a single file
bandit myfile.py

# Scan a directory recursively
bandit -r src/

# Scan current project
bandit -r .
```

---

## Severity & Confidence Flags

```bash
bandit -r src -l    # low severity and above
bandit -r src -ll   # medium severity and above (recommended)
bandit -r src -lll  # high severity only

bandit -r src -i    # low confidence and above
bandit -r src -ii   # medium confidence and above
bandit -r src -iii  # high confidence only
```

---

## Configuration — `pyproject.toml` (Recommended)

Bandit supports configuration via `pyproject.toml`. Always pass `-c pyproject.toml` to activate it.

```toml
[tool.bandit]
exclude_dirs = [".venv", "tests"]
skips = []
```

> **Note:** `severity` is not a valid key in `pyproject.toml` — pass `-ll` via CLI or justfile instead.

Run with config:

```bash
bandit -r . -ll -c pyproject.toml
```

---

## Why Scan `.` Instead of `src/`

Scanning `.` (with `.venv` and `tests` excluded via config) is the safer default — it catches any stray `.py` files accidentally placed outside `src/`.

```bash
# Recommended manual scan
bandit -r . -ll -c pyproject.toml
```

---

## Output Formats

```bash
bandit -r src -ll -f json -o report.json   # JSON
bandit -r src -ll -f html -o report.html   # HTML
bandit -r src -ll -f csv  -o report.csv    # CSV
```

---

## Skip Specific Tests

```bash
# Skip by test ID
bandit -r src --skip B101,B102

# Run only specific tests
bandit -r src --tests B201,B301
```

Or via `pyproject.toml`:

```toml
[tool.bandit]
exclude_dirs = [".venv", "tests"]
skips = ["B101"]
```

---

## Common Test IDs

| ID | Issue |
|---|---|
| B101 | Use of `assert` |
| B102 | Use of `exec` |
| B105 / B106 | Hardcoded passwords |
| B201 | Flask debug mode enabled |
| B301 | Use of `pickle` |
| B324 | Weak MD5 / SHA1 hash |
| B501 | Weak SSL/TLS settings |
| B601 | Shell injection via `subprocess` |

---

## Justfile Integration

```makefile
# Run Security Scan
bandit:
    @echo "🔒  ({{env_type}}) Running Bandit on src/..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run bandit -r . -ll -c pyproject.toml; \
    else \
        bandit -r . -ll -c pyproject.toml; \
    fi
```

---

## Pre-commit Hook

Bandit integrates cleanly with pre-commit. It only scans **staged files**, so `.venv` is never touched — no exclude needed.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.9.4
    hooks:
      - id: bandit
        args: ["-ll", "-c", "pyproject.toml"]
        exclude: ^tests/
```

---

## Professional Security Layering

| Stage | Tool | Purpose |
|---|---|---|
| `git commit` | bandit (pre-commit) | Automatic scan on staged files |
| `just bandit` | bandit (manual) | Full project scan |
| CI/CD pipeline | bandit + pip-audit | Code + dependency scanning |
| Production | Sentry / runtime monitoring | Runtime protection |

---

## Bandit vs Other Tools

| Tool | What it scans |
|---|---|
| **Bandit** | Your code — insecure patterns (SAST) |
| **Semgrep** | Multi-language SAST, more customizable |
| **pip-audit** | Dependencies — known CVEs in packages |
| **SonarQube** | Multi-language, enterprise SAST |

> Bandit and pip-audit solve **different problems** and are commonly used together in professional setups.

---

## Key Reminders

- Bandit is **dev only** — never add to prod dependencies
- Always use `-c pyproject.toml` when running manually
- Pre-commit scopes to staged files only — no `.venv` exclude needed
- `-ll` (medium and above) is the recommended severity threshold for most projects
- Scanning `.` is safer than `src/` — catches stray files outside your source directory
