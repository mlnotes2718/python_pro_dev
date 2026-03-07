# Python Notebook Tools — Professional Reference Guide

> Covers tool overview, use cases, frequency, and detailed usage for **jupytext**, **nbconvert**, **nbdime**, and **nbqa**.
> Installation shown for both **uv** and **conda** environments.

---

## 1. Tool Overview & Decision Matrix

| Tool | Purpose | When to Use | Frequency in Industry |
|---|---|---|---|
| **jupytext** | Sync notebook ↔ `.py` for linting | Logic lives permanently in notebooks | Common in notebook-heavy teams |
| **nbconvert** | Export notebook to HTML/PDF/script | Sharing reports with stakeholders | Very common, almost universal |
| **nbdime** | Human-readable notebook diffs & merges | Any team using git with notebooks | Growing rapidly, becoming standard |
| **nbqa** | Run ruff/mypy/bandit inside notebook cells | Enforcing code quality in notebooks | Moderate, notebook-first teams |
| **nbmake** | Run notebooks as pytest tests | CI validation that notebooks execute | Less common, CI-focused teams |
| **papermill** | Parameterize and execute notebooks via CLI | Scheduled pipelines, experiment runs | Common in data engineering teams |
| **nbstripout** | Strip outputs before commit | Preventing PII/secret leaks in outputs | Common where data privacy matters |
| **ydata-profiling** | Automated EDA reports | Quick dataset overview | Common in EDA-heavy teams |
| **pandera** | DataFrame schema validation | Data quality enforcement | Growing rapidly |

---

## 2. When to Use Each Tool

### jupytext
Use when:
- Significant reusable logic lives in notebooks long-term
- You want ruff/mypy/bandit to cover notebook code
- Team needs `.py` mirrors for clean git history without losing notebook UX

Skip when:
- Notebooks are pure EDA/visualization with outputs as the deliverable
- All logic is properly extracted to `src/`

### nbconvert
Use when:
- Sharing analysis with non-technical stakeholders
- Generating HTML/PDF reports from executed notebooks
- Converting notebooks to scripts for pipeline use

Skip when:
- Internal team review (nbdime is better for this)

### nbdime
Use when:
- Any team storing notebooks in git
- Reviewing notebook PRs
- Resolving merge conflicts in notebooks

Skip when:
- Notebooks are never committed to git (rare)

### nbqa
Use when:
- Notebook logic is complex enough to warrant linting
- Team enforces ruff/mypy standards across all Python including notebooks
- Pre-commit hooks should cover notebooks

Skip when:
- Notebooks are exploratory scratchpads
- All real logic lives in `src/`

---

## 3. Installation

### 3.1 uv

```bash
# Add all notebook tools as dev dependencies
uv add --dev jupytext nbconvert nbdime nbqa

# Optional extras
uv add --dev nbmake nbstripout ydata-profiling
uv add pandera  # production dependency, not dev

# Verify installations
uv run jupytext --version
uv run jupyter nbconvert --version
uv run nbdime --version
uv run nbqa --version
```

### 3.2 conda

```bash
# Activate your environment first
conda activate myenv

# Install from conda-forge (preferred channel for data science tools)
conda install -c conda-forge jupytext nbconvert nbdime nbqa

# Optional extras
conda install -c conda-forge nbmake nbstripout

# ydata-profiling and pandera via pip inside conda env
pip install ydata-profiling pandera

# Verify installations
jupytext --version
jupyter nbconvert --version
nbdime --version
nbqa --version
```

> **Note for conda users:** Always prefer `conda-forge` over `defaults` channel for notebook tools — packages are more up to date and better maintained.

---

## 4. Detailed Usage Guide

---

### 4.1 jupytext

#### What it does
Keeps a `.py` mirror of your notebook in sync automatically. The `.py` file is committed to git; the `.ipynb` stays local or is regenerated on demand.

#### Setup — pair a notebook with a `.py` file

```bash
# Pair an existing notebook
uv run jupytext --set-formats ipynb,py:percent notebook.ipynb

# This creates notebook.py and adds pairing config to notebook.ipynb metadata
```

The `py:percent` format uses `# %%` cell markers — readable and compatible with VS Code, PyCharm, and Spyder.

#### Sync workflow

```bash
# Sync .ipynb → .py (after working in notebook)
uv run jupytext --sync notebook.ipynb

# Sync .py → .ipynb (after editing .py or pulling from git)
uv run jupytext --sync notebook.py

# Convert .py back to .ipynb explicitly
uv run jupytext --to notebook notebook.py
```

#### Auto-sync via jupytext config

Add to `pyproject.toml` to auto-sync on every save in Jupyter:

