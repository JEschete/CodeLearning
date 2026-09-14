# Curriculum Overview

The course progresses from building a small program to managing resources and using the C++ standard library.

1. **Getting Started:** Edit, build, run, and diagnose a basic console program.
2. **Structure of a C++ Program:** Learn about headers, declarations, definitions, the `main` function, and source-file organization.
3. **Variables and Constants:** Work with fundamental types, initialization, scope, and values that should not change.
4. **Arrays and Vectors:** Store sequences in fixed-size arrays and dynamically sized `std::vector` containers.
5. **Strings in C++:** Compare C-style character arrays with the safer and more convenient `std::string` type.
6. **Expressions, Statements, and Operators:** Understand how values are computed and how expressions form program statements.
7. **Control Flow:** Select and repeat work with conditions, loops, and branching statements.
8. **Functions:** Divide a program into reusable operations with parameters, return values, and suitable interfaces.
9. **Pointers and References:** Refer to existing objects, work with addresses, and understand object lifetime and indirection.
10. **Object-Oriented Programming:** Define classes that combine state, behavior, and invariants, then create objects from them.
11. **Operator Overloading:** Give user-defined types meaningful behavior with existing C++ operator syntax.
12. **Inheritance:** Derive a class from another class when the types have a genuine substitutable relationship.
13. **Polymorphism:** Use virtual functions and base-class interfaces to select behavior at runtime.
14. **Smart Pointers:** Represent ownership with RAII types such as `std::unique_ptr` and `std::shared_ptr`.
15. **The Standard Template Library (STL):** Use generic containers, iterators, algorithms, and related utilities from the standard library.
16. **I/O Streams:** Read and write formatted or unformatted data through console, file, and string streams.
17. **Exception Handling:** Report and handle exceptional failures while preserving resource safety.
18. **Lambda Expressions:** Define small function objects near the code that uses them, often for algorithms and callbacks.
19. **Enumerations:** Model a fixed set of named values, preferably with scoped `enum class` types when appropriate.

> [!NOTE]
> **How the sausage is made: the order follows dependencies**
>
> Expressions and control flow operate on values; functions organize those operations; classes organize related values and functions; pointers and references make identity and lifetime explicit; and smart pointers automate common ownership rules. The standard library then combines these ideas through templates, iterators, algorithms, and RAII. Later topics are easier when those earlier relationships are solid.

## Concepts to Track Throughout the Course

- **Type:** What operations are valid for a value, and how is it represented?
- **Scope:** Where can a name be used?
- **Lifetime:** When does an object begin and cease to exist?
- **Ownership:** Which part of the program is responsible for releasing a resource?
- **Interface versus implementation:** What must callers know, and what can remain hidden?
- **Compile time versus runtime:** Which decisions and errors occur during the build, and which occur while the program executes?

These recurring questions connect individual language features and make unfamiliar C++ code easier to reason about.

