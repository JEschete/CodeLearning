"""
Dictionaries in Python
"""

# Dictionaries in python will always have a key and a value. The key is the name of the item, and the value is the data associated with that item.
user_dictionary = {
    'username': 'codingwithJude',
    'name': 'Jude',
    'age': 35,
}

print(user_dictionary)

#if we want to access a specific value in the dictionary, we can use the key to access it. For example, if we want to access the username, we can do the following:
print(user_dictionary.get('username'))

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

for x in user_dictionary.items():
    print(x)
    # which will only print the keys of the dictionary. If we want to print the values as well, we can do the following:

for x, y in user_dictionary.items():
    print(x, y)
    # which will print both the keys and values of the dictionary.

# When you want to copy a dictionary, a little more is needed
user_dictionary_2 = user_dictionary
user_dictionary_2.pop('age')
print(user_dictionary)

# The above code will remove the 'age' key from the user_dictionary as well, because user_dictionary_2 is just a reference to the user_dictionary. 
# If we want to copy the dictionary and not have it be a reference, we can do the following:
user_dictionary['age'] = 35
user_dictionary_2 = user_dictionary.copy()
user_dictionary_2.pop('age')
print(user_dictionary)
print(user_dictionary_2)
