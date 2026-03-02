project_name := "python_pro_dev"

# Returns 'uv' if the command is installed, otherwise 'conda'
env_type := `command -v uv >/dev/null && echo uv || echo conda`

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

# # Run Type Checking
# typecheck:
#     @echo "🛡️  ({{env_type}}) Running Mypy..."
#     @if [ "{{env_type}}" = "uv" ]; then uv run mypy .; else mypy .; fi

# # Run Linting
# lint:
#     @echo "🔍 ({{env_type}}) Running Ruff..."
#     @if [ "{{env_type}}" = "uv" ]; then uv run ruff check . --fix; else ruff check . --fix; fi

# Run Tests
test *args:
    @echo "🧪 ({{env_type}}) Running Pytest..."
    @if [ "{{env_type}}" = "uv" ]; then uv run pytest {{args}}; else pytest {{args}}; fi

# Run Linting on src directory only
lint:
    @echo "🔍 ({{env_type}}) Running Ruff on src/..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run ruff check src --fix; \
    else \
        ruff check src --fix; \
    fi

# Run Type Checking on src directory only
typecheck:
    @echo "🛡️  ({{env_type}}) Running Mypy on src/..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run mypy src; \
    else \
        mypy src; \
    fi    

# Run all checks
all: lint typecheck test 

# Remove build, cache, and coverage artifacts
clean:
    @echo "🧹 Cleaning up project..."
    rm -rf .pytest_cache
    rm -rf .coverage
    rm -rf htmlcov
    rm -rf .mypy_cache
    rm -rf .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    @echo "✨ Cleaned!"