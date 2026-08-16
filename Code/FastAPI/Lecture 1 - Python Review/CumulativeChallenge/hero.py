"""Hero model for the cumulative challenge."""

from .character import Character
from .weapon import Weapon


class Hero(Character):
    """A playable character that has a weapon and an inventory."""

    def __init__(self, name: str, health_points: int, weapon: Weapon):
        """Initialize inherited state, composition, and starting inventory."""
        # TODO:
        # - Call Character.__init__ through super().
        # - Store weapon in self.weapon.
        # - Create self.inventory as a list containing "repair patch".
        raise NotImplementedError("Complete Hero.__init__().")

    def equip(self, weapon: Weapon) -> None:
        """Replace the current weapon and print what was equipped."""
        # TODO: Store the supplied Weapon and print a formatted message.
        raise NotImplementedError("Complete Hero.equip().")

    def collect_item(self, item: str) -> None:
        """Add a non-empty item to the inventory."""
        # TODO: Reject a blank item with ValueError, then append its stripped name.
        raise NotImplementedError("Complete Hero.collect_item().")

    def use_repair_patch(self) -> bool:
        """Consume one repair patch, heal 4 points, and report whether one existed."""
        # TODO: Use membership, remove(), heal(), and a Boolean return value.
        raise NotImplementedError("Complete Hero.use_repair_patch().")

    def attack(self) -> int:
        """Print an attack message and return the equipped weapon's damage."""
        # TODO: Use the composed Weapon object; do not duplicate its damage on Hero.
        raise NotImplementedError("Complete Hero.attack().")
