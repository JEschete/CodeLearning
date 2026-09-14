# Installation and Setup

## Tool Choice

The course demonstrates C++ with CodeLite. These notes use Visual Studio 2026 on Windows instead. The C++ concepts are the same, but project creation, build commands, and debugger controls may appear in different places.

Visual Studio is a good fit here because it integrates the Microsoft C++ (MSVC) toolchain, MSBuild, a debugger, code analysis, and profiling tools. CodeLite remains a valid lighter-weight, cross-platform option.

## Install Visual Studio for C++

1. Visit the [Visual Studio website](https://visualstudio.microsoft.com/).
2. Download the appropriate edition: Community, Professional, or Enterprise.
3. Run the Visual Studio Installer.
4. Select the **Desktop development with C++** workload.
5. Keep the recommended MSVC build tools and Windows SDK components selected. Add **C++ CMake tools for Windows** if you plan to use CMake projects.
6. Complete the installation and restart Windows if the installer requests it.
7. Launch Visual Studio and sign in if prompted.

> [!NOTE]
> **How the sausage is made: an IDE is only part of the installation**
>
> The editor displays and organizes the code, but a native C++ build also needs a compiler, linker, standard-library implementation, and platform headers and libraries. The **Desktop development with C++** workload installs a compatible set of these components. Installing only the Visual Studio shell can leave the IDE without a usable C++ toolchain.

## Create a Console Project

For a new beginner project:

1. Select **Create a new project** on the start window.
2. Filter by **C++**, choose **Console App**, and select **Next**.
3. Enter the project name and location, then select **Create**.
4. Edit the generated `.cpp` source file.

A Console App template supplies a project configuration and a small `main` function. An **Empty Project** supplies the configuration without generating starter source code.

## Add Existing Source Files to a Project

To place an existing `.cpp` file in a new Visual Studio project:

1. Select **File > New > Project** and create an **Empty Project**.
2. In Solution Explorer, right-click **Source Files** and select **Add > Existing Item**.
3. Select the existing `.cpp` file.
4. Add any project headers under **Header Files** in the same way, if desired.

To create a file from Visual Studio, right-click the appropriate project filter and select **Add > New Item**, then choose **C++ File (`.cpp`)** or **Header File (`.h`)**.

The **Source Files** and **Header Files** nodes are usually filters used to organize the Solution Explorer display; they do not have to match physical folders on disk.

> [!NOTE]
> **How the sausage is made: solution and project files are build metadata**
>
> A `.sln` file groups one or more projects. A C++ `.vcxproj` file records source items, compiler options, linker options, target platforms, and build configurations for one project. Neither file contains the C++ program itself, but Visual Studio uses them to decide how to build that program.

## Open Existing Work

- To open an existing Visual Studio build, select **Open a project or solution** and choose its `.sln` or `.vcxproj` file.
- To browse loose files, select **Open a local folder**. Opening a folder does not automatically create an MSBuild C++ project.
- Folder View can provide build commands when the folder contains a supported build configuration, such as a `CMakeLists.txt` file. Otherwise, create a project or configure an external build system.

## Select a Build Configuration

The toolbar normally provides two important selectors:

- **Debug** or **Release:** Debug favors diagnostics and debugging; Release normally enables more optimization.
- **x64**, **x86**, or another platform: this selects the target architecture and associated settings.

These combinations have separate output and intermediate files. Building `Debug|x64` does not also build `Release|x64`.

> [!NOTE]
> **How the sausage is made: Debug and Release can behave differently**
>
> Optimization changes how the compiler transforms code, while debug information changes what the debugger can show. Correct programs should preserve their observable behavior in either configuration, but undefined behavior and timing-dependent bugs may appear differently when optimization or memory layout changes.

## Verify the Installation

Build and run this small program in a Console App project:

```cpp
#include <iostream>

int main() {
	std::cout << "Hello, C++!\n";
	return 0;
}
```

1. Build with **Build > Build Solution** or `Ctrl+Shift+B`.
2. Run without the debugger with `Ctrl+F5`, or start debugging with `F5`.
3. Confirm that the console prints `Hello, C++!` and that the build reports success.

## Common Setup Problems

- **No C++ templates or compiler:** Open Visual Studio Installer, select **Modify**, and add the **Desktop development with C++** workload.
- **Build command unavailable in Folder View:** Open a solution/project or add a supported folder-based build configuration such as CMake.
- **Source file is not compiled:** Confirm that the `.cpp` file belongs to the project and is not marked **Excluded From Build** for the active configuration.
- **The wrong program starts:** In a multi-project solution, right-click the intended project and select **Set as Startup Project**.

