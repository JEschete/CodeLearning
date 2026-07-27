"""
Polymorphism 
- means to have many forms. 

# Say we have
zoo : Animal = []
dog  = Dog()
zoo.append(dog)

and another file with

class Dog(Animal):
**Dog methods**

class Bird(Animal):
**Bird methods**

class Lion(Animal):
**Lion methods**


The zoo.append(dog) will work because dog inherits from Animal.

Doing
dog = Animal()
zoo.append(dog)

Also works. 

dog2 = Dog()
bird = Bird()
lion = Lion()

# These all work because the animals inherit type of Animal. 
zoo.append(dog)
zoo.append(dog2)
zoo.append(bird)
zoo.append(lion)

class Animal: 
    def talk(self):
        print('Does not make a sound')

class Dog(Animal): 
    def talk(self):
        print('Bark!')

class Bird(Animal): 
    def talk(self):
        print('Chirp!')

class Lion(Animal): 
    def talk(self):
        print('Roar!')

zoo = Animal[]
dog = Animal()
dog2 = Dog()
bird = Bird()
lion = Lion()

zoo.append(dog)
zoo.append(dog2)
zoo.append(bird)
zoo.append(lion)

How will we use Polymorphism? 

Create a new battle function within our main.py file
- Uses our enemy talk() and enemy attack() methods

"""
