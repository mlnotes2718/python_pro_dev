# just — Task Runner

## What It Does

`just` is a command runner (similar to `make`, but without the footguns). It reads a `justfile` in the project root and exposes named recipes that can be run with `just <recipe>`. It handles multi-step tasks, environment detection, and conditional logic — keeping all dev workflows in one place.

---

## Installation

```bash
brew install just          # macOS
cargo install just         # Any platform with Rust
# or via prebuilt binary: https://just.systems/
```

---

## How This Project Uses It

The `justfile` detects whether `uv` or `conda` is available and routes every command accordingly:

```just
env_type := `command -v uv >/dev/null && echo uv || echo conda`
```

This means every `just` command works identically whether you're using `uv` or `conda`.

---

## All Available Commands

```bash
just              # List all available commands (default)
just setup        # Create environment + install pre-commit hooks
just lint         # Run Ruff linter with auto-fix
just typecheck    # Run mypy static type checker
just test         # Run pytest with coverage
just sec          # Run Bandit security scan
just audit        # Run pip-audit dependency CVE scan
just health       # Check environment consistency
just precommit    # Run all pre-commit hooks manually against all files
just run          # Full pipeline: lint → typecheck → health → audit → sec → test → clean
just clean        # Remove all caches (.pytest_cache, .mypy_cache, __pycache__, etc.)
```

---

## Recipe Reference

### `just setup`
Installs all project dependencies and registers git hooks. Run once after cloning.

```bash
just setup
```

### `just run`
The full quality gate — runs every check in sequence. Use before opening a PR or making a release.

```bash
just run
```

Equivalent to:
```bash
just lint && just typecheck && just health && just audit && just sec && just test && just clean
```

### `just test *args`
Passes any extra arguments directly to pytest:

```bash
just test -k test_add_func         # Run a single test by name
just test --tb=short               # Short traceback format
just test tests/test_main.py       # Run a specific file
```

### `just clean`
Removes all generated caches. Safe to run at any time — nothing important is deleted.

```bash
just clean
```

---

## Adding New Recipes

Edit `justfile` and add a new recipe:

```just
# Run the app
run-app:
    @if [ "{{env_type}}" = "uv" ]; then uv run python src/main.py; else python src/main.py; fi
```

Then run it with:
```bash
just run-app
```

---

## Why just Over make

- No tab-vs-space gotchas
- Recipes are self-documenting (`just --list`)
- Variables and conditionals are readable
- Cross-platform (works on Windows, macOS, Linux)
- No implicit rules or magic behaviour
