
# Python Data Types, Strings, Numbers, and Dictionaries: Notes

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
- Boolean checks: `isalnum()`, `isalpha()`, `isascii()`, `isdecimal()`, `isdigit()`, `isnumeric()`, `isprintable()`, `islower()`, `isupper()`, `istitle()`, `isspace()`, `isidentifier()`
- Trimming/splitting: `strip()`, `lstrip()`, `rstrip()`, `split()`, `rsplit()`, `splitlines()`, `partition()`, `rpartition()`, `expandtabs()`
- Replace/prefix/suffix: `replace()`, `removeprefix()`, `removesuffix()`
- Alignment/padding: `center()`, `ljust()`, `rjust()`, `zfill()`
- Other common tools: `join()`, `startswith()`, `endswith()`, `encode()`, `format()`, `format_map()`, `maketrans()`, `translate()`

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

## 4. Lists in Python

**Definition:** Lists are ordered, mutable collections that can store mixed data types.

### 4.1 Creating Lists
- Basic list: `my_list = [1,2,3]`
- Mixed-type list: `my_list2 = ['string', 100, 11.2]`
- String list: `my_list3 = ['one', 'two', 'three']`

### 4.2 Basic List Operations
- Length: `len(my_list)`
- Index access: `my_list[0]`
- Slicing:
    - `my_list[1:]` (from index 1 to end)
    - `my_list[:-1]` (all except last item)
- Concatenation: `my_list + my_list2 + my_list3`
- Store combined result: `new_list = my_list + my_list2 + my_list3`

### 4.3 Mutability (Lists Can Change In Place)
- Update an item:
```python
my_list3[0] = my_list3[0].upper()
```
- Add to the end: `my_list3.append('six')`
- Remove last item: `my_list3.pop()`

### 4.4 Sorting and Reversing
- Sort numeric list in place: `my_list.sort()`
- Sort string list alphabetically: `my_list3.sort()`
- Reverse order in place:
```python
my_list3.reverse()
```

### 4.5 Practical Reminders
- Lists are mutable, unlike strings.
- `sort()` and `reverse()` change the original list (in place).
- After list operations, print the list to verify state (e.g., `my_list3`).

---

## 5. Numbers in Python

### 5.1 Arithmetic Operators
- Addition: `1 + 1`
- Subtraction: `2 - 1`
- Multiplication: `3 * 3`
- Division: `2 / 2` (returns float in Python 3)
- Modulus: `50 % 9` (returns remainder)

### 5.2 Practice Example
- Write an expression that equals 100, e.g., `50 + 50` or `110 - 10`.

### 5.3 Quiz: Python Numbers and Operators
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

---

## 6. Dictionaries in Python

**Definition:** Dictionaries store data as key-value pairs and are accessed by key (not index).

### 6.1 Create a Dictionary
- Example:
```python
my_dict = {'Name':'Jude', 'age':35, 'height':'5\'10"'}
```
- Keys here are `'Name'`, `'age'`, and `'height'`.

### 6.2 Access Values by Key
- Example: `my_dict['age']`
- Print example: `print(my_dict['age'])`
- Key access returns the value associated with that key.

### 6.3 Dictionary Syntax and Rules
- Dictionaries use curly braces `{}`.
- Each entry is written as `key: value`.
- Entries are separated by commas.
- Keys are typically strings in beginner workflows and should be meaningful.

### 6.4 When to Use List vs Dictionary
- Use a **list** when order/index position matters and you need indexing/slicing/sorting.
- Use a **dictionary** when fast key lookup matters (you know a label, not an index).
- Tradeoff:
    - Dictionary gain: quick access by key.
    - Dictionary loss: no index-based slicing, and you generally do not treat it as a sortable ordered sequence in beginner usage.

### 6.5 Real-World Lookup Example
```python
prices_lookup = {'apple': 2.99, 'orange': 1.99, 'milk': 5.80}
prices_lookup['apple']
```
- This pattern is useful when you want “value by name” lookups.

