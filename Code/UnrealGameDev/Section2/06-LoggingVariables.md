Logging Variables
-----------------------------------
In Unreal we have the UE_LOG(), it is not a function but a macro. Macros are different from functions in that they are expanded by the preprocessor before compilation. This means they can do things that functions cannot, such as logging the file name and line number automatically.

```cpp
    int NumberOfApples = 10;
    UE_LOG(LogTemp, Display, TEXT("NumberOfApples: %d"), NumberOfApples);
```

To decompose the above:
    - UE_LOG is the macro name.
    - LogTemp is the log category. Unreal Engine uses log categories to organize log messages.
    - Display is the verbosity level. Other common levels include Warning and Error.
        - Display: logs the message to the output log with normal verbosity.
        - Warning: logs the message to the output log with warning verbosity.
        - Error: logs the message to the output log with error verbosity.
    - TEXT("NumberOfApples: %d") is the format string, similar to printf in C.
    - NumberOfApples is the variable being logged.
    - %d is a format specifier for integers.
    - %f is a format specifier for floating-point numbers.
    - %s is a format specifier for strings.

```cpp
	FString MyName = "Jude Eschete";
    UE_LOG(LogTemp, Display, TEXT("My name is: %s"), *MyName);
```

Above we have to put an * in front of MyName in the UE_LOG() call to get the underlying TCHAR pointer from the FString. This is because UE_LOG expects a C-style string for the %s format specifier, and FString provides the underlying TCHAR pointer when dereferenced with *.
