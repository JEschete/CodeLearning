"""Print Formatting

Write an expression using any of the string formatting methods we have learned (except f-strings, see note below) to return the phrase 'Python rules!'

For example, these phrases both return 'I like apples' :

    'I like %s' %'apples'
    'I like {}'.format('apples')

Your solution should be entered on one line. You can not use variable names, only the strings themselves.

NOTE: At this time, f-strings won't work! Udemy Coding Exercises use Python 3.5.2, and f-strings require Python 3.6 or higher."""

p = "rules!"
print("Python %s" % "rules!")
print("Python {}".format("rules!"))
print("Python {p}".format(p="rules!"))
print(f"Python {p}")
