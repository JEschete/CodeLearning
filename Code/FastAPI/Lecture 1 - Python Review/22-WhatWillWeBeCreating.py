"""
Enemy Battle Project

Acceptance criteria:

- Enemies can fight one another.
- Zombie and Ogre are different kinds of Enemy.
- Each enemy has a type, health points, attack damage, and special behavior.
- Shared behavior is defined once and reused where practical.

The project will demonstrate encapsulation, abstraction, inheritance, and
polymorphism. We will begin with an Enemy class in OOP/Enemy.py and use it from
OOP/Main.py.

Target usage after Enemy has been implemented:

    from Enemy import Enemy

    enemy = Enemy("Zombie")
    print(
        f"{enemy.type_of_enemy} has {enemy.health_points} health points "
        f"and does {enemy.attack_damage} damage."
    )

This is a design preview rather than executable code in this lesson. Importing a
class before its module and definition exist would raise an import error.
"""

