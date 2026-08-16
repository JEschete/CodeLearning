"""
Constructors
What are constructors in Python?

Constructors are used to create and initialize objects from a class. A class is the
blueprint, while each object created from that class is a separate instance.

For example, OOP/Main.py contains:

from Enemy import Enemy
enemy = Enemy('Zombie')

Enemy is the class, and Enemy('Zombie') is a call to that class. The call creates an
Enemy instance and assigns a reference to it to the enemy variable. Each call creates
a new and separate Enemy object.

Python constructor lessons commonly refer to __init__ as the constructor. More
precisely, Python first creates the object and then calls __init__ to initialize that
new object. Most classes only need to define __init__; the earlier creation step is
handled automatically by Python.

Three forms commonly discussed in beginner lessons are:
- Inherited/default initializer
- No-argument initializer
- Parameterized initializer

Inherited/default initializer

If a class does not define __init__, it inherits one from its parent class. The Enemy
class in the OOP example no longer works this way: it defines the parameterized
initializer shown below. A simple class with no explicit parent ultimately inherits
object.__init__, which accepts no custom initialization arguments.

No-argument initializer

def __init__(self):
    print('New enemy created with no starting values')

This initializer has no parameters for the caller to provide. self is still present,
but Python supplies it automatically. Calling Enemy() would run this method once for
the newly created object.

Parameterized initializer

def __init__(self, type_of_enemy, health_points=10, attack_damage=1):
    self.type_of_enemy = type_of_enemy
    self.health_points = health_points
    self.attack_damage = attack_damage

type_of_enemy is required because it has no default value. health_points and
attack_damage are optional because they have default values. The order of the
parameters determines how positional arguments are matched to them.

The assignments beginning with self create instance attributes. This means each
Enemy object stores its own type, health, and damage. Changing one enemy's instance
attributes does not change another enemy's instance attributes.

def talk(self):
    print('I am an enemy')

The self parameter refers to the particular instance receiving the method call, not
to the class as a whole. For example, when enemy.talk() is called, Python passes enemy
to talk as self. You write self in the method definition but do not pass it manually.

If we do:
enemy = Enemy('Zombie')

'Zombie' is assigned to type_of_enemy. The omitted optional arguments use their
defaults, so this zombie starts with 10 health points and 1 attack damage.

If we do:
enemy = Enemy('Zombie', 15, 3)

the supplied 15 and 3 are used instead of the default values. This zombie starts with
15 health points and 3 attack damage.

__init__ performs setup by changing the new object through self. It should not return
the newly created object; Python makes the finished instance the result of Enemy().

"""