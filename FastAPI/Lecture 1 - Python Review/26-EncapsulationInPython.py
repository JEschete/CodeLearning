"""
Encapsulation

What is encapsulation?

Encapsulation means keeping related data and behavior together inside one unit, such
as a class, and deciding how the rest of the program should interact with that data.
It is not only about hiding attributes. It is also about giving an object control over
its own valid state.

In the Enemy class, these values are state:

- type_of_enemy
- health_points
- attack_damage

Methods such as talk(), walk_forward(), and attack() are behavior that uses that
state. Keeping both on each Enemy object is the basic form of encapsulation.

Public attributes

The current Enemy initializer contains:

class Enemy:
    def __init__(self, type_of_enemy, health_points=10, attack_damage=1):
        self.type_of_enemy = type_of_enemy
        self.health_points = health_points
        self.attack_damage = attack_damage

These three instance attributes are public. Public is Python's normal default; there
is no public keyword to add. Other code can read or reassign them directly:

zombie.type_of_enemy = 'Orc'

This is allowed, but it means the Enemy object cannot check whether that change makes
sense. The same issue would allow health_points to be set to an invalid value or
attack_damage to be changed without following any game rule.

Public attributes are not automatically bad. They are often the simplest choice for
plain data that has no validation rules. More control becomes useful when an object
must protect an invariant: a rule that should always remain true, such as health not
falling below zero.

Python's access conventions

Python does not enforce access modifiers in the same way as languages with public,
protected, and private keywords. Instead, attribute names communicate intent:

- name has no leading underscore and is part of the public interface.
- _name means "internal use" by convention. It is still directly accessible, but
    callers are being asked not to depend on it.
- __name uses name mangling. Python changes its internal name to include the class
    name, which helps prevent accidental name collisions in subclasses.
- __name__ is reserved for special Python names such as __init__; it does not mean
    private.

Double leading underscores

An attribute can be written like this inside Enemy:

class Enemy:
    def __init__(self, type_of_enemy, health_points=10, attack_damage=1):
        self.__type_of_enemy = type_of_enemy
                self.__health_points = health_points
                self.__attack_damage = attack_damage

Python name-mangles __type_of_enemy to a name based on the class, approximately
_Enemy__type_of_enemy. This discourages ordinary direct access and avoids an
accidental clash with the same attribute name in a subclass.

It is important to be precise: double underscores do not provide true privacy or
security. The mangled name can still be accessed deliberately. Name mangling is a
tool for avoiding accidental interference, especially during inheritance, rather
than a locked boundary.

Also, assigning zombie.type_of_enemy after changing the class to use
self.__type_of_enemy would not update the mangled attribute. It could create a new,
separate public attribute on that object. This is one reason access should be designed
clearly instead of only adding underscores.

Controlling access through behavior

A class can expose methods that perform meaningful changes rather than allowing every
attribute to be changed freely. For example, an Enemy could provide behavior for
taking damage. That behavior could subtract health, prevent health from dropping
below zero, and report whether the enemy was defeated. The rule would live in one
place instead of being repeated by every caller.

Properties are another Python tool for encapsulation. A property allows callers to
use attribute-style access while the class runs a method behind the scenes. A property
can calculate a value, validate assignments with a setter, or be read-only when no
setter is provided.

This does not mean every attribute needs a getter and setter. Use a public attribute
when direct access is harmless. Use a property or a meaningful method when reading or
changing the value requires rules, validation, calculation, or side effects.

Why use encapsulation?

- An object can protect the rules that keep its state valid.
- Validation and state changes can be defined in one place.
- Callers depend on a clear interface instead of internal storage details.
- The internal representation can change with fewer changes to calling code.
- Bugs caused by unrelated code changing state unexpectedly become less likely.

Encapsulation compared with abstraction

- Encapsulation focuses on packaging state with behavior and controlling access.
- Abstraction focuses on exposing what callers need while hiding unnecessary detail.

They often work together. An Enemy method can provide a simple abstract operation to
the caller while also encapsulating the rules for changing that enemy's state.
"""