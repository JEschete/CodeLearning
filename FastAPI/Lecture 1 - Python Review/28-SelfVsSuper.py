"""
Self vs Super

self refers to the current object that is created or being instantiated, while super is used to refer to the parent class. 
self is used when there is a need to differentiate between the instance variables and parameters with the same name. 
while super is used to call the parent class methods and or constructors. 
"""

# Say we have

class Person: 
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(Person):
    def __init__(self, name, age, degree):
        super().__init__(name=name, age=age) # we have to call the super for the attributes of the parent. 
        self.degree = degree