### 6.6 Dictionaries Can Hold Many Data Types
```python
d = {'k1': 123, 'k2': [0, 1, 2], 'k3': {'insideKey': 100}}
```
- Values can be numbers, strings, lists, or even other dictionaries.

### 6.7 Nested Access (Stacked Calls)
- Get list inside dict: `d['k2']`
- Get nested dict value: `d['k3']['insideKey']`
- Mix key access + list indexing: `d['k2'][2]`
- Method chaining example from nested value patterns:
```python
d = {'key1': ['a', 'b', 'c']}
d['key1'][2].upper()   # 'C'
```

### 6.8 Add and Overwrite Key-Value Pairs
- Add new pair:
```python
d = {'k1': 100, 'k2': 200}
d['k3'] = 300
```
- Overwrite existing value:
```python
d['k1'] = 'NEW VALUE'
```

### 6.9 Useful Dictionary Methods
- Keys only: `d.keys()`
- Values only: `d.values()`
- Key-value pairs: `d.items()`

### 6.10 Practical Reminders
- Unlike lists, dictionaries are not accessed with numeric positions like `[0]`.
- Use meaningful keys when you want labeled data fields (e.g., name/age/height).
- `d.items()` returns key-value pairs as tuple-like pairs in a view object.

---

## 7. Tuples in Python

**Definition:** Tuples are very similar to lists, but they are **immutable** (cannot be changed after creation).

### 7.1 Tuple Syntax and Creation
- Tuples use parentheses `()` instead of square brackets `[]`.
- Example tuple:
```python
t = (1, 2, 3)
```
- Comparable list:
```python
mylist = [1, 2, 3]
```
- Confirm types:
```python
type(t)       # tuple
type(mylist)  # list
```

### 7.2 Tuple Basics (Like Lists)
- Length works the same: `len(t)`
- Mixed types are allowed: `('one', 2)`
- Indexing works: `t[0]`
- Negative indexing works: `t[-1]`
- Slicing works similarly to lists.

### 7.3 Built-in Tuple Methods
Tuples have fewer methods than lists. The two core methods are:
- `count()` → counts occurrences of a value
- `index()` → returns the first index where a value appears

Example:
```python
t = ('a', 'a', 'b')
t.count('a')   # 2
t.index('a')   # 0
t.index('b')   # 2
```

### 7.4 Immutability (Key Difference from Lists)
- Lists support item reassignment:
```python
mylist[0] = 'NEW'
```
- Tuples do **not** support item reassignment:
```python
t[0] = 'NEW'   # TypeError
```
- Common error message: `TypeError: 'tuple' object does not support item assignment`.

### 7.5 Why Tuples Are Useful
- Tuples are useful when data should **not** change accidentally.
- This provides stronger data integrity in larger programs.
- As a beginner, you may use lists more often, but tuples become valuable when immutability is desired.

### 7.6 Nested Access Pattern Reminder
Tuples (like other containers) can be part of chained access patterns in Python. In general:
- Access container element first (by key or index), then
- Apply the next index/method call to the returned object.

---

## 8. Sets in Python

**Definition:** Sets are unordered collections of **unique** elements.

### 8.1 Creating a Set
- Create an empty set:
```python
myset = set()
```
- Note: an empty set prints like `set()`.

### 8.2 Adding Elements
- Add a value with `.add()`:
```python
myset.add(1)
myset.add(2)
```
- Trying to add a duplicate does not create another copy:
```python
myset.add(2)
```
- Result still contains each value only once.

### 8.3 Set Appearance and Behavior
- Non-empty sets display with curly braces, e.g. `{1, 2}`.
- Even though curly braces are used, sets are not dictionaries because they have no key-value pairs.
- Sets are unordered, so do not rely on position/index behavior.

### 8.4 Casting a List to a Set (Common Use)
One of the most useful beginner patterns is removing duplicates:

```python
mylist = [1,1,1,1,2,2,2,3,3,3]
set(mylist)
```

