"""
- Create a function that takes in 3 parameters(firstname, lastname, age) and
returns a dictionary based on those values
"""

def person_builder(first_name: str, last_name: str, age: int) -> dict[str, str | int]:
    person = {
        "First":first_name,
        "Last":last_name,
        "Age":age
    }

    return person

person = person_builder("John", "Jacob", 35)

print(f"Hi, my name is {person['First']} {person['Last']}, and I'm {person['Age']} years old. ")