"""
Booleans and Operators
"""

like_coffee = True
like_tea = False
favorite_food = "Pizza"
favorite_number = 32

print(type(like_coffee))
print(type(favorite_food))
print(type(favorite_number))

# Comparison operators evaluate expressions and produce Boolean values.
# A single = assigns a value; == checks whether two values are equal.
print(1 == 2)  # False
print(1 != 2)  # True
print(1 > 2)  # False
print(1 < 2)  # True
print(1 >= 1)  # True
print(1 <= 2)  # True

# Logical operators combine or reverse Boolean expressions.
print(1 > 3 and 5 < 7)  # False: both expressions must be True.
print(1 > 3 or 5 < 7)  # True: at least one expression is True.
print(not (1 == 1))  # False: not reverses True to False.