- This returns only unique values from the list.

### 8.5 Practical Reminders
- Sets accept only unique elements.
- Duplicate inserts are ignored.
- Sets are great for quick deduplication.
- You usually use sets when uniqueness matters more than order.

---

## 9. Booleans in Python

**Definition:** Booleans represent truth values: `True` or `False`.

### 9.1 Boolean Values and Capitalization
- Python Boolean literals are capitalized:
    - `True`
    - `False`
- Using lowercase `true`/`false` causes an error because Python treats them as variable names.

### 9.2 Boolean Type
- Check type with:
```python
type(True)
type(False)
```
- Both return `bool`.

### 9.3 Comparison Operators Return Booleans
- Many expressions evaluate to Boolean results.
- Examples:
```python
1 > 2      # False
1 == 1     # True
```
- These comparisons are foundational for control flow and logic.

### 9.4 Why Booleans Matter
- Booleans help programs decide what to do next.
- Typical pattern: if a condition is `True`, execute a block of code.
- You’ll use Booleans heavily with `if`, `elif`, `else`, and logical operators later.

### 9.5 `None` as a Placeholder
- `None` is a special keyword (capital `N`) used to represent “no value yet.”
- Example:
```python
b = None
```
- Useful when you want to define a variable now and assign a real value later.
- Reminder: some in-place methods (like list sorting) return `None`.

---

## 10. Files in Python (Basic I/O)

**Definition:** File I/O means reading from and writing to files (such as `.txt`) using Python.

### 10.1 Creating a Text File in Jupyter
- Jupyter supports a magic command to quickly create files:
```python
%%writefile myfile.txt
Hello this is a text file
This is the second line
This is the third line
```
- `%%writefile` must be on the first line of the cell.

### 10.2 Opening Files
- Basic syntax:
```python
myfile = open('myfile.txt')
```
- Common error:
    - `FileNotFoundError: [Errno 2] No such file or directory`
- Typical causes:
    1) Wrong filename
    2) Wrong file path / wrong working directory

### 10.3 Check Current Working Directory
- In Jupyter, run:
```python
pwd
```
- This helps confirm where Python is looking for files.

### 10.4 Reading a File
- Read all contents as one string:
```python
myfile.read()
```
- New lines appear as `\n` in the string output.

### 10.5 File Cursor and `seek(0)`
- After `.read()`, the cursor is at the end of the file.
- Reading again may return an empty string unless you reset:
```python
myfile.seek(0)
```

### 10.6 Read Lines as a List
- Get each line as a list element:
```python
myfile.seek(0)
myfile.readlines()
```
- Useful for indexing and looping over lines.

### 10.7 File Paths (Windows vs macOS/Linux)
- Windows paths often use escaped backslashes in strings:
```python
'C:\\Users\\YourName\\Folder\\myfile.txt'
```
- macOS/Linux paths use forward slashes:
```python
'/Users/YourName/Folder/myfile.txt'
```

### 10.8 Best Practice: `with open(...) as ...`
- Preferred pattern (auto-closes file):
```python
with open('myfile.txt') as f:
    contents = f.read()
```
- Avoids forgetting to call `.close()` manually.

### 10.9 File Modes and Permissions
- `r` → read only
- `w` → write only (overwrites existing file; creates file if missing)
- `a` → append only (adds to end of file)
- `r+` → read and write
- `w+` → write and read (overwrites if exists; creates if missing)

### 10.10 Appending to a File
```python
with open('my_new_file.txt', mode='a') as f:
    f.write('\nFour on fourth')
```
- `\n` is often needed to start on a new line.

### 10.11 Creating a New File with Write Mode
```python
with open('brand_new_file.txt', mode='w') as f:
    f.write('I created this file')
```
- If file doesn’t exist, `w` creates it.

### 10.12 Practical Reminders
- Use `with open(...)` as your default approach.
- Reset cursor with `seek(0)` when re-reading the same file object.
- Choose file mode intentionally to avoid accidental overwrites.

