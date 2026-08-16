"""
String Formatting in Python
"""

first_name = "Jude"
print("Hi " + first_name)

# An f-string evaluates expressions inside curly braces. It is usually clearer
# than joining several values with +.
print(f"Hi {first_name}")

# The string's .format() method fills placeholders from left to right.
sentence = "Hi {} {}"
last_name = "Eschete"
print(sentence.format(first_name, last_name))