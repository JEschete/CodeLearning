"""
Inheritance - The process of acquiring properties from one class to other classes. 
Creates a hierarchy between classes. 

We can make a parent class
class Animal

then
class Dog(Animal)
**In herits all the attributes of the animal class**
Is a child of animal. 
"""

class Animal: 
    def __init__(self, weight=20, color='brown', age=5, animal_type='mammal'):
        self.weight = weight
        self.color = color
        self.age = age
        self.animal_type = animal_type

    def eat(self):
        print('Animal Eating')

    def sleep(self):
        print('Animal Sleeping')

class Dog(Animal):
    can_shed: bool
    domestic_name: str

    def talk(self):
        print('Bark')

    def eat(self):
        print('Chews on bone!')

class Bird(Animal):
    birdType: str
    def talk(self):
        print('Chirp!')

    def fly(self):
        print('Bird begins to soar')


new_dog = Dog(35, 'Gold', 6, 'Canis Lupus')
new_dog.can_shed = False


print(new_dog.talk())

"""
Method overriding. 
We are adding our own function to the Dog class using the same function name. 
Method overriding is when a child class has its own method already present in the parent class. 
When the child class does not have the same method, it will default to the parent method. 
"""
# if we do
animal = Animal()
# The following will fail because animal has no methods for fly or talk. 
# animal.talk()
# animal.fly()

"""
How are we going to use Inheritance? 

Currently our only class is Enemy()
- Enemy() is our Parent Class

We will create two child classes. 
- Zombie
- Ogre

Look at zombie class

"""

class Enemy: 

    def __init__(self, type_of_enemy, health_points=10, attack_damage=1):
        self.__type_of_enemy = type_of_enemy 
        self.health_points = health_points
        self.attack_damage = attack_damage

    def talk(self):
        print(f'I am a {self.__type_of_enemy}. Be prepared to fight.')

    def walk_forward(self):
        print(f'{self.__type_of_enemy} moves closer to you.')

    def attack(self): 
        print(f'{self.__type_of_enemy} attacks for {self.attack_damage} damage.')

    def get_type_of_enemy(self):
        return self.__type_of_enemy

class Zombie(Enemy):
    def __init__(self, health_points, attack_damage):
        super().__init__(
            type_of_enemy='Zombie', 
            health_points=health_points, 
            attack_damage=attack_damage
            )
        
    def talk(self):
        print('*Grumbling...*') # Overriding the Talk method

    def spread_disease(self):
        print('The zombie is trying to spread infection') # New Zombie only method. 

class Ogre(Enemy):
    def __init__(self, health_points, attack_damage):
        super().__init__(
            type_of_enemy='Ogre', 
            health_points=health_points, 
            attack_damage=attack_damage
            )

    def talk(self):
        print('Ogre is slamming hands all around.')