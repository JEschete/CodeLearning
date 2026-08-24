Variables and Data Types
----------------------------------------
What is a variable? 
- A type of container that stores a specific type of data.
- You can think of it as a box with a name that stores information. 
- These are not the definitions in a purely computer science context.
- In programming, variables are used to store data that can be manipulated and retrieved throughout the program.
- They are more accurately labels on a specific location in memory where the data is stored.

A note on initialization (important):
- C++ does NOT give local variables a default value. A local built-in type starts out holding whatever
  garbage was already in that memory, and reading it is undefined behavior.
- The "Zero value" listed for each type below is what you get when you explicitly value-initialize
  (int x{};) or when the variable has static storage duration (globals, static locals).
- It is NOT what you get from "int x;" inside a function.
    ```cpp
    void Example() {
        int  garbage;       // indeterminate, UB to read
        int  zeroed{};      // 0, value-initialized
        static int global;  // 0, static storage is zero-initialized
    }
    ```
- Unreal makes this easy to get wrong: UPROPERTY members are zeroed for you by the engine's object construction, which builds the false intuition that "variables start at zero." Plain locals do not.

A note on data widths:
- The widths below are for MSVC on Windows x64, which is what Unreal builds with. They are not universal.
- The C++ standard only specifies minimums, so the same type can be a different size on another platform. The long entry below is the type where this bites hardest.

Types of data: 
Basic C++ Data Types: 
- Char
    - Data width: 1 byte (8-bits)
    - Example: 'A'
    - Zero value: '\0'
    - Example usage: char initial = 'A';
    - Used for: storing single characters
    - Common shortcomings: 
        - Limited to storing single characters.
        - Plain char has implementation-defined signedness. It is a distinct type from both signed char and unsigned char, so use those explicitly when you mean a small number rather than a letter.
- bool
    - Data width: 1 byte (sizeof(bool) is implementation-defined, but 1 on every platform you will meet)
    - Example: true
    - Zero value: false
    - Example usage: bool isAlive = true;
    - Used for: storing true/false values
    - Common shortcomings: limited to storing true/false values
- int
    - Data width: 4 bytes (32-bits) (the standard only guarantees 16 bits, but it is 32 everywhere relevant)
    - Example: 42
    - Zero value: 0
    - Example usage: int age = 42;
    - Used for: storing whole numbers
    - Common shortcomings: Signed by default so values range from [-2147483648, 2147483647]. Note [] is inclusive while () is exclusive. 
- float
    - Data width: 4 bytes (32-bits)
    - Example: 3.14f
    - Zero value: 0.0f
    - Example usage: float pi = 3.14f;
    - Used for: storing decimal numbers
    - Common shortcomings: 
        - Limited precision compared to double (roughly 7 significant decimal digits), defined by the
          IEEE 754 standard.
        - Most decimal fractions cannot be represented exactly, so 3.14f does not actually hold 3.14
          (see the worked example below). Never compare floats with ==; compare against an epsilon.
    - A float in binary:
        - First bit: sign bit (0 for positive, 1 for negative)
        - Next 8 bits: exponent (stored with a bias of 127)
        - Remaining 23 bits: mantissa (fractional part)
        - Example: 3.14f = 0 10000000 10010001111010111000011
            - first bit is 0, so the value is positive
            - next 8 bits are: 10000000 so the exponent is 128 - 127 = 1
            - The next 23 bits are: 10010001111010111000011 so the mantissa is 1.10010001111010111000011 (implicit leading 1)
            - To calculate the fractional part: 
                - Take each bit of the mantissa (after the leading 1) and multiply it by 2 raised to the negative power of its position.
                - Example: 0.10010001111010111000011 = 1*(2^-1) + 0*(2^-2) + 0*(2^-3) + 1*(2^-4) + 0*(2^-5) + 0*(2^-6) + 0*(2^-7) + 1*(2^-8) + 1*(2^-9) + 1*(2^-10) + 1*(2^-11) + 0*(2^-12) + 1*(2^-13) + 0*(2^-14) + 1*(2^-15) + 1*(2^-16) + 1*(2^-17) + 0*(2^-18) + 0*(2^-19) + 0*(2^-20) + 0*(2^-21) + 1*(2^-22) + 1*(2^-23)
            - Final value: 1.10010001111010111000011 * 2^1 = 3.1400001049041748046875
            - Note this is NOT exactly 3.14. The nearest float to 3.14 sits slightly above it, and that
              gap is the whole reason floating point comparisons need a tolerance.
                
