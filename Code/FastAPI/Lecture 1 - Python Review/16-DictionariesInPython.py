"""
Dictionaries in Python
"""

# A dictionary maps unique keys to values. Keys must be hashable, while values
# can be any type and do not need to be unique.
user_dictionary = {
    'username': 'codingwithJude',
    'name': 'Jude',
    'age': 35,
}

print(user_dictionary)

# Bracket lookup raises KeyError if the key is missing.
print(user_dictionary['username'])

# .get() returns None for a missing key, or a supplied default value.
print(user_dictionary.get('username'))
print(user_dictionary.get('location', 'Not provided'))

# we can add to a dictionary by using the key and assigning a value to it. For example, if we want to add a new key called 'married' and assign it a value of True, we can do the following:
user_dictionary['married'] = True
print(user_dictionary)

# We can also check the length of a dictionary by using the len() function. For example, if we want to check how many items are in the user_dictionary, we can do the following:
print(len(user_dictionary))

# We can remove keys from a dictionary by using the pop() method. For example, if we want to remove the 'age' key from the user_dictionary, we can do the following:
user_dictionary.pop('age')
print(user_dictionary)

# we can clear all items from a dictionary by using the clear() method. For example, if we want to clear all items from the user_dictionary, we can do the following:
user_dictionary.clear()
print(user_dictionary)

# We can also use the del keyword to delete a dictionary entirely. For example, if we want to delete the user_dictionary, we can do the following:
del user_dictionary

# You can also loop through a dictionary using a for loop. For example, if we want to loop through the user_dictionary and print out each key and value, we can do the following:
user_dictionary = {
    'username': 'codingwithJude',
    'name': 'Jude',
    'age': 35,
}

# .items() produces one (key, value) tuple per dictionary entry.
for item in user_dictionary.items():
    print(item)

# Unpacking each tuple gives the key and value separate names.
for key, value in user_dictionary.items():
    print(key, value)

# Assignment creates a second name for the same dictionary object.
user_dictionary_2 = user_dictionary
user_dictionary_2.pop('age')
print(user_dictionary)

# Removing through either name changes that one shared object.
user_dictionary['age'] = 35
user_dictionary_2 = user_dictionary.copy()
user_dictionary_2.pop('age')
print(user_dictionary)
print(user_dictionary_2)

# .copy() creates a shallow copy: top-level changes are independent, but nested
# mutable values would still be shared between these dictionaries.
