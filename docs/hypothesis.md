# Hypothesis — Property-Based Testing

## What It Does

Hypothesis is a property-based testing library. Instead of writing tests with fixed example values, you describe the *properties* a function should always satisfy, and Hypothesis automatically generates hundreds of inputs to try to disprove them. When it finds a failure, it shrinks the input to the smallest possible failing case and remembers it for future runs.

This catches edge cases that hand-written examples miss: extreme floats, empty strings, very large numbers, and combinations you'd never think to test.

---

## Installation

Hypothesis is included in the dev dependencies:

```toml
[dependency-groups]
dev = [
    "hypothesis",
]
```

---

## Running Hypothesis Tests

Hypothesis tests are regular pytest tests — they run automatically with `just test`. No separate command needed.

```bash
just test                          # Runs all tests including Hypothesis
just test -k test_add_func         # Run a specific property test
```

---

## Core Concepts

### Strategies

Strategies are objects that describe what kind of data to generate:

```python
import hypothesis.strategies as st

st.integers()                            # Any integer
st.floats(allow_nan=False, allow_infinity=False)  # Finite floats
st.text()                                # Any string
st.lists(st.integers(), min_size=1)      # Non-empty list of ints
st.booleans()                            # True or False
st.one_of(st.integers(), st.text())      # Either an int or a string
```

### @given decorator

```python
from hypothesis import given
import hypothesis.strategies as st

@given(st.integers(), st.integers())
def test_add_is_commutative(a, b):
    assert add_func(a, b) == add_func(b, a)
```

Hypothesis will run this test with many generated `(a, b)` pairs.

---

## Tests in This Project

### Commutativity

```python
@given(
    st.floats(allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=False, allow_infinity=False),
)
def test_add_func_commutative(a, b):
    """a + b should always equal b + a"""
    assert add_func(a, b) == add_func(b, a)
```

### Identity element

```python
@given(
    st.floats(allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=False, allow_infinity=False),
)
def test_add_func_zero_identity(a, b):
    """adding 0 should not change the value"""
    assume(b == 0)
    assert add_func(a, b) == a
```

`assume()` tells Hypothesis to discard examples where the condition is false and try again. Use it sparingly — it reduces the effective search space.

### Output invariants

```python
@given(st.lists(st.integers(), min_size=1))
def test_show_data_any_column(values):
    """show_data should always print the column name"""
    df = pd.DataFrame({"my_col": values})
    f = io.StringIO()
    with redirect_stdout(f):
        show_data(df)
    assert "my_col" in f.getvalue()
```

---

## Good Properties to Test

| Property | Example |
|---|---|
| Commutativity | `f(a, b) == f(b, a)` |
| Associativity | `f(f(a, b), c) == f(a, f(b, c))` |
| Identity element | `f(a, identity) == a` |
| Idempotency | `f(f(a)) == f(a)` |
| Round-trip | `decode(encode(x)) == x` |
| Output invariants | Result always has expected length, type, or structure |
| No exceptions | Function never raises for valid inputs |

---

## Shrinking and the Database

When Hypothesis finds a failing example, it automatically shrinks it to the simplest possible input that still fails. It also stores failing examples in a local `.hypothesis/` database so they are replayed on future runs even after the code is fixed — ensuring regressions are caught.

Add `.hypothesis/` to `.gitignore` unless you want to share the example database across machines.

---

## Settings

Adjust how many examples Hypothesis generates:

```python
from hypothesis import given, settings

@settings(max_examples=500)   # default is 100
@given(st.integers())
def test_something(x):
    ...
```

For CI you may want fewer examples for speed; for a thorough local run, use more.
