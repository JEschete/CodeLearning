"""
Variables
"""

# Variables give names to values so those values can be reused and updated.
cost = 10  # An integer stores a whole number.
tax_percent = 0.25  # A float can store a number with a decimal point.
tax = cost * tax_percent

price = cost + tax

print(price)  # Displays 12.5, the sum of cost and tax.

username = "CodingwithJude"  # A string is a sequence of characters.
first_name = "Jude"

# Python strings can use single or double quotes. Be consistent within a project.
print(username + " " + first_name)  # + joins, or concatenates, strings.

first_num = 10
second_num = 2
print(first_num)
print(second_num)

first_num = 1
print(first_num)  # first_num was reassigned from 10 to 1.
print(second_num)  # second_num is independent and still stores 2.

first_name = "Brooke"  # Variables that contain strings can also be reassigned.

