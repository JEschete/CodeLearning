"""
Inheritance

Inheritance lets a child class reuse and specialize behavior from a parent class.
It models an IS-A relationship: a Dog is an Animal.

- Inherited methods can be used without being rewritten.
- A child can add new attributes and methods.
- A child overrides a method by defining a method with the same name.

Use inheritance when the child genuinely satisfies the parent's meaning and
interface, not only to avoid repeating code.
"""


class Animal:
    def __init__(self, weight=20, color="brown", age=5, animal_type="mammal"):
        self.weight = weight
        self.color = color
        self.age = age
        self.animal_type = animal_type

    def eat(self):
        print("Animal is eating.")

    def sleep(self):
        print("Animal is sleeping.")


class Dog(Animal):
    def __init__(self, name, weight=20, color="brown", age=5):
        super().__init__(weight, color, age, animal_type="dog")
        self.name = name
        self.can_shed = True

    def talk(self):
        print(f"{self.name} says bark!")

    def eat(self):
        print(f"{self.name} chews on a bone.")


class Bird(Animal):
    def talk(self):
        print("Chirp!")

    def fly(self):
        print("The bird begins to soar.")


new_dog = Dog("Buddy", weight=35, color="gold", age=6)
new_dog.talk()  # Dog's own method.
new_dog.eat()  # Overrides Animal.eat().
new_dog.sleep()  # Inherited from Animal.

"""
Project connection

Enemy is the parent class in the OOP folder. Zombie and Ogre inherit its shared
state and behavior, call super().__init__() for that setup, and override methods such
as talk(). See OOP/Enemy.py, OOP/Zombie.py, and OOP/Ogre.py for those classes.
"""