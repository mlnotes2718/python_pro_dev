# The Strategy: "Code in Git, Results in Artifacts"

This strategy, which we will call **"Clean-Logic Versioning,"** is designed to solve the fundamental conflict between Jupyter Notebooks and Git: the fact that notebooks are massive JSON blobs containing both **executable code** (the logic) and **volatile execution output** (the noise).

The purpose of this strategy is to ensure your Git history remains a precise, high-signal audit trail of your code's evolution, while maintaining a secondary, reproducible record of your results for verification and educational purposes.

---

### The Three-Tier Strategy

Depending on your specific goal, you should apply the "Clean-Logic" strategy using one of the three following approaches:

#### 1. The Normal Development Workflow (The "Default")

This is for your day-to-day coding where your main objective is keeping the repo lightweight and clean.

* **The Process:** Use `nbstripout` as an automated filter. Every time you commit, Git automatically strips outputs, execution counts, and metadata.
* **The Result:** Your repository only tracks your actual logic. `nbdime` will provide crisp, code-focused diffs during pull requests, and your repository size will remain tiny.

#### 2. The Refactoring & Verification Workflow

This is for scenarios where you are modifying libraries or optimizing code and need to guarantee that your output remains consistent (Regression Testing).

* **The Process:** 1. **Baseline:** Run the current notebook, capture the outputs, and export to a `baseline_report.html`.
2. **Refactor:** Modify your code cells.
3. **Verify:** Run the notebook again and compare the new outputs against your baseline report.
* **The Result:** You treat your notebook as a unit test suite. You only commit the refactored code once you have mathematically verified that the outputs are identical, maintaining the "Clean-Logic" standard in your Git history.

#### 3. The Tutorial & Documentation Workflow

This is for when your audience needs to see the results to learn from the notebook.

* **The Process:** 1. **Finalize:** Perfect your code and verify the results locally.
2. **Export:** Use `jupyter nbconvert` to save the notebook as an **HTML** or **PDF** file.
3. **Version:** Commit the clean `.ipynb` file to Git (for the code) and the `.html` file to a `docs/` folder (for the reference).
* **The Result:** Your repo provides a clean, mergeable codebase for developers, while your GitHub Pages (or `docs/` folder) provides a fully rendered, interactive tutorial for users.

---

### Summary Checklist

* **Git Repo:** Contains only the "Clean" logic.
* **`nbstripout`:** Enforces the "Clean" standard.
* **`nbdime`:** Enables human-readable code diffs.
* **`HTML/PDF Artifacts`:** Capture the "Expected Output" for reference, refactoring baselines, or tutorials.



---

To initialize this "Code-in-Git, Results-in-Artifacts" strategy, follow this **3-step setup** for every new project. This creates a professional environment that separates your logic from your execution artifacts.

---

### Step 1: Install & Configure the Tools

You only need to do this once per environment.

```bash
# 1. Install necessary packages
pip install nbdime nbstripout

# 2. Configure Git to use nbdime for diffing/merging
nbdime config-git --enable

# 3. Configure nbstripout to automatically clear outputs on commit
git config filter.ipynb.smudge "nbstripout -t"
git config filter.ipynb.clean "nbstripout"

```

---

### Step 2: Set Project-Level Rules

This forces Git to treat all `.ipynb` files as "code-only" files for version control. Create a file named `.gitattributes` in your project root:

```text
# .gitattributes
*.ipynb filter=ipynb
*.ipynb diff=jupyternotebook
*.ipynb merge=jupyternotebook

```

---

### Step 3: The Daily "Tutorial-Ready" Workflow

Once configured, this is your standard workflow to maintain clean Git history while keeping tutorial outputs accessible:

1. **Develop:** Write and test your code locally in the notebook.
2. **Verify & Export:** Before committing, use a helper script or Makefile to run the notebook and save the output as an HTML file in a `docs/` folder.
* *Why:* This preserves the "expected output" for your users without committing bloated JSON to Git.


3. **Git Add/Commit:** Just run `git add .` and `git commit`.
* *The Automation:* `nbstripout` will automatically strip the outputs from the `.ipynb` file in your repository, keeping your `git diff` clean and focused on code.


4. **Publish:** Push your code and your `docs/index.html` to your repository.

---

### Summary of Strategy Benefits

* **Clean Diffs:** Using `nbdime` on "stripped" notebooks means you only ever see actual code changes.
* **Lightweight Repo:** No more massive commit history filled with embedding results or cell execution counts.
* **Better Documentation:** Your HTML/PDF exports act as a permanent, readable reference for the tutorial, independent of the code's versioning.

---


TLDR:

- Basically, for accurately do notebook diff to capture code change, we need to remove output. This will be the standard process.
- For cases where we need the output, run all in nb and convert to html. Repo remain clean, expected result shown in html
- For cases where we need the output to check against code change, we can run the notebook first and perform code change.
