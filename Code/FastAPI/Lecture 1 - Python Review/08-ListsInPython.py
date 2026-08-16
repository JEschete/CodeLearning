"""
Lists are a collection of data. 
They can store multiple values in a single variable.
"""

my_list = [80, 96, 72, 100, 8]
print(my_list)

people_list = ["Jude", "Brooke", "John", "Jane"]
print(people_list)

print(my_list[0]) # This will print the first value in the list, which is 80. Lists are zero-indexed, meaning the first value is at index 0, the second value is at index 1, and so on.

# print(people_list[4]) # This will throw an error because there is no value at index 4. The last value in the list is at index 3.
print(people_list[-1]) # This will print the last value in the list, which is "Jane". Negative indexing allows us to access values from the end of the list.

people_list[0] = "Jude Eschete" # This will change the value at index 0 from "Jude" to "Jude Eschete". Lists are mutable, meaning we can change their values after they have been created.
print(people_list[0])
print(len(people_list)) # This will print the length of the list, which is 4. The len() function returns the number of values in a list.

"""
 This will print the values at index 0 and 1, which are "Jude Eschete" and "Brooke". 
 The colon indicates a range of values, and the second value is not included in the range. 
 This is known as slicing, and it allows us to access a subset of values in a list.
"""
print(people_list[0:2]) 

print(people_list[2:4]) 

my_list.append(55)
print(my_list) # This will add the value 55 to the end of the list. The append() method is used to add values to a list.
my_list.insert(1, 42)
print(my_list) # This will add the value 42 to the list at index 1. The insert() method is used to add values to a list at a specific index.
my_list.remove(72)
print(my_list) # This will remove the value 72 from the list. The remove() method is used to remove a specific value from a list.
my_list.pop(0)
print(my_list) # This will remove the value at index 0 from the list, which is 80. The pop() method is used to remove values from a list at a specific index.
my_list.sort()
print(my_list) # This will sort the values in the list in ascending order.