# Just — Installation Notes for uv Environments

## The Problem

In a uv environment, `uv add just` installs a **Python package also named `just`** — this is a completely different tool that has nothing to do with the `just` command runner.

```
just (command runner)  → written in Rust, runs Justfiles ✅
just (Python package)  → unrelated tool, same name ❌
```

This causes a conflict where running `just` launches the wrong binary from `.venv/bin/just`.

---

## The Fix — Install via Script

Since `just` is a Rust binary, it must be installed outside of uv/pip:

```bash
# Install just to ~/bin
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/bin

# Add ~/bin to PATH (add to ~/.zshrc or ~/.bashrc)
export PATH="$HOME/bin:$PATH"

# Reload shell
source ~/.zshrc

# Verify
which just        # should show /Users/<you>/bin/just
just --version    # should show e.g. just 1.46.0
```

---

## Alternative Installation Methods

| Method | Command |
|---|---|
| Install script | `curl ... \| bash -s -- --to ~/bin` |
| Conda | `conda install -c conda-forge just` |
| Cargo (Rust) | `cargo install just` |
| Homebrew (macOS) | `brew install just` |

> **Note:** Never use `uv add just` or `pip install just` — these install the wrong package.

---

## If Wrong `just` Already Installed

```bash
# Remove the Python just package
uv remove just

# Verify correct binary is found
which just   # should NOT point to .venv/bin/just
```
