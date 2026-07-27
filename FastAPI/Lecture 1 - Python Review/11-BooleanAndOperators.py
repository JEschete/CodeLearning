"""
Boolean and Operators

"""

like_coffee = True
like_tea = False
favorite_food = "Pizza"
favorite_number = 32

print(type(like_coffee))
print(type(favorite_food))
print(type(favorite_number))

# Booleans are used to compare things using the comparison operators. 
print(1 == 2) # Will return False and different than a single =, == is a comparison, does left equal right
print(1 != 2) # Will return True because 1 is not equal to 2
print(1 > 2) # Will return false because 1 is not greater than 2
print(1 < 2) # Will return true
print(1 >= 1) # Will return true
print(1 <= 2) # Will return true

# Logical Operators, Not AND OR
print(1 > 3 and 5 < 7) # and says both conditions must be true, so this will return false. 
print(1 > 3 or 5 < 7) # either condition can be true, this will be true because 5 is less than 7
print(not(1==1)) # not flips the logical evaluation of the statement. 