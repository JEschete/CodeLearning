"""
For and While loops in Python
"""
my_list = [1, 2, 3, 4, 5]
# We *can* do the following, but it is not the best way to iterate through a list
print(my_list[0])
print(my_list[1])
print(my_list[2])
print(my_list[3])
print(my_list[4])

# Instead, we can use a for loop to iterate through the list
print()
for iterator in my_list:
    print(iterator)

# iterator can be called anything, can be x y or i usually. 

for x in range(3, 6):
    print(x)

sum_of_for_loop = 0
for x in my_list:
    sum_of_for_loop += x
print(f"Sum of for loop: {sum_of_for_loop}")
# the abnove sum will print the sum of all the numbers in the list my_list which should be 15

# The for loop after this operates on a list of strings, and prints out each string with the word "Happy" in front of it.
my_list_2 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for x in my_list_2:
    print(f"Happy {x}!")

i = 0
while i < 5:
    i += 1
    print(i)
# The above while loop will print the numbers 1 through 5, because it starts with i = 0, and then increments i by 1 each time through the loop, until i is no longer less than 5.
# If we did not increment i, the while loop would run forever, because i would always be less than 5. This is called an infinite loop, and it is something we want to avoid in our code.

# The following code demonstrates the use of the continue statement in a while loop. 
# The continue statement will skip the rest of the code in the loop for the current iteration, and move on to the next iteration of the loop. 
i = 0
while i < 5:
    i += 1
    if i == 3:
        continue
    print(i)
else: 
    print("i is now larger or equal to 5, so the while loop has ended.")

# The following code demonstrates the use of the break statement in a while loop.
# A break statement will exit the loop entirely, and move on to the next line of code after the loop.
i = 0
while i < 5:
    i += 1
    if i == 3:
        continue
    print(i)
    if i == 4:
        break
else: 
    print("i is now larger or equal to 5, so the while loop has ended.")