- double
    - Data width: 8 bytes (64-bits)
    - Example: 3.141592653589793
    - Zero value: 0.0
    - Example usage: double pi = 3.141592653589793;
    - Used for: storing decimal numbers with higher precision than float (roughly 15-17 significant decimal digits)
    - Common shortcomings: 
        - Still cannot represent most decimal fractions exactly, defined by the IEEE 754 standard. It is
          more precise than float, not exact.
        - Twice the memory and bandwidth of a float, which matters once you are storing millions of them.
    - A double in binary: 
        - First bit: sign bit (0 for positive, 1 for negative)
        - Next 11 bits: exponent (stored with a bias of 1023)
        - Remaining 52 bits: mantissa (fractional part)
        - Example: 3.141592653589793 = 0 10000000000 1001001000011111101101010100010001000010110100011000
            - first bit is 0, so the value is positive
            - next 11 bits are: 10000000000 so the exponent is 1024 - 1023 = 1
            - The next 52 bits are: 1001001000011111101101010100010001000010110100011000 so the mantissa is 1.1001001000011111101101010100010001000010110100011000 (implicit leading 1)
            - To calculate the fractional part: 
                - Take each bit of the mantissa (after the leading 1) and multiply it by 2 raised to the negative power of its position.
                - Example: 0.1001001000011111101101010100010001000010110100011000 = 1*(2^-1) + 0*(2^-2) + 0*(2^-3) + 1*(2^-4) + 0*(2^-5) + 0*(2^-6) + 1*(2^-7) + 0*(2^-8) + 0*(2^-9) + 0*(2^-10) + 0*(2^-11) + 1*(2^-12) + 1*(2^-13) + 1*(2^-14) + 1*(2^-15) + 1*(2^-16) + 1*(2^-17) + 0*(2^-18) + 1*(2^-19) + 1*(2^-20) + 0*(2^-21) + 1*(2^-22) + 0*(2^-23) + 1*(2^-24) + 0*(2^-25) + 1*(2^-26) + 0*(2^-27) + 0*(2^-28) + 0*(2^-29) + 1*(2^-30) + 0*(2^-31) + 0*(2^-32) + 0*(2^-33) + 1*(2^-34) + 0*(2^-35) + 0*(2^-36) + 0*(2^-37) + 0*(2^-38) + 1*(2^-39) + 0*(2^-40) + 1*(2^-41) + 1*(2^-42) + 0*(2^-43) + 1*(2^-44) + 0*(2^-45) + 0*(2^-46) + 0*(2^-47) + 1*(2^-48) + 1*(2^-49) + 0*(2^-50) + 0*(2^-51) + 0*(2^-52)
            - Final value: 1.1001001000011111101101010100010001000010110100011000 * 2^1 = 3.14159265358979311599796346854...
            - Same story as the float: this is the nearest double to pi, not pi itself.

Other Data types: 
- String
    - Data width: varies (depends on the implementation)
        - C-Style Strings: An array of chars, terminated by a '\0'
        - std::string: A sequence of characters managed by the C++ Standard Library
    - Example: "My name is Jude"
    - Zero value: ""
    - Example usage: std::string name = "My name is Jude";
    - Used for: storing sequences of characters (text)
    - Common shortcomings: 
        - C-Style Strings: fixed size, manual memory management, no bounds checking.
        - The classic broken example, which packs two SEPARATE bugs that are easy to confuse:
        ```cpp
        const char* printMessage(const char* message) {
            char string_buffer[32];
            strcpy(string_buffer, message);  // Bug 1: buffer overflow
            return string_buffer;            // Bug 2: dangling pointer
        }
        ``` 
        - Then you do something like: 
        ```cpp
        // 131 characters, so 132 bytes once you count the '\0'
        char test_message[] = "This is a longer string, I wonder what would happen if we passed the test message to the printMessage function, could it handle it?";

        printMessage(test_message);
        ```
        - Bug 1, buffer overflow: string_buffer holds 32 chars, but strcpy has no idea how big the
          destination is. It copies all 132 bytes, writing 100 bytes past the end of the buffer and
          stomping on whatever happened to be next on the stack. This is the bug that gets weaponized
          into exploits.
        - Bug 2, dangling pointer: string_buffer lives in the stack frame of printMessage. That frame is
          gone the moment the function returns, so the returned pointer aims at memory that is no longer
          yours. This one happens regardless of size. Even a message that fits comfortably in 32 chars
          still returns garbage.
        - Both are undefined behavior, which is worse than a crash. The code may appear to work fine
          right up until it doesn't. GCC will at least warn on the second one:
          "warning: address of local variable 'string_buffer' returned [-Wreturn-local-addr]"
        - Worth noting: a signature like "char[32] printMessage(...)" does not even compile. C++ does not
          let you return a raw array from a function at all, and you cannot initialize an array from a
          pointer either ("char string_buffer[32] = message;"). Those are syntax errors, a separate
          category from the two runtime bugs above.
        - The fix is to let the standard library own the memory:
        ```cpp
        std::string printMessage(const std::string& message) {
            return message;  // sizes itself, frees itself, copies out safely
        }
        ```
        - std::string: may have performance overhead compared to C-Style Strings (a heap allocation for
          longer strings, though short ones usually fit inline thanks to small-string optimization).
        
