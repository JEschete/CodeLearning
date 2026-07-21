"""
Sets are similar to lists but are unordered and cannot contain duplications. 
Use curly brackets to create a set.
"""

my_set = {1, 2, 3, 4, 5, 1, 2}
print(my_set) # This will print the set, which is {1, 2, 3, 4, 5}. The duplicate values of 1 and 2 have been removed.
print(len(my_set)) # This will print the length of the set, which is 5. The len() function returns the number of values in a set.

for x in my_set:
    print(x) # This will print each value in the set. The order of the values may vary because sets are unordered.

# Sets are not ordered in memory, and we can't always know the order. 
# We cannot call by index like we can with lists.

my_set.discard(3) 
print(my_set) # This will remove the value 3 from the set. The discard() method is used to remove a specific value from a set.  
my_set.add(42)
print(my_set) # This will add the value 42 to the set. The add() method is used to add values to a set.
my_set.clear()
print(my_set) # This will clear all values from the set, resulting in an empty set
my_set.update([6,7,8,9])
print(my_set) # This will add the values 6, 7, 8, and 9 to the set. The update() method is used to add multiple values to a set.

"""
A Tuple is similar to a list but is immutable, meaning we cannot change its values after it has been created.
Tuples are created using parentheses.
"""

my_tuple = (1, 2, 3, 4, 5)
print(my_tuple) # This will print the tuple
print(len(my_tuple)) # This will print the length of the tuple, which is 5. The len() function returns the number of values in a tuple.
# Tuples can have elements called by index like lists, but they are immutable and cannot be changed after creation.
print(my_tuple[0]) # This will print the first value in the tuple, which is 1. Tuples are zero-indexed, meaning the first value is at index 0, the second value is at index 1, and so on.

# Sets are typically used when you want to store unique values and do not care about the order of the values. They are fast. 
# Tuples are typically used when you want to store a collection of values that should not be changed after creation. They are also fast.

