# Gitleaks — Secret Scanning

## What It Does

Gitleaks scans your git repository for secrets — API keys, passwords, tokens, private keys, and other credentials that should never be committed. It checks both staged changes (on commit) and the full repository history (on push).

Committing a secret to git is a serious security incident even if you immediately delete the file. The secret is preserved in git history and, if pushed to a remote, may have been scraped by bots within seconds. Gitleaks prevents this at the source.

---

## Installation

Gitleaks is managed as a pre-commit hook — no manual installation required after `just setup`.

For standalone use:
```bash
brew install gitleaks          # macOS
# or download from https://github.com/gitleaks/gitleaks/releases
```

---

## How It's Configured

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.30.0
  hooks:
    - id: gitleaks
      args: ["--redact", "--report-format=csv", "--report-path=./log/gitleaks_report.csv"]
      stages: [pre-commit, pre-push]
```

| Argument | Effect |
|---|---|
| `--redact` | Replace the actual secret value with `REDACTED` in output (so the scan report itself doesn't contain the secret) |
| `--report-format=csv` | Output findings as CSV |
| `--report-path=./log/gitleaks_report.csv` | Save the report to the log directory |

Gitleaks runs on **both** `pre-commit` and `pre-push` — catching secrets at the earliest moment and as a second check before anything reaches the remote.

---

## What Gitleaks Detects

Gitleaks ships with a built-in ruleset covering common secret patterns:

- AWS access keys and secret keys
- GitHub tokens (`ghp_`, `gho_`, `github_pat_`)
- Google API keys
- Slack tokens
- Stripe secret keys
- Private SSH keys (`-----BEGIN ... PRIVATE KEY-----`)
- Generic high-entropy strings that look like secrets
- JWT tokens
- Database connection strings with embedded credentials
- And many more (100+ rules built-in)

---

## What To Do If It Fires

### On a file you haven't committed yet

Remove the secret from the file, load it from the environment instead, and re-stage.

### On a file already committed but not pushed

The secret is in local git history. You must remove it from history before pushing:

```bash
# Using git-filter-repo (recommended)
pip install git-filter-repo
git filter-repo --path path/to/secret-file --invert-paths
```

Or use BFG Repo Cleaner.

### On a secret already pushed

1. **Immediately revoke the secret** at its source (AWS console, GitHub settings, etc.) — assume it is compromised
2. Remove it from history using `git filter-repo`
3. Force-push the cleaned history (coordinate with your team)
4. Notify any affected parties

Do not delay step 1 — secrets pushed to public repos are scraped by automated bots within minutes.

---

## Allowlisting False Positives

If Gitleaks flags something that isn't a real secret (e.g. a test fixture, a known-safe hash), you can allowlist it.

**Inline allow:**
```python
# gitleaks:allow
test_api_key = "AKIAIOSFODNN7EXAMPLE"  # This is a documented example key
```

**Config-based allow (`.gitleaks.toml`):**
```toml
[allowlist]
  description = "Known safe strings"
  regexes = ['''AKIAIOSFODNN7EXAMPLE''']
```

Always add a comment explaining *why* a finding is being suppressed.

---

## Running Gitleaks Manually

```bash
# Scan the working tree
gitleaks detect --source .

# Scan git history
gitleaks detect --source . --log-opts="--all"

# Scan a specific branch
gitleaks detect --source . --log-opts="origin/main..HEAD"
```

---

## Keeping Secrets Out of the Repo

The best way to avoid Gitleaks firing is to never commit secrets in the first place:

1. **Use `.env` files** for local secrets — ensure `.env` is in `.gitignore`
2. **Use `python-dotenv`** to load them at runtime (`load_dotenv()`)
3. **Use environment variables** in CI (GitHub Actions secrets, etc.)
4. **Never hardcode credentials** in source files, config files, or test fixtures

```python
# Good
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

# Bad — Gitleaks will catch this
api_key = "sk-abc123..."
```
