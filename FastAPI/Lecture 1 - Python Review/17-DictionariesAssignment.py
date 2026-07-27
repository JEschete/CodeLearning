"""
Based on the dictionary:

my_vehicle = {
    "model": "Ford",
    "make": "Explorer",
    "year": 2018,
    "mileage": 40000
}
- Create a for loop to print all keys and values

- Create a new variable vehicle2, which is a copy of my_vehicle

- Add a new key 'number_of_tires' to the vehicle2 variable that is equal to 4

- Delete the mileage key and value from vehicle2

- Print just the keys from vehicle2
"""

my_vehicle = {
    "model": "Ford",
    "make": "Explorer",
    "year": 2018,
    "mileage": 40000
}

# If you don't put .items() after the dictionary, it will only print the keys of the dictionary, and you have more than one iterator
# Python will throw an error because it doesn't know what to do with the second iterator.
# The error shown will be: ValueError: too many values to unpack (expected 2)
for key, value in my_vehicle.items():
    print(f"{key}: {value}")

vehicle2 = my_vehicle.copy()
vehicle2["number_of_tires"] = 4
vehicle2.pop("mileage")

for key in vehicle2:
    print(key)

