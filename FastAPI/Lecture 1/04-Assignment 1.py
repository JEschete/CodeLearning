"""
Write a Python program that can do the following:
- You have $50
- You buy an item that is $15, that has a 3% tax
- Using the print()  Print how much money you have left, after purchasing the item.
"""

# Initial amount of money
money = 50
cost = 15

tax = 0.03
total_tax = cost * tax
total_cost = cost + total_tax

remaining_money = money - total_cost

print("Remaining money: $", remaining_money)

# But why not do this instead?
print(50 - (15 + (15 * 0.03))) 
# The above line of code does the same thing as the previous code, but it is less readable and harder to understand. It is better to use variables to store values and make the code more readable.