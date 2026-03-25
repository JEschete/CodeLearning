# Section 3 Challenge: Mini Grocery Receipt Logger

## Goal
Write **one small Python program** that uses the main concepts from Section 3:

- strings
- lists
- dictionaries
- tuples
- sets
- booleans
- numbers
- basic file I/O

Keep it simple and readable.

---

## Program Scenario
You are logging a tiny grocery purchase.

Use this data inside your script:

```python
store_name = "Corner Market"
items = ["apple", "milk", "apple", "bread"]
prices = {"apple": 1.50, "milk": 3.25, "bread": 2.75}
tax_rate = 0.07
```

---

## Requirements

### 1) Strings
- Print a receipt header using f-strings.
- Example idea: `Welcome to Corner Market`.

### 2) Lists + Dictionaries + Numbers
- Loop through `items` and calculate subtotal using `prices`.
- Calculate tax and final total.
- Round money values to 2 decimals in printed output.

### 3) Sets
- Create a set from `items` to get unique purchased items.
- Print the unique item names.

### 4) Tuple
- Create a tuple summary:

```python
summary = (item_count, unique_item_count, final_total)
```

- Print the tuple.

### 5) Booleans
- Create at least one boolean check, for example:

```python
is_budget_ok = final_total <= 10
```

- Print a message based on `True`/`False`.

### 6) File I/O
- Save a short receipt report to `receipt.txt` using:

```python
with open("receipt.txt", "w") as f:
	...
```

- Then reopen and print file contents to confirm it worked.

---

## Expected Output (example shape, not exact text)

```text
Welcome to Corner Market
Items purchased: ['apple', 'milk', 'apple', 'bread']
Unique items: {'apple', 'milk', 'bread'}
Subtotal: 9.00
Tax: 0.63
Final Total: 9.63
Summary tuple: (4, 3, 9.63)
Budget check: True
```

---

## Stretch (Optional)
- Use `None` for a placeholder variable (for example, `discount = None`) and assign it later.
- Save each receipt line as a separate line in the file.

