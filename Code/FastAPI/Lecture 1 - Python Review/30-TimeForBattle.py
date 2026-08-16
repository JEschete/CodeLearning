"""
Enemy Battle

This example combines inheritance, method overriding, polymorphism, and
encapsulation:

- Enemy defines behavior shared by all enemies.
- Zombie and Ogre override talk() and special_attack().
- battle() uses the same methods without checking each enemy's exact type.
- take_damage() owns the rule that health cannot fall below zero.

Turns alternate. After the first attack, the battle checks whether the defender is
still alive so a defeated enemy cannot counterattack.
"""

import random


class Enemy:
    def __init__(self, type_of_enemy, health_points=10, attack_damage=1):
        self.type_of_enemy = type_of_enemy
        self.health_points = health_points
        self.attack_damage = attack_damage

    def talk(self):
        print(f"I am a {self.type_of_enemy}. Prepare to fight!")

    def attack(self):
        print(f"{self.type_of_enemy} attacks for {self.attack_damage} damage.")
        return self.attack_damage

    def take_damage(self, damage):
        if damage < 0:
            raise ValueError("Damage cannot be negative.")
        self.health_points = max(0, self.health_points - damage)

    def special_attack(self):
        print(f"{self.type_of_enemy} has no special attack.")

    @property
    def is_alive(self):
        return self.health_points > 0


class Zombie(Enemy):
    def __init__(self, health_points=10, attack_damage=1):
        super().__init__("Zombie", health_points, attack_damage)

    def talk(self):
        print("*Grumbling...*")

    def special_attack(self):
        if random.random() < 0.50:
            self.health_points += 2
            print("Zombie regenerated 2 HP!")


class Ogre(Enemy):
    def __init__(self, health_points=20, attack_damage=3):
        super().__init__("Ogre", health_points, attack_damage)

    def talk(self):
        print("The ogre slams its hands on the ground.")

    def special_attack(self):
        if random.random() < 0.20:
            self.attack_damage += 4
            print("Ogre attack increased by 4!")


def battle(enemy_one, enemy_two):
    enemy_one.talk()
    enemy_two.talk()

    round_number = 1
    while enemy_one.is_alive and enemy_two.is_alive:
        print(f"\nRound {round_number}")

        enemy_one.special_attack()
        enemy_two.take_damage(enemy_one.attack())
        print(f"{enemy_two.type_of_enemy} HP: {enemy_two.health_points}")
        if not enemy_two.is_alive:
            break

        enemy_two.special_attack()
        enemy_one.take_damage(enemy_two.attack())
        print(f"{enemy_one.type_of_enemy} HP: {enemy_one.health_points}")
        round_number += 1

    winner = enemy_one if enemy_one.is_alive else enemy_two
    print(f"\n{winner.type_of_enemy} wins!")
    return winner


if __name__ == "__main__":
    random.seed(7)  # Makes the lesson output repeatable.
    battle(Zombie(), Ogre())