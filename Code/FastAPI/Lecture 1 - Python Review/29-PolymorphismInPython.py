"""
Polymorphism

Polymorphism means that one operation can work with objects of different types.
Each object supplies its own implementation of the expected behavior.

In Python, inheritance is one way to establish that common interface, but duck
typing also allows unrelated classes to participate when they provide the required
methods. Type hints document intended types; they do not enforce them at runtime.
"""


class Animal:
    def talk(self):
        print("The animal makes a sound.")


class Dog(Animal):
    def talk(self):
        print("Bark!")


class Bird(Animal):
    def talk(self):
        print("Chirp!")


class Lion(Animal):
    def talk(self):
        print("Roar!")


zoo: list[Animal] = [Animal(), Dog(), Bird(), Lion()]

for animal in zoo:
    animal.talk()  # Python selects the method for the object's actual class.

"""
Project connection

The battle function can use the same operations on Zombie and Ogre objects without
branching on their exact types. Calling talk(), attack(), or special_attack() selects
the implementation supplied by each object.
"""
