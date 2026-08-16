"""
self vs. super()

self

self is the conventional name for the first parameter of an instance method. Python
passes the current instance into that parameter automatically. A method uses self to
read or change that object's attributes and to call its other methods.

    self.name = name

The expression on the right, name, is a parameter containing a value. The expression
on the left, self.name, is an attribute stored on the object. Their names may match,
but parameters and attributes are different things.

super()

super() returns a proxy that follows the class's method resolution order. A child
class uses that proxy to call the next implementation of a method, commonly the
parent's __init__:

    super().__init__(name=name, age=age)

Use super().__init__(...), with parentheses after super. super.__init__(...) is not
the same operation.

What super().__init__ does

The values on the right come from the child's parameters. The names on the left must
match parameters accepted by the parent's __init__:

    parent_parameter=child_value

This call passes arguments to the parent initializer; it does not create attributes
by itself. The assignments inside the parent, such as self.name = name, create the
attributes. The parent receives the same child object as self, so those attributes
belong to the finished child object.

When Student("Avery", 21, "Computer Science") runs, Python:

1. Creates a Student instance.
2. Calls Student.__init__ with that instance as self.
3. super().__init__ calls Person.__init__ with the same object as self.
4. Person.__init__ creates self.name and self.age.
5. Control returns to Student.__init__, which creates self.degree.

Does every child need __init__?

No. If a child does not define __init__, it inherits the parent's initializer. Define
a child initializer only when the child needs extra state, different defaults, fixed
parent values, calculated values, or other custom setup.

If a child defines its own __init__, Python does not automatically call the parent's
initializer. Call super().__init__(...) when the child still needs the parent's
setup. The child only needs to supply the parent's required arguments; optional
parameters can use their defaults.

Python commonly calls __init__ a constructor, but initializer is more precise. Python
creates the instance first and then calls __init__ to initialize it.
"""


class Person:
    def __init__(self, name, age=18, country="USA"):
        self.name = name
        self.age = age
        self.country = country

    def describe(self):
        print(f"{self.name} is {self.age} and lives in {self.country}.")


# Example 1: No child initializer is needed.
# Employee inherits Person.__init__ and Person.describe unchanged.
class Employee(Person):
    pass


employee = Employee("Jordan", 30)
employee.describe()


# Example 2: The child adds its own state.
class Student(Person):
    def __init__(self, name, degree, age=18, country="USA"):
        # Left-side names are Person parameters; right-side names are local values.
        super().__init__(name=name, age=age, country=country)
        self.degree = degree

    def introduce(self):
        print(
            f"I am {self.name}, I am {self.age}, and I study {self.degree} "
            f"in {self.country}."
        )


student = Student("Avery", "Computer Science", age=21)
student.introduce()


# Example 3: Parameter and attribute names do not have to match.
class Account:
    def __init__(self, account_owner):
        self.owner = account_owner


class SavingsAccount(Account):
    def __init__(self, customer_name, interest_rate):
        # customer_name is passed to Account's account_owner parameter.
        super().__init__(account_owner=customer_name)
        self.interest_rate = interest_rate


savings = SavingsAccount("Morgan", interest_rate=0.04)
print(f"{savings.owner}'s interest rate is {savings.interest_rate:.0%}.")


# Example 4: A child can fix one parent value instead of exposing it to callers.
class Enemy:
    def __init__(self, enemy_type, health=10, attack_damage=1):
        self.enemy_type = enemy_type
        self.health = health
        self.attack_damage = attack_damage


class Zombie(Enemy):
    def __init__(self, health=10, attack_damage=1):
        super().__init__(
            enemy_type="Zombie",
            health=health,
            attack_damage=attack_damage,
        )


zombie = Zombie(health=20, attack_damage=3)
print(
    f"{zombie.enemy_type}: {zombie.health} health, "
    f"{zombie.attack_damage} attack damage."
)

