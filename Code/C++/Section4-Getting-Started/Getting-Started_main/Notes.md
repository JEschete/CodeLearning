Section Overview
------------------
Codelite IDE quick tour (won't be doing this because I am using Visual Studio 2026)

Our first program
- Building
- Running
- Errors
- Warnings

Writing our First Program
------------------

See our file `main.cpp` in the `Section4-Getting-Started` folder. This is where we will write our first C++ program.

Building
-----------------
First we have to compile our program. In Visual Studio, you can do this by clicking on the "Build" menu and selecting "Build Solution" or by pressing `Ctrl + Shift + B`. This will compile your code and check for any errors or warnings.

For Visual Studio 2026, if we open in folder view, we cannot build the project. We need to create a new project and add the `main.cpp` file to it. To do this, go to "File" -> "New" -> "Project..." and select "Empty Project". Name your project and click "Create". Then, right-click on the "Source Files" folder in the Solution Explorer, select "Add" -> "Existing Item...", and choose the `main.cpp` file.

In Visual Studio 2026 we have 3 options, Build, Rebuild, and Clean. 
- Build: This option compiles only the files that have changed since the last build. It is faster than rebuilding the entire project.
- Rebuild: This option cleans the project and then compiles all the files, regardless of whether they have changed or not. It is useful when you want to ensure that everything is up to date.
- Clean: This option removes all the compiled files and intermediate files from the project. It is useful when you want to start fresh or if you are experiencing build issues.

Compiler Errors
-----------------
Programming Languages have rules. 
- Syntax errors occur when the code violates the rules of the programming language. For example, forgetting a semicolon at the end of a statement or using an undefined variable will result in a syntax error. The compiler will provide an error message indicating the line number and nature of the error.
```cpp
std::cout << "Errors <<std::endl;
return 0;
```
The above code will produce a syntax error because the string is not properly closed with a quotation mark.

- Semantic errors occur when the code is syntactically correct but does not produce the expected behavior. For example, using the wrong variable type or performing an invalid operation will result in a semantic error. The compiler may not catch these errors, but they can lead to unexpected results during runtime.
```cpp
a + b;
```
The above code will produce a semantic error if `a` and `b` are not defined or if they are of incompatible types.

Compiler Warnings
-----------------
Do NOT ignore compiler warnings. 
- The Compiler has recognized that there is a potential issue in your code that may lead to unexpected behavior. Warnings are not errors, but they indicate that something may be wrong or could be improved. It is important to address warnings to ensure the correctness and maintainability of your code.

- It's only a warning because the compiler is still able to generate correct machine code. 

```cpp
int miles_driven;
std::cout << miles_driven;
```

The above code will produce a warning because the variable `miles_driven` is declared but not initialized before being used. This can lead to undefined behavior, as the value of `miles_driven` is indeterminate.

What are Linker Errors?
------------------
Linker errors occur when the compiler is able to compile the code, but the linker is unable to find the necessary definitions for functions or variables that are referenced in the code. This can happen if you forget to include a library or if you have a typo in a function name.

An exmaple of a linker error is when you try to call a function that is declared but not defined. For example, if you declare a function `void myFunction();` in your code but do not provide a definition for it, the linker will produce an error indicating that it cannot find the definition for `myFunction`. 



What are Runtime Errors?
------------------
A runtime error occurs when the program is running and encounters an unexpected condition that prevents it from continuing. This can happen due to various reasons, such as dividing by zero, accessing an array out of bounds, or trying to open a file that does not exist.

An example of a runtime error is when you try to divide a number by zero. For example, if you have the following code:
```cpp
int a = 10;
int b = 0;

return a / b;
```
The above code will produce a runtime error because dividing by zero is undefined behavior in C++. The program will terminate with an error message indicating that a division by zero has occurred.


What are Logic Errors?
------------------
A logic error occurs when the program runs without crashing, but it produces incorrect results due to a flaw in the logic of the code. Logic errors can be difficult to detect because the program may appear to run correctly, but the output is not what was expected.

An example of a logic error is when you use the wrong formula to calculate the area of a rectangle. For instance, if you accidentally use `length + width` instead of `length * width`, the program will run without errors, but the result will be incorrect.

Section Challenge
------------------
Create a C++ program that asks the user for their favorite number between 1 and 100, then read this number from the console. 

Suppose the user enters 24.
Then display the following to the console: 

Amazing!! That's my favorite number too!
No really!! 24 is my favorite number!