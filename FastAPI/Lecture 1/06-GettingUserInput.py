"""
User Input
"""

first_name = input("Enter your first name: ") # The input() function is used to get user input from the console. The string inside the parentheses is displayed as a prompt to the user.
days = input("Enter the number of days before your birthday: ") # The input() function returns a string, so we need to convert it to an integer using the int() function.

"""
To have strings span multiple lines with f-formatting, 
we close the other string and open the new one with the f before the string. 
This allows for better readability and organization of the code.
"""
print(f"Hi {first_name}, only {days} days "
      f"before your birthday!") 