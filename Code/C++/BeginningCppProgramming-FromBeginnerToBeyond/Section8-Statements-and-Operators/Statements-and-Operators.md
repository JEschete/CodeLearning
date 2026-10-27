# Expressions, Statements, and Operators

We are going to cover expressions, statements, and operators in C++.

## Expressions

An expression is a combination of variables, constants, and operators that produces a value.

- The most basic building block of a program.
- A sequence of operators and operands that specifies a computation.
- Computes a value from a number of operands.
- There is much more to expressions than what is covered here.

### Examples

```cpp
34 // Literal
favorite_number // Variable
1.5 + 2.8 // addition
2 * 5 // multiplication
a > b // relational
a = b // assignment
```

## Statements

A statement is a complete line of code that performs an action.

- A complete line of code that performs an action.
- Usually ends with a semicolon.
- Contains expressions.

```cpp
int x; // Declaration statement
favorite_number = 42; // Assignment statement
1.5 + 2.8; // Expression statement, kind of useless without assignment or output
x = 2 * 5; // Assignment statement
if (a > b) cout << "a is greater than b"; // If statement
; // Null statement
```

## Operators

Using Operators, C++ has a rich set of operators.

- unary: operates on a single operand, e.g., `-a`, `!b`.
- binary: operates on two operands, e.g., `a + b`, `a * b`
- ternary: operates on three operands, e.g., `a ? b : c`

Operators are symbols that specify the type of computation to perform on the operands.

- Assignment
- Arithmetic
- Increment
- Decrement
- Equality
- Relational
- Logical
- Compound
- Precedence

## The Assignment Operator (=)

lhs = rhs

- rhs is an expression that is evaluated to a value.
- The value of the RHS is stored to the LHS.

C++ is statically typed, which means the type of a variable must be known at compile time.

- The Value of the rhs must be type compatible with the lhs.
- The lhs must be assignable

- Assignment expression is evaluated to what was just assigned.
- More than one variable can be assigned in a single statement, e.g., `a = b = c = 5;`

## Arithmetic Operators

Arithmetic operators are used to perform mathematical operations.

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Modulus: `%` (remainder after division)
- Increment: `++`
- Decrement: `--`

The order of operations in C++ is:

- Parentheses `()`
- Increment `++` and Decrement `--`
- Multiplication `*`, Division `/`, and Modulus `%`
- Addition `+` and Subtraction `-`
- Relational operators `<`, `<=`, `>`, `>=`
- Equality operators `==` and `!=`
- Logical AND `&&`
- Logical OR `||`
- Assignment `=`

## Increment and Decrement Operator

Increment Operator ++
Decrement Operator --

Increments or decrements its operand by 1.

Can be used with integers, floating point types, and pointers.

There are prefix ++num
There are postfix num++

The difference between prefix and postfix are:

- Prefix: The value is incremented or decremented before it is used in an expression.
- Postfix: The value is incremented or decremented after it is used in an expression.

If I have the statement

```cpp
int x = 5;
int y = ++x; // Prefix increment
int z = x++; // Postfix increment
```

- In the prefix increment, `x` is incremented before it is assigned to `y`, so `y` will be 6 and `x` will be 6.
- In the postfix increment, `x` is assigned to `z` before it is incremented, so `z` will be 6 and `x` will be 7.

The same goes for the decrement operator.

## Mixed Type Expressions

This is where the operands could have different types.
C++ operations occur on same type operands.
If operands are of different types, C++ will convert one.
Important! Since it could affect calculation results.
C++ will attempt to automatically convert types (coercion) if it can't a compiler error will occur.

Conversions

- Higher vs Lower types are based on the size of the values and the type they can hold.
- long double, double, float, unsigned long, long, unsigned int, int
- short and char types are always converted to int
- Type Coercion: conversion of one operand to another data type.
- Promotion: conversion of a lower type to a higher type.
- Used in mathematical operations to ensure operands are of compatible types.
- Demotion: conversion of a higher type to a lower type.
- used with assignment to lower type.

Examples:

- lower op higher
- The lower type will be promoted to the higher type before the operation is performed.
    2 * 5.2
    2 is promoted to 2.0 (double) before the multiplication is performed.

- lower = higher;
 int num {0};
 num = 100.2; // Demotion: double is converted to int, fractional part is truncated

Explicit type casting - static_cast<type>

```cpp
int total_amount {100};
int total_number {8};

double average {0.0};

average = total_amount / total_number;
cout << average << endl; // this will display 12.

average = static_cast<double>(total_amount) / total_number;
cout << average << endl; // this will display 12.5
```

## Testing for equality

The == and != operators

- Compares the values of 2 expressions
- Evaluates to a boolean value (`true` or `false`) depending on whether the comparison is true or not.
- Commonly used in control flow statements

expr1 == expr2 // checks if expr1 is equal to expr2
expr1 != expr2 // checks if expr1 is not equal to expr2
100 == 200 // evaluates to false
num1 != num2 // checks if num1 is not equal to num2

## Relational Operators

Relational operators are used to compare two values.

They are:

- greater than >
- less than <
- greater than or equal to >=
- less than or equal to <=
- <=> // three-way comparison operator (C++20 and later)

## Logical Operators

not ! - negation
and && - logical AND
or || - logical OR

Short Circuit Evaluation
When evaluating a logical expreession C++ stops as soon as the result is known.
For example:

```cpp
bool a = false;
bool b = true;

if (a && b) {
    // This block will not be executed because 'a' is false.
    // C++ will not evaluate 'b' due to short-circuit evaluation.
}
```

## Compound Assignment operators

They are: 
+= is lhs += rhs; lhs = lhs + (rhs);
-= is lhs -= rhs; lhs = lhs - (rhs);
*= is lhs *= rhs; lhs = lhs * (rhs);
%= is lhs %= rhs; lhs = lhs % (rhs);
/= is lhs /= rhs; lhs = lhs / (rhs);
&= is lhs &= rhs; lhs = lhs & (rhs);
|= is lhs |= rhs; lhs = lhs | (rhs);
^= is lhs ^= rhs; lhs = lhs ^ (rhs);
<<= is lhs <<= rhs; lhs = lhs << (rhs);
>>= is lhs >>= rhs; lhs = lhs >> (rhs);

## Operator Precedence

Higher to Lower 
Operator                                Associativity
---------
[] -> . ()                              left to right
++ -- -(unary) *(de-ref) & sizeof       right to left
* / %                                   left to right
+ -                                     left to right
<< >>                                   left to right
< <= > >=                               left to right
== !=                                   left to right
&                                       left to right
^                                       left to right
|                                       left to right
&&                                      left to right
||                                      left to right
= op= ?:                                right to left

