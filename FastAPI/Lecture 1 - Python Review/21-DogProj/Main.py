from Dog import *

dog = Dog()

for attribute in dir(dog):
    if not attribute.startswith("__"):
        print(f"{attribute}: {getattr(dog, attribute)}")

