
# Python Data Types, Strings, and Numbers: Notes

## 1. Core Data Types

| Name         | Type   | Description                                   |
|--------------|--------|-----------------------------------------------|
| Integer      | int    | Whole numbers                                 |
| Float        | float  | Numbers with a decimal                        |
| String       | str    | Ordered sequence of characters                |
| List         | list   | Ordered sequence of objects                   |
| Dictionary   | dict   | Unordered key:value pairs                     |
| Tuple        | tuple  | Ordered, immutable sequence of objects        |
| Set          | set    | Unordered collection of unique objects        |
| Boolean      | bool   | Logical value indicating True or False        |

---

## 2. Variable Naming and Typing

- Use lowercase names
- Avoid using Python keywords
- Python uses dynamic typing (variables can change type)
    - **Pros:** Easy to work with, faster development
    - **Cons:** May result in unexpected bugs; always check types with `type()`

---

## 3. Strings in Python

**Definition:** Strings are sequences of characters, created with single or double quotes. Example: `'hello'` is the same as `"hello"`.

### 3.1 String Creation and Printing
- Create a string: `string1 = "Hello"`
- Print characters: `print(string1[0] + " is the letter H")`

### 3.2 String Indexing and Slicing
- Access individual characters:
    - `string1[0]` gives `'H'`
    - `string1[-1]` gives the last character
- Extract substrings:
    - `string1[1:4]` gives `'ell'` (index 1 to 3)
    - `string1[:3]` gives `'Hel'` (first three characters)
    - `string1[2:]` gives `'llo'` (from index 2 to end)
- More slicing examples:
    - `mystring = 'abcdefghijk'`
    - `mystring[2:]` gives `'cdefghijk'`
    - `mystring[:3]` gives `'abc'`
    - `mystring[3:6]` gives `'def'`
    - `mystring[1:3]` gives `'bc'`
    - `mystring[::-1]` reverses the string (e.g., `'kjihgfedcba'`)
- Advanced slicing:
    - Use step values to skip characters: `longer_string[1:-1:2]` (e.g., `'hsi  ogrsrn xml'` from `"This is a longer string example"`)
- Compare characters:
    - `mystring[9] == mystring[-2]` returns `True` if both are the same character

### 3.3 String Operations
- Concatenate strings: `a + " " + b + " " + c`
- Repeat strings: `" Worhl " * 10`
- Strings are immutable (cannot be changed in place)
- Rebuild instead of mutating: `"P" + name[1:]`
- Get the length of a string: `len(escape)`

### 3.4 Escape Sequences
- `\n` : Newline
- `\t` : Tab
- `\"` : Double quote
- `\\` : Backslash
- `\'` : Single quote
- `\r` : Carriage return
- `\a` : Bell sound (may not work everywhere)

**Examples:**
```python
escape = "hello\nworld"
print(escape)
escape = "hello\tworld"
print(escape)
escape = "She said: \"Hello!\""
print(escape)
escape = "Backslash: \\ and single quote: \\'"
print(escape)
escape = "Carriage return: hello\rworld"
print(escape)
escape = "Bell sound (may not work everywhere): hello\aworld"
print(escape)
```

### 3.5 Useful String Methods (Quick Reference)
- Case conversion: `upper()`, `lower()`, `capitalize()`, `title()`, `swapcase()`, `casefold()`
- Search/count: `find()`, `rfind()`, `index()`, `count()`
- Boolean checks: `isalnum()`, `isalpha()`, `isdigit()`, `isnumeric()`, `islower()`, `isupper()`, `isspace()`, `isidentifier()`
- Trimming/splitting: `strip()`, `lstrip()`, `rstrip()`, `split()`, `rsplit()`, `splitlines()`, `partition()`, `rpartition()`
- Replace/prefix/suffix: `replace()`, `removeprefix()`, `removesuffix()`
- Alignment/padding: `center()`, `ljust()`, `rjust()`, `zfill()`
- Other common tools: `join()`, `startswith()`, `endswith()`, `encode()`, `translate()`

### 3.6 String Formatting
#### `.format()` method
- Basic insertion: `"This is a string {}".format('Inserted')`
- Positional placeholders: `'The {2} {1} {0}'.format('fox','brown','quick')`
- Keyword placeholders: `'The {q} {b} {f}'.format(f='fox', b='brown', q='quick')`

#### Float formatting with `.format()`
- Example value: `result = 100 / 777`
- Precision pattern: `"The result was {r:5.3f}".format(r=result)`
    - `5` = minimum width
    - `.3f` = 3 digits after the decimal

#### f-strings
- Basic variable interpolation: `f'Hello, his name is {name}'`
- Multiple variables: `f'{name} is {age} years old.'`

---

## 4. Numbers in Python

### 4.1 Arithmetic Operators
- Addition: `1 + 1`
- Subtraction: `2 - 1`
- Multiplication: `3 * 3`
- Division: `2 / 2` (returns float in Python 3)
- Modulus: `50 % 9` (returns remainder)

### 4.2 Practice Example
- Write an expression that equals 100, e.g., `50 + 50` or `110 - 10`.

### 4.3 Quiz: Python Numbers and Operators
**Question 1:** Which one of these is a floating point number?
- 4
- 500
- 270000
- 6
- **3.2** (This has a decimal point in it!)

**Question 2:** Which of these will output the result 36? What are the outputs of each?
- `30+*6` → SyntaxError (invalid syntax)
- `6^6` → 0 (bitwise XOR, not exponentiation)
- `6**6` → 46656 (6 to the power of 6)
- **`6*6` → 36 (6 multiplied by 6)**
- **`6+6+6+6+6` → 30 (sum of five sixes)**

**Question 3:** In Python 3, what is the output of `1/2`?
- 1
- 0
- **0.5** (Python 3 performs true division by default!)

