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

