"""
Functions in Python
"""

def my_function(): # Inside the parentheses, we can put parameters that we want to pass into the function. 
    print("Hello from my_function!")

# If we run the script, nothing will happen because we have not called the function yet.

my_function() # This will call the function and print "Hello from my_function!"

def print_my_name(name): # This function takes in a parameter called name, and will print it out.
    print(f"My name is {name}.")

print_my_name("Jude") # This will call the function and print "My name is Jude."

# we can have more than one parameter in a function, and we can also have default values for parameters.
def print_my_name_and_age(first_name, last_name): # This function takes in two parameters, name and age, and will print them out. 
    print(f"My name is {first_name} {last_name}.")

print_my_name_and_age("Jude", "Eschete") # This will call the function and print "My name is Jude and I am 36 years old."

# Functions can have variables that live within them, this introduces the concept of scope. 
# Variables that are defined within a function are only accessible within that function, and cannot be accessed outside of it.
# These are known as local variables, and they are created when the function is called, and destroyed when the function is finished executing.
# Variables outside of a function are known as global variables, and they can be accessed from anywhere in the code.

def print_color_red():
    color = "red" # This is a local variable, and can only be accessed within this function.
    print(f"My favorite color is {color}.")

color = "blue" # This is a global variable, and can be accessed from anywhere in the code.
print(color) # This will print "blue"
print_color_red() # This will print "My favorite color is red."

def print_numbers(highest_number, lowest_number):
    print(highest_number)
    print(lowest_number)

print_numbers(10, 3) # This will print "10" and "3"
# However if we do: 
print_numbers(3, 10) # This will print "3" and "10" because the order of the parameters matters. This can be confusing, so we can use keyword arguments to specify which parameter we are passing in.
print_numbers(lowest_number=3, highest_number=10) # This will print "10" and "3" because we are specifying which parameter we are passing in. This is known as keyword arguments, and it can make our code more readable.

def multiply_numbers(a, b):
    return a * b

result = multiply_numbers(3, 4) # This will return 12, and we can store it in a variable.
print(result) # This will print "12"

def print_list(list_of_numbers):
    for x in list_of_numbers:
        print(x)

numbers_list = [1, 2, 3, 4, 5]
print_list(numbers_list) # This will print "1", "2", "3", "4", "5" because we are passing in a list of numbers to the function, and the function is iterating through the list and printing each number.

def buy_item(cost_of_item):
    return cost_of_item + add_tax_to_item(cost_of_item) # This will return the cost of the item plus the tax, and we can store it in a variable.

def add_tax_to_item(cost_of_item):
    current_tax_rate = 0.03
    return cost_of_item * current_tax_rate # This will calculate the tax on the item, and return it.

final_cost = buy_item(50) # This will return 51.5, and we can store it in a variable.
print(f"${final_cost}")
