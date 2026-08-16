"""
Flow Control: if, elif, and else
"""

x = 1
# An if block runs only when its condition is True.
if x == 1:
    print("x is 1")

print("Outside of if statement")

# if we set x = 2
x = 2
if x == 1:
    print("x is 1")
    # The above statement will not be executed because x is not equal to 1
else:
    print("x is not 1")
    # The above statement will be executed because x is not equal to 1

hour = 21
# Python runs the first matching branch and skips the remaining branches.
if hour < 15:
    print("Good morning")
elif hour < 20:
    print("Good afternoon")
else:
    print("Good night")

# The above statement flow is as follows:
# If hour is less than 15, print "Good morning".
# Otherwise, if hour is less than 20, print "Good afternoon".
# If neither condition is True, print "Good night".