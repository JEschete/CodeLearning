# Introduction

## Why Learn C++?

### It is widely used

- A large amount of production software is written in C++ and still needs to be maintained and extended.
- The language has a mature ecosystem, an active standards committee, and a large developer community.

### It is relevant across many domains

- C++ is used to build software for Windows, Linux, macOS, game consoles, and embedded systems.
- Common domains include game engines, browsers, databases, networking, real-time systems, high-performance computing, finance, and infrastructure for machine learning.
- Unreal Engine uses C++ as its primary programming language.

### It provides control and flexibility

- C++ can produce high-performance native programs with direct control over memory and other resources.
- It supports procedural, object-oriented, generic, and functional programming styles.
- Standards-compliant source code can be portable, although operating-system APIs, third-party libraries, and compiler extensions can reduce portability.

> [!NOTE]
> **How the sausage is made: performance is not automatic**
>
> C++ gives a programmer tools for controlling memory layout, allocations, object lifetimes, and generated machine code. Those tools make high performance possible, but the algorithm, data layout, compiler settings, and quality of the implementation still determine whether a particular program is fast.

### It supports several career paths

C++ skills are useful in industries such as games, simulation, robotics, embedded systems, finance, desktop software, and infrastructure engineering. Demand and compensation vary by location, industry, and experience.

## Modern C++ and the C++ Standard

C++ is defined by an international ISO standard. "Modern C++" usually refers to C++11 and later standards, which introduced features such as smart pointers, move semantics, range-based loops, lambdas, and improved concurrency support.

A compiler implements a particular version of the standard. Support can vary, so a project selects a language mode such as C++17, C++20, or C++23 and uses features supported by its toolchain.

> [!NOTE]
> **How the sausage is made: the language is not the compiler**
>
> The ISO standard describes how valid C++ programs should behave. MSVC, GCC, and Clang are separate compiler implementations of that specification. Visual Studio is an IDE that can invoke the MSVC toolchain; it is not itself the C++ language or compiler.

## Source and Header Files

C++ projects commonly contain these files:

- **Source files** (`.cpp`) contain definitions and executable code. Each source file is normally compiled separately.
- **Header files** (`.h` or `.hpp`) share declarations, type definitions, templates, and inline definitions between source files.

The language does not assign different meanings to `.h` and `.hpp`. Teams choose one extension according to convention. A `.hpp` extension often signals that a header contains C++ rather than C declarations, but the compiler does not gain extra C++ behavior from the extension alone.

> [!NOTE]
> **How the sausage is made: `#include` is mostly textual inclusion**
>
> Before normal compilation, the preprocessor handles directives such as `#include`. It effectively inserts the selected header's contents into the source file. The resulting source is called a **translation unit**. Header guards or `#pragma once` prevent the same header from being included repeatedly within one translation unit.

## The C++ Build Process

A typical build has three conceptual stages:

1. **Preprocessing:** Expands directives such as `#include`, `#define`, and conditional-compilation blocks.
2. **Compilation:** Parses and type-checks each translation unit, optimizes it, and generates an object file. Windows toolchains commonly use `.obj`; Unix-like toolchains commonly use `.o`.
3. **Linking:** Combines object files with required libraries, resolves references between them, and produces an executable or library.

```text
File1.cpp + headers --> compiler --> File1.obj --\
File2.cpp + headers --> compiler --> File2.obj ----> linker + libraries --> program.exe
main.cpp  + headers --> compiler --> main.obj  --/
```

Object files contain machine code plus metadata that the linker still needs. They are normally platform-, architecture-, and build-configuration-specific, so an object file built for one target cannot be assumed to work on another.

The linker can produce several kinds of output, including:

- an executable such as `.exe` on Windows;
- a shared library such as `.dll`, `.so`, or `.dylib`; or
- a static library such as `.lib` or `.a`.

> [!NOTE]
> **How the sausage is made: declarations connect separate files**
>
> A declaration tells the compiler that a name and type exist. A definition supplies the function body or storage. This lets one source file compile a call to a function defined in another source file. The linker later matches the call's unresolved symbol to that definition. If it cannot find exactly one valid definition, the build fails at the linking stage.

## Testing and Debugging

- **Testing** checks whether the program behaves as expected for selected inputs and conditions.
- **Debugging** investigates why actual behavior differs from expected behavior.
- Compiler diagnostics, static analysis, sanitizers, automated tests, and an interactive debugger catch different classes of problems; no single tool proves that a non-trivial program is correct.

## Integrated Development Environments

An integrated development environment (IDE) brings common development tools into one interface. It usually provides:

- a source-code editor;
- project and build configuration;
- compiler and linker integration;
- a debugger;
- code navigation, completion, and analysis; and
- test and version-control integration.

The course uses CodeLite, while these notes use Visual Studio 2026 on Windows.

- **CodeLite** is a lightweight, cross-platform IDE available for Windows, Linux, and macOS.
- **Visual Studio** provides deeper integration with Microsoft's Windows development tools, including MSVC, MSBuild, profiling, and debugging. The full Visual Studio IDE is Windows-only; Visual Studio for Mac was retired in 2024.

> [!NOTE]
> **How the sausage is made: the IDE coordinates other tools**
>
> When Visual Studio builds a C++ project, its project system and MSBuild determine what is out of date, then invoke tools such as the MSVC compiler and linker with the configured options. The IDE presents their diagnostics in one place, but those command-line tools perform the actual build.
