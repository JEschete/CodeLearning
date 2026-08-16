"""
User Input
"""

first_name = input("Enter your first name: ")  # input() always returns a string.
days = int(input("Enter the number of days before your birthday: "))
# int() converts the entered text to an integer. Non-numeric input raises ValueError.

"""
Adjacent string literals inside parentheses are joined automatically.
Each part needs the f prefix if it contains a value in curly braces.
"""
print(
      f"Hi {first_name}, only {days} days "
      f"before your birthday!"
)