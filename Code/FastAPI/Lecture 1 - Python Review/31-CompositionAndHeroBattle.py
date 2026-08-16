"""
Composition and a Hero Battle

Composition builds an object from other objects. It models a HAS-A relationship:
a Hero has a Weapon. Inheritance models an IS-A relationship: a Zombie is an Enemy.

The Hero delegates part of its attack behavior to its current Weapon. Replacing the
weapon changes the hero's damage without creating a new Hero subclass.

These classes are a self-contained lesson example. They do not import or modify the
separate OOP/Hero.py and OOP/Weapon.py project files.

The @property decorator

A decorator is a line beginning with @ that changes how the function immediately
below it is used. @property makes a method available through attribute syntax:

	hero.is_alive       # Property access: no parentheses

Without @property, the same method would be called with parentheses:

	hero.is_alive()     # Normal method call

is_alive is a good property because it represents a cheap, derived fact about the
object. It calculates its answer from health_points every time it is accessed, so we
do not need a separate Boolean that could become out of sync. Because no setter is
defined, outside code can read hero.is_alive but cannot assign to it.

Use a property when a value naturally feels like an attribute, needs no arguments,
is quick to calculate, and has no surprising side effects. Prefer a normal method
for actions, expensive work, input/output, or calculations that need arguments.

The if __name__ == "__main__" guard

Python automatically gives every module a __name__ variable. Its value depends on
how the file is used:

- When Python runs this file directly, __name__ is set to "__main__".
- When another file imports this module, __name__ is set to the module's name.

Therefore, the condition at the bottom is True only when this lesson is run directly:

	if __name__ == "__main__":
		# Create objects and run the demonstration.

The class and function definitions above the guard are available in both cases, but
the demonstration battle inside the guard does not run during an import. This avoids
unexpected output and object creation when another module only wants to reuse Weapon,
Hero, Opponent, or battle(). The double-underscore names __name__ and __main__ are
often called "dunder" names, short for "double underscore."
"""


class Weapon:
	def __init__(self, name, damage):
		if damage <= 0:
			raise ValueError("Weapon damage must be positive.")
		self.name = name
		self.damage = damage


class Hero:
	def __init__(self, name, health_points, weapon):
		self.name = name
		self.health_points = health_points
		self.weapon = weapon  # A Hero HAS-A Weapon.

	def equip(self, weapon):
		self.weapon = weapon
		print(f"{self.name} equips {weapon.name}.")

	def attack(self):
		print(
			f"{self.name} attacks with {self.weapon.name} "
			f"for {self.weapon.damage} damage."
		)
		return self.weapon.damage

	def take_damage(self, damage):
		self.health_points = max(0, self.health_points - damage)

	@property
	def is_alive(self):
		"""Return current survival state; access this as hero.is_alive."""
		return self.health_points > 0


class Opponent:
	def __init__(self, name, health_points, attack_damage):
		self.name = name
		self.health_points = health_points
		self.attack_damage = attack_damage

	def attack(self):
		print(f"{self.name} attacks for {self.attack_damage} damage.")
		return self.attack_damage

	def take_damage(self, damage):
		self.health_points = max(0, self.health_points - damage)

	@property
	def is_alive(self):
		"""Return current survival state; access this as opponent.is_alive."""
		return self.health_points > 0


def battle(hero, opponent):
	# Properties use attribute syntax here, so is_alive has no parentheses.
	while hero.is_alive and opponent.is_alive:
		opponent.take_damage(hero.attack())
		print(f"{opponent.name} HP: {opponent.health_points}")
		if not opponent.is_alive:
			break

		hero.take_damage(opponent.attack())
		print(f"{hero.name} HP: {hero.health_points}")

	winner = hero if hero.is_alive else opponent
	print(f"{winner.name} wins!")
	return winner


if __name__ == "__main__":
	sword = Weapon("Iron Sword", damage=6)
	bow = Weapon("Hunting Bow", damage=5)
	hero = Hero("Avery", health_points=15, weapon=sword)
	hero.equip(bow)

	ogre = Opponent("Ogre", health_points=14, attack_damage=4)
	battle(hero, ogre)

