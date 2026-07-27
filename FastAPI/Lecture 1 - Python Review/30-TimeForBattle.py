"""
Before we start a battle: 
- Lets give our enemies special attacks. 
- If an enemy does not have a special attack, we print "Enemy does not have a special attack."

Add code into the: 
- Enemy (Parent)
- Both children Zombie and Ogre

we will for Enemy()
def special_attack(self):
    print('Enemy has no special attack')

for zombie and ogre:
def special_attack(self):
    did_special_attack_work = random.random() < 0.50
    if did_special_attack_work:
        self.health_points += 2
        print('Zombie regenerated 2 HP!')

def special_attack(self):
    did_special_attack_work = random.random() < 0.20
    if did_special_attack_work:
        self.attack_damage += 4
        print('Ogre attack has increased by 4!')

In main: 

def battle(e1: Enemy, e2: Enemy) {
    e1.talk()
    e2.talk()
    
    while e1.health_points > 0 and e2.health_points > 0
     e1.special_attack()
     e2.special_attack()
     e2.attack()
     e1.health_points -= e2.attack_damage
     e1.attack()
     e2.health_points -= e1.attack_damage

     if e1.health_points > 0:
         print('Enemy 1 wins!')
     else:
         print('Enemy 2 wins!')
}

zombie = Zombie(10,1)
ogre = Ogre(20,3)

battle(zombie, ogre)
"""