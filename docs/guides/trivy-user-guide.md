# Trivy Security Scanner — User Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Pre-commit Hook Setup](#pre-commit-hook-setup)
4. [Quick Start](#quick-start)
5. [Scanning](#scanning)
6. [Configuration File](#configuration-file)
7. [CI/CD Integration](#cicd-integration)

---

## Overview

Trivy is an open-source, all-in-one security scanner maintained by Aqua Security. It detects:

- **Vulnerabilities** — CVEs in dependencies (pip, npm, cargo, go.mod, etc.)
- **Secrets** — Hardcoded API keys, tokens, and passwords in source code
- **Misconfigurations** — Issues in Dockerfiles, Kubernetes manifests, and Terraform configs

---

## Installation

> Trivy is a system-level binary, not a Python package. Install it at the OS level, not via pip or uv.

### macOS (Local Developer Machines)

| Method | Notes |
|---|---|
| **curl** | Recommended — lightweight, no package manager dependency |
| Homebrew | Machine-wide, can be fragile to reinstall |

**Recommended — curl:**

```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ~/.local/bin

# Add to PATH in ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.zshrc

# Verify
trivy --version
```

### Linux (Deployment / CI Servers)

| Method | Notes |
|---|---|
| **apt** | Recommended for Ubuntu/Debian — integrates with system updates |
| curl | Recommended for mixed or unknown distros |
| yum/dnf | For RHEL/CentOS/Fedora environments |

**Recommended for Ubuntu/Debian — apt:**

```bash
sudo apt-get install wget apt-transport-https gnupg
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
sudo apt-get update && sudo apt-get install trivy
```

**Universal fallback — curl:**

```bash
# Latest version
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Pin to a specific version (recommended for deployment consistency)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.59.0
```

> **Tip:** Pin the Trivy version in deployment environments to avoid unexpected behaviour changes between releases.

---

## Pre-commit Hook Setup

Pre-commit hooks run Trivy automatically before every `git commit`, catching issues before they reach the repository.

### Install pre-commit

```bash
# via pip
pip install pre-commit

# via uv
uv add --dev pre-commit
```

### Local vs Remote Hooks

When configuring Trivy as a pre-commit hook, you have two approaches:

#### Local Hook

The hook command runs directly on the developer's machine using the locally installed Trivy binary.

**Pros:**
- Full control over flags and behaviour
- No dependency on an upstream repo changing their hook config
- Transparent and easy to debug
- Consistent with however Trivy was installed (curl, apt, etc.)

**Cons:**
- Trivy must be installed on every developer's machine
- Version consistency across team must be managed manually

#### Remote Hook

The hook is pulled from a remote git repository (e.g. `mxab/pre-commit-trivy`), which runs Trivy inside a Docker container.

**Pros:**
- No need to install Trivy locally
- Version is pinned via the `rev:` tag in config

**Cons:**
- Requires Docker Desktop to be running at commit time
- Swaps one dependency (Trivy) for another (Docker)
- Slower — spins up a container on every commit
- Aqua Security does not maintain an official self-contained remote hook

> **Recommendation:** Use the **local hook**. Since developers install Trivy via curl (a one-liner), the overhead is minimal. The local hook is simpler, faster, and gives your team full control.

### Local Hook Configuration

Create `.pre-commit-config.yaml` in your project root:

```yaml
repos:
  - repo: local
    hooks:
      - id: trivy-scan
        name: Trivy Security Scan
        entry: trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
        args: ["."]
        language: system
        pass_filenames: false
```

#### Optional: Separate hooks per concern

For clearer failure messages, split into individual hooks:

```yaml
repos:
  - repo: local
    hooks:
      - id: trivy-vuln
        name: Trivy - Vulnerability Scan
        entry: trivy fs --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1
        args: ["."]
        language: system
        pass_filenames: false

      - id: trivy-secret
        name: Trivy - Secret Scan
        entry: trivy fs --scanners secret --exit-code 1
        args: ["."]
        language: system
        pass_filenames: false

      - id: trivy-misconfig
        name: Trivy - Dockerfile & Misconfig Scan
        entry: trivy fs --scanners misconfig --severity HIGH,CRITICAL --exit-code 1
        args: ["."]
        language: system
        pass_filenames: false
```

### Activate the hooks

```bash
# Install hooks into your local git repo
pre-commit install

# Run manually on all files (recommended on first setup)
pre-commit run --all-files
```

### Developer Onboarding (Two Steps)

Document these two commands in your project README so new developers can onboard quickly:

```bash
# 1. Install Trivy (Mac)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ~/.local/bin

# 2. Install pre-commit hooks
pre-commit install
```

---

## Quick Start

### Scan current directory (all checks)

```bash
trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --ignore-unfixed .
```

### Scan a remote Git repository

```bash
trivy repo https://github.com/your-org/your-repo
```

### Scan a specific branch

```bash
trivy repo --branch develop https://github.com/your-org/your-repo
```

---

## Scanning

### Filesystem & Source Code

```bash
# Scan everything in current directory
trivy fs .

# Vulnerabilities only
trivy fs --scanners vuln .

# Secrets only
trivy fs --scanners secret .

# Vulnerabilities + secrets + Dockerfile misconfigs
trivy fs --scanners vuln,secret,misconfig .

# Filter by severity
trivy fs --severity HIGH,CRITICAL .

# Ignore vulnerabilities with no available fix
trivy fs --ignore-unfixed .

# Output as JSON
trivy fs --format json --output results.json .
```

### Git Repositories

```bash
# Scan public repo
trivy repo https://github.com/your-org/your-repo

# Scan specific branch
trivy repo --branch develop https://github.com/your-org/your-repo

# Scan specific tag
trivy repo --tag v1.0.0 https://github.com/your-org/your-repo

# Scan private repo
GITHUB_TOKEN=your_token trivy repo https://github.com/your-org/private-repo
```

### Dockerfile & IaC Misconfigurations

Trivy detects Dockerfile issues automatically when using the `misconfig` scanner:

```bash
# Scan Dockerfile in current directory
trivy fs --scanners misconfig .

# Scan a specific Dockerfile
trivy config ./Dockerfile
```

### Scanner Reference

| Scanner | Flag | What it detects |
|---|---|---|
| Vulnerabilities | `vuln` | CVEs in pip, npm, cargo, go.mod, etc. |
| Secrets | `secret` | API keys, tokens, passwords in code |
| Misconfigurations | `misconfig` | Dockerfile, K8s YAML, Terraform issues |

### Severity Levels

| Level | Description |
|---|---|
| `CRITICAL` | Immediate action required |
| `HIGH` | Fix as soon as possible |
| `MEDIUM` | Plan to fix |
| `LOW` | Fix when convenient |
| `UNKNOWN` | Insufficient data to classify |

> **Recommended minimum threshold:** `HIGH,CRITICAL` for CI/CD gates.

---

## Configuration File

Instead of repeating flags on every command, define defaults in a `trivy.yaml` config file at the project root.

### `trivy.yaml` — Quick Run Config

```yaml
# trivy.yaml
# Place in project root. Trivy auto-detects this file.

scan:
  scanners:
    - vuln
    - secret
    - misconfig

severity:
  - HIGH
  - CRITICAL

vulnerability:
  ignore-unfixed: true

output: table  # options: table, json, sarif, cyclonedx
```

With this file in place, you can run a full scan with just:

```bash
trivy fs .
```

### Config File with JSON Output (for CI/CD)

```yaml
# trivy.yaml (CI/CD variant)

scan:
  scanners:
    - vuln
    - secret
    - misconfig

severity:
  - HIGH
  - CRITICAL

vulnerability:
  ignore-unfixed: true

format: json
output: trivy-results.json

exit-code: 1  # fail pipeline if issues found
```

> **Tip:** Commit `trivy.yaml` to your repository so all developers and CI/CD pipelines share the same scan configuration automatically.

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Trivy
        run: |
          curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.59.0

      - name: Run Trivy Scan
        run: trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 .
```

### GitLab CI

```yaml
trivy-scan:
  stage: test
  before_script:
    - curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.59.0
  script:
    - trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 .
```

---

*For full documentation, visit [https://aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy)*