```toml
[tool.jupytext]
formats = "ipynb,py:percent"
```

Or create `jupytext.toml` at project root:

```toml
formats = "ipynb,py:percent"
notebook_metadata_filter = "-all"   # strip notebook-level metadata from .py
cell_metadata_filter = "-all"       # strip cell-level metadata from .py
```

#### What the `.py` file looks like

```python
# %% [markdown]
# ## EDA — Sales Analysis

# %%
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/sales.csv")
df.head()

# %%
df.describe()
```

#### Git workflow with jupytext

```bash
# .gitignore — keep .py, optionally keep .ipynb
echo "*.ipynb" >> .gitignore   # if stripping notebooks from git
# OR commit both — nbdime handles the .ipynb diffs

# Commit only the .py mirror
git add notebook.py
git commit -m "analysis: add sales EDA"

# Colleague pulls and recreates notebook
uv run jupytext --to notebook notebook.py
uv run jupyter nbconvert --to notebook --execute notebook.ipynb  # re-run to get outputs
```

#### Pre-commit integration

```yaml
- repo: https://github.com/mwouts/jupytext
  rev: v1.16.4
  hooks:
    - id: jupytext
      args: [--sync]
      stages: [pre-commit]
```

---

### 4.2 nbconvert

#### What it does
Converts executed notebooks to shareable formats: HTML, PDF, script, slides, Markdown, LaTeX.

#### Basic conversions

```bash
# HTML — most common, preserves all outputs and charts
uv run jupyter nbconvert --to html analysis.ipynb
# Output: analysis.html

# HTML with custom template (cleaner, no code cells shown)
uv run jupyter nbconvert --to html --no-input analysis.ipynb
# Output: analysis.html (outputs only, no source code — great for stakeholders)

# PDF (requires LaTeX: sudo apt install texlive-xetex)
uv run jupyter nbconvert --to pdf analysis.ipynb

# Python script (strips outputs, keeps code)
uv run jupyter nbconvert --to script analysis.ipynb
# Output: analysis.py

# Markdown (useful for documentation sites)
uv run jupyter nbconvert --to markdown analysis.ipynb
```

#### Execute then convert in one step

```bash
# Re-execute notebook top to bottom, then convert to HTML
uv run jupyter nbconvert --to html --execute analysis.ipynb

# Execute with timeout (fail if a cell takes longer than 300s)
uv run jupyter nbconvert --to html --execute --ExecutePreprocessor.timeout=300 analysis.ipynb
```

#### Output to specific directory

```bash
# Send all reports to reports/ folder
uv run jupyter nbconvert --to html --output-dir reports/ analysis.ipynb

# Batch convert all notebooks in a folder
uv run jupyter nbconvert --to html --output-dir reports/ notebooks/*.ipynb
```

#### just recipe example

```makefile
# justfile
report:
    jupyter nbconvert --to html --no-input --output-dir reports/ notebooks/analysis.ipynb
    @echo "Report saved to reports/analysis.html"

report-execute:
    jupyter nbconvert --to html --execute --no-input --output-dir reports/ notebooks/analysis.ipynb
```

---

### 4.3 nbdime

#### What it does
Provides diff and merge tools that understand notebook structure — ignores execution counts and metadata noise, focuses on actual content and output changes.

#### Setup — integrate with git

```bash
# One-time setup: register nbdime as git diff/merge driver
uv run nbdime config-git --enable

# Verify
cat .git/config  # should show nbdime entries
```

This makes `git diff`, `git log -p`, and `git merge` all use nbdime automatically for `.ipynb` files.

#### Diff commands

```bash
# Terminal diff — structured, readable
uv run nbdiff notebook_v1.ipynb notebook_v2.ipynb

# Web-based visual diff — best for charts and rich outputs
uv run nbdiff-web notebook_v1.ipynb notebook_v2.ipynb

# Diff against git history
uv run nbdiff HEAD notebook.ipynb              # vs last commit
uv run nbdiff HEAD~3 HEAD notebook.ipynb      # vs 3 commits ago
uv run nbdiff main feature-branch notebook.ipynb  # vs another branch
```

#### Merge commands

```bash
# Merge with conflict resolution
uv run nbmerge base.ipynb local.ipynb remote.ipynb -o merged.ipynb

# Interactive web-based merge tool
uv run nbmerge-web base.ipynb local.ipynb remote.ipynb
```

#### What nbdime ignores vs shows

| Element | `git diff` (raw) | nbdime |
|---|---|---|
| Cell source code | ✅ noisy JSON | ✅ clean, readable |
| Cell outputs/charts | ✅ massive JSON blob | ✅ rendered visually |
| Execution count | ✅ noisy noise | ❌ ignored |
| Cell metadata | ✅ noisy | ❌ ignored |
| Notebook metadata | ✅ noisy | ❌ ignored |
| Cell order changes | hard to read | ✅ shown clearly |

