# Structure of a C++ Program

This section covers:

- keywords;
- identifiers;
- punctuation;
- operators;
- syntax;
- preprocessor directives;
- comments;
- the `main` function; and
- namespaces; and
- basic console input and output.

## Keywords

Keywords are reserved tokens with predefined meanings in C++. They cannot be redefined or used as ordinary identifiers for variables, functions, classes, and other entities. Examples include `int`, `return`, `if`, `else`, `while`, and `for`.

Keywords are case-sensitive: `return` is a keyword, while `Return` is not. The exact set depends on the selected C++ standard, so it is more reliable to consult the current [C++ keyword reference](https://en.cppreference.com/w/cpp/keyword) than to memorize a fixed count.

Some keywords appear less often in beginner programs. For example, C++20 introduced `concept` and `requires` for constraints, plus `co_await`, `co_return`, and `co_yield` for coroutines.

> [!NOTE]
> **How the sausage is made: not every special word is a keyword**
>
> Some identifiers, including `final`, `override`, `import`, and `module`, have special meaning only in particular contexts. C++ also provides alternative operator tokens such as `and`, `or`, and `not`. The compiler recognizes these according to the language grammar; they are not library functions or macros.

## Identifiers

Identifiers are names for variables, functions, classes, namespaces, and other program entities. They follow these core rules:

- An identifier cannot be a keyword.
- A basic identifier begins with a letter or underscore and can continue with letters, digits, or underscores. Modern C++ also permits many Unicode characters under additional rules.
- Identifiers are case-sensitive, so `myVariable` and `myvariable` are different names.
- Meaningful, descriptive names improve readability.

Avoid inventing names that:

- contain a double underscore anywhere, such as `value__count`;
- begin with an underscore followed by an uppercase letter, such as `_Buffer`; or
- begin with an underscore in the global namespace.

Those forms are reserved for the implementation. Using ordinary names such as `favorite_number`, `calculate_total`, and `Account` avoids collisions with compiler and standard-library internals.


## Punctuation

Punctuation tokens structure source code and separate its elements. Common examples include:

- `;` (semicolon): Terminates many declarations and expression statements. Compound statements such as `{ ... }` do not generally need a trailing semicolon, although a class definition does.
- `{` and `}` (braces): Delimit blocks, function bodies, class definitions, namespaces, and braced initializer lists.
- `(` and `)` (parentheses): Group expressions and appear in function declarations, calls, conditions, and casts.
- `[` and `]` (brackets): Appear in array declarations and subscripting, lambda captures, and attributes.
- `,` (comma): Separates items such as function arguments, parameters, declarators, and initializer elements. C++ also has a comma operator, though it is less common.
- `.` (dot): Accesses a member of an object.
- `->` (arrow): Accesses a member through a pointer-like expression.
- `:` (colon): Appears in labels, `case` labels, access specifiers, base-class lists, constructor initializer lists, bit-fields, and the conditional operator `?:`.
- `::` (scope-resolution operator): Qualifies a name with its namespace, class, enumeration, or global scope, as in `std::cout`.

The role of a token depends on context. For example, `*` can mean multiplication, pointer declaration, or pointer dereference.

## Operators

C++ has many operators, grouped here by their most common purposes.

### Arithmetic Operators

- `+`: addition
- `-`: subtraction
- `*`: multiplication
- `/`: division
- `%`: remainder for integral operands

For integer operands, `/` discards the fractional part by truncating toward zero. For example, `7 / 2` produces `3`, while `7.0 / 2.0` produces `3.5`.

C++ defines operator **precedence** and **associativity** rather than literally applying the classroom PEMDAS/BODMAS mnemonic. Multiplication, division, and remainder have higher precedence than addition and subtraction. Operators in each of those groups associate from left to right:

```cpp
int result = 10 - 4 + 2;       // (10 - 4) + 2 == 8
int scaled = 2 + 3 * 4;        // 2 + (3 * 4) == 14
int explicit_result = (2 + 3) * 4; // 20
```

Use parentheses when they make the intended grouping easier to see.

### Comparison Operators

- `==`: equal to
- `!=`: not equal to
- `<`: less than
- `>`: greater than
- `<=`: less than or equal to
- `>=`: greater than or equal to

The meaning of a comparison depends on the operand types:

- Integers are compared by numeric value.
- Floating-point calculations can introduce rounding, so two results that are mathematically equal may not have identical representations.
- `std::string` relational comparisons are lexicographical: characters are compared in sequence rather than interpreting the text as a number. For example, `std::string{"20"} < std::string{"3"}` is `true` because `'2'` precedes `'3'`.
- Built-in character arrays and C-style string pointers require care: `==` on pointers compares addresses, not text content. Use `std::string` for value-like string comparisons.

Some languages or tools may compare numeric-looking strings numerically, but ordinary `std::string` comparisons in C++ do not.

### Logical Operators

The built-in logical operators contextually convert their operands to `bool` and produce a `bool` result.

- `&&` is logical AND and is `true` only when both operands are true.
- `||` is logical OR and is `true` when at least one operand is true.
- `!` is logical NOT and reverses the truth value of its operand.

#### AND

| `a` | `b` | `a && b` |
|---:|---:|---:|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

#### OR

| `a` | `b` | <code>a &#124;&#124; b</code> |
|---:|---:|---:|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

#### NOT

| `a` | `!a` |
|---:|---:|
| 0 | 1 |
| 1 | 0 |

The built-in `&&` and `||` operators short-circuit. If the left operand determines the result, the right operand is not evaluated:

```cpp
if (pointer != nullptr && pointer->is_ready()) {
    // Dereference only occurs when pointer is non-null.
}
```

> [!NOTE]
> **How the sausage is made: logical and bitwise operations are different**
>
> Logical operators treat each operand as one truth value and return `bool`. Bitwise operators operate on the individual bits of integral or unscoped enumeration values. Although `true` converts to `1` and `false` to `0`, choosing the correct operator communicates intent and avoids subtle errors.

#### NAND, NOR, and XOR

C++ has no dedicated logical NAND, NOR, or XOR operator, but they can be expressed using the existing logical operators.

Logical NAND is `!(a && b)`:

| `a` | `b` | `!(a && b)` |
|---:|---:|---:|
| 0 | 0 | 1 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

Logical NOR is `!(a || b)`:

| `a` | `b` | <code>!(a &#124;&#124; b)</code> |
|---:|---:|---:|
| 0 | 0 | 1 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 0 |

For Boolean operands, logical XOR can be written as `a != b`:

| `a` | `b` | `a != b` |
|---:|---:|---:|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

This equivalence assumes `a` and `b` are Boolean values. For arbitrary values, convert each operand to `bool` first; for example, `static_cast<bool>(a) != static_cast<bool>(b)`.

#### De Morgan's Laws

De Morgan's laws relate AND and OR through negation:

1. The negation of a conjunction is the disjunction of the negations: `!(a && b)` is equivalent to `!a || !b`.
2. The negation of a disjunction is the conjunction of the negations: `!(a || b)` is equivalent to `!a && !b`.

### Bitwise Operators

The built-in bitwise operators act on integral or unscoped enumeration values one bit position at a time:

- `&`: bitwise AND; a result bit is `1` when both input bits are `1`.
- `|`: bitwise OR; a result bit is `1` when either input bit is `1`.
- `^`: bitwise XOR; a result bit is `1` when the input bits differ.
- `~`: bitwise NOT; every bit is inverted.
- `<<`: left shift.
- `>>`: right shift.

Using the conceptual 8-bit unsigned values `00010101` (21) and `00001111` (15):

#### Bitwise AND

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
b           00001111       15
a & b       00000101        5
```

#### Bitwise OR

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
b           00001111       15
a | b       00011111       31
```

#### Bitwise XOR

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
b           00001111       15
a ^ b       00011010       26
```

#### Bitwise NOT

Within an 8-bit unsigned value, inverting `00010101` (21) produces `11101010` (234):

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
~a          11101010      234
```

In a C++ expression, small integer types are usually **promoted** to `int` before `~` is applied. Narrowing the result back to eight bits makes the intended width explicit:

```cpp
#include <cstdint>

std::uint8_t value = 21;
std::uint8_t inverted = static_cast<std::uint8_t>(~value); // 234
```

> [!NOTE]
> **How the sausage is made: bit width is part of the answer**
>
> A NOT, NAND, NOR, or XNOR result has meaning only when its width is known because every bit in that width is inverted. Writing `~21` does not describe an 8-bit operation by itself. The integer promotions and the width of `int` affect the expression before any conversion back to a smaller type.

#### Left Shift

Left-shifting unsigned `00010101` (21) by two positions produces `01010100` (84) in this example:

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
a << 2      01010100       84
```

For an unsigned value with a valid shift count, shifting left by $n$ corresponds to multiplication by $2^n$, reduced modulo the width of the result type. For example, shifting by two corresponds to multiplication by $2^2 = 4$.

#### Right Shift

Right-shifting unsigned `00010101` (21) by two positions produces `00000101` (5):

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
a >> 2      00000101        5
```

For unsigned values, zeros enter from the left, and shifting right by $n$ corresponds to integer division by $2^n$. Signed negative values require more care and should not be reasoned about as if they were unsigned bit patterns.

A negative shift count, or a count greater than or equal to the width of the promoted left operand, causes undefined behavior. Left-shifting a signed value can also cause undefined behavior when the mathematical result is not representable. Unsigned types are generally the clearest choice for bit manipulation.

#### Bitwise NAND, NOR, and XNOR

C++ has no dedicated bitwise NAND, NOR, or XNOR operator, but each can be composed from the existing operators. The following results again assume an 8-bit width.

Bitwise NAND uses `~(a & b)`. It produces `0` where both input bits are `1` and `1` everywhere else:

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
b           00001111       15
~(a & b)    11111010      250
```

Bitwise NOR uses `~(a | b)`. It produces `1` only where both input bits are `0`:

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
b           00001111       15
~(a | b)    11100000      224
```

Bitwise XNOR uses `~(a ^ b)`. It produces `1` where the input bits are equal:

```text
expression  binary    decimal
----------  --------  -------
a           00010101       21
b           00001111       15
~(a ^ b)    11100101      229
```

### Why Use Shift Operators?

Shifts are useful when the operation itself is about bit positions, such as:

- building or testing bit masks;
- packing fields into a protocol or hardware register;
- graphics and low-level data formats; and
- some cryptographic and hashing operations.

Do not replace multiplication or division by a power of two merely because a shift is assumed to be faster. Modern optimizing compilers routinely perform that transformation when it is valid, and signed arithmetic can make a hand-written replacement incorrect. Use arithmetic operators for arithmetic intent and shift operators for bit-level intent unless measurement and target-specific requirements justify otherwise.

### Connection to Digital Logic

This material is not covered by the course, but it connects the operators to an EECE background.

A **half-adder** uses XOR for the sum bit and AND for the carry-out bit:

| `A` | `B` | `A XOR B` (Sum) | `A AND B` (Carry-out) |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

A **full-adder** also accepts a carry-in bit, `Cin`:

| `A` | `B` | `Cin` | `A XOR B XOR Cin` (Sum) | `(A AND B) OR (Cin AND (A XOR B))` (Carry-out) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 1 | 0 |
| 0 | 1 | 0 | 1 | 0 |
| 0 | 1 | 1 | 0 | 1 |
| 1 | 0 | 0 | 1 | 0 |
| 1 | 0 | 1 | 0 | 1 |
| 1 | 1 | 0 | 0 | 1 |
| 1 | 1 | 1 | 1 | 1 |

This demonstrates how XOR and AND can represent a half-adder, and how XOR, AND, and OR combine in a full-adder.

### Shift Tokens as Stream Operators

The `<<` and `>>` tokens are also used by C++ streams:

- `std::cout << value` inserts `value` into an output stream.
- `std::cin >> value` extracts a value from an input stream.

These are not nonstandard operators. The standard library overloads the same C++ operator tokens for stream types. Operand types and overload resolution determine whether a use represents a bit shift, stream insertion, stream extraction, or another user-defined operation.

```cpp
int shifted = 8 << 1;       // Integer left shift: 16
std::cout << shifted << '\n'; // Stream insertion
```

## Syntax

Syntax is the set of grammatical rules that determines how C++ declarations, expressions, statements, and other constructs are formed.

- Many declarations and expression statements end with a semicolon (`;`), but not every statement does.
- Blocks are enclosed in braces (`{}`), and nested blocks introduce nested scopes.
- C++ is case-sensitive, so `Variable` and `variable` are different identifiers.
- Whitespace usually separates tokens and improves readability. It is not interchangeable everywhere: `intvalue` and `int value` are different token sequences, and whitespace inside a string literal is data.
- `//` begins a comment that continues to the end of the line.
- `/* ... */` forms a block comment. Block comments do not nest.

Comments are intended for human readers. During translation, comments are replaced with whitespace before the compiler analyzes normal C++ syntax.

## Preprocessor Directives

Preprocessing occurs before normal C++ parsing and compilation. Directives begin with `#` and occupy a logical source line. The preprocessor can include files, expand macros, select source regions, and communicate certain information to the implementation.

After preprocessing, each source file and everything it includes form a **translation unit**, which is then compiled. An `#include` is therefore closer to source inclusion than to linking a library. Header guards or `#pragma once` prevent a header's contents from being processed repeatedly within the same translation unit.

### Directive Summary

- `#include` locates a file and processes its contents as part of the current translation unit.
- `#define` defines an object-like or function-like macro.
- `#undef` removes a macro definition from that point onward.
- `#if` conditionally includes source according to a preprocessor constant expression.
- `#ifdef` includes source when a macro name is defined; it is shorthand for `#if defined(NAME)`.
- `#ifndef` includes source when a macro name is not defined; it is shorthand for `#if !defined(NAME)`.
- `#elif` tests another condition when earlier branches in the same group were false.
- `#else` selects the fallback branch.
- `#endif` ends a conditional group.
- `#line` changes the presumed source line number and, optionally, filename used by diagnostics and predefined macros.
- `#error` requires the implementation to issue a diagnostic, making the translation fail.
- `#warning` requests a warning and is standard beginning with C++23; some compilers supported it earlier as an extension.
- `#pragma` sends implementation-defined instructions to the compiler or toolchain.

C++23 also adds `#elifdef` and `#elifndef` as direct forms of `#elif defined(NAME)` and `#elif !defined(NAME)`.

> [!IMPORTANT]
> The preprocessor does not understand C++ types, scopes, overload resolution, or object lifetimes. It works primarily with preprocessing tokens and preprocessor conditions. Macro output must still form valid C++ when the compiler parses it.

> [!NOTE]
> **How the sausage is made: macros are token substitution**
>
> A macro is not a typed variable or function. Its replacement tokens are expanded before C++ semantic analysis, which is why macros can ignore scope, evaluate arguments more than once, and produce confusing diagnostics. Prefer `constexpr`, inline functions, templates, and other language features unless preprocessing is specifically required.

## Preprocessor Examples and When to Use Them

### `#include`: Make Declarations Available

```cpp
#include <iostream>          // Search the implementation's include paths.
#include "temperature.hpp"  // Search for a project header.
```

Use `#include` when a translation unit needs declarations or definitions from a header. Angle brackets are conventionally used for standard or externally supplied headers, while quotation marks are conventionally used for project headers. Do not `#include` a `.cpp` implementation file as a substitute for compiling and linking it.

### `#define`: Define a Macro

```cpp
#define PROJECT_VERSION_MAJOR 2
#define STRINGIFY_DETAIL(value) #value
#define STRINGIFY(value) STRINGIFY_DETAIL(value)

constexpr char version_text[] = STRINGIFY(PROJECT_VERSION_MAJOR); // "2"
```

Use macros when preprocessing itself is necessary, such as build-provided feature flags, conditional compilation, stringizing tokens, token concatenation, or compatibility with a C API. Although `#define PI 3.14159` performs a valid replacement, modern C++ should normally use a typed constant:

```cpp
inline constexpr double pi = 3.14159;
```

Avoid function-like macros for ordinary calculations because they do not provide normal type checking and can evaluate an argument more than once.

### `#ifdef`: Compile When a Macro Exists

```cpp
#ifdef ENABLE_TRACE
std::clog << "Entering calculate_total\n";
#endif
```

Use `#ifdef` for a binary feature or diagnostic switch that is either defined or absent. Build systems commonly define such macros with a compiler option instead of editing the source.

### `#ifndef`: Header Guards and Absent Features

```cpp
#ifndef TEMPERATURE_HPP_INCLUDED
#define TEMPERATURE_HPP_INCLUDED

double celsius_to_fahrenheit(double celsius);

#endif // TEMPERATURE_HPP_INCLUDED
```

Use this pattern as a portable **header guard**. It prevents repeated declarations when multiple include paths reach the same header in one translation unit. `#ifndef` can also select code when an optional feature macro is absent.

### `#if`, `#elif`, `#else`, and `#endif`: Select One Configuration

```cpp
#if defined(_WIN32)
constexpr char path_separator = '\\';
#elif defined(__linux__) || defined(__APPLE__)
constexpr char path_separator = '/';
#else
#error "Unsupported operating system"
#endif
```

Use a conditional group when genuinely different source is required for platforms, compiler capabilities, generated configurations, or optional features. Keep platform-dependent regions narrow; ordinary runtime choices generally belong in `if` statements instead.

The `defined(NAME)` operator can be used only in preprocessor conditions. In a `#if` expression, an identifier left after macro expansion is generally replaced with `0`, so explicitly testing `defined(...)` makes intent clearer.

### `#undef`: Remove a Macro

```cpp
#ifdef min
#undef min
#endif
```

Use `#undef` to remove a conflicting macro from a platform or third-party header, or to limit a temporary macro's effective region. Because macros do not obey C++ block scope, avoid defining broad macros that need frequent cleanup.

### `#line`: Remap Generated Source Locations

```cpp
#line 200 "generated_rules.cpp"
static_assert(sizeof(int) >= 4);
```

Use `#line` primarily in code generators so compiler diagnostics can refer to the original template or source location. It is rarely appropriate in handwritten application code because it makes physical and reported line numbers differ.

### `#error`: Reject an Unsupported Build

```cpp
#if defined(LEGACY_MODE) && defined(STRICT_MODE)
#error "LEGACY_MODE and STRICT_MODE cannot be enabled together"
#endif
```

Use `#error` when a configuration is invalid and allowing compilation to continue would produce a misleading or unsupported program. It is better suited to build-time configuration rules than ordinary runtime input validation.

### `#warning`: Report a Suspicious Build Configuration

```cpp
#ifdef LEGACY_MODE
#warning "LEGACY_MODE is deprecated and will be removed"
#endif
```

Use `#warning` for a non-fatal build-time migration notice when compiling as C++23 or when the selected compiler documents support for it. It is not portable to every older language mode or toolchain.

### `#pragma`: Request Implementation-Specific Behavior

```cpp
#pragma once
```

Use a pragma only when the target compiler documents it. `#pragma once` is widely supported and keeps a header from being included more than once per translation unit, but it is not part of the ISO C++ standard. Traditional `#ifndef` header guards remain the fully portable alternative.

### `__has_include`: Check for an Available Header

```cpp
#if __has_include(<version>)
#include <version>
#else
#error "This build requires the <version> header"
#endif
```

`__has_include` is a C++17 preprocessor operator, not a directive. Use it when source must adapt to environments where an optional header may or may not be installed. Do not use it to hide an undeclared required dependency; the build configuration should report that clearly.


## Comments
Comments add human-readable notes to source code without becoming part of the program's executable behavior. C++ has two comment forms:

- A line comment starts with `//` and continues to the end of that line.
- A block comment starts with `/*` and ends with `*/`. It can span multiple lines, but block comments cannot be nested reliably.

```cpp
// Convert the user's input from Celsius to Fahrenheit.
double fahrenheit = celsius * 9.0 / 5.0 + 32.0;

/*
This block comment spans
more than one line.
*/
```

During an early translation phase, each comment is replaced with a space character. Consequently, comments do not reach normal C++ parsing or generated machine code. They can still separate tokens, so removing one manually is not always equivalent to replacing it with nothing: `first/**/second` becomes the two tokens `first second`, not the single token `firstsecond`.

## The `main` Function

In an ordinary **hosted** C++ executable, `main` is the designated function called by the runtime after startup initialization. A typical definition looks like this:

```cpp
#include <iostream>

int main() {
    std::cout << "Hello, World!\n";
    return 0;
}
```

A hosted program contains exactly one definition of `main` in the global scope; `main` cannot be overloaded. It must return `int`. Returning `0` reports successful termination to the host environment. A nonzero status conventionally reports failure, although the precise interpretation is platform-dependent. Reaching the closing brace of `main` is equivalent to `return 0;`.

Another standard form accepts command-line arguments:

```cpp
#include <iostream>

int main(int argc, char* argv[]) {
    std::cout << "Number of arguments: " << argc << '\n';

    for (int i = 0; i < argc; ++i) {
        std::cout << "Argument " << i << ": " << argv[i] << '\n';
    }

    return 0;
}
```

This version has two parameters:

- `argc` is the nonnegative number of command-line arguments.
- `argv` points to an array of C-style strings containing those arguments. `argv[0]` conventionally identifies the program invocation, and `argv[argc]` is a null pointer sentinel.

The declarations `char* argv[]` and `char** argv` are equivalent in a function parameter list. This form allows a program to process arguments supplied when it is launched from a command line, terminal, script, or another process.

> [!NOTE]
> **How the sausage is made: `main` is not the first code that runs**
>
> The operating system loads the executable and transfers control to startup code supplied by the platform and C++ runtime. That code prepares the process, initializes objects with static storage duration, obtains the command-line arguments, and then calls `main`. After `main` returns, the runtime performs normal termination work and reports the status to the host environment.


## Namespaces

Namespaces organize related declarations and reduce collisions between independently chosen names. Functions, classes, variables, and other declarations can be grouped under a namespace name. Most C++ standard-library names are declared in `std`, which is why code commonly uses names such as `std::cout` and `std::string`.

You can define your own namespaces like this:

```cpp
#include <iostream>

namespace MyNamespace {
    void myFunction() {
        std::cout << "Hello from MyNamespace!\n";
    }
}
```

To use the function, qualify its name with the namespace:

```cpp
MyNamespace::myFunction();
```

Alternatively, a `using` declaration can make that specific name available for unqualified lookup in the current scope:

```cpp
using MyNamespace::myFunction;
myFunction(); // The namespace prefix is no longer needed in this scope.
```

### Why `std::cout` Instead of `cout`?

`cout` is declared in the `std` namespace. The qualified name `std::cout` tells the compiler exactly which `cout` is intended. Without the `std::` qualifier or a suitable `using` declaration, ordinary unqualified name lookup does not find it.

Prefer qualification in broadly shared code. In particular, avoid `using namespace std;` in header files because it makes every name in `std` a candidate for unqualified lookup in code that includes that header. A targeted declaration such as `using std::cout;` has a smaller effect.

### What Is a Naming Conflict?

Different namespaces may contain entities with the same unqualified name without conflicting. Ambiguity occurs when unqualified lookup makes multiple matching names visible and the compiler cannot determine which one is intended:

```cpp
namespace audio {
    void play() {}
}

namespace video {
    void play() {}
}

using namespace audio;
using namespace video;

// play();       // Error: the call is ambiguous.
audio::play();   // Clear: call audio::play.
video::play();   // Clear: call video::play.
```

Explicit qualification resolves the ambiguity and documents which library or subsystem owns the selected name.

`std` is the primary namespace for C++ standard-library facilities. It contains standard functions, classes, templates, and objects. Programs generally use these names by qualifying them, as in `std::vector` or `std::cout`. With a few narrowly specified exceptions, user code must not add declarations to `std`.

Third-party libraries may also define their own namespaces to avoid naming conflicts with the standard library or other libraries. For example, a library called `MathLib` might define its own namespace like this:

```cpp
namespace MathLib {
    double add(double a, double b) {
        return a + b;
    }
}
```

It can then be called with a qualified name:

```cpp
double sum = MathLib::add(3.0, 4.0);
```

The `::` token is the scope-resolution operator. It qualifies a name with a namespace, class, enumeration, or the global scope.

> [!NOTE]
> **How the sausage is made: namespaces affect names, not runtime objects**
>
> A namespace is a declarative region used during name lookup; creating one does not allocate an object at runtime. The same namespace can be reopened in multiple files, which allows a library to distribute related declarations across headers and source files while retaining one qualified naming hierarchy.

### Targeted `using` Declarations

```cpp
using std::cout;
using std::cin;
using std::endl;
```

These declarations allow `cout`, `cin`, and `endl` to be used without the `std::` prefix in the current scope. This is called a **using-declaration** because each declaration introduces one specific name. It is different from the broader **using-directive** `using namespace std;`.

Targeted using-declarations can reduce repetition in a small scope while limiting the number of introduced names. Use them judiciously to avoid conflicts, especially in larger projects or code that combines multiple libraries. In examples and shared interfaces, explicit names such as `std::cout` are often clearest.

## Basic I/O with `std::cin` and `std::cout`

The `<iostream>` header declares four standard stream objects:

- `std::cout` represents standard output, typically connected to a terminal.
- `std::cin` represents standard input, typically connected to a keyboard or terminal.
- `std::cerr` represents standard error and is configured to flush after each output operation by default.
- `std::clog` also represents standard error but is intended for buffered diagnostic or logging output.

These streams can be redirected, so their destinations and sources are not necessarily a screen and keyboard. For example, a shell can redirect standard output to a file while leaving standard error visible in the terminal.

- `<<` is the stream-insertion operator when its left operand is an output stream. It inserts the value on the right into that stream.
- `>>` is the stream-extraction operator when its left operand is an input stream. It extracts and converts input into the object on the right.

The arrow direction is a useful visual mnemonic for data flow, but operand types and operator overload resolution give these tokens their actual meaning.

### Output with `std::cout` and `<<`

Insert a value into `std::cout` with `<<`:

```cpp
int data = 42;
std::cout << data;
```

Insertion operations can be chained to output several values in one statement:

```cpp
int data1 = 42;
std::cout << "data 1 is " << data1;
```

Output does not automatically end with a line break. Add one explicitly:

```cpp
std::cout << "data 1 is " << data1 << std::endl; // Newline, then flush.
std::cout << "data 2 is " << data2 << '\n';      // Newline without a required flush.
```

Prefer `\n` for ordinary line endings. Use `std::endl` when an immediate flush is intentionally required, not merely as a general newline.

#### What Does It Mean to Flush the Output Buffer?

Output can be collected in a memory buffer so the program can send larger batches to the underlying destination instead of performing an expensive operation for every character. Flushing requests that pending characters be passed from the C++ stream buffer to its underlying destination.

A flush does not necessarily guarantee that bytes have reached physical hardware because the operating system and device may have additional buffers. Output may also be flushed automatically, such as during normal program termination, when a buffer fills, or when another tied stream requires it. By default, reading from `std::cin` first flushes its tied `std::cout`, which helps make an interactive prompt visible before input is requested.

```cpp
std::cout << "Working..." << std::flush; // Flush without adding a newline.
```

> [!NOTE]
> **How the sausage is made: buffering reduces system-call overhead**
>
> Writing to a terminal or file can cross from the program into the operating system. Collecting many small insertions in a buffer usually reduces the number of those transitions. `std::endl` performs an extra flush, so using it on every line can make output substantially slower without improving correctness.

### Input with `std::cin` and `>>`

Extract a formatted value from `std::cin` with `>>`:

```cpp
int data = 0;
std::cin >> data;
```

Extraction operations can be chained to read several values:

```cpp
int data1 = 0;
int data2 = 0;
std::cin >> data1 >> data2;
```

Formatted extraction can fail when the input cannot be converted to the requested type, when input reaches end-of-file, or when the underlying device reports an error. The stream records that condition in state flags. Subsequent formatted extractions normally fail until the state is handled.

Initialize destination objects and test the stream before using input-dependent results:

```cpp
int data = 0;

if (std::cin >> data) {
    std::cout << "You entered " << data << '\n';
} else {
    std::cerr << "Expected an integer.\n";
}
```

Detailed input recovery is not required yet, but it is important not to assume that every extraction succeeds.