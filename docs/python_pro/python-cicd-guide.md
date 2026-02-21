# Professional Python Development: CI/CD Workflow Guide

## Essential Tools Overview

### Core Development Tools
- **ruff** - Fast linting and code formatting (replaces black, flake8, isort)
- **mypy** - Static type checking to catch bugs before runtime
- **pytest** - Unit testing framework
- **pytest-cov** - Code coverage measurement
- **pre-commit** - Git hooks that run checks before commits
- **bandit** - Security vulnerability scanner

### Dependency Management
- **uv** - Modern, fast package manager (recommended for pure Python projects)
- **conda** - Alternative for projects with non-Python dependencies (data science/ML)

**Note:** All dev tools (ruff, mypy, pytest, etc.) work with either uv or conda.

---

## Project Structure

### Recommended: src/ Layout
```
myproject/                          # Repository root
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI/CD
├── src/
│   └── myproject/                  # Your importable package
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/
│   ├── __init__.py
│   └── test_module1.py
├── docs/
├── .gitignore
├── .pre-commit-config.yaml         # Pre-commit hooks config
├── pyproject.toml                  # Central configuration
└── README.md
```

**Why `src/` layout?**
- Forces proper package installation
- Tests run against installed package (not loose files)
- Catches packaging errors early
- Modern best practice

---

## Initial Setup

### 1. Create Project Environment

#### Option A: Using uv (recommended for pure Python)
```bash
# Create project directory
mkdir myproject && cd myproject
git init

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install ruff mypy pytest pytest-cov pre-commit bandit pydantic
```

#### Option B: Using conda (for data science/ML projects)
```bash
# Create project directory
mkdir myproject && cd myproject
git init

# Create conda environment
conda create -n myproject python=3.11
conda activate myproject

# Install main dependencies via conda
conda install numpy pandas scikit-learn

# Install dev tools via pip
pip install ruff mypy pytest pytest-cov pre-commit bandit pydantic
```

### 2. Create Project Structure
```bash
mkdir -p src/myproject tests docs .github/workflows
touch src/myproject/__init__.py
touch pyproject.toml .gitignore .pre-commit-config.yaml
```

---

## Configuration Files

### `pyproject.toml` - Central Configuration
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "myproject"
version = "0.1.0"
description = "My awesome project"
dependencies = [
    "pydantic>=2.0",
    "numpy",
]

[project.optional-dependencies]
dev = [
    "ruff",
    "mypy",
    "pytest",
    "pytest-cov",
    "pre-commit",
    "bandit",
]

[tool.setuptools.packages.find]
where = ["src"]

# Ruff configuration
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]  # Error, pyflakes, import, naming, warnings
ignore = []

# Mypy configuration
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

# Pytest configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"

# Coverage configuration
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*"]

[tool.coverage.report]
fail_under = 80  # Require at least 80% coverage
```

### `.pre-commit-config.yaml` - Automated Pre-Commit Checks
```yaml
repos:
  # Ruff for linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  # Mypy for type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
  
  # Bandit for security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]
        
  # Basic pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Install pre-commit hooks:**
```bash
pre-commit install
```

### `.github/workflows/ci.yml` - GitHub Actions CI/CD
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"
      
      - name: Lint with ruff
        run: |
          ruff check .
          ruff format --check .
      
      - name: Type check with mypy
        run: mypy src/
      
      - name: Security scan with bandit
        run: bandit -r src/
      
      - name: Test with pytest
        run: pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          echo "Deploy steps here"
          # ./deploy.sh or other deployment commands
```

### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
.env
```

---

## Daily Development Workflow

### 1. Start New Feature
```bash
git checkout -b feature/new-feature
```

### 2. Write Code

**Example: `src/myproject/users.py`**
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    """User model with validation."""
    name: str = Field(min_length=1)
    email: str
    age: int = Field(ge=0, le=150)
    
def create_user(name: str, email: str, age: int) -> User:
    """Create and validate a new user."""
    return User(name=name, email=email, age=age)
```

**Example: `tests/test_users.py`**
```python
import pytest
from pydantic import ValidationError
from myproject.users import User, create_user

def test_create_user_valid():
    user = create_user("Alice", "alice@example.com", 30)
    assert user.name == "Alice"
    assert user.age == 30

def test_create_user_invalid_age():
    with pytest.raises(ValidationError):
        create_user("Bob", "bob@example.com", -5)

def test_create_user_invalid_name():
    with pytest.raises(ValidationError):
        create_user("", "test@example.com", 25)
```

### 3. Run Manual Checks (During Development)
```bash
# Format code
ruff format .

# Lint and auto-fix
ruff check . --fix

# Type check
mypy src/

# Run tests with coverage
pytest

# Or run all tests verbosely
pytest -v --cov=src --cov-report=term-missing

# Security scan
bandit -r src/

