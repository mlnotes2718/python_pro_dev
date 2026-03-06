# mypy — Static Type Checker

## What It Does

mypy analyses Python type annotations at build time without running the code. It catches an entire class of bugs before they reach production: wrong argument types, missing return values, `None` dereferences, and API misuse.

This project runs mypy in **strict mode**, which enables all optional checks and enforces annotations on every function.

---

## Running mypy

```bash
just typecheck                # Run via just
uv run mypy .                 # Run directly
uv run mypy src/main.py       # Check a single file
```

mypy runs automatically on `git push` via the pre-push hook.

---

## Configuration (pyproject.toml)

```toml
[tool.mypy]
python_version = "3.11"
exclude = ['^tests/']
strict = true
show_error_codes = true
warn_unused_configs = true
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
check_untyped_defs = false
```

### What `strict = true` enables

| Flag | What it checks |
|---|---|
| `disallow_untyped_defs` | Every function must have type annotations |
| `disallow_incomplete_defs` | No partially annotated functions |
| `check_untyped_defs` | Type-check functions even without annotations |
| `warn_return_any` | Warn when a function returns `Any` |
| `warn_unused_ignores` | Catch stale `# type: ignore` comments |
| `no_implicit_reexport` | Explicit re-exports only |
| `strict_equality` | Catch always-true/false comparisons |

### `ignore_missing_imports = true`

Suppresses errors for third-party libraries that don't ship type stubs. This is important in conda environments where niche ML libraries often lack stubs. For libraries with stubs (like pandas), install the stub package instead:

```toml
[dependency-groups]
dev = [
    "pandas-stubs>=3.0.0.260204",
]
```

---

## Writing Type-Safe Code

### Basic annotations

```python
def add_func(x: int | float, y: int | float) -> int | float:
    return x + y

def main() -> int:
    return 0
```

### With pandas

```python
import pandas as pd

def show_data(df: pd.DataFrame) -> None:
    print(df)
```

### Optional values

```python
import os

passwd: str | None = os.getenv("PASSWORD")
if passwd is None:
    raise OSError("PASSWORD not set")
# After the check, mypy knows passwd is str
```

---

## Common Errors and Fixes

### `error: Function is missing a return type annotation`

Add `-> ReturnType` to the function signature. Use `-> None` for functions that don't return a value.

### `error: Argument 1 has incompatible type "str | None"; expected "str"`

You need to handle the `None` case before passing the value:

```python
value = os.getenv("KEY")
if value is None:
    raise ValueError("KEY not set")
use(value)  # mypy now knows value is str
```

### `error: Cannot find implementation or library stub for module named "somelib"`

Either:
- Install stubs: `uv add --dev somelib-stubs`
- Or add to `pyproject.toml`: `ignore_missing_imports = true` (already set globally)
- Or suppress per-import: `import somelib  # type: ignore[import]`

---

## Test Override

Tests are excluded from strict checking because test helper functions and fixtures don't always benefit from full annotation:

```toml
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
check_untyped_defs = false
```

This keeps test code practical while keeping production code fully type-safe.
