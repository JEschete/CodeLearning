"""
Imports in Python
- A module is a Python file whose code can be imported and reused.
- Separating related functions into focused modules can make code easier to maintain.
"""

import Imports.grades_average_service as grade_service

# as gives the imported module a shorter local name. Aliases can also avoid
# collisions when two modules have the same name.

homework_assignment_grades = {
    'homework_1': 85,
    'homework_2': 100,
    'homework_3': 81,
}

average_grade = grade_service.calculate_homework(homework_assignment_grades)
print(f"Average homework grade: {average_grade}")