# Run pre-commit on all files (optional)
pre-commit run --all-files
```

### 4. Commit Code
```bash
git add .
git commit -m "Add user validation with pydantic"
```

**What happens:**
- Pre-commit hooks automatically run:
  - ✓ Ruff format & lint
  - ✓ Mypy type check
  - ✓ Bandit security scan
  - ✓ Trailing whitespace, YAML checks, etc.
- If any check fails → commit blocked, fix issues
- If all pass → commit succeeds

### 5. Push and Create Pull Request
```bash
git push origin feature/new-feature
```

**What happens:**
- GitHub Actions CI runs automatically:
  - Runs on multiple Python versions (3.10, 3.11, 3.12)
  - All linting, type checking, security scanning
  - Full test suite with coverage
  - Coverage report uploaded to Codecov
- CI status shows in PR (✓ or ✗)

### 6. Code Review & Merge
- Team reviews code
- CI must pass (green checkmark)
- Merge to `main`

### 7. Deployment (Automatic)
- CI runs again on `main` branch
- If all tests pass → deploy job runs (only on `main`)
- Code deployed to production

---

## Complete CI/CD Flow Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                   Developer Workflow                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                 Write code in feature branch
                            │
                            ▼
              Run manual checks (optional but recommended)
              • ruff format/check
              • mypy
              • pytest
              • bandit
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│  git commit                                               │
│    ↓                                                      │
│  Pre-commit hooks run automatically:                     │
│    ✓ Ruff lint & format                                  │
│    ✓ Mypy type check                                     │
│    ✓ Bandit security scan                                │
│    ✓ File checks (trailing whitespace, YAML, etc.)      │
│                                                           │
│  If hooks fail → Fix issues, commit again                │
│  If hooks pass → Commit succeeds                         │
└───────────────────────────────────────────────────────────┘
                            │
                            ▼
                      git push origin feature/new-feature
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│  GitHub Actions CI (runs on GitHub servers)              │
│    ↓                                                      │
│  Triggered on: push to any branch, pull requests         │
│    ✓ Test on Python 3.10, 3.11, 3.12                     │
│    ✓ Ruff check & format validation                      │
│    ✓ Mypy type checking                                  │
│    ✓ Bandit security scanning                            │
│    ✓ Full pytest suite with coverage                     │
│    ✓ Upload coverage reports                             │
│                                                           │
│  Results shown in PR/commit (✓ passed or ✗ failed)       │
└───────────────────────────────────────────────────────────┘
                            │
                            ▼
                    Create Pull Request
                            │
                            ▼
                   Code review by team
                            │
                            ▼
                 CI must pass + approval received
                            │
                            ▼
                      Merge to main
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│  GitHub Actions CI runs again on main                     │
│    ✓ All tests pass                                      │
│    ✓ Coverage threshold met                              │
│    ↓                                                      │
│  Deploy job runs (only on main branch):                  │
│    → Deploy to staging/production                        │
│    → Update documentation                                │
│    → Publish package (if applicable)                     │
└───────────────────────────────────────────────────────────┘
```

---

## When CI Runs

| Event | Where | What Runs |
|-------|-------|-----------|
| `git commit` | **Local machine** | Pre-commit hooks (ruff, mypy, bandit) |
| `git push` to feature branch | **GitHub** | Full CI (all tests, all Python versions) |
| Open/update Pull Request | **GitHub** | Full CI (ensures merge safety) |
| Merge to `main` | **GitHub** | Full CI + Deploy job |

**Key insight:** CI runs on ALL branches, not just feature branches. This provides maximum safety.

---

## Tool Purposes Summary

| Tool | Purpose | When It Runs |
|------|---------|--------------|
| **ruff** | Linting + formatting (catches style issues, unused imports) | Pre-commit, CI |
| **mypy** | Static type checking (catches type errors before runtime) | Pre-commit, CI |
| **pytest** | Unit testing (verifies code correctness) | Manual, CI |
| **pytest-cov** | Code coverage (shows untested code) | Manual, CI |
| **pre-commit** | Runs checks automatically before commits | Every `git commit` |
| **bandit** | Security scanning (finds common vulnerabilities) | Pre-commit, CI |

---

## Best Practices Checklist

- ✅ Use `src/` layout for proper package structure
- ✅ Configure all tools in `pyproject.toml` (single source of truth)
- ✅ Install pre-commit hooks to catch issues before commit
- ✅ Set up CI to run on all branches and PRs
- ✅ Aim for >80% test coverage
- ✅ Use type hints and enforce with mypy
- ✅ Run security scans with bandit
- ✅ Keep dependencies updated
- ✅ Write tests alongside code (not after)
- ✅ Make CI a requirement for merging PRs

---

## Quick Reference Commands
```bash
# Install package in development mode
pip install -e ".[dev]"

# Format code
ruff format .

# Lint with auto-fix
ruff check . --fix

# Type check
mypy src/

# Run tests with coverage
pytest --cov=src --cov-report=html

# View coverage report in browser
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux

# Security scan
bandit -r src/

# Run all pre-commit hooks manually
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate

# Clean up cache files
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

---

## Advanced Topics

### Running Tests in Parallel
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (auto-detect CPU cores)
pytest -n auto
```

