store_name = "Corner Market"
items = ["apple", "milk", "apple", "bread"]
prices = {"apple": 1.50, "milk": 3.25, "bread": 2.75}
tax_rate = 0.07

""" 
Print header using f-strings, I'll go with width 20. 
Example: Welcome to Corner Market

Loop through items, I'll use a for loop to write the line items and calculate subtotal. 

Then after I will calculate the tax and total. 
I then create a set to get unique items, then print the item names.

I create a tuple of the item count, unique item count, final total.
I then print the tuple. 

I then make a Boolean to check if the total is less than $10. 
"""

with open(
    ".\\Section 3 - Python Object and Data Structure Basics\\receipt.txt", "w"
) as f:
    welcome_line = "Welcome to {}".format(store_name)
    top_bottom_line = "*" * (len(welcome_line) + 8)
    header = "*" + welcome_line.center(30, " ") + "*"
    f.write(top_bottom_line + "\n")
    f.write(header + "\n")

    subtotal = 0
    for item in items:
        f.write(f"* {item:<17}{prices[item]:>10.2f}  *\n")
        subtotal += prices[item]

    f.write(top_bottom_line + "\n")
    f.write(f"* {'Subtotal:':<17}${subtotal:>9.2f}  *\n")
    tax = subtotal * tax_rate
    f.write(f"* {'Tax:':<17}${tax:>9.2f}  *\n")
    total = subtotal + tax
    f.write(f"* {'Total:':<17}${total:>9.2f}  *\n")
    f.write(top_bottom_line + "\n")

    unique_items = set(items)
    f.write(", ".join(unique_items) + "\n")

    summary = (len(items), len(unique_items), total)
    f.write(f"{summary}\n")
    balance_good = total <= 10
    if balance_good:
        f.write("Budget good: True \n")
    else:
        f.write("Budget good: False \n")
