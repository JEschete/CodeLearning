
def calculate_homework(homework_assigments):
    sum_of_grades = 0
    for homework in homework_assigments.values():
        sum_of_grades += homework
    final_grade = round(sum_of_grades / len(homework_assigments), 2)
    print(final_grade)