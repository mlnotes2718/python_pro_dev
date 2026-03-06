# Ruff — Linter & Formatter

## What It Does

Ruff is an extremely fast Python linter and code formatter written in Rust. It replaces `flake8`, `isort`, `pyupgrade`, `pep8-naming`, and `black` with a single tool that runs in milliseconds even on large codebases.

In this project Ruff handles two jobs:
1. **Linting** — catches bugs, style issues, and security antipatterns
2. **Formatting** — enforces consistent code style (replaces Black)

---

## Running Ruff

```bash
just lint                          # Lint + auto-fix via just
uv run ruff check . --fix          # Lint with auto-fix (direct)
uv run ruff format .               # Format all files (direct)
uv run ruff check . --no-fix       # Lint only, no changes (CI mode)
```

Ruff also runs automatically on every `git commit` via the pre-commit hook.

---

## Configuration (pyproject.toml)

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
  "E",    # pycodestyle errors
  "F",    # pyflakes (undefined names, unused imports)
  "I",    # isort (import ordering)
  "B",    # flake8-bugbear (common bugs and design issues)
  "UP",   # pyupgrade (modernise syntax for target Python version)
  "N",    # pep8-naming
  "S",    # flake8-bandit (security rules)
  "SIM",  # flake8-simplify
  "C4",   # flake8-comprehensions
]

ignore = [
  "E501",   # line length — handled by formatter
  "S101",   # allow assert statements
  "S311",   # allow random (non-cryptographic use)
  "T201",   # allow print statements
]
```

### Rule categories explained

| Code | Plugin | What it catches |
|---|---|---|
| `E` / `W` | pycodestyle | Indentation, whitespace, blank lines |
| `F` | pyflakes | Undefined names, unused imports, undefined `__all__` |
| `I` | isort | Import order (stdlib → third-party → local) |
| `B` | bugbear | Mutable default args, assert in production, loop variable capture |
| `UP` | pyupgrade | `Union[x, y]` → `x \| y`, `Optional[x]` → `x \| None` |
| `N` | pep8-naming | Class names, function names, constant names |
| `S` | bandit subset | Hardcoded passwords, `eval`, unsafe YAML load |
| `SIM` | simplify | `if x == True` → `if x`, unnecessary `else` after return |
| `C4` | comprehensions | `list(x for x in y)` → `[x for x in y]` |

---

## Per-file Ignores

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # asserts are idiomatic in tests
```

Add more as needed — for example, migration files often need `E501` ignored.

---

## Formatter Configuration

```toml
[tool.ruff.format]
quote-style = "double"    # consistent double quotes
indent-style = "space"    # spaces, not tabs
```

The formatter is Black-compatible by default. Running `ruff format` is equivalent to running Black.

---

## Fixing Issues

Most issues can be auto-fixed:

```bash
uv run ruff check . --fix          # Fix everything fixable
uv run ruff check . --fix-only     # Fix without reporting unfixable
```

For issues that require human judgment (e.g. a genuine bug flagged by `B`), Ruff reports them but does not modify the code.

---

## Suppressing a Rule

For a single line:
```python
x = eval(user_input)  # noqa: S307
```

For a whole file, add to `per-file-ignores` in `pyproject.toml`.

Avoid blanket `# noqa` with no rule code — it silences everything silently.
