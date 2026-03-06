Here is your guide in **Markdown (.md) format**:

---

# Exception Handling & Testing Guide (Python)

## 1. Core Philosophy

Exception handling is about:

* Enforcing rules
* Protecting system integrity
* Failing safely
* Avoiding silent corruption

There are three layers to think about:

1. **Input validation**
2. **Business logic**
3. **System boundaries (top level)**

Each layer has different responsibilities.

---

# 2. Validation Order in Business Logic

Always validate in this order:

1. **Invalid input**
2. **Business rule violations**
3. **State mutation**

### Example

```python
def withdraw(self, amount):
    if amount < 0:
        raise ValueError("Amount cannot be negative")

    if amount > self.balance:
        raise ValueError("Insufficient funds")

    self.balance -= amount
```

### Why This Order Matters

* Invalid input should be rejected immediately.
* Business rules should be enforced before mutation.
* State changes must happen only after validation succeeds.

---

# 3. What NOT To Do in Business Logic

Avoid catching broad exceptions:

```python
try:
    do_something()
except Exception as e:
    logging.debug(e)  # ❌ Bad practice
```

### Why This Is Dangerous

* Hides real bugs
* Suppresses stack traces
* May allow corrupted state
* Makes debugging harder

Business logic should:

* Raise specific exceptions
* Not swallow unexpected errors

---

# 4. Proper Use of try/except

## Catch Only What You Can Handle

```python
try:
    withdraw(amount)
except ValueError as e:
    return str(e)
```

Good because:

* It handles expected domain errors
* It does not hide unexpected ones

---

# 5. Top-Level Exception Handling

Catching broad exceptions is acceptable **only at system boundaries**.

Examples of boundaries:

* `main()` function
* API request handler
* CLI entry point
* Background job runner

### Correct Pattern

```python
import logging

def main():
    try:
        run_application()
    except Exception:
        logging.exception("Unexpected error occurred")
        return "Internal server error"
```

### Why Use `logging.exception()`?

* Logs full traceback
* Logs at ERROR level
* Preserves debugging information

Do NOT use:

```python
logging.debug(e)
```

Because:

* Debug logs may be disabled in production
* No traceback included

---

# 6. What Happens During a Network Outage?

If a network call fails:

```python
def fetch_data():
    return requests.get(url).json()
```

Possible exceptions:

* ConnectionError
* Timeout
* DNS errors
* OSError

If not caught locally:

* The exception bubbles up
* It reaches the top-level handler
* It gets logged
* A safe failure response is returned

This is expected behavior.

---

# 7. When To Handle Network Errors Locally

Handle them locally only if you can recover.

### Retry Example

```python
def fetch_data():
    for _ in range(3):
        try:
            return requests.get(url, timeout=3)
        except requests.Timeout:
            continue
    raise ServiceUnavailable("API not reachable")
```

Good practice because:

* It anticipates transient failures
* It retries safely
* It converts low-level errors into domain errors

---

# 8. Pytest Strategy

You should test:

## 1. Expected Exceptions

```python
with pytest.raises(ValueError, match="Amount cannot be negative"):
    account.withdraw(-10)
```

## 2. Business Rule Violations

```python
with pytest.raises(ValueError, match="Insufficient funds"):
    account.withdraw(200)
```

## 3. Correct State Mutation

```python
account.withdraw(30)
assert account.balance == 70
```

This prevents subtle bugs such as:

* Using `+` instead of `-`
* Modifying wrong variable
* Silent logic changes

---

# 9. Test Order vs Validation Order

## Validation Order (Important)

In the main code:

* Input validation first
* Business rules second
* Mutation last

Order matters.

## Test Execution Order (Should Not Matter)

In pytest:

* Tests must be independent
* Order should not affect outcome
* Each test must set up its own state

If test order matters, that’s a design smell.

---

# 10. Clean Architecture Rule Summary

### Inside Business Logic

* Raise specific exceptions
* Do not catch broad `Exception`
* Validate before mutating state

### At System Boundaries

* Catch broad exceptions
* Log with `logging.exception()`
* Return safe fallback response
* Do not silently continue execution

---

# 11. Final Engineering Principle

Let exceptions travel upward until they reach:

* A place that can recover
  OR
* A boundary that can fail safely

If neither exists → fail fast and loud.

Silent failures are worse than crashes.

---

# 12. Professional Mindset

* Fail early
* Fail clearly
* Log properly
* Never hide bugs
* Test for both errors and correctness
* Protect against subtle logic regressions

---

End of Guide.
