# Bandit — Security Linter

## What It Does

Bandit is a static analysis tool that scans Python source code for common security vulnerabilities. It checks for issues like hardcoded passwords, use of `eval`, unsafe deserialization, insecure HTTP, weak cryptography, shell injection risks, and more.

Bandit runs on source code without executing it — making it fast and safe to use in CI.

---

## Running Bandit

```bash
just sec                                        # Run via just
uv run bandit -r . -ll -c pyproject.toml        # Run directly
```

Bandit runs automatically on every `git commit` via the pre-commit hook.

---

## Configuration (pyproject.toml)

```toml
[tool.bandit]
exclude_dirs = ["tests", ".venv"]
skips = []
```

The pre-commit hook passes additional flags:

```yaml
args: ["-ll", "-c", "pyproject.toml"]
```

| Flag | Meaning |
|---|---|
| `-r .` | Recurse through the directory |
| `-ll` | Report only medium and high severity issues (skip low) |
| `-c pyproject.toml` | Use pyproject.toml for configuration |

---

## Severity and Confidence Levels

Bandit rates each finding on two axes:

| Level | Severity | Confidence |
|---|---|---|
| LOW | Minor concern | Possibly a false positive |
| MEDIUM | Noteworthy | Likely an issue |
| HIGH | Serious vulnerability | High confidence it's real |

The `-ll` flag (used in this project) skips LOW severity findings to reduce noise. Adjust to `-l` to include them if you want maximum coverage.

---

## Common Findings

### B105 / B106 / B107 — Hardcoded passwords

```python
# Bad — Bandit will flag this
password = "mysecret"

# Good — load from environment
password = os.getenv("PASSWORD")
```

### B602 / B603 — Shell injection

```python
# Risky — user input in shell command
subprocess.call(f"ls {user_input}", shell=True)

# Safe — use list form, no shell
subprocess.call(["ls", user_path])
```

### B301 / B302 — Insecure deserialization

```python
# Dangerous
data = pickle.loads(untrusted_bytes)

# Better — use json or a safe format
data = json.loads(untrusted_string)
```

### B320 / B410 — XML vulnerabilities

```python
# Vulnerable to XXE
from xml.etree import ElementTree
tree = ElementTree.parse(untrusted_xml)

# Safe alternative
import defusedxml.ElementTree as ET
tree = ET.parse(untrusted_xml)
```

---

## Suppressing False Positives

For a single line:

```python
result = subprocess.call(cmd, shell=True)  # nosec B602
```

For a block, use `# nosec` with a comment explaining why:

```python
# nosec B101 — assert is intentional here as an invariant check
assert expected == actual
```

Avoid bare `# nosec` with no rule code — it silences all Bandit checks on that line without explanation.

---

## Bandit vs Ruff S Rules

This project uses both. They overlap on the `S` ruleset in Ruff (which is a Bandit subset). The full Bandit CLI catches additional issues not yet ported to Ruff's `S` rules. Running both gives complete coverage:

- **Ruff `S` rules** — fast, integrated into linting, runs on commit
- **Bandit CLI** — comprehensive, authoritative source, also runs on commit

If a rule appears in both, that's fine — redundant safety checks are not a problem.
