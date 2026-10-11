# What is an Array and a Vector?

## Arrays

An array is a compound data type or data structure.
It is a collection of elements of the same type.
Each element can be accessed directly.

Why do we need arrays?

```cpp
int test_score_1 {0};
int test_score_2 {0};
int test_score_3 {0};
int test_score_4 {0};
int test_score_5 {0};
```

The above is unwieldy and not scalable.

Instead, we can use an array to store the test scores:

```cpp
int test_scores[5] {0};
```

Characteristics

- Fixed Size
- Elements are all the same type
- Stored contiguously in memory
- Individual elements can be accessed by their position or index.
- First element is at index 0
- Last element is at index size - 1
- Arrays do not check to see if you are out of bounds.
- Arrays should always be initialized.
- Arrays are very efficient.
- Iteration(looping) is often used to process.

## Declaring and initializing Arrays

Declaring and Initializing
Element_Type array_name [constant number of elements];

```cpp
int test_scores [5];

int high_score_per_level [10];
const int days_in_year {365};
double hi_temperature_per_day [days_in_year];
```

Above are examples of declaring and initializing arrays in C++.
The size of the array must be a constant expression, and it is recommended to initialize arrays to avoid undefined behavior.
All three above have not been explicitly initialized with values.

The above is also using the built in array type in C++.

In modern C++, it is often recommended to use `std::array` or `std::vector` for better safety and flexibility.

```cpp
#include <array>
#include <vector>

using namespace std;

array<int, 5> nums{};
vector<int> test_scores_vector (5, 0);
```

Now we have access to the methods provided by `std::array` and `std::vector` such as `size()`, `at()`, `front()`, `back()`, and more.

To initialize the built in:
Element_Type array_name [constant number of elements] {initial values};

```cpp
int test_scores[5] {90, 85, 78, 92, 88}; // all values initialized
int high_score_per_level[10] {3,5}; // first two values initialized, rest are 0
const double days_in_year {365};
double hi_temperature_per_day[days_in_year] {0}; // all values initialized to 0.0

int another_array [] {1, 2, 3, 4, 5}; // Here the size of the array is deduced from the number of initial values provided.
```

## Accessing an Array

To access elements in an array, you use the index of the element you want to access. The index starts at 0 for the first element.
array_name [element_index]

Changing element values is the same as accessing them:
array_name [element_index] = new_value;

### Example

```cpp
int test_scores[5] {90, 85, 78, 92, 88};
test_scores[0] = 95; // changing the first element
test_scores[4] = 90; // changing the last element
```

How does it work?

- The name of the array represents the location of the first element in the array (index 0).
- The [index] represents the offset from the beginning of the array.
- C++ simply performs a calculation to find the correct element.
- Remember there is no bounds checking, so accessing an index outside the array's range leads to undefined behavior.

## Multi-dimensional Arrays

`Element_Type array_name [dim1_size][dim2_size];`

```cpp
    int movie_rating [3][4]; // contains garbage data
```

## Declaring and Initializing Vectors

Suppose we want to store test scores for my school.
I have no way of knowing how many students will register next year.
Options:

- Pick a size that you are not likely to exceed and use static arrays.
- Use a dynamic array such as a vector.

### What is a Vector?

- Container in the C++ Standard Template Library
- An array that can grow and shrink in size at execution time.
- Provides similar semantics and syntax as arrays
- Very efficient
- Can provide bounds checking with the `at()` method.
- Can use lots of cool functions like sort, reverse, and find from the C++ Standard Library.

To declare:

```cpp
    #include <vector>
    using namespace std;

    vector<char> vowels;
    vector<int> test_scores;
```

### Characteristics of Vectors

- Dynamic size
- Elements are all the same type
- Stored contiguously in memory
- Individual elements can be accessed by their position or index
- First element is at index 0
- Last element is at index size() - 1
- [] - no checking to see if you are out of bounds
- Provides many useful functions that do bounds checks.
- Elements are initialized to default values when the vector is created.
- Very efficient
- iteration (looping) is often used to process.

## Accessing and Modifying Vector Elements

Accessing vector elements - array syntax
vector_name [element_index]
test_scores[1]

```cpp
vector <int> test_scores {100,95,99,87,88};

cout << "First score at index 0: " << test_scores[0] << endl;
cout << "Second score at index 1: " << test_scores[1] << endl;
cout << "Last score at index 4: " << test_scores[4] << endl;
```

Accessing vector elements - vector syntax
vector_name.at(element_index)
test_scores.at(1)

```cpp
vector <int> test_scores {100,95,99,87,88};

cout << "First score at index 0: " << test_scores.at(0) << endl;
cout << "Second score at index 1: " << test_scores.at(1) << endl;
cout << "Last score at index 4: " << test_scores.at(4) << endl;
```

Changing the contents of vector elements - vector syntax

vector_name.at(element_index) = new_value;

```cpp
vector <int> test_scores {100,95,99,87,88};

cin >> test_scores.at(0);
cin >> test_scores.at(1);
cin >> test_scores.at(2);
cin >> test_scores.at(3);
cin >> test_scores.at(4);

test_scores.at(0) = 90;
```

So, when do vectors grow as needed?
vector_name.push_back(element);

```cpp
vector <int> test_scores {100,95,99,87,88};
test_scores.push_back(77); // adds 77 to the end of the vector
```

What if you are out of bounds?

- Arrays never do bounds checking.
- Many vector methods provide bounds checking.
- An exception and error message is generated.
