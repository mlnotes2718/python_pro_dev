# Modern Python Project Structure (Using uv)

This document summarizes best practices for structuring and running Python projects using modern tooling.

Topics covered:
- `src` layout
- module execution (`python -m`)
- `__name__ == "__main__"`
- dependency management with `uv`
- recommended development workflow

---

# 1. The `src` Project Layout

A modern Python project often uses a **src layout**.

```

project/
│
├── src/
│   └── ml_project/
│       ├── **init**.py
│       ├── pipelines/
│       ├── models/
│       ├── utils/
│       └── main.py
│
├── tests/
├── notebooks/
├── pyproject.toml
└── README.md

```

## Why `src` exists

Without `src`, Python may import your package directly from the project root instead of the installed package.

This can hide packaging errors.

Example problem:

```

project/
│
├── ml_project/
│   └── module.py

```

Tests may pass because Python finds the module in the local folder, but users installing the package may encounter errors.

The `src` layout forces Python to use the **installed package**, ensuring correctness.

---

# 2. Installing the Project (Editable Mode Concept)

Python projects normally install packages into `site-packages`.

Editable installs create a **link to the source code** instead.

Conceptually:

```

site-packages/
ml_project → /project/src/ml_project

```

This means:

- changing source code updates immediately
- no reinstall needed

Historically this was done with:

```

pip install -e .

```

With modern tools like `uv`, this is handled automatically.

---

# 3. Running Python Modules Properly

There are two ways to run Python code.

## Running a file

```

python main.py

```

Python treats the file as a **standalone script**.

Problem: package imports may break.

---

## Running a module

```

python -m package.module

```

Example:

```

python -m ml_project.main

```

This tells Python:

```

run module inside package system

```

Benefits:

- correct import behavior
- respects package hierarchy
- recommended for structured projects

---

# 4. The `__name__ == "__main__"` Guard

Every Python file has a special variable:

```

**name**

```

### When running a file directly

```

python main.py

```

Value becomes:

```

**name** = "**main**"

```

---

### When importing the file

```

import main

```

Value becomes:

```

**name** = "main"

```

---

## Why the guard exists

Example:

```

def train():
print("Training model")

train()

```

Importing this module would run training immediately.

To prevent this:

```

def train():
print("Training model")

if **name** == "**main**":
train()

```

Now the function only runs when the file is executed directly.

---

# 5. Using uv for Dependency Management

Modern Python development increasingly uses `uv`.

Typical tools replaced:

| Traditional Tool | uv Replacement |
|------------------|---------------|
| pip | uv |
| virtualenv | uv venv |
| pip-tools | uv lock/sync |

`uv` manages:

- environments
- dependencies
- lockfiles
- execution

---

# 6. Key uv Commands

## Create environment

```

uv venv

```

---

## Install dependencies

```

uv sync

```

This installs everything defined in:

```

pyproject.toml
uv.lock

```

Including your project package.

---

## Add dependency

```

uv add pandas

```

This updates:

```

pyproject.toml
uv.lock

```

---

## Run commands inside environment

```

uv run python -m ml_project.main

```

or

```

uv run pytest

```

---

# 7. uv sync vs uv pip install

## uv sync

```

uv sync

```

Purpose:

- reproduce environment exactly
- install dependencies
- install project package
- enforce lockfile

Best for:

- development
- CI/CD
- team projects

---

## uv pip install

```

uv pip install package

```

Purpose:

- install something manually
- pip-compatible behavior

Typically used only for debugging or quick experiments.

---

# 8. Recommended Development Workflow

A typical modern workflow looks like this.

## Clone project

```

git clone repo
cd project

```

---

## Setup environment

```

uv venv
uv sync

```

---

## Run application

```

uv run python -m ml_project.main

```

---

## Run tests

```

uv run pytest

```

---

## Lint code

```

uv run ruff check .

```

---

# 9. Example pyproject.toml

Minimal example:

```

[project]
name = "ml_project"
version = "0.1.0"

dependencies = [
"pandas",
"scikit-learn"
]

[tool.setuptools.packages.find]
where = ["src"]

```

This tells Python that the package lives in:

```

src/

```

---

# 10. Summary of Best Practices

Recommended stack:

```

src layout
uv for dependency management
python -m for execution
**name** guard for entry scripts
pytest for testing
ruff for linting

```

Typical command sequence:

```

uv venv
uv sync

uv run python -m ml_project.main
uv run pytest

```

This setup ensures:

- correct imports
- reproducible environments
- clean project structure
- scalable ML pipelines
