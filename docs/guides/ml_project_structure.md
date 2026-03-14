# Production-Grade Machine Learning Project Structure (uv + src)

This document describes a **scalable Machine Learning project architecture** suitable for:

* production ML pipelines
* team collaboration
* CI/CD workflows
* reproducible environments

The setup uses modern Python tooling:

* **uv** for dependency management
* **src layout** for correct packaging
* **pytest** for testing
* **ruff** for linting

---

# 1. Recommended Project Structure

```
ml-project/
│
├── src/
│   └── ml_project/
│       │
│       ├── pipelines/
│       │   ├── training_pipeline.py
│       │   └── inference_pipeline.py
│       │
│       ├── models/
│       │   ├── train_model.py
│       │   └── predict_model.py
│       │
│       ├── data/
│       │   ├── ingestion.py
│       │   ├── validation.py
│       │   └── preprocessing.py
│       │
│       ├── features/
│       │   └── feature_engineering.py
│       │
│       ├── evaluation/
│       │   └── evaluate_model.py
│       │
│       ├── config/
│       │   └── config.py
│       │
│       ├── logging/
│       │   └── logger.py
│       │
│       ├── exception/
│       │   └── custom_exception.py
│       │
│       └── main.py
│
├── tests/
│   ├── test_data.py
│   ├── test_features.py
│   └── test_models.py
│
├── configs/
│   └── config.yaml
│
├── notebooks/
│   └── exploration.ipynb
│
├── artifacts/
│
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

---

# 2. Key Directory Responsibilities

## src/

Contains **all production code**.

Keeping code under `src` ensures Python imports the **installed package**, preventing import bugs.

---

## pipelines/

Orchestrates the ML workflow.

Example:

```
training_pipeline.py
```

Typical pipeline steps:

```
data ingestion
→ data validation
→ feature engineering
→ model training
→ evaluation
```

Pipeline code should **coordinate steps**, not implement them.

---

## data/

Handles **data ingestion and preprocessing**.

Examples:

```
ingestion.py
validation.py
preprocessing.py
```

Responsibilities:

* reading raw datasets
* schema validation
* cleaning data
* splitting train/test

---

## features/

Contains **feature engineering logic**.

Example:

```
feature_engineering.py
```

Responsibilities:

* encoding
* scaling
* feature transformations
* feature selection

---

## models/

Contains **model training and prediction logic**.

Example files:

```
train_model.py
predict_model.py
```

Responsibilities:

* train model
* save model artifacts
* load model for inference

---

## evaluation/

Handles **model performance evaluation**.

Example:

```
evaluate_model.py
```

Responsibilities:

* compute metrics
* compare models
* generate evaluation reports

---

## config/

Manages configuration objects.

Example:

```
config.py
```

Configurations may include:

* dataset paths
* hyperparameters
* artifact locations

---

## logging/

Centralized logging configuration.

Example:

```
logger.py
```

Good logging enables:

* debugging
* monitoring pipelines
* production observability

---

## exception/

Custom exception handling.

Example:

```
custom_exception.py
```

Centralizing exceptions improves:

* debugging
* error traceability
* production stability

---

# 3. Entry Point: main.py

`main.py` starts the pipeline.

Example:

```python
from ml_project.pipelines.training_pipeline import run_training_pipeline


def main():
    run_training_pipeline()


if __name__ == "__main__":
    main()
```

Why the guard?

```
if __name__ == "__main__":
```

It ensures the pipeline runs **only when executed directly**, not when the module is imported.

---

# 4. Running the Project with uv

## Create environment

```
uv venv
```

---

## Install dependencies

```
uv sync
```

This installs:

* dependencies from `pyproject.toml`
* locked versions from `uv.lock`
* your project package

---

## Run the pipeline

```
uv run python -m ml_project.main
```

Using `-m` runs the module within Python’s **package system**, ensuring correct imports.

---

# 5. Running Tests

Tests live in:

```
tests/
```

Run tests with:

```
uv run pytest
```

Testing helps verify:

* data transformations
* feature engineering
* model training

---

# 6. Code Quality

Linting with Ruff:

```
uv run ruff check .
```

Formatting:

```
uv run ruff format .
```

---

# 7. Configuration Management

Instead of hardcoding parameters, store them in configuration files.

Example:

```
configs/config.yaml
```

Typical configuration:

```
dataset_path: data/train.csv
test_size: 0.2
model_type: random_forest
n_estimators: 100
```

This enables:

* reproducible experiments
* easy parameter changes
* environment-specific configurations

---

# 8. Artifacts Directory

```
artifacts/
```

Stores generated files:

* trained models
* processed datasets
* evaluation reports

Artifacts are typically **excluded from Git**.

---

# 9. Notebooks

```
notebooks/
```

Used for:

* exploration
* visualization
* prototyping

Production code should **not live in notebooks**.

---

# 10. Typical ML Workflow

A typical development workflow:

```
git clone repo
cd ml-project

uv venv
uv sync

uv run python -m ml_project.main
```

Testing:

```
uv run pytest
```

Linting:

```
uv run ruff check .
```

---

# 11. Benefits of This Architecture

Advantages include:

### Scalability

Supports complex ML pipelines.

### Reproducibility

`uv.lock` ensures identical environments.

### Clean separation of concerns

Each module has a clear responsibility.

### Production readiness

Easier to deploy, monitor, and maintain.

---

# 12. Key Design Principles

This architecture follows several principles:

* modular pipeline design
* configuration-driven systems
* separation of experimentation and production
* reproducible environments
* testable components

---

# 13. Summary

Recommended modern ML stack:

```
src layout
uv dependency management
python -m module execution
pytest testing
ruff linting
config-driven pipelines
```

Typical command workflow:

```
uv venv
uv sync

uv run python -m ml_project.main
uv run pytest
uv run ruff check .
```

This structure scales from **research prototypes to production ML systems**.
