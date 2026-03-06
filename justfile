project_name := "python_pro_dev"

# Returns 'uv' if the command is installed, otherwise 'conda'
env_type := `[ -n "$CONDA_PREFIX" ] && echo "conda" || echo "uv"`

# Default: List commands
default:
    @just --list

# Setup the environment
setup:
    @echo "🚀 Using {{env_type}} environment..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv sync; \
        uv run pre-commit install; \
    else \
        conda env create -f ./conda_env/dev_env.yml; \
        pre-commit install --hook-type pre-commit --hook-type pre-push; \
    fi

## Start of development commands

# Run Tests
test *args:
    @echo "🧪 ({{env_type}}) Running Pytest..."
    @if [ "{{env_type}}" = "uv" ]; then uv run pytest {{args}}; else pytest {{args}}; fi

# Run Linting on src directory only
lint:
    @echo "🔍 ({{env_type}}) Running Ruff on src/..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run ruff check . --fix; \
    else \
        ruff check . --fix; \
    fi

# Run Type Checking on src directory only
typecheck:
    @echo "🛡️  ({{env_type}}) Running Mypy on src/..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run mypy .; \
    else \
        mypy .; \
    fi

# Run Security Scan on src directory only
sec:
    @echo "🔒  ({{env_type}}) Running Bandit on src/..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run bandit -r . -ll -c pyproject.toml; \
    else \
        bandit -r . -ll -c pyproject.toml; \
    fi

# Run pip-audit on the current environment
audit:
    @echo "🔒  ({{env_type}}) Running audit..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run pip-audit --local; \
    else \
        pip-audit --local; \
    fi

# Check environment health
health:
    @echo "🩺 Checking environment health..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv pip check; \
        uv sync; \
    else \
        conda doctor; \
    fi

precommit:
    @echo "🔍  ({{env_type}}) Running pre-commit..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run pre-commit run --all-files; \
    else \
        pre-commit run --all-files; \
    fi

# Run all checks
run: lint typecheck health audit sec test clean

# Remove build, cache, and coverage artifacts
clean:
    @echo "🧹 Cleaning up project..."
    rm -rf .pytest_cache
    rm -rf .coverage
    rm -rf htmlcov
    rm -rf .mypy_cache
    rm -rf .ruff_cache
    rm -rf .hypothesis
    find . -type d -name "__pycache__" -exec rm -rf {} +
    @echo "✨ Cleaned!"
