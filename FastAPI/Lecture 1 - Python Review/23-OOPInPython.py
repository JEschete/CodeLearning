"""
Object-Oriented Programming (OOP)

What is object-oriented programming?

Object-oriented programming is a way to organize a program around objects. An
object keeps related data and behavior together instead of storing them in unrelated
variables and functions.

The main vocabulary of OOP is:

- Class: A blueprint that describes the data and behavior its objects will have.
- Object: One specific instance created from a class.
- Attribute: Data stored on an object.
- Method: A function defined by a class that describes an object's behavior.
- Instantiation: The process of creating an object from a class.

See the FastAPI\Lecture 1 - Python Review\OOP folder for the Enemy example.

In that example, Enemy is a class. It describes what every enemy should know and
what every enemy should be able to do. A variable such as zombie refers to one Enemy
object, while big_zombie refers to a different Enemy object.

Enemy('Zombie') instantiates an Enemy. 'Zombie' is used as starting data for that
new object. Each call to Enemy(...) creates a separate instance, so the zombie and
big_zombie objects can have different health points and attack damage.

The Enemy object's data is stored in attributes:

- type_of_enemy describes the kind of enemy.
- health_points stores how much health that enemy has.
- attack_damage stores how much damage that enemy can deal.

Its behavior is represented by methods:

- talk() prints what the enemy says.
- walk_forward() moves the idea of the enemy forward in the program.
- attack() uses the enemy's own attack damage.

When zombie.attack() is called, zombie is the object receiving the method call.
Inside the method, self refers to that same zombie object. This is how one method
can work with the correct instance's attributes.

Why use OOP?

- Related state and behavior stay together in one understandable unit.
- A class can be reused to create many similar but independent objects.
- Changes to an object's behavior can be made in the class instead of at every call.
- Larger programs can be divided into classes with focused responsibilities.

OOP is often introduced through four related ideas:

- Abstraction exposes useful behavior while hiding unnecessary implementation detail.
- Encapsulation keeps related state and behavior together and controls how state is used.
- Inheritance lets one class build on behavior supplied by another class.
- Polymorphism lets different object types respond to the same operation in their own way.

Not every value needs to become an object. OOP is most useful when a group of data
and operations represents a meaningful thing or responsibility in the program.
"""

