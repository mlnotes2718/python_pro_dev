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
