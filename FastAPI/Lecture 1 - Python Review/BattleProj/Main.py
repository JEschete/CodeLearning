from Enemy import * 

enemy = Enemy()

enemy.type_of_enemy = 'Zombie' # Here we are setting the type_of_enemy attribute of the enemy object to 'Zombie'.

print(f'{enemy.type_of_enemy} has {enemy.health_points} health points and does {enemy.attack_damage} damage.')