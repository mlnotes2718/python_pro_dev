# Dependency Management: uv + conda Summary

### The Core Mental Model
The ecosystem splits cleanly into two layers. Conda owns the system layer — Python interpreter, CUDA, native compiled libraries. uv owns the Python layer — package resolution, lockfiles, virtual environments. Understanding this split is the foundation of every decision below.

### Why pip Alone Falls Short
pip's resolver is greedy and sequential — it solves one install at a time without a full picture of the dependency graph. This is why installing packages one by one can silently create an inconsistent environment, and why bundling everything into one command became a workaround. PyPI metadata quality is also historically inconsistent, with many packages having loose or incomplete version constraints. pip has no awareness of native system libraries, so conflicts at that level are invisible to it.

### Why uv Is Better Than pip
uv uses a proper backtracking resolver that sees the full dependency graph before installing anything. Adding packages one at a time is safe because uv re-resolves the entire graph on each uv add. The uv.lock file freezes the exact resolved version of every transitive dependency, making environments fully reproducible. Conflict error messages are specific and actionable. For pure Python dependency management, uv is a substantial upgrade over pip in every dimension.

### Why Conda Still Has a Role
Conda's solver reasons about system-level native dependencies — CUDA, BLAS/MKL, HDF5, and so on — which are completely invisible to both pip and uv. For GPU workloads, scientific computing with platform-optimized binaries, or any project needing non-Python system dependencies, conda handles what uv fundamentally cannot. Outside of those cases, conda adds complexity without benefit.

## Decision Tree

```
Start a new project
        ↓
Does the project need system-level / native dependencies?
(CUDA, cuDNN, HDF5, MKL, R, platform-compiled binaries)
        ↓
       NO ──────────────────────────→ uv only
        ↓
       YES
        ↓
Does the system dependency exist on conda-forge?
        ↓
       YES ─────────────────────────→ conda (system layer) + uv (Python layer)
        ↓
       NO ──────────────────────────→ conda (system layer) + uv + pip as explicit last resort
```


### Channel Resolution Order (conda)
When conda installs a package, it searches channels in configured priority order: `defaults → conda-forge → PyPI`. PyPI must always be last and treated as an intentional, documented exception — never a default. Installing from PyPI first bypasses conda's solver, making it blind to those packages. This can cause native library conflicts (e.g. two BLAS implementations), unpredictable import behavior, and a loss of conda's environment integrity guarantees.

## Best Practices
### For uv-only projects:

- Default to uv for every project unless you have a concrete reason not to
- Commit both `pyproject.toml` and `uv.lock` — never edit the lockfile manually
- Add packages one at a time freely — uv's resolver handles the full graph each time
- Never commit `.venv/`

### For conda + uv projects:

- Let conda install only what it must — Python interpreter, CUDA, system libs
- Install uv via conda-forge into the env, then use uv for all Python packages
- Commit `environment.yml` (conda layer) and `uv.lock` (Python layer) side by side
- Explicitly flag any PyPI-only packages in `environment.yml` under the `pip:` block so they're visible and auditable
- Verify that uv and conda are pointing at the same Python interpreter — mismatch is the most common setup error
- Use `--no-python-downloads` when initializing uv inside a conda env so uv doesn't try to manage its own Python

### For both:

- Never mix conda and pip/uv installs for Python packages in the same env without explicit intent
- Keep conda responsible for the system layer only — don't use it to install Python packages that uv can handle
- In CI/CD, uv-only pipelines are significantly simpler and faster; conda adds overhead that's only justified if the system layer is genuinely needed

## What to Version Control
| File | Purpose | Commit? |
|---|---|---|
| `pyproject.toml` | Direct Python dependencies | Always |
| `uv.lock` | Full resolved Python dep tree | Always |
| `environment.yml` | Conda system layer | conda+uv projects only |
| `.venv/` | Virtual environment folder | Never |
| `.env` | Secrets and config | Never |



## conda + uv Setup (Reference)
```bash
# 1. Conda handles the system layer
conda create -n myproject python=3.11
conda activate myproject
conda install -c conda-forge cudatoolkit=12.1

# 2. Install uv via conda-forge
conda install -c conda-forge uv

# 3. Initialize uv project — let conda own Python
uv init --no-python-downloads

# 4. Add Python packages via uv
uv add dbt-core dagster pandas

# 5. Sync environment from lockfile
uv sync
```

### Reproducing the environment:
```bash
conda env create -f environment.yml
conda activate myproject
conda install -c conda-forge uv
uv sync
```

### environment.yml structure:
```yml
name: myproject
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - cudatoolkit=12.1
  - uv
  - pip:
      - some-pypi-only-package   # explicit, auditable exception
```