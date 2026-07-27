"""
Flow Control: If Else ELIF
"""

x = 1
# If statements 
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
if hour < 15:
    print("Good morning")
elif hour < 20:
    print("Good afternoon")
else:
    print("Good night")

# The above statement flow is as follows:
# If hour is less than 15, print "Good morning" 
# If hour is not less than 15, check if hour is less than 20, if so print "Good afternoon"
# If hour is not less than 20, print "Good night"