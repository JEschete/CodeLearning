"""
For and while Loops in Python
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
for number in my_list:
    print(number)

# The loop variable can use any valid name; descriptive names make code clearer.

# range includes its start value but excludes its stop value, so this prints 3-5.
for number in range(3, 6):
    print(number)

sum_of_for_loop = 0
for number in my_list:
    sum_of_for_loop += number
print(f"Sum of for loop: {sum_of_for_loop}")
# The sum of all numbers in my_list is 15.

# The for loop after this operates on a list of strings, and prints out each string with the word "Happy" in front of it.
my_list_2 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for day in my_list_2:
    print(f"Happy {day}!")

i = 0
while i < 5:
    i += 1
    print(i)
# The above while loop will print the numbers 1 through 5, because it starts with i = 0, and then increments i by 1 each time through the loop, until i is no longer less than 5.
# If we did not increment i, the while loop would run forever, because i would always be less than 5. This is called an infinite loop, and it is something we want to avoid in our code.

# continue skips the rest of the current iteration and starts the next one.
i = 0
while i < 5:
    i += 1
    if i == 3:
        continue
    print(i)
else:
    # A loop's else block runs when the loop ends without break.
    print("i reached 5, so the while loop ended normally.")

# break exits the loop immediately. Its else block is then skipped.
i = 0
while i < 5:
    i += 1
    if i == 3:
        continue
    print(i)
    if i == 4:
        break
else:
    print("This line is skipped because the loop used break.")

print("The second loop stopped early when i reached 4.")