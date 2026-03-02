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
    with patch("main.load_dotenv"):  # prevent dotenv from overwriting
        with patch.dict("os.environ", {"PASSWORD": "secret"}):
            result = main()
            assert result == 0


def test_main_no_password() -> None:
    with patch("main.load_dotenv"):
        with patch.dict("os.environ", {}, clear=True):
            with patch("main.logger") as mock_logger:
                with pytest.raises(
                    OSError, match="PASSWORD environment variable not set"
                ):
                    main()
                    mock_logger.error.assert_called_with(
                        "[TEST] PASSWORD environment variable not set"
                    )