### Generating HTML Coverage Reports
```bash
# Generate and open coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Using Coverage Badges
Add to your `README.md`:
```markdown
[![codecov](https://codecov.io/gh/username/myproject/branch/main/graph/badge.svg)](https://codecov.io/gh/username/myproject)
```

### Configuring Different CI Behaviors per Branch
```yaml
# In .github/workflows/ci.yml
jobs:
  test:
    # Always run tests
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: pytest
  
  deploy-staging:
    # Only deploy to staging from develop branch
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        run: ./deploy-staging.sh
  
  deploy-production:
    # Only deploy to production from main branch
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: ./deploy-production.sh
```

### Matrix Testing with Multiple Dependencies
```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
    pydantic-version: ["1.10", "2.0"]
steps:
  - name: Install dependencies
    run: |
      pip install pydantic==${{ matrix.pydantic-version }}
```

---

## Troubleshooting Common Issues

### Pre-commit Hooks Fail
```bash
# See what failed
git commit -m "message"  # Will show errors

# Run manually to debug
pre-commit run --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify -m "message"

# Update hooks
pre-commit autoupdate
```

### Mypy Type Errors
```bash
# Check specific file
mypy src/myproject/users.py

# Ignore specific error (use sparingly)
# Add comment in code
result = some_function()  # type: ignore[attr-defined]

# Or configure in pyproject.toml
[tool.mypy]
ignore_missing_imports = true  # For third-party libraries without types
```

### Tests Pass Locally but Fail in CI
Common causes:
- Different Python versions
- Missing dependencies in CI
- Environment-specific paths
- Timezone/locale differences

Solution:
```bash
# Test locally with same Python version as CI
pyenv install 3.11
python3.11 -m pytest

# Or use tox to test multiple versions
pip install tox
tox
```

### Coverage Too Low
```bash
# Find untested code
pytest --cov=src --cov-report=term-missing

# Generate detailed HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Temporarily lower threshold while improving
[tool.coverage.report]
fail_under = 70  # Increase gradually to 80+
```

---

## Footnote: Pydantic

**Pydantic** is a **production code library** (not a development tool) used for:

### Purpose
- **Data validation** - Automatically validates data types and constraints
- **Settings management** - Parse and validate configuration from environment variables
- **API data models** - Define request/response schemas (commonly used with FastAPI)
- **Type safety** - Runtime validation of Python type hints

### Example Use Cases

#### 1. Data Validation
```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    is_active: bool = True

# Automatic validation
user = User(name="Alice", email="alice@example.com", age=30)  # ✓ Valid
# User(name="", email="invalid", age=-5)  # ✗ Raises ValidationError
```

#### 2. Settings/Configuration Management
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    debug: bool = False
    max_connections: int = 100
    
    model_config = ConfigDict(env_file='.env')

# Loads from environment variables or .env file
settings = Settings()
print(settings.database_url)  # From DATABASE_URL env var
```

#### 3. API Request/Response Models (with FastAPI)
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str
    age: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):  # Pydantic validates incoming JSON
    # If validation fails, FastAPI automatically returns 422 error
    return UserResponse(id=123, **user.model_dump())
```

#### 4. Complex Nested Models
```python
from typing import List
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class Company(BaseModel):
    name: str
    address: Address
    employees: List[User]

company = Company(
    name="Tech Corp",
    address={"street": "123 Main St", "city": "San Francisco", "zip_code": "94105"},
    employees=[
        {"name": "Alice", "email": "alice@example.com", "age": 30},
        {"name": "Bob", "email": "bob@example.com", "age": 25}
    ]
)
```

### Why Pydantic is Production Code
- Ships with your application
- Users interact with it (via API validation)
- Part of your core business logic
- Not just for testing or development

### Integration with Dev Tools
- **mypy** - Pydantic works seamlessly with type checking
- **pytest** - Test your Pydantic models for validation logic
- **FastAPI** - Pydantic is the foundation of FastAPI's request/response handling

### Testing Pydantic Models
```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from myproject.models import User

def test_user_valid():
    user = User(name="Alice", email="alice@example.com", age=30)
    assert user.name == "Alice"
    assert user.age == 30

def test_user_invalid_email():
    with pytest.raises(ValidationError) as exc_info:
        User(name="Bob", email="not-an-email", age=25)
    assert "email" in str(exc_info.value)

def test_user_invalid_age():
    with pytest.raises(ValidationError):
        User(name="Charlie", email="charlie@example.com", age=-5)

def test_user_serialization():
    user = User(name="Alice", email="alice@example.com", age=30)
    data = user.model_dump()
    assert data == {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "is_active": True
    }
```

Pydantic is considered one of the most important libraries in modern Python development for building robust, type-safe applications.

---

## Additional Resources

### Official Documentation
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Learning Resources
- [Real Python - Testing](https://realpython.com/pytest-python-testing/)
- [Real Python - Type Checking](https://realpython.com/python-type-checking/)
- [Python Packaging User Guide](https://packaging.python.org/)

### Community Standards
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 518 - Build System](https://peps.python.org/pep-0518/)

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Maintained by:** Your Team

---

## License

This guide is provided as-is for educational purposes.

