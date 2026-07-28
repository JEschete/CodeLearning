"""
Abstraction

What is Abstraction in Python?

Abstraction means presenting the useful part of something while hiding details that
the caller does not need in order to use it. It helps us focus on what an object can
do instead of every step describing how it does it.

An abstraction has two useful sides:

- Interface: The operations that other code is allowed or expected to use.
- Implementation: The internal instructions that make those operations work.

The word interface here means the visible way that code is used. It does not have to
refer to a special Python language feature.

Abstraction in the Enemy example

See FastAPI/Lecture 1 - Python Review/OOP for the Enemy example.

The Enemy class provides methods such as:

- talk()
- walk_forward()
- attack()

Code using an Enemy can call zombie.attack() without knowing how the message is
formatted or where the damage value is stored. The attack method is the operation
the caller sees. Reading self.attack_damage and printing the result are implementation
details inside that method.

This is already a simple form of abstraction. The methods give the caller a small,
meaningful set of operations instead of requiring it to repeat the internal steps.

The current Enemy class is a concrete class, not an abstract class. Concrete means
that it supplies its method implementations and can be instantiated directly with
Enemy(...). An object does not need to inherit from an abstract class for its methods
to provide a useful abstraction.

Ways Python code can provide abstraction

- A function hides the steps needed to calculate a result.
- A class exposes methods while managing the details behind those methods.
- A module groups related tools behind names that other files can import.
- An abstract base class can define operations that subclasses must implement.

Formal abstract classes

For a formal contract between related classes, Python provides the abc module. A
class can inherit from ABC, and @abstractmethod can mark a method that a concrete
subclass must implement. Python prevents that abstract class from being instantiated
until all required abstract methods have implementations.

Python does not have an interface keyword like some other languages. Abstract base
classes and protocols can serve similar roles, but they are more advanced tools than
the simple method-based abstraction shown by Enemy.

Why use abstraction?

- Callers have fewer details to understand at one time.
- Internal implementation can change without forcing every caller to change.
- A clear operation can be reused instead of repeating its steps.
- Related classes can be designed around a consistent set of operations.
- Responsibilities become easier to test and maintain as a program grows.

Abstraction can support the DRY principle (Don't Repeat Yourself), but its main goal
is a clear boundary. A good abstraction gives a useful name to an operation and hides
only the details that callers should not need.

Abstraction compared with encapsulation

- Abstraction asks, "What useful operation should this object expose?"
- Encapsulation asks, "How should this object's state and behavior be kept together
    and accessed safely?"

The ideas often work together. For example, attack() is an abstraction for an enemy
action, while keeping attack_damage on the Enemy object is part of encapsulation.

Too much abstraction can make small programs harder to follow. Create an abstraction
when it makes the caller simpler, protects it from change, or represents a meaningful
responsibility in the program.

"""