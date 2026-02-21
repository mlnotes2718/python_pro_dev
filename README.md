# Python Professional Development

This project tries to migrate Python project into a more professional style.

Please refer to `./docs` for all the references and notes

This repo is setup with uv and compatible with conda environment.

- For a start, we introduce linting and formatting. We use `ruff` as the defacto tool.
- Next we include `mypy` for static analysis on type hinting.
- Next we include `pytest` for testing

In the programming side:
- Look deeper into `try-except`
- Do not over-engineer or under-engineer class and function.
- Do not over-use and under-use lambda and list comprehension
- Use functional principal when writing function 


## LLM Suggestion
Here is an assessment of your plan with some professional-grade refinements to help you level up.

---

## 1. Tooling & Workflow

You’ve picked the "modern stack." `ruff` is currently the industry favorite because it replaces Flake8, Black, and isort all at once with incredible speed.

* **The Missing Link: Automation.** Don’t run these manually. Use **pre-commit hooks**. This ensures that code cannot even be committed to your local git history unless it passes your `ruff`, `mypy`, and `pytest` checks.
* **Mypy Strategy:** Start with `--disallow-untyped-defs`. If you don't force yourself to type-hint function signatures, you’ll likely skip them when things get busy.

---

## 2. Refining the Programming Logic

Your focus on "balance" (not over/under engineering) is the hardest part of senior-level development. Here is how to calibrate that balance:

### Deep Dive: `try-except`

