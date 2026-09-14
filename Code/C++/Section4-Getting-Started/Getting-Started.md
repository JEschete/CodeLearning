# Getting Started

## Section Goals

- Become familiar with the Visual Studio C++ workflow used in these notes.
- Read and explain a small console program.
- Build and run the program.
- Distinguish compiler errors, linker errors, runtime failures, logic errors, and warnings.

The course's CodeLite tour is skipped because this project uses Visual Studio 2026. The language concepts remain the same even though the menus and project files differ.

## The First Program

The section's program is in [main.cpp](main.cpp). It asks for a favorite number, reads an integer from standard input, and writes a response to standard output.

Its main pieces are:

- `#include <iostream>` makes the standard stream declarations available.
- `int main()` defines the program's main entry function in a hosted C++ environment.
- `std::cout` writes characters to standard output, which is normally the console here.
- `std::cin` reads characters from standard input and converts them to the requested type.
- `return 0;` reports successful completion to the host environment.

> [!NOTE]
> **How the sausage is made: execution starts before `main`**
>
> The operating system starts the executable, and the C++ runtime prepares the process before calling `main`. This preparation includes runtime initialization and initialization of non-local objects. Returning from `main` hands an integer status back to the host and performs normal termination work. Reaching the closing brace of `main` has the same effect as `return 0;`, but writing it explicitly is useful while learning.

## Building the Program

A **build** is more than compilation: it can preprocess source, compile changed translation units, and link the resulting object files. In Visual Studio, select **Build > Build Solution** or press `Ctrl+Shift+B`.

Visual Studio offers three related commands:

- **Build:** Uses dependency information to perform work needed to bring the selected projects and configuration up to date. This may compile changed source files and relink the program.
- **Rebuild:** Cleans the selected projects and then builds them again. Use it when investigating stale generated output or when a clean build is specifically required.
- **Clean:** Removes outputs and intermediate files produced for the selected projects and configuration. It does not compile or link anything.

For ordinary development, use **Build**. Rebuilding every time discards the speed benefit of incremental compilation.

If the folder was opened without a recognized build configuration, **Build Solution** may be unavailable because Folder View did not create an MSBuild project. Open a `.sln` or `.vcxproj` file, create a project containing the source, or provide a supported folder-based build system such as CMake.

> [!NOTE]
> **How the sausage is made: how an incremental build decides what to do**
>
> MSBuild compares project inputs, outputs, configuration, and dependency information. A changed `.cpp` file normally causes its object file to be regenerated. A changed header can cause every translation unit that includes it, directly or indirectly, to be recompiled. If object files change, the linker normally produces a new executable.

## Running and Debugging

- Press `Ctrl+F5` to run without attaching the debugger.
- Press `F5` to run under the debugger.
- Use breakpoints and step commands to pause execution and inspect program state.

A successful build only establishes that the toolchain produced an executable. It does not establish that the program is logically correct for every input.

## Compiler Errors

A compiler rejects source that is **ill-formed** according to the language rules. Introductory material often divides these diagnostics into syntax and semantic errors.

### Syntax Errors

A syntax error means the source does not follow the language's grammatical structure. This example has an unterminated string literal:

```cpp
std::cout << "Errors << std::endl;
return 0;
```

The missing quotation mark can cause several diagnostics because the compiler can no longer parse the following text as intended.

### Semantic Compile Errors

Code can be grammatically recognizable but still violate type, declaration, or other language rules. For example, a string literal cannot initialize an `int`:

```cpp
int count = "three";
```

Using an undeclared name is also a compile-time error:

```cpp
total = 42;
```

Compiler messages do not always label errors as "syntax" or "semantic." The useful distinction is whether the compiler can translate the source and what rule the diagnostic says was violated.

> [!NOTE]
> **How the sausage is made: one mistake can produce many diagnostics**
>
> After an early parsing or type error, the compiler tries to recover and continue checking the file. Its recovery may interpret later code incorrectly, producing follow-on messages. Start with the first relevant diagnostic, fix it, and build again before assuming every reported error is independent.

## Compiler Warnings

A warning identifies code that the compiler considers suspicious but is still willing to translate. A warning is not proof of a bug, and the absence of warnings is not proof of correctness. Each warning should still be understood and either fixed or deliberately justified.

```cpp
int miles_driven;
std::cout << miles_driven << '\n';
```

In this C++20 project, reading the uninitialized automatic `int` produces undefined behavior. A compiler or static analyzer may diagnose the problem, but diagnostics for this case are not guaranteed in every context.

Initialize an object when a meaningful initial value exists, and enable a useful warning level. For MSVC, `/W4` is a strong starting point for new learning projects; third-party headers may occasionally require targeted handling.

## Linker Errors

A linker error occurs after individual translation units compile but their object files cannot be combined into the requested program. A common cause is declaring and calling a function without providing its definition:

```cpp
int add(int left, int right);

int main() {
	return add(2, 3);
}
```

The call can be compiled because the declaration describes `add`, but linking fails if no object file or library supplies the matching definition.

Other common causes include:

- a required `.cpp` file is missing from the project;
- a required static or import library is not passed to the linker;
- a declaration and definition have different signatures; or
- the same non-inline entity is defined more than once.

Including a header normally supplies declarations. It does not automatically compile or link the corresponding implementation.

> [!NOTE]
> **How the sausage is made: linkers match symbols, not intentions**
>
> A C++ compiler encodes information such as function names, namespaces, parameter types, and calling conventions into object-file symbols. This process is commonly called **name mangling**. A small signature or configuration mismatch can therefore make the caller and definition appear to the linker as different symbols.

## Runtime Failures and Undefined Behavior

A runtime failure happens while an executable is running. Examples include an uncaught exception, a failed assertion, or an operating-system fault caused by invalid memory access.

Some bad operations instead have **undefined behavior**. For example, integer division by zero is undefined:

```cpp
int numerator = 10;
int denominator = 0;

return numerator / denominator;
```

C++ does not guarantee that this code will print an error or terminate cleanly. It might appear to work, crash, trap, or behave differently after an optimization or unrelated code change. Accessing outside a built-in array's bounds is another common source of undefined behavior.

Trying to open a missing file is different: a standard file stream normally enters a failure state that the program can test and handle. The missing file does not by itself require the process to crash.

> [!WARNING]
> **How the sausage is made: undefined does not mean random**
>
> It means the C++ standard places no requirements on the program after that operation. Compilers optimize under the assumption that a valid program does not execute undefined behavior, so the visible result can be surprising. Warnings, sanitizers, debugger checks, and tests help find these bugs, but none detects every case.

## Logic Errors

A logic error occurs when the program builds and runs but produces an unintended result. For example, this uses the perimeter-like expression instead of the rectangle-area formula:

```cpp
int area = length + width; // Intended: length * width
```

The compiler cannot infer the programmer's intended formula. Tests, assertions, code review, and debugging are the main tools for finding logic errors.

## Section Challenge

Create a program that:

1. asks the user for a favorite number from 1 through 100;
2. reads the number from the console; and
3. includes the entered value in its response.

For an input of `24`, the output should include:

```text
Amazing!! That's my favorite number too!
No really!! 24 is my favorite number!
```

The current [main.cpp](main.cpp) solves the introductory input/output exercise. It initializes `favorite_number` before extraction, but it does not yet verify that extraction succeeded or that the number is in the requested range. Input validation can be added after learning conditionals and stream states.

