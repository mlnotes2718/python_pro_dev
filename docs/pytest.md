# pytest & pytest-cov — Testing & Coverage

## What They Do

**pytest** is the standard Python testing framework. It discovers and runs tests, provides rich assertion output, and has a huge ecosystem of plugins.

**pytest-cov** integrates coverage measurement into pytest runs, reporting exactly which lines of source code are exercised by your tests.

---

## Running Tests

```bash
just test                          # Run all tests with coverage
just test -k test_add_func         # Run tests matching a name pattern
just test tests/test_main.py       # Run a specific file
just test --tb=short               # Compact traceback output
just test -x                       # Stop on first failure
just test -v                       # Verbose output
```

Tests run automatically on `git push` via the pre-push hook.

---

## Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = "--strict-markers --cov=src --cov-report=term-missing"
log_cli = true

[tool.coverage.report]
exclude_lines = [
    "if __name__ == .__main__.:",
]
```

### Options explained

| Option | Purpose |
|---|---|
| `testpaths = ["tests"]` | Only look for tests in `tests/` |
| `pythonpath = ["src"]` | Add `src/` to `sys.path` so `from main import ...` works |
| `--strict-markers` | Fail if an undeclared marker is used |
| `--cov=src` | Measure coverage for the `src/` directory |
| `--cov-report=term-missing` | Print uncovered line numbers to the terminal |
| `log_cli = true` | Show `logging` output during test runs |

---

## Test Structure

Tests live in `tests/`. Each file is named `test_<module>.py`. Functions are named `test_<behaviour>`.

```
tests/
└── test_main.py
```

### Example tests

```python
def test_add_func() -> None:
    assert add_func(2, 3) == 5
    assert add_func(1.5, 2.5) == 4.0
```

### Mocking environment variables

```python
def test_main_success(monkeypatch) -> None:
    monkeypatch.setenv("PASSWORD", "secret")
    with patch("main.load_dotenv"):
        result = main()
        assert result == 0
```

### Testing exceptions

```python
def test_main_no_password() -> None:
    with (
        patch("main.load_dotenv"),
        patch.dict("os.environ", {}, clear=True),
        pytest.raises(OSError, match="PASSWORD environment variable not set"),
    ):
        main()
```

### Capturing stdout

```python
def test_show_data(capsys: pytest.CaptureFixture) -> None:
    df = pd.DataFrame({"a": [1, 2]})
    show_data(df)
    captured = capsys.readouterr()
    assert "a" in captured.out
```

---

## Coverage

After running `just test`, coverage is printed inline:

```
---------- coverage: platform darwin, python 3.11 ----------
Name          Stmts   Miss  Cover   Missing
-------------------------------------------
src/main.py      34      2    94%   45-46
```

Lines listed under "Missing" are not covered by any test. Aim for 90%+ on business logic.

### Excluding lines from coverage

```toml
[tool.coverage.report]
exclude_lines = [
    "if __name__ == .__main__.:",   # Entry point guard
    "raise NotImplementedError",
    "\\.\\.\\.",                    # Ellipsis (abstract methods)
]
```

---

## Useful pytest Fixtures

| Fixture | Purpose |
|---|---|
| `monkeypatch` | Temporarily set env vars, attributes, or dict values |
| `capsys` | Capture stdout/stderr |
| `tmp_path` | Provides a temporary directory unique to each test |
| `caplog` | Capture log output |

---

## Markers

Declare custom markers in `pyproject.toml` to avoid `--strict-markers` failures:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
]
```

Then use them:

```python
@pytest.mark.slow
def test_heavy_computation():
    ...
```

Run only fast tests:
```bash
just test -m "not slow"
```
