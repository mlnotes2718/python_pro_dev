# Professional Python Development — Summary Reference

---

## 1. Type Hinting
- Use `int`, `str`, `list`, `dict`, `Optional`, `Union`, `Any` from `typing`
- Enables static analysis and self-documenting code
- 📖 [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- 📖 [Python Docs – typing module](https://docs.python.org/3/library/typing.html)

---

## 2. Functions vs Classes
- Functions for **stateless actions**, Classes for **stateful objects**
- Avoid classes when a simple function will do
- 📖 [Real Python – OOP in Python](https://realpython.com/python3-object-oriented-programming/)

---

## 3. Separate Config from Code
- Use `.env` files, `config.yaml`, or environment variables
- Never hardcode secrets or paths
- 📖 [python-dotenv](https://github.com/theskumar/python-dotenv)
- 📖 [12-Factor App – Config](https://12factor.net/config)

---

## 4. Code Quality — Linting & Formatting
- `ruff` — fast linter (replaces flake8, isort)
- `black` — opinionated auto-formatter
- 📖 [Ruff Docs](https://docs.astral.sh/ruff/)
- 📖 [Black Docs](https://black.readthedocs.io/en/stable/)

---

## 5. Static Type Checking
- `mypy` catches type errors before runtime
- Run as part of CI pipeline
- 📖 [mypy Docs](https://mypy.readthedocs.io/en/stable/)

---

## 6. Docstrings
- Use Google or NumPy style consistently
- Document params, returns, and exceptions
- 📖 [Google Style Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- 📖 [NumPy Style Docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)

---

## 7. Project Structure
- Use `src/` layout to separate source from tests/configs
- Use `pyproject.toml` for packaging metadata
- 📖 [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- 📖 [src layout explained](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

---

## 8. Testing
- `pytest` for unit and integration tests
- `pytest-cov` for coverage (aim 80%+)
- Use fixtures and mocking (`unittest.mock`)
- 📖 [pytest Docs](https://docs.pytest.org/en/stable/)
- 📖 [Real Python – Testing](https://realpython.com/pytest-python-testing/)

---

## 9. Dependency Management
- Pin all dependencies — use `poetry` or `pip-tools`
- Separate dev vs prod dependencies
- Always use virtual environments
- 📖 [Poetry Docs](https://python-poetry.org/docs/)
- 📖 [pip-tools](https://github.com/jazzband/pip-tools)

---

## 10. Error Handling
- Use specific exceptions, never bare `except:`
- Fail loudly and early
- 📖 [Python Docs – Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- 📖 [Real Python – Exception Handling](https://realpython.com/python-exceptions/)

---

## 11. Logging
- Use `logging` module, not `print()`
- Use log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- 📖 [Python Docs – logging](https://docs.python.org/3/library/logging.html)
- 📖 [Real Python – Logging](https://realpython.com/python-logging/)

---

## 12. Security
- Never use `eval()` on user input
- Never commit secrets to version control
- Use `.gitignore` for `.env` files
- 📖 [OWASP Python Security](https://owasp.org/www-project-python-security/)

---

## Bonus — Tools Summary Table

| Category | Tool | Purpose |
|---|---|---|
| Formatting | `black` | Auto-format code |
| Linting | `ruff` | Fast linter |
| Type checking | `mypy` | Static type analysis |
| Testing | `pytest` | Unit/integration tests |
| Coverage | `pytest-cov` | Test coverage report |
| Dependencies | `poetry` | Package management |
| Config | `python-dotenv` | Load `.env` files |
| Pre-commit hooks | `pre-commit` | Run checks before git commit |

---

## Key References
- 📘 [PEP 8 – Style Guide](https://peps.python.org/pep-0008/)
- 📘 [Real Python](https://realpython.com/)
- 📘 [Python Docs](https://docs.python.org/3/)
- 📘 [Hypermodern Python (Claudio Jolowicz)](https://cjolowicz.github.io/posts/hypermodern-python-01-setup/)
- 📘 [Architecture Patterns with Python (O'Reilly)](https://www.cosmicpython.com/book/preface.html) *(free online)*
