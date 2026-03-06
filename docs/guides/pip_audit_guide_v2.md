# pip-audit — Comprehensive User Guide
> Python Dependency Vulnerability Auditing

---

## Table of Contents

1. [Purpose](#1-purpose)
2. [Advantages](#2-advantages)
3. [Installation](#3-installation)
4. [Basic Usage](#4-basic-usage)
5. [Common Options](#5-common-options)
6. [Output Formats](#6-output-formats)
7. [Auto-fixing Vulnerabilities](#7-auto-fixing-vulnerabilities)
8. [Ignoring Specific Vulnerabilities](#8-ignoring-specific-vulnerabilities)
9. [Resolving CVEs](#9-resolving-cves)
10. [Environment Guide](#10-environment-guide)
11. [Conda Environment Considerations](#11-conda-environment-considerations)
12. [conda-audit — Deep Dive](#12-conda-audit--deep-dive)
13. [safety — Alternative Tool](#13-safety--alternative-tool)
14. [Tool Comparison and Recommendation](#14-tool-comparison-and-recommendation)
15. [Preventing Tool Sprawl](#15-preventing-tool-sprawl)
16. [Integration with just (Justfile)](#16-integration-with-just-justfile)
17. [Integration with pre-commit](#17-integration-with-pre-commit)
18. [CI/CD Integration](#18-cicd-integration)
19. [Tips and Best Practices](#19-tips-and-best-practices)
20. [Quick Reference](#20-quick-reference)

---

## 1. Purpose

pip-audit is a command-line tool that scans Python environments and dependency files for packages with known security vulnerabilities. It queries the Open Source Vulnerabilities (OSV) database — maintained by Google and the Python Packaging Advisory Database (PyPA) — and reports any installed packages that have published CVEs or security advisories against them.

In short: pip-audit answers the question *"are any of my dependencies known to be insecure?"* before that question is answered in production by an attacker.

---

## 2. Advantages

### 2.1 Broad Vulnerability Coverage
- Queries the OSV database, aggregating CVEs, GitHub Security Advisories (GHSA), and PyPA advisories in one place.
- Catches vulnerabilities not yet reflected in pip's own metadata or PyPI's simple index.

### 2.2 Works Without an Installed Environment
- Can audit a `requirements.txt` file directly — no need to install dependencies first.
- Ideal for CI pipelines where installing all packages just to audit them wastes time.

### 2.3 Auto-fix Support
- The `--fix` flag automatically upgrades vulnerable packages to the lowest safe version, minimising unnecessary upgrades.

### 2.4 Multiple Output Formats
- Supports `text`, `json`, `cyclonedx-json`, and `cyclonedx-xml` — easy integration with SBOM pipelines, security dashboards, and compliance tooling.

### 2.5 Lightweight and Fast
- Pure Python, no system dependencies.
- Network calls go to the OSV API only — no heavyweight scanning agents required.

### 2.6 Lockfile-Aware (via uv)
- `uv run pip-audit --local` audits exactly what `uv sync` installed — nothing more, nothing less — giving accurate results for exactly what is deployed.

### 2.7 CI/CD Friendly
- Exits with a non-zero code when vulnerabilities are found — pipeline failures are automatic with no extra configuration.

---

## 3. Installation

### 3.1 uv (recommended)
Install as an isolated tool — keeps pip-audit out of your project's dependency tree:
```bash
uv tool install pip-audit
```

Or run ephemerally without installing:
```bash
uvx pip-audit
```

### 3.2 pip
```bash
pip install pip-audit
```

### 3.3 conda
```bash
conda install -c conda-forge pip-audit
```

---

## 4. Basic Usage

### 4.1 Audit the Current Environment
```bash
pip-audit
```
Inspects all packages installed in the currently active Python environment.

### 4.2 Audit a Requirements File
```bash
pip-audit -r requirements.txt
```

### 4.3 Audit a Specific Package
```bash
pip-audit --package requests==2.20.0
```

### 4.4 uv Project (Recommended)
Audit exactly what `uv sync` installed, scoped to the local `.venv`:
```bash
uv run pip-audit --local
```

`--local` is preferred over bare `uv run pip-audit` because it restricts the audit to packages installed directly into `.venv`, excluding any globally accessible packages that are not part of your project.

> **Note on the pipe approach:** `uv export --format requirements-txt | uvx pip-audit -r /dev/stdin` is documented commonly but triggers a venv creation step internally that fails with uv-managed Python due to a broken `ensurepip`. Use `uv run pip-audit --local` instead.

---

## 5. Common Options

| Flag | Description |
|---|---|
| `-r FILE` | Audit a requirements file |
| `-o FORMAT` | Output format: `text` (default), `json`, `cyclonedx-json`, `cyclonedx-xml` |
| `--fix` | Auto-upgrade vulnerable packages to safe versions |
| `--dry-run` | Preview fixes without applying them |
| `--ignore-vuln ID` | Skip a specific vulnerability by ID (e.g. `GHSA-xxxx`) |
| `--skip-editable` | Skip editable installs |
| `--no-deps` | Audit only direct packages, not transitive dependencies |
| `--local` | Audit only packages installed in the current environment (not global) |
| `-s SOURCE` | Vulnerability source: `osv` (default) or `pypi` |
| `--package NAME==VER` | Audit a specific package without installing it |

---

## 6. Output Formats

### 6.1 Default Text Output
```bash
uv run pip-audit --local
```

### 6.2 JSON (CI / dashboards)
```bash
uv run pip-audit --local -o json
```

### 6.3 CycloneDX SBOM
```bash
uv run pip-audit --local -o cyclonedx-json > sbom.json
uv run pip-audit --local -o cyclonedx-xml  > sbom.xml
```

---

## 7. Auto-fixing Vulnerabilities

pip-audit can upgrade vulnerable packages to the lowest non-vulnerable version automatically.

**Preview fixes without applying:**
```bash
uv run pip-audit --local --fix --dry-run
```

**Apply fixes:**
```bash
uv run pip-audit --local --fix
```

> **Note for uv projects:** `--fix` modifies the active environment directly. Prefer updating version constraints in `pyproject.toml` and running `uv lock` afterwards to keep the lockfile consistent and the fix reproducible.

---

## 8. Ignoring Specific Vulnerabilities

If a CVE does not apply to your usage (e.g. a vulnerable code path is never called), you can suppress it.

**Inline flag:**
```bash
uv run pip-audit --local --ignore-vuln GHSA-xxxx-xxxx-xxxx
```

**Persistent via `pyproject.toml`:**
```toml
[tool.pip-audit]
ignore-vulns = ["GHSA-xxxx-xxxx-xxxx"]
```

> Always document *why* a vulnerability is ignored. This is essential for audit trails and compliance reviews.

---

## 9. Resolving CVEs

When pip-audit reports a vulnerability, there are four resolution strategies. Work through them in order.

### 9.1 Upgrade the Package (Preferred)

The simplest and safest resolution. Check if a fixed version exists:

```bash
# See what fixed versions are available
pip-audit --package vulnerable-pkg==x.y.z

# Update in pyproject.toml, then re-lock
uv lock
uv sync
uv run pip-audit --local
```

Most CVEs are resolved in a patch release. Upgrading to the lowest fixed version minimises the risk of introducing breaking changes.

### 9.2 Use pip-audit --fix

Let pip-audit handle the upgrade automatically:

```bash
uv run pip-audit --local --fix --dry-run   # preview first
uv run pip-audit --local --fix             # apply
```

After applying, sync the lockfile:
```bash
uv lock
```

### 9.3 Find an Alternative Package

If the vulnerable package is abandoned or has no fix:
- Search PyPI or the OSV advisory for recommended replacements.
- Update `pyproject.toml` to replace the dependency.
- Run `uv lock && uv sync` to update the environment.

### 9.4 Suppress with Justification (Last Resort)

Only suppress a CVE when you have confirmed the vulnerable code path is not reachable in your application, or when the fix introduces a breaking change that cannot yet be absorbed.

**Document it properly in `pyproject.toml`:**
```toml
[tool.pip-audit]
# GHSA-xxxx-xxxx-xxxx: affects the XML parser in pkg>=1.0,<1.5
# We do not use the XML parser — only the JSON API. Safe to suppress.
# Revisit when pkg>=1.5 is stable. Ticket: PROJ-1234
ignore-vulns = ["GHSA-xxxx-xxxx-xxxx"]
```

A suppressed CVE without documentation is a liability. It will be questioned in security reviews and forgotten over time.

### 9.5 CVE Resolution Decision Tree

```
pip-audit reports a vulnerability
         │
         ▼
Does a fixed version exist?
    ├── Yes → Upgrade (uv lock && uv sync)
    └── No  → Is the package actively maintained?
                  ├── Yes → Wait / pin below vulnerable range & monitor
                  └── No  → Find alternative package
                                │
                                └── No alternative exists?
                                        └── Suppress with full justification in pyproject.toml
```

### 9.6 Verifying Resolution

After any fix, always re-run pip-audit to confirm the CVE is cleared:
```bash
uv run pip-audit --local
```

For CI, consider saving the JSON output before and after to diff:
```bash
uv run pip-audit --local -o json > audit_after.json
```

---

## 10. Environment Guide

| Environment | Recommended Command | Notes |
|---|---|---|
| uv | `uv run pip-audit --local` | Audits `.venv` only — preferred |
| pip + venv | `pip-audit` | Audits active environment directly |
| pip + requirements.txt | `pip-audit -r requirements.txt` | Audits file without installing |
| conda (pip packages) | `pip list --format=freeze \| pip-audit -r /dev/stdin --no-deps` | Covers pip-installed packages only |
| conda (full) | `pip-audit` + `conda-audit` | See Section 11 and 12 for full coverage |

---

## 11. Conda Environment Considerations

pip-audit only sees **pip-installed packages**. In a conda environment, packages installed from conda channels (e.g. `conda-forge`) are invisible to pip-audit. This is a critical gap for data science projects that mix conda and pip packages.

### 11.1 Auditing pip Packages in Conda
```bash
pip list --format=freeze | pip-audit -r /dev/stdin --no-deps
```

### 11.2 Full Coverage Strategy for Conda

| Tool | Covers | Install |
|---|---|---|
| `pip-audit` | pip-installed packages (PyPI) | `conda install -c conda-forge pip-audit` |
| `conda-audit` | conda-channel packages | `conda install -c conda-forge conda-audit` |

Run both in sequence:
```bash
pip list --format=freeze | pip-audit -r /dev/stdin --no-deps
conda-audit
```

---

## 12. conda-audit — Deep Dive

### 12.1 What is conda-audit?

conda-audit is a security auditing tool specifically designed for conda environments. It scans packages installed via conda channels (conda-forge, defaults, etc.) against the OSV vulnerability database — the same database pip-audit uses for PyPI packages.

```bash
conda install -c conda-forge conda-audit
conda-audit
```

### 12.2 Advantages

**Covers the conda blind spot.** pip-audit is entirely blind to conda-channel packages. conda-audit fills this gap and is the only dedicated tool for this purpose.

**Same OSV database.** Uses the same vulnerability data source as pip-audit, so the advisory quality is consistent between the two tools.

**Simple invocation.** No flags required for a basic audit — `conda-audit` inspects the active conda environment automatically.

**Conda-native.** Understands conda package metadata, channel provenance, and versioning schemes that pip-based tools cannot parse.

### 12.3 Disadvantages and Limitations

**Immature tooling.** conda-audit is significantly less mature than pip-audit. It has fewer contributors, less frequent releases, and a smaller community. Bug fixes and new features arrive slowly.

**Thinner vulnerability database coverage.** The OSV database has far more entries for PyPI packages than for conda packages. Many conda-specific packages — particularly scientific libraries — lack published advisories even when vulnerabilities are known. This creates a false sense of security.

**No auto-fix.** Unlike pip-audit's `--fix` flag, conda-audit has no remediation capability. It reports vulnerabilities but leaves all fixing to the user.

**No output format options.** conda-audit only outputs plain text. There is no JSON, CycloneDX, or SBOM output, making it harder to integrate into automated pipelines or compliance tooling.

**Duplicate reporting.** In mixed conda/pip environments, some packages exist in both the conda and pip layers. conda-audit and pip-audit may report the same vulnerability twice for the same package, requiring manual deduplication.

**Conda-only.** Not useful outside a conda environment. Adds zero value in uv or pure pip projects.

### 12.4 Use Cases

| Use Case | Use conda-audit? |
|---|---|
| Data science project with heavy conda-forge usage | ✅ Yes — essential |
| Security compliance audit requiring full environment coverage | ✅ Yes — required |
| Pure pip or uv project | ❌ No — adds no value |
| Quick developer scan | ❌ No — pip-audit alone is sufficient |
| CI pipeline with conda environment | ✅ Yes — run alongside pip-audit |

### 12.5 Honest Assessment

conda-audit is a necessary tool for conda-heavy projects but should not be relied upon as the primary security signal. Its value is as a **supplementary layer** on top of pip-audit, not a replacement. Given its thin database coverage, a clean conda-audit result does not mean your conda packages are vulnerability-free — it means no known advisories have been published in the OSV database for those packages.

For conda-based production systems with hard compliance requirements, consider supplementing with a commercial scanner (e.g. Snyk, Grype) that maintains its own conda vulnerability database.

---

## 13. safety — Alternative Tool

### 13.1 What is safety?

safety is a Python dependency vulnerability scanner maintained by pyup.io (acquired by Safetycli). It checks installed packages or requirements files against the Safety DB — its own curated vulnerability database — and optionally against PyPI advisories.

```bash
pip install safety
safety check
safety check -r requirements.txt
```

### 13.2 Advantages

**Mature and widely adopted.** safety has been around since 2015 and has a large user base. It is battle-tested across many CI systems and workflows.

**Safety DB.** Maintains its own curated database separate from OSV/PyPI. This can catch vulnerabilities that haven't yet made it into the OSV database, though the gap has narrowed significantly.

**Rich CLI output.** Good human-readable output with remediation guidance included inline.

**Policy files.** Supports `.safety-policy.yml` for configuring ignore rules, severity thresholds, and continue-on-vulnerability behaviour — useful for teams that need fine-grained control.

**Scan without installing.** Like pip-audit, can scan a requirements file without activating an environment.

### 13.3 Disadvantages and Limitations

**Freemium model.** The free tier uses a limited public database. Full Safety DB access requires a paid license (safety CLI 3.x+). The free database has significant gaps compared to the paid version.

**Database fragmentation.** Safety DB is separate from OSV. In practice this means you may need to cross-reference both databases to get full coverage, which defeats the purpose of a single scanning tool.

**No conda support.** Like pip-audit, safety only sees pip-installed packages. It adds no value for conda-native packages.

**Slower to adopt OSV.** The pivot to a paid model in safety 3.x introduced friction — many open source projects dropped safety from their CI in response.

**Authentication required in newer versions.** safety 3.x requires a free API key even for basic use, adding setup friction compared to pip-audit which works out of the box.

### 13.4 safety vs pip-audit — Detailed Comparison

| Dimension | pip-audit | safety |
|---|---|---|
| Vulnerability database | OSV (Google/PyPA) | Safety DB (pyup.io) + optionally OSV |
| Free full database access | ✅ Yes | ⚠️ Limited — full access requires paid plan |
| Authentication required | ❌ No | ⚠️ API key required (free tier available) |
| Auto-fix | ✅ `--fix` flag | ❌ No |
| Output formats | text, JSON, CycloneDX JSON/XML | text, JSON |
| SBOM generation | ✅ CycloneDX | ❌ No |
| Policy/ignore files | ✅ `pyproject.toml` | ✅ `.safety-policy.yml` |
| conda support | ❌ pip only | ❌ pip only |
| uv compatibility | ✅ `uv run pip-audit --local` | ⚠️ Works but no native uv integration |
| Maintenance | ✅ Actively maintained (PyPA) | ✅ Actively maintained (Safetycli) |
| Open source | ✅ Apache 2.0 | ✅ MIT (CLI), proprietary (full DB) |
| CI/CD integration | ✅ Native exit codes, JSON output | ✅ Native exit codes, JSON output |
| Maturity | Medium (2021) | High (2015) |

---

## 14. Tool Comparison and Recommendation

### 14.1 Full Landscape

| Tool | Best For | Weakness |
|---|---|---|
| `pip-audit` | uv/pip projects, OSS, CI pipelines | Blind to conda-channel packages |
| `conda-audit` | conda-heavy data science environments | Immature, thin DB coverage, no auto-fix |
| `safety` | Teams needing policy files, legacy pipelines | Paid for full DB, no SBOM, auth friction |

### 14.2 Recommendation by Project Type

**uv project (this guide's primary context):**
```
pip-audit only — uv run pip-audit --local
```
pip-audit with the OSV database gives full PyPI coverage for free, integrates cleanly with uv, and supports auto-fix and SBOM output. safety adds nothing here that pip-audit doesn't already provide for free.

**Pure pip / venv project:**
```
pip-audit only — pip-audit
```
Same reasoning. The OSV database coverage for PyPI is comprehensive and free.

**conda data science project:**
```
pip-audit + conda-audit
```
Two tools are genuinely necessary here because they cover different package layers. Accept that conda-audit's coverage is imperfect and treat its results as a supplementary signal, not a guarantee.

**Enterprise / compliance-heavy project:**
```
pip-audit (primary) + Grype or Snyk (secondary)
```
For hard compliance requirements, a commercial scanner with a dedicated, continuously updated database is more reliable than any OSS tool. Use pip-audit for developer feedback loops and CI gates; use the commercial tool for periodic deep scans and compliance reporting.

**Legacy project already using safety:**
```
Keep safety if it's working — no urgent reason to migrate
```
If safety is already embedded in your CI and working, the migration cost outweighs the benefit. The databases are largely overlapping. Only migrate if you hit the paid tier wall or need SBOM output.

### 14.3 Bottom Line

For new Python projects in 2025, **pip-audit is the default choice**. It is free, open source, maintained by the PyPA, produces SBOM output, and integrates cleanly with modern tooling like uv. safety made sense before pip-audit existed; for new projects starting today, the free tier of safety offers no meaningful advantage over pip-audit.

---

## 15. Preventing Tool Sprawl

Running pip-audit, conda-audit, safety, bandit, and other scanners independently across dev, CI, and pre-commit creates duplication, inconsistency, and maintenance overhead. The goal is **one tool per concern, one entry point per workflow**.

### 15.1 The Problem with Too Many Tools

- Same CVE reported by multiple tools creates noise and alert fatigue.
- Different tools configured differently in CI vs local leads to "works on my machine" security gaps.
- Each tool adds install overhead, potential version conflicts, and maintenance burden.
- Developers start ignoring output when too many tools produce too much output.

### 15.2 Consolidation Strategy

**One tool per layer:**

| Layer | Tool | Reason |
|---|---|---|
| pip/PyPI packages | `pip-audit` | Free, OSV, SBOM, auto-fix |
| conda packages | `conda-audit` | Only option for conda-channel packages |
| Python code security | `bandit` | Static analysis, different concern from dep scanning |
| Secrets | `gitleaks` | Dedicated secret scanning |

Do not run both pip-audit and safety. Pick one. pip-audit is the better default for new projects.

**One entry point per workflow:**

| Workflow | Entry Point |
|---|---|
| Local on-demand | `just audit` |
| Pre-push gate | pre-commit hook |
| CI | `just audit` (same command as local) |

This means CI never diverges from local — developers always know exactly what CI will run because it is the same `just` recipe.

### 15.3 Consolidating into just

```just
# Dependency vulnerability audit
audit:
    @echo "🔒  ({{env_type}}) Running pip-audit..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run pip-audit --local; \
    else \
        pip list --format=freeze | pip-audit -r /dev/stdin --no-deps; \
        conda-audit; \
    fi

# All checks — pre-commit handles lint/typecheck/bandit/pip-audit on push
# audit here covers conda environments not handled by pre-commit
run: precommit test clean
```

For uv projects where pip-audit is already in pre-commit, `audit` as a standalone recipe is useful for on-demand checks and conda environments. It is not needed in `run` if pre-commit already covers it.

### 15.4 Consolidating into pre-commit

Keep pre-commit focused on **fast, static checks at commit time** and **slow checks at push time**. Do not add tools to pre-commit just because they exist.

```
pre-commit hooks:
├── pre-commit stage (fast, no network)
│   ├── ruff           (lint + format)
│   ├── bandit         (security linting)
│   ├── gitleaks       (secret scanning)
│   └── standard hooks (trailing whitespace, YAML/TOML/JSON validation)
└── pre-push stage (slower, network ok)
    ├── mypy           (type checking)
    ├── pytest         (tests)
    └── pip-audit      (dependency scanning — network call)
```

Resist the temptation to add safety alongside pip-audit in pre-commit. It is redundant and slows down every push.

### 15.5 Signs of Tool Sprawl to Watch For

- Two tools reporting the same CVE ID in the same pipeline run.
- A tool that only runs in CI but not locally (or vice versa).
- Tools installed as `dev` dependencies that could be `uvx` / `uv tool` instead.
- A pre-commit hook that no one remembers why it was added.
- Ignored output — if developers routinely skip or dismiss tool output, the tool is adding noise, not value.

---

## 16. Integration with just (Justfile)

### 16.1 pip-audit Recipe

```just
audit:
    @echo "🔒  ({{env_type}}) Running pip-audit..."
    @if [ "{{env_type}}" = "uv" ]; then \
        uv run pip-audit --local; \
    else \
        pip list --format=freeze | pip-audit -r /dev/stdin --no-deps; \
        conda-audit; \
    fi
```

### 16.2 Full run Recipe

With pre-commit handling lint, typecheck, bandit, and pip-audit on push:

```just
run: precommit test clean
```

---

## 17. Integration with pre-commit

pip-audit runs as a local hook on `pre-push` only, since it requires a network call. The `files` filter ensures it only triggers when `pyproject.toml` or `uv.lock` actually change.

### 17.1 Hook Configuration (uv projects)

```yaml
# pip-audit
- repo: local
  hooks:
    - id: pip-audit
      name: pip-audit
      entry: uv run pip-audit --local
      language: system
      pass_filenames: false
      files: ^(pyproject\.toml|uv\.lock)$
      stages: [pre-push]   # network call — avoid blocking commits
```

### 17.2 Why pre-push, not pre-commit

| Stage | Reason |
|---|---|
| `pre-commit` | Runs on every commit — network call makes this slow and blocks fast iteration |
| `pre-push` | Runs only before pushing — acceptable latency, catches issues before they reach CI |

### 17.3 Why the files filter matters

Without the `files` filter, pip-audit runs on every push regardless of whether dependencies changed. The filter `^(pyproject\.toml|uv\.lock)$` ensures the hook only fires when the lockfile or project config is modified, keeping pushes fast for non-dependency changes.

---

## 18. CI/CD Integration

### 18.1 GitHub Actions (uv)

```yaml
- name: Audit dependencies
  run: uv run pip-audit --local
```

### 18.2 GitHub Actions with JSON artifact

```yaml
- name: Audit dependencies
  run: uv run pip-audit --local -o json > audit-results.json

- uses: actions/upload-artifact@v4
  with:
    name: audit-results
    path: audit-results.json
```

pip-audit exits with a non-zero code when vulnerabilities are found, so no extra configuration is needed to fail the pipeline.

---

## 19. Tips and Best Practices

- Run pip-audit regularly, not just at install time — new CVEs are discovered continuously against existing package versions.
- In uv projects, always use `uv run pip-audit --local` rather than the pipe approach — the pipe triggers an internal venv creation step that fails with uv-managed Python.
- Use `--no-deps` only when auditing via the pipe approach. With `--local`, it is not needed.
- Document every `--ignore-vuln` entry with a comment explaining why the CVE does not apply — essential for compliance audits and future developers.
- In uv projects, audit the live environment (`--local`) rather than trying to parse the lockfile directly — it gives accurate results for exactly what is installed.
- For conda projects, run both pip-audit and conda-audit. Accept that conda-audit's database coverage is imperfect and treat results as a supplementary signal.
- Do not run both pip-audit and safety in the same pipeline — they cover the same ground and double the noise. Pick one and be consistent.
- Prefer `uv tool install pip-audit` or `uvx pip-audit` over `uv add --dev pip-audit` — auditing tools belong in the tool layer, not the project dependency tree.

---

## 20. Quick Reference

| Task | Command |
|---|---|
| Audit uv project | `uv run pip-audit --local` |
| Audit pip environment | `pip-audit` |
| Audit requirements.txt | `pip-audit -r requirements.txt` |
| Audit conda pip packages | `pip list --format=freeze \| pip-audit -r /dev/stdin --no-deps` |
| Audit conda packages | `conda-audit` |
| JSON output | `uv run pip-audit --local -o json` |
| Preview fixes | `uv run pip-audit --local --fix --dry-run` |
| Apply fixes | `uv run pip-audit --local --fix` |
| Ignore a CVE | `uv run pip-audit --local --ignore-vuln GHSA-xxxx-xxxx-xxxx` |
| Audit specific package | `pip-audit --package requests==2.20.0` |
| Generate CycloneDX SBOM | `uv run pip-audit --local -o cyclonedx-json > sbom.json` |



## 21. Conda-audit lags and its alternative
### The Gap conda-audit Would Have Covered

conda-audit's job is to catch CVEs in **conda-channel packages** — things like `numpy`, `scipy`, `libstdc++`, `openssl`, `libcurl` installed via conda-forge or defaults. Without it, those packages are completely invisible to pip-audit.

### Real-World Risk Level

The risk depends heavily on what your conda environment actually contains:

| Package Type | Risk Without conda-audit |
|---|---|
| Pure Python packages (also on PyPI) | **Low** — pip-audit catches these if they're pip-installed |
| Scientific libs with C extensions (numpy, scipy) | **Medium** — CVEs exist but conda-audit's DB coverage was thin anyway |
| System-level libs (openssl, libcurl, libssl) | **High** — these have serious CVEs and no pip-based tool sees them |
| conda-forge build tools | **Low** — rarely have published advisories |

The highest risk is the **system-level libraries** — `openssl`, `libcurl`, `zlib`, `libffi`. These are the ones that generate high-severity CVEs and are completely invisible to any pip-based tool.

---

### Alternatives Worth Considering

**Grype (by Anchore)**
The strongest alternative. It scans conda environments natively, has excellent coverage of system-level libraries, and is actively maintained:
```bash
brew install grype           # macOS
grype dir:.                  # scan current directory
grype conda:environment.yml  # scan conda env file
```
Free, open source, no auth required. Far more mature than conda-audit.

**Trivy (by Aqua Security)**
Originally a container scanner but supports conda environments and filesystem scans. Good for teams already using it for Docker image scanning — one tool covering both:
```bash
brew install trivy
trivy fs .
```

**Snyk**
Commercial but has a generous free tier. Understands conda environments and provides remediation advice. Best choice if your team needs a dashboard and compliance reports.

---

### Practical Recommendation

Given conda-audit is lagging, the pragmatic path is:

1. **For now** — accept the gap. pip-audit still covers all pip-installed packages. Document the known blind spot explicitly in your security notes.

2. **When you're ready to add conda coverage** — reach for **Grype** rather than conda-audit. It's more mature, broader coverage, and actively maintained.

3. **If compliance is a hard requirement now** — add Grype immediately. It's a single binary, no auth, works out of the box.


## Grype can replace pip-audit
The gap is real but the practical risk for most data science projects is lower than it sounds — the majority of actual exploitable CVEs in Python data science work tend to come through pip-installed packages, which pip-audit already covers.

No, grype is not conda-only — it's a **general-purpose vulnerability scanner** that covers significantly more ground than pip-audit. Here's the full picture:

### What Grype Actually Scans

| Ecosystem | Grype | pip-audit |
|---|---|---|
| PyPI (pip packages) | ✅ | ✅ |
| conda packages | ✅ | ❌ |
| System libs (openssl, libcurl, zlib) | ✅ | ❌ |
| OS packages (apt, rpm, brew) | ✅ | ❌ |
| Docker / container images | ✅ | ❌ |
| npm / Node.js | ✅ | ❌ |
| Ruby gems | ✅ | ❌ |
| Java (jar, war) | ✅ | ❌ |

Grype is a **superset** of pip-audit's coverage. If you adopt Grype, pip-audit becomes redundant for PyPI scanning — Grype covers that layer too.

---

### So is pip-audit still needed with Grype?

**Technically no — Grype replaces pip-audit entirely.** But there are nuances:

**Keep pip-audit if:**
- You want a **lightweight, Python-specific** tool that's fast and simple to run in pre-commit hooks. Grype is heavier and slower for a quick dep check.
- You need **`--fix`** — Grype reports vulnerabilities but cannot auto-upgrade packages. pip-audit's `--fix` flag has no equivalent in Grype.
- You want **CycloneDX SBOM output** scoped specifically to Python dependencies — pip-audit's output is cleaner for Python-only SBOMs.
- You want **pre-commit integration** — pip-audit is a lightweight Python tool that slots naturally into pre-commit. Grype is a binary scanner better suited for CI.

**Replace pip-audit with Grype if:**
- You want **one tool for everything** — Python, conda, system libs, containers.
- You're already using Grype for Docker image scanning and want to consolidate.
- Reducing tool count matters more than pip-audit's auto-fix capability.

---

### Recommended Split (Avoids Tool Sprawl)

The cleanest approach that avoids duplication:

| Tool | Role | When |
|---|---|---|
| `pip-audit` | Fast dev feedback, auto-fix, pre-commit hook | Local + pre-push |
| `Grype` | Deep scan — conda, system libs, full environment | CI periodic scan or pre-push |

pip-audit stays in pre-commit for **speed and auto-fix**. Grype runs in CI for **broad coverage**. No overlap in purpose even though their PyPI coverage overlaps — they serve different workflows.

---

### If You Want a Single Tool

If the goal is truly minimal tooling:

```
Grype only
```

Accept that you lose auto-fix and the pre-commit integration is heavier. For a conda data science project where system-level library coverage matters, this is a reasonable trade.

```bash
# Install
brew install grype

# Scan current Python environment
grype dir:.

# Scan conda environment specifically
grype conda:environment.yml

# Scan a Docker image
grype your-image:latest
```

---

### Bottom Line

Grype **replaces** pip-audit in scope but not in workflow role. The pragmatic answer for your setup:

- **uv project** → pip-audit only. Grype adds little value when there are no conda or system-level packages to worry about.
- **conda project** → Grype alone is the cleanest single-tool solution. It covers pip, conda, and system libs in one scan, and eliminates the need to wait for conda-audit to catch up.
