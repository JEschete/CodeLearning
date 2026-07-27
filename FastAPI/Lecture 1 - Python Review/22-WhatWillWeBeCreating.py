"""
A fighter
Acceptance Criteria
- Enemies that can fight one another
- Different types of Enemies
    - Zombie
    - Ogre
- Each enemeny has different powers, health points, and attack damage. 

We will implement using the four pillars of OOP:
- Encapsulation
- Abstraction
- Inheritance
- Polymorphism

What do we need to start? 
Enemy Object:
- Name/Type of Enemy
- Health Points
- Attack Damage

What would it look like, there would be an Enemy.py file.

we would do something like this:
from Enemy import * 
    enemy = Enemy()

print(f'{enemy.type_of_enemy} has {enemy.health_points} health points and does {enemy.attack_damage} damage.')

but the above is undefined. Overall this will break because we have not defined the Enemy class yet.

"""

