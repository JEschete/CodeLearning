# from Enemy import *
from Zombie import *
from Ogre import *

def battle(e1: Enemy, e2: Enemy):
    e1.talk()
    e2.talk()
    print()
    
    while e1.health_points > 0 and e2.health_points > 0:
        print('----------')
        e1.special_attack()
        e2.special_attack()
        print(f'{e1.get_type_of_enemy()}: {e1.health_points} HP Left')
        print(f'{e2.get_type_of_enemy()}: {e2.health_points} HP Left')
        e2.attack()
        e1.health_points -= e2.attack_damage
        e1.attack()
        e2.health_points -= e1.attack_damage
        print()

    print('----------')
    if e1.health_points > 0:
        print()
        print(f'{e1.get_type_of_enemy()} wins!')
        print(f'{e1.get_type_of_enemy()} finished with {e1.health_points} hp remaining')
    else:
        print()
        print(f'{e2.get_type_of_enemy()} wins!')
        print(f'{e2.get_type_of_enemy()} finished with {e2.health_points} hp remaining')


"""
zombie = Enemy('Zombie') # we instantiated an object of type Enemy and assigned it to the variable enemy.

print(zombie.get_type_of_enemy()) # Here we are setting the type_of_enemy attribute of the enemy object to 'Zombie'.
zombie.attack_damage = 1
zombie.health_points = 10
print(f'{zombie.get_type_of_enemy()} has {zombie.health_points} health points and does {zombie.attack_damage} damage.')

# The above technically does work. However it doesn't initialize an object on creation. 

zombie.talk() # Here we are calling the talk method of the enemy object, which will print 'I am an enemy!'.
zombie.walk_forward() # Here we are calling the walk_forward method of the enemy object, which will print 'The enemy moves closer to you.'.
zombie.attack() # Here we are calling the attack method of the enemy object, which will print 'The enemy attacks for 1 damage.'.


zombie = Zombie(10, 1)
print()

print(zombie.get_type_of_enemy())
zombie.talk()
zombie.spread_disease()

print()

ogre = Ogre(15,2)
ogre.talk()
ogre.attack()

"""

zombie = Zombie(10, 1)
ogre = Ogre(15,1)

battle(zombie, ogre)
