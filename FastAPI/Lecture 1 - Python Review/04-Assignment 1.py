"""
Write a Python program that can do the following:
- You have $50
- You buy an item that is $15, that has a 3% tax
- Using print(), display how much money you have left after purchasing the item.
"""

# Initial amount of money
money = 50
cost = 15

tax_rate = 0.03
total_tax = cost * tax_rate
total_cost = cost + total_tax

remaining_money = money - total_cost

print(f"Remaining money: ${remaining_money:.2f}")

# But why not do this instead?
print(f"Remaining money: ${50 - (15 + (15 * 0.03)):.2f}")
# This produces the same result, but named variables make each value's purpose
# clear and make the calculation easier to update.