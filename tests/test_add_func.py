from src.ruff_test import add_func

assert add_func(2, 3) == 5
assert add_func(2.5, 3.5) == 6.0
assert add_func(-1, 1) == 0