#### Pre-commit integration

```yaml
- repo: https://github.com/jupyter/nbdime
  rev: 4.0.2
  hooks:
    - id: nbdime-hooks
      stages: [pre-commit]
```

---

### 4.4 nbqa

#### What it does
Wraps your existing Python tools (ruff, mypy, bandit, isort) to run inside notebook cells, treating each cell as a Python module.

#### Basic usage

```bash
# Run ruff on all notebooks in notebooks/ folder
uv run nbqa ruff notebooks/

# Run ruff with auto-fix
uv run nbqa ruff notebooks/ --fix

# Run ruff on a single notebook
uv run nbqa ruff notebooks/analysis.ipynb

# Run mypy
uv run nbqa mypy notebooks/

# Run bandit security scan
uv run nbqa bandit notebooks/ -ll

# Run isort (if not using ruff's I rules)
uv run nbqa isort notebooks/
```

#### Typical findings in notebooks (and how to handle them)

```python
# Common nbqa finding: unused import in cell
import numpy as np   # F401 if np never used in that cell

# Fix: add noqa comment for intentional notebook-style imports
import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
```

> **Note:** Many ruff findings in notebooks are intentional (broad imports at top, print statements, etc.). Use per-file ignores or `# noqa` comments liberally in notebooks — the goal is catching real bugs, not enforcing strict module-style conventions.

#### Recommended nbqa config for notebooks

Add to `pyproject.toml`:

```toml
[tool.nbqa.addopts]
ruff = "--ignore=E402,F401,T201"   # ignore import order, unused imports, print in notebooks
mypy = "--ignore-missing-imports"  # notebooks often import without stubs
```

#### Pre-commit integration

```yaml
- repo: https://github.com/nbQA-dev/nbQA
  rev: 1.9.1
  hooks:
    - id: nbqa-ruff
      args: [--fix]
      stages: [pre-commit]
    - id: nbqa-mypy
      stages: [pre-push]   # slow, push only
```

---

## 5. Recommended Combined Setup

### For notebook-first teams (logic stays in notebooks)

```
jupytext   → .py mirror for ruff/mypy coverage
nbdime     → readable diffs and merge conflict resolution
nbqa       → run ruff/mypy directly inside cells
nbconvert  → export reports to HTML for stakeholders
```

### For EDA + report notebooks

```
nbdime     → readable diffs (essential)
nbconvert  → HTML/PDF report delivery (essential)
nbqa       → optional, only if notebooks contain complex logic
jupytext   → skip (logic should live in src/)
```

### Pre-commit hook order recommendation

```yaml
# Fast checks on commit
- nbdime-hooks      # pre-commit: validates notebook structure
- nbqa-ruff         # pre-commit: lint notebook cells

# Slow checks on push
- nbqa-mypy         # pre-push: type check notebook cells
```

---

## 6. Quick Reference Cheatsheet

```bash
# jupytext
jupytext --sync notebook.ipynb          # sync notebook ↔ .py
jupytext --to notebook notebook.py      # recreate .ipynb from .py

# nbconvert
jupyter nbconvert --to html analysis.ipynb                    # export to HTML
jupyter nbconvert --to html --no-input analysis.ipynb         # HTML, no code shown
jupyter nbconvert --to html --execute analysis.ipynb          # re-run then export
jupyter nbconvert --to html --output-dir reports/ notebooks/*.ipynb  # batch export

# nbdime
nbdime config-git --enable              # one-time git integration
nbdiff notebook_v1.ipynb notebook_v2.ipynb    # terminal diff
nbdiff-web notebook_v1.ipynb notebook_v2.ipynb  # visual diff
nbdiff HEAD notebook.ipynb              # diff vs last commit

# nbqa
nbqa ruff notebooks/ --fix             # lint + fix all notebooks
nbqa mypy notebooks/                   # type check all notebooks
nbqa bandit notebooks/ -ll             # security scan all notebooks
```

---

## 7. Environment Notes

### uv (primary)
All tools installed as dev dependencies in `pyproject.toml`. Run via `uv run <tool>` to ensure correct environment is used.

### conda (ML projects)
- Install via `conda-forge` where available for better compatibility with ML packages
- For tools not on conda-forge (`ydata-profiling`, `pandera`), use `pip install` inside the activated conda env
- Always activate the conda env before running tools: `conda activate myenv`
- Conda envs should be locked via `conda env export > environment.yml` for reproducibility