Professional code avoids "Pokemon Exception Handling" (Catching 'em all).

* **The Rule:** Only catch exceptions you actually know how to handle. If you can't fix it or log it meaningfully, let it crash.
* **Context Managers:** Learn to use the `with` statement and `contextlib`. It’s often cleaner than a `try-finally` block for resource management.

### The "Goldilocks" Principle (Classes vs. Functions)

* **Under-engineering:** Putting everything in one giant script with global variables.
* **Over-engineering:** Creating a class for something that could be a simple function. If a class has only two methods and one of them is `__init__`, it probably shouldn't be a class.
* **The Professional Way:** Use **Data Classes** (`from dataclasses import dataclass`) for objects that just store data, and use classes only when you need to manage complex internal state.

### Functional Principles

This is the "secret sauce" of bug-free code.

* **Immutability:** Try to avoid changing variables in place. Instead of modifying a list, return a new one.
* **Pure Functions:** Aim for functions where the same input **always** produces the same output and has no "side effects" (like printing to console or changing a global variable).


<details>

<summary>

#### Handling Numpy and Pandas
Handling this professionally requires a balance between **functional purity** (copying everything) and **performance** (memory efficiency).

---

</summary>

##### 1. The "Hidden Mutation" Problem

When you pass a DataFrame into a function, Python passes it **by assignment**. If the function modifies that DataFrame, it changes for the rest of your program.

###### The Amateur Way (In-place Mutation)

```python
import pandas as pd

def add_tax(df: pd.DataFrame) -> None:
    # This modifies the original data outside the function!
    df["total"] = df["price"] * 1.15 

my_df = pd.DataFrame({"price": [10, 20]})
add_tax(my_df) 
# my_df is now changed forever. This makes debugging a nightmare.

```

---

##### 2. The Professional Way: Explicit Copying

To stick to functional principles, your function should return a **new** object.

###### Option A: The `.copy()` Method

Use this when the DataFrame is small to medium-sized. It ensures the original data remains "read-only."

```python
def calculate_tax(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a new dataframe with tax applied, leaving the original intact."""
    new_df = df.copy() 
    new_df["total"] = new_df["price"] * 1.15
    return new_df

```

###### Option B: Method Chaining (The "Pandas Way")

Professional Pandas code often uses `.assign()`. This automatically returns a new copy of the DataFrame with the changes applied, which is much more "Functional."

```python
def get_tax_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(total=lambda x: x["price"] * 1.15)

```

---

##### 3. Handling Large Data (Performance vs. Purity)

If your NumPy array is 10GB, you cannot simply `.copy()` it every time. You’ll run out of RAM (OOM Error).

**The Professional Compromise:**

1. **Strict Naming:** If a function *must* mutate data for performance, name it clearly: `mutate_array_in_place(arr)`.
2. **The "View" vs "Copy" check:** Use `np.may_share_memory(a, b)` to verify if two variables are pointing to the same data.
3. **Local Scope:** Keep mutations hidden inside a function, but return a final result that is "frozen."

---

##### 4. Summary Table: Managing State

| Scenario | Tool/Method | Why? |
| --- | --- | --- |
| **Small Data** | `.copy()` | Maximizes safety and predictability. |
| **Adding Columns** | `.assign(...)` | Clean, functional, and chainable. |
| **Large Arrays** | `inplace=True` | Saves memory, but requires heavy documentation. |
| **Checking Links** | `df1 is df2` | Quickly check if two labels point to one object. |

</details>
---

## 3. Comparison of Python Styles

| Feature | Amateur/Scripting | Professional/Production |
| --- | --- | --- |
| **Error Handling** | `except Exception: pass` | Specific exceptions + Logging |
| **Types** | Dynamic (guessed) | Explicit (Type Hints) |
| **Testing** | Manual "print" checks | `pytest` + CI/CD pipelines |
| **Configuration** | Hardcoded strings | Environment variables (`.env`) |
| **Environment** | Global Python install | Virtual environments (`uv` or `poetry`) |

---

## A Suggestion for your "Next Step"

To bridge the gap between "writing functions" and "professional architecture," I recommend looking into **Dependency Injection**. It sounds intimidating, but it's the primary way professional developers make their code testable with `pytest`.

**Would you like me to show you a "Before vs. After" example of a piece of code transformed from a basic script into this professional structure?**

Let’s take a common task—fetching data from an API and saving it— and transform it from "scripting" style to "professional" style.

### The "Before" (Amateur/Scripting)

This code is hard to test, has no type safety, and uses "Pokemon" exception handling.

```python
import requests

def get_data(url):
    try:
        r = requests.get(url)
        return r.json()
    except:
        print("Error happened")

def save(data):
    with open("data.txt", "w") as f:
        f.write(str(data))

# Execution
data = get_data("https://api.example.com/items")
save(data)

```

---

### The "After" (Professional/Production)

Notice the use of **Type Hints**, **Specific Exceptions**, **Dependency Injection**, and **Functional Principles**.

```python
import logging
from typing import Dict, Any, Protocol
import requests

# 1. Define an Interface (Protocol) for flexibility
class Storage(Protocol):
    def save(self, data: Dict[str, Any]) -> None: ...

# 2. Functional & Specific Logic
class FileStorage:
    def __init__(self, filename: str):
        self.filename = filename

    def save(self, data: Dict[str, Any]) -> None:
        try:
            with open(self.filename, "w") as f:
                f.write(str(data))
        except IOError as e:
            logging.error(f"Failed to write to disk: {e}")
            raise

# 3. Pure Logic & Dependency Injection
def fetch_payload(url: str) -> Dict[str, Any]:
    """Pure function for fetching data with specific error handling."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Catch 4xx/5xx errors specifically
    return response.json()

def process_workflow(url: str, storage: Storage) -> None:
    """Orchestrator: Easy to test by passing a 'Mock' storage."""
    try:
        data = fetch_payload(url)
        storage.save(data)
    except requests.RequestException as e:
        logging.error(f"Network error: {e}")

```

---

### Why this is "Professional":

1. **Mypy Friendly:** Every function has clear inputs and outputs defined (e.g., `Dict[str, Any]`).
2. **Pytest Friendly:** In `process_workflow`, you can pass a "fake" storage object to test the logic without actually writing to a hard drive.
3. **Ruff Friendly:** This structure avoids global variables and nested logic that linters hate.
4. **Error Handling:** It distinguishes between a *network* error and a *disk* error rather than just saying "Error happened."

### The Functional Principle at Play

Notice that `fetch_payload` doesn't know about `FileStorage`. It just does one thing and returns a value. This makes it a "Lego brick" you can reuse anywhere.

**Would you like me to generate a `pytest` file for this "After" example so you can see how professionals write test suites?**