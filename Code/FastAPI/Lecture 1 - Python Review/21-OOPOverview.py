"""
Object-Oriented Programming Overview

Object-oriented programming (OOP) organizes code around objects that combine:

- State: data an object stores, such as a dog's name or age.
- Behavior: actions an object performs, such as barking.

A class describes a kind of object. Each object created from that class is a
separate instance and can hold different state.

OOP can help group related code, reuse behavior, and make larger programs easier to
change. It is one design approach, not a requirement for every program.

Python does not formally separate values into "primitive" and "object" categories:
integers, floats, strings, and Booleans are all objects of built-in types.
"""


class Dog:
    """Represent one dog with its own state and behavior."""

    def __init__(self, name, breed, age):
        self.name = name
        self.breed = breed
        self.age = age

    def bark(self):
        print(f"{self.name} says woof!")


buddy = Dog("Buddy", "Golden Retriever", 5)
luna = Dog("Luna", "Goldendoodle", 2)

buddy.bark()
luna.bark()

# Four related OOP ideas explored in the following lessons:
# - Encapsulation
# - Abstraction
# - Inheritance
# - Polymorphism

