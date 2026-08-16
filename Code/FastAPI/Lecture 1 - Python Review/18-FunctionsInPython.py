"""
Functions in Python
"""


def my_function():  # Parameters would go inside the parentheses.
    print("Hello from my_function!")

# If we run the script, nothing will happen because we have not called the function yet.

my_function()  # Calls the function and prints "Hello from my_function!"


def print_my_name(name):
    print(f"My name is {name}.")


print_my_name("Jude")  # The string "Jude" is the argument for name.


# A function can have more than one parameter.
def print_full_name(first_name, last_name):
    print(f"My name is {first_name} {last_name}.")


print_full_name("Jude", "Eschete")  # Prints "My name is Jude Eschete."


# A name assigned inside a function is normally local to that function call.
# A global name can be read inside a function, but assigning that name inside the
# function creates a local name unless the global keyword is used.

def print_color_red():
    color = "red"  # This local variable is separate from the global color below.
    print(f"My favorite color is {color}.")


color = "blue"
print(color)  # Prints "blue".
print_color_red()  # Prints "My favorite color is red."


def print_numbers(highest_number, lowest_number):
    print(highest_number)
    print(lowest_number)


print_numbers(10, 3)
# Positional arguments are assigned by order; names do not enforce their meaning.
print_numbers(3, 10)
# Keyword arguments explicitly select parameters, so their call order can vary.
print_numbers(lowest_number=3, highest_number=10)


def multiply_numbers(first_number, second_number):
    return first_number * second_number


result = multiply_numbers(3, 4)
print(result)  # Prints 12.


def print_list(list_of_numbers):
    for number in list_of_numbers:
        print(number)


numbers_list = [1, 2, 3, 4, 5]
print_list(numbers_list)


def add_tax_to_item(cost_of_item):
    tax_rate = 0.03
    return cost_of_item * tax_rate


def buy_item(cost_of_item):
    return cost_of_item + add_tax_to_item(cost_of_item)


final_cost = buy_item(50)
print(f"${final_cost:.2f}")