- long
    - Data width: 4 bytes (32-bits) on Windows. THIS IS THE BIG PLATFORM TRAP.
        - Windows uses the LLP64 model: only long long and pointers widen to 64 bits, long stays at 32.
        - Linux and macOS use LP64, where long IS 8 bytes. That is where the "long is 64-bit" idea comes from.
        - The standard only guarantees long is at least 32 bits. Verified on this machine:
          char=1 bool=1 int=4 long=4 longlong=8 float=4 double=8
    - Example: 1234567890L
    - Zero value: 0L
    - Example usage: long bigNumber = 1234567890L;
    - Used for: storing whole numbers, historically "bigger than an int"
    - Common shortcomings: 
        - The size changes between platforms, so code assuming 64 bits silently wraps on Windows the
          moment you pass 2147483647.
        - Use long long (guaranteed at least 64 bits) if you actually need the range. Better still, in
          Unreal use the fixed-width aliases int32 / int64 / uint8, which are the same size everywhere.
          This is exactly why Epic's coding standard tells you to avoid bare int and long.
- long double
    - Data width: 8 bytes on MSVC, where it is just an alias for double and buys you NO extra precision.
        - On GCC/Clang for x86 it is the 80-bit x87 format, padded out to 16 bytes. That is where the
          "16 bytes" figure comes from.
        - Since Unreal builds with MSVC on Windows, treat this type as offering nothing over double.
    - Example: 3.141592653589793238L
    - Zero value: 0.0L
    - Example usage: long double pi = 3.141592653589793238L;
    - Used for: nothing you need in Unreal. Listed here for completeness.

- FString
    - Unreal Engine's string class.
    - Data width: variable, managed by Unreal's memory allocator.
    - Example: FString message = TEXT("Hello, Unreal!");
    - Zero value: FString();
    - Used for: storing and manipulating text in Unreal Engine.
    - Common shortcomings:
        - Not compatible with standard C++ string functions.
        - Requires conversion to std::string or const char* for interoperability with standard C++ libraries.

A note on
```cpp
    std::string printMessage(const std::string& message) {
    return message;  // sizes itself, frees itself, copies out safely
    }
```

We have not covered the standard library yet, so the above broken down: 
std:: is a namespace in the C++ standard library. It contains all the standard library classes and functions, such as std::string, std::vector, std::cout, and many others. The double colon (::) is the scope resolution operator, which is used to access members of a namespace.

We can add a using directive to avoid typing std:: repeatedly:
```cpp
using namespace std;
```

Next printMessage is the function name, and inside of the () are its parameters. In this case, it takes a single parameter named message of type const std::string&. The const keyword indicates that the function will not modify the argument, and the & symbol denotes that it is passed by reference, avoiding a copy.

Pass by reference vs pass by value:
- Pass by reference (const std::string& message) avoids copying the argument, which can be more efficient for large objects.
- Pass by value (std::string message) makes a copy of the argument, which can be less efficient but allows the function to modify the copy without affecting the original.

Case conventions: 
- camelCase: Used for variables and function names (e.g., myVariable, printMessage).
- PascalCase: Used for class names and other types (e.g., MyClass, FString).
- snake_case: Used for variables and function names, typically in C-style code (e.g., my_variable, print_message).
- UPPER_SNAKE_CASE: Used for constants (e.g., MY_CONSTANT).
- kebab-case: Used for file names and URLs (e.g., my-file-name, print-message).

The next video had me remove the following from our .cpp file, so I'm putting it here for posterity. 

```cpp
	/*The video tells us to do a int MyInt; I wrote int32
    MyInt; because int32 is the Unreal Engine type for an
    integer. If we left it as int32 MyInt; it would have no
	value and contain garbage data. */
    int32 MyInt = 100;  
	MyInt = 50;

	bool MyBool = true;  // Can also be set to false, that's it. 

	float MyFloat = 3.14f;
    char MyChar = 'A'; // We DO NOT use double quotes for a char, only single quotes.

	FString MyString = "Hello, Unreal!";  // FString is the Unreal Engine string type.
```