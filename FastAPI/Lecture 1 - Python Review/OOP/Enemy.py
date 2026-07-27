class Enemy: 

    # With the default constructor, the following 3 lines are no longer needed. 
    # type_of_enemy: str
    # health_points: int
    # attack_damage: int

    # We need to make constructors. 
    # This is created by done by default. It is the empty/default constructor
    # def __init__(self): 
    #    pass

    # The following is a No-argument initializer
    # def __init__(self):
    #     print('Create new enemy!')

    # The folloring is the parameterized constructor. 
    # This makes us set things when we instantiate the object. 
    def __init__(self, type_of_enemy, health_points=10, attack_damage=1)
        self.type_of_enemy = type_of_enemy
        self.health_points = health_points
        self.attack_damage = attack_damage

    def talk(self):
        print(f'I am a {self.type_of_enemy}. Be prepared to fight.')

    def walk_forward(self):
        print(f'{self.type_of_enemy} moves closer to you.')

    def attack(self): 
        print(f'{self.type_of_enemy} attacks for {self.attack_damage} damage.')

    # Self is talking about itself. It is a reference to the object that is calling the method. In this case, it is the enemy object. 
    # The self parameter is used to access the attributes and methods of the class in Python. It is a convention to use self as the first parameter of instance methods in Python classes.