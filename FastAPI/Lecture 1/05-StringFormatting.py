"""
String Formatting in Python
"""

first_name = "Jude" 
print("Hi " + first_name)

# We can also use f-formatting to make the code more readable and easier to understand.
# The f before the string indicates that it is an f-string, which allows for the use of variables inside the string. The variable first_name is enclosed in curly braces, which tells Python to replace it with its value when the string is printed.
print(f"Hi {first_name}") 

 # The format() method is used to replace the curly braces in the string with the value of the variable first_name. This is another way to format strings in Python.
sentence = "Hi {} {}"
last_name = "Eschete"
print(sentence.format(first_name, last_name))