from Enemy import *

zombie = Enemy('Zombie') # we instantiated an object of type Enemy and assigned it to the variable enemy. Because type of enemy doesn't have a default parameter we *have* to pass one. 
big_zombie = Enemy('Big Zombie', 100, 10) # we overwrote the default parameters. 

# Now we can quickly create objects. 
# Though if do the following: 
zombie.type_of_enemy = 'Orc'
# This changes the type of enemy and doesn't really keep things straight and can be confusing. 

# The below lines are commented because we made a default constructor. 
# zombie.type_of_enemy = 'Zombie' # Here we are setting the type_of_enemy attribute of the enemy object to 'Zombie'.
# zombie.attack_damage = 1
# zombie.health_points = 10
print(f'{zombie.type_of_enemy} has {zombie.health_points} health points and does {zombie.attack_damage} damage.')

# The above technically does work. However it doesn't initialize an object on creation. 

zombie.talk() # Here we are calling the talk method of the enemy object, which will print 'I am an enemy!'.
zombie.walk_forward() # Here we are calling the walk_forward method of the enemy object, which will print 'The enemy moves closer to you.'.
zombie.attack() # Here we are calling the attack method of the enemy object, which will print 'The enemy attacks for 1 damage.'.

