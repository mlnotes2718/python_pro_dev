# tests/test_main.py
import pytest
from unittest.mock import patch
from main import add_func, multiply, show_data, main
import pandas as pd

# --- Test simple functions (easy wins) ---
def test_add_func():
    assert add_func(2, 3) == 5
    assert add_func(1.5, 2.5) == 4.0

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(2.5, 2) == 5.0

def test_show_data(capsys):
    df = pd.DataFrame({"a": [1, 2]})
    show_data(df)
    captured = capsys.readouterr()
    assert "a" in captured.out

# --- Test main() with PASSWORD set ---
def test_main_success():
    with patch.dict("os.environ", {"PASSWORD": "secret"}):
        result = main()
        assert result == 0

# --- Test main() without PASSWORD ---
def test_main_no_password():
    with patch.dict("os.environ", {}, clear=True):
        with patch("main.os.getenv", return_value=None):
            with pytest.raises(OSError, match="PASSWORD environment variable not set"):
                main()