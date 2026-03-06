# pip-audit — Dependency CVE Scanning

## What It Does

`pip-audit` scans your installed Python packages against the Python Packaging Advisory Database (PyPA) and OSV (Open Source Vulnerabilities). It reports any packages with known CVEs (Common Vulnerabilities and Exposures) and suggests the fixed version.

This catches supply chain vulnerabilities — situations where a dependency you're using has a published security bug, even if your own code is fine.

---

## Running pip-audit

```bash
just audit                         # Run via just
uv run pip-audit --local           # Run directly
```

pip-audit runs automatically on `git push` via the pre-push hook (not on commit, to avoid slowing down the commit loop).

---

## Configuration

pip-audit is configured via the pre-commit hook and the `just audit` recipe:

```yaml
# .pre-commit-config.yaml
- id: pip-audit
  entry: just audit
  files: ^(pyproject\.toml|uv\.lock)$
  stages: [pre-push]
```

The hook only triggers when `pyproject.toml` or `uv.lock` changes, avoiding unnecessary scans on every push.

The `--local` flag scans only the packages installed in the current environment, rather than resolving from the network.

---

## Reading the Output

A clean scan:
```
No known vulnerabilities found
```

A finding:
```
Found 1 known vulnerability in 1 package
Name    Version  ID                  Fix Versions
------  -------  ------------------  ------------
requests 2.28.0  PYSEC-2023-74       2.31.0
```

When you see a finding:
1. Check the advisory ID at https://osv.dev
2. Upgrade the package: `uv add requests>=2.31.0`
3. Run `uv lock` and `uv sync` to apply
4. Re-run `just audit` to confirm it's resolved

---

## Ignoring a Finding

If a CVE doesn't apply to your usage (e.g. the vulnerable code path is never called), you can ignore it:

```bash
uv run pip-audit --ignore-vuln PYSEC-2023-74
```

Or create an `ignore.txt` file and pass it:

```bash
uv run pip-audit --ignore-vuln-file ignore.txt
```

Document the reason in a comment whenever you ignore a finding — reviewers need to understand why it was dismissed.

---

## pip-audit vs Grype

| Feature | pip-audit | Grype |
|---|---|---|
| Python packages | ✅ | ✅ |
| OS packages (apt, rpm) | ❌ | ✅ |
| Container image scanning | ❌ | ✅ |
| conda environments | Partial | ✅ |
| Speed | Fast | Moderate |
| Setup complexity | None | Requires install |

**When to upgrade to Grype:**

- You are building Docker images and need to scan the full container
- You are using conda where pip-audit has incomplete visibility into the environment
- You need to scan OS-level packages alongside Python packages

Grype usage:
```bash
# Install
brew install anchore/grype/grype

# Scan the Python virtual environment
grype dir:.venv

# Scan a Docker image
grype my-app:latest

# Scan a conda environment (by directory)
grype dir:/opt/conda/envs/myenv
```
