"""Shared character state for the cumulative challenge."""


class Character:
    """Store and safely update state shared by heroes and enemies."""

    def __init__(self, name: str, health_points: int):
        """Validate and store a name plus current and maximum health."""
        # TODO:
        # - Reject a blank name and health_points <= 0 with ValueError.
        # - Store the stripped name in self.name.
        # - Store health in self._health_points and self._max_health_points.
        raise NotImplementedError("Complete Character.__init__().")

    @property
    def health_points(self) -> int:
        """Return current health without allowing direct assignment."""
        # TODO: Return the internal current-health attribute.
        raise NotImplementedError("Complete Character.health_points.")

    @property
    def is_alive(self) -> bool:
        """Return whether this character has health remaining."""
        # TODO: Derive this Boolean from health_points.
        raise NotImplementedError("Complete Character.is_alive.")

    def take_damage(self, amount: int) -> None:
        """Apply non-negative damage without allowing health below zero."""
        # TODO: Reject negative amounts, then use max() to update health.
        raise NotImplementedError("Complete Character.take_damage().")

    def heal(self, amount: int) -> None:
        """Restore non-negative health without exceeding maximum health."""
        # TODO: Reject negative amounts, then use min() to update health.
        raise NotImplementedError("Complete Character.heal().")
