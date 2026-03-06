# Pytest Notes

## Mocking in Tests

Mocking allows you to replace real objects (functions, classes, modules) with fake ones during tests. This gives you full control over the test environment.

---

## Common Mocking Patterns

### 1. Mock a function (`patch`)

Replaces a function with a silent mock — any calls to it do nothing and return `None`.

```python
from unittest.mock import patch

def test_main_success() -> None:
    with patch("main.load_dotenv"):   # load_dotenv() does nothing during this test
        with patch.dict("os.environ", {"PASSWORD": "secret"}):
            result = main()
            assert result == 0
```

### 2. Mock environment variables (`patch.dict`)

Temporarily sets or clears environment variables for the duration of the test.

```python
# Set specific env vars
with patch.dict("os.environ", {"PASSWORD": "secret"}):
    ...

# Clear ALL env vars
with patch.dict("os.environ", {}, clear=True):
    ...
```

### 3. Mock a logger (`patch`)

Replaces the logger with a silent mock — suppresses log output during tests.

```python
# Without patch("main.logger") → real logger runs → error log appears in output
# With patch("main.logger")    → logger is mocked → no log output (cleaner)

def test_main_no_password() -> None:
    with patch("main.load_dotenv"):
        with patch.dict("os.environ", {}, clear=True):
            with patch("main.logger"):          # suppresses intentional error log
                with pytest.raises(OSError, match="PASSWORD environment variable not set"):
                    main()
```

---

## Why Mock `load_dotenv`?

Without mocking `load_dotenv`, it runs for real during tests and can **overwrite** your `patch.dict` environment variables:

```
patch.dict sets PASSWORD="secret"
    ↓
main() calls load_dotenv(override=True)
    ↓
load_dotenv overwrites PASSWORD with value from .env file  ← problem!
    ↓
os.getenv("PASSWORD") returns .env value, not your mock value
```

Fix by mocking it:

```python
with patch("main.load_dotenv"):   # load_dotenv does nothing
    with patch.dict("os.environ", {"PASSWORD": "secret"}):  # this is now safe
        main()
```

---

## Why Mock the Logger?

When testing error paths, your real logger will write error messages to the log — which looks alarming even though it's intentional.

```python
# This intentional error log appears in output — confusing but harmless
2026-03-02 17:31:55,533 | ERROR | root | PASSWORD environment variable not set
```

Mocking the logger suppresses it for a cleaner test output:

```python
with patch("main.logger"):   # logger calls go nowhere
    with pytest.raises(OSError, ...):
        main()
# → no error log in output ✅
```

---

## Patch Target — Important Rule

Always patch where the object is **used**, not where it is **defined**.

```python
# main.py imports os and load_dotenv
import os
from dotenv import load_dotenv

# ✅ Correct - patch where it's used (in main module)
patch("main.load_dotenv")
patch("main.os.getenv")
patch("main.logger")

# ❌ Wrong - patching the source has no effect on main.py
patch("dotenv.load_dotenv")
patch("os.getenv")
```

---

## Full Test Example

```python
# tests/test_main.py
from unittest.mock import patch

import pandas as pd
import pytest

from main import add_func, main, multiply, show_data


def test_add_func() -> None:
    assert add_func(2, 3) == 5
    assert add_func(1.5, 2.5) == 4.0


def test_multiply() -> None:
    assert multiply(3, 4) == 12
    assert multiply(2.5, 2) == 5.0


def test_show_data(capsys: pytest.CaptureFixture) -> None:
    df = pd.DataFrame({"a": [1, 2]})
    show_data(df)
    captured = capsys.readouterr()
    assert "a" in captured.out


def test_main_success() -> None:
    with patch("main.load_dotenv"):
        with patch.dict("os.environ", {"PASSWORD": "secret"}):
            result = main()
            assert result == 0


def test_main_no_password() -> None:
    with patch("main.load_dotenv"):
        with patch.dict("os.environ", {}, clear=True):
            with patch("main.logger"):   # suppresses intentional error log
                with pytest.raises(OSError, match="PASSWORD environment variable not set"):
                    main()
```

---

## pyproject.toml — Pytest Config

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "--strict-markers --cov=src --cov-report=term-missing"
log_cli = true   # stream logs live to terminal
```

| Option | Description |
|---|---|
| `testpaths` | Where pytest looks for tests |
| `pythonpath` | Adds `src/` to Python path so imports work |
| `addopts` | Default flags passed to every pytest run |
| `log_cli` | Stream logs live to terminal during tests |
