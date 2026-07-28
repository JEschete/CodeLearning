"""Utilities for calculating grade averages."""


def calculate_homework(homework_assignments: dict[str, int | float]) -> float:
    """Return the mean homework grade rounded to two decimal places."""
    if not homework_assignments:
        raise ValueError("At least one homework grade is required.")

    total_points = sum(homework_assignments.values())
    return round(total_points / len(homework_assignments), 2)