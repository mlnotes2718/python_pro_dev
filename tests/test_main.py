from unittest.mock import patch

import hypothesis.strategies as st
import pandas as pd
import pytest
from hypothesis import assume, given

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


def test_main_success(monkeypatch) -> None:
    # 1. Mock the environment variable
    monkeypatch.setenv("PASSWORD", "secret")

    # 2. Mock load_dotenv (using patch as a decorator is often cleaner)
    with patch("main.load_dotenv"):
        result = main()
        assert result == 0


def test_main_no_password() -> None:
    # Everything goes into one block, separated by commas
    with (
        patch("main.load_dotenv"),
        patch.dict("os.environ", {}, clear=True),
        patch("main.logger"),
        pytest.raises(OSError, match="PASSWORD environment variable not set"),
    ):
        main()


# ── new hypothesis tests (added alongside) ──────────────────────────────────


@given(
    st.floats(allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=False, allow_infinity=False),
)
def test_add_func_commutative(a, b):
    """a + b should always equal b + a"""
    assert add_func(a, b) == add_func(b, a)


@given(
    st.floats(allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=False, allow_infinity=False),
)
def test_add_func_zero_identity(a, b):
    """adding 0 should not change the value"""
    assume(b == 0)
    assert add_func(a, b) == a


@given(
    st.floats(allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=False, allow_infinity=False),
)
def test_multiply_commutative(a, b):
    """a * b should always equal b * a"""
    assert multiply(a, b) == multiply(b, a)


@given(
    st.floats(allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=False, allow_infinity=False),
)
def test_multiply_by_zero(a, b):
    """multiplying by 0 should always return 0"""
    assume(b == 0)
    assert multiply(a, b) == 0


@given(st.lists(st.integers(), min_size=1))
def test_show_data_any_column(values):
    """show_data should always print column name regardless of content"""
    import io
    from contextlib import redirect_stdout

    df = pd.DataFrame({"my_col": values})
    f = io.StringIO()
    with redirect_stdout(f):
        show_data(df)
    output = f.getvalue()
    assert "my_col" in output
