"""Weapon composition model for the cumulative challenge."""


class Weapon:
    """Represent a named weapon with a fixed positive damage value."""

    def __init__(self, name: str, damage: int):
        """Validate and store the weapon's name and damage."""
        # TODO: Reject a blank name and damage <= 0 with ValueError, then store
        # the stripped name and damage as public attributes.
        raise NotImplementedError("Complete Weapon.__init__().")

    def describe(self) -> str:
        """Return text in the form 'Pulse Blade (6 damage)'."""
        # TODO: Return the formatted description instead of printing it.
        raise NotImplementedError("Complete Weapon.describe().")
