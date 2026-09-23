# What is a Variable? 
In c++ variables are used to store data. A variable is a named location in memory that can hold a value. The value of a variable can change during the execution of a program, hence the name "variable".
Variables are given unique names called identifiers, which are used to refer to the variable in the code. The type of a variable determines what kind of data it can hold, such as integers, floating-point numbers, characters, or more complex data structures.

Just for my own insanity, in Assembly a variable is a label that points to a memory address. The value of the variable is stored at that memory address, and the label is used to refer to that value in the code. In Assembly, variables are typically defined using directives such as `.data` or `.bss`, and their values can be changed by writing to the memory address they point to.

Specific to the course: 
- A variable is an abstraction for a memory location that can hold a value.
- Allows programmers to use meaningful names and not memory addresses
- Variables have: 
    - Type: their "category" (integer, real number, string, person, account,...)
    - Value: the contents (2, 3.14, "Hello", "John", 1000,...)

- Variables must be declared before they are used. 
- A variables value may change

# Declaring and Initializing Variables
When you are declaring a variable you are telling the compiler that you want to create a variable with a specific name and type. The syntax for declaring a variable is as follows:

```cpp
int dogs; 
```

Note above we did not assign a value to the variable, we just declared it. The variable `dogs` is of type `int` and can hold integer values.

If we wanted to initialize the variable: 
```cpp
int dogs;

dogs = 5;
```
The above code declares the variable `dogs` and then assigns it the value of 5.

We can also declare and initialize a variable in one line:
```cpp
int dogs = 5;
```

The above code declares the variable `dogs` and initializes it with the value of 5 in one line. Saving time. 

## Naming Variables
When naming variables, there are some rules and conventions to follow:
- Can contain letters, numebers, and underscores
- must begin with a letter or underscore
- cannot be a reserved keyword (like `int`, `return`, `if`, etc.)
- Cannot redeclare a name in the same scope. 

Naming variables - style and best practices
- Be consistent with naming conventions
- Use meaningful and descriptive names
- Never use variables before intializing them
- Declare variables close to where they are used

Different ways to initialize variables. 
```cpp
int dogs = 5;          // Direct initialization, C-like
int cats(3);           // Constructor-style initialization
int birds{21};           // Uniform initialization (C++11 and later)
```

## Global Variables
Globals are automatically initialized to zero if not explicitly initialized. They are declared outside of any function, usually at the top of the file. Global variables can be accessed from any function in the file, and their values persist for the lifetime of the program.

They have potential problems because they can be modified from anywhere in the code, which can lead to unexpected behavior and make debugging difficult. It is generally recommended to minimize the use of global variables and instead use local variables or pass data through function parameters.

in the following code: 

```cpp
#include <iostream>
using namespace std;

int main() {
    int localVariable = 10; // This is a local variable
    cout << "Local Variable: " << localVariable << endl;
    return 0;
}
```

In the above code, `localVariable` is a local variable that is declared and initialized within the `main` function. It can only be accessed within the scope of the `main` function.

```cpp
#include <iostream>
using namespace std;

int age{18}; // This is a global variable

int main() {
    cout << "Local Variable: " << age << endl;
    return 0;
}
```
In the above code, `age` is a global variable that is declared and initialized outside of any function. It can be accessed from any function in the file, including the `main` function.

```cpp
#include <iostream>
using namespace std;

int age{18}; // This is a global variable

int main() {
    int age{16}; // This is a local variable that shadows the global variable, shadows means that the local variable takes precedence over the global variable within its scope
    cout << "Local Variable: " << age << endl;
    return 0;
}
```
In the above code, there is a global variable `age` and a local variable `age` declared within the `main` function. The local variable shadows the global variable, meaning that within the scope of the `main` function, the local variable takes precedence over the global variable. When we print the value of `age`, it will output `16`, which is the value of the local variable.

This is not a good practice, as it can lead to confusion and make the code harder to read and maintain. It is generally recommended to use different names for local and global variables to avoid shadowing.

## C++ Built-in Primitives
Primatives are fundamental data types that are built into the C++ language. They are the basic building blocks for creating variables and performing operations in C++. The size of primitives can vary depending on the platform and compiler, but they generally have a fixed size and range of values.

The types of C++ built-in primitives include:
- `char`: Represents a single character, such as a letter or symbol. The size of a `char` is typically 1 byte.
- `char16_t`: Represents a 16-bit character, which can store Unicode characters. The size of a `char16_t` is typically 2 bytes.
- `char32_t`: Represents a 32-bit character, which can store Unicode characters. The size of a `char32_t` is typically 4 bytes.
- `wchar_t`: Represents a wide character, which can store larger character sets. The size of a `wchar_t` can vary depending on the platform and compiler.

Integer Types:
Can be signed or unsigned, and can have different sizes. The most common integer types are:
- signed `short` int: Usually at least 16-bits, can hold negative and positive values.
- signed `int`: Usually at least 16-bits, can hold negative and positive values.
- signed `long` int: Usually at least 32-bits, can hold negative and positive values.
- signed `long long` int: Usually at least 64-bits, can hold negative and positive values.

- unsigned `short` int: Usually at least 16-bits, can only hold positive values.
- unsigned `int`: Usually at least 16-bits, can only hold positive values.
- unsigned `long` int: Usually at least 32-bits, can only hold positive values.
- unsigned `long long` int: Usually at least 64-bits, can only hold positive values.

Floating point Types:
Used to represent non-integer numbers
represented by a mantissa and an exponent
precision is the unmber of digints in the mantissa
precision and size are compiler dependent

Types: 
- `float`: /7 decinmal digits, typical range 1.2*10^-38 to 3.4*10^38, usually 32-bits
- `double`: no less than float/15 decimal digits, typical range 2.3*10^-308 to 1.7*10^308, usually 64-bits
- `long double`: no less than double/19 decimal digits, typical range 3.4*10^-4932 to 1.1*10^4932, usually 80-bits

Boolean types: 
used to represent true or false values
zero is false, 
non-zero is true

bool
usually 8-bits
uses the true and false keywords.

Overflow Example: 
```cpp
short value1 {30000};
short value2 {1000};
short mult {value1 * value2}; // mult will overflow and wrap around to a negative value

cout << "The value of multo of " << value1 << " and " << value2 << " is: " << mult << endl;
```

The above will output: 
```
The value of multo of 30000 and 1000 is: -27648
```
## Sizeof Operator

The `sizeof` operator is used to determine the size, in bytes, of a data type or variable. It can be applied to both primitive types and user-defined types. The result of the `sizeof` operator is a compile-time constant, which means it is determined during compilation and does not change at runtime.

Examples:
```cpp  
sizeof(int); // Returns the size of an int in bytes
sizeof(double); // Returns the size of a double in bytes
sizeof(myVariable); // Returns the size of the variable myVariable in bytes
```