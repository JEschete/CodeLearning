"""Enemy hierarchy for the cumulative challenge."""

import random

from .character import Character


class Enemy(Character):
    """Base enemy with shared attack behavior and overridable special behavior."""

    def __init__(self, name: str, health_points: int, attack_damage: int):
        """Initialize inherited state and validate attack damage."""
        # TODO: Call super().__init__(), reject attack_damage <= 0, and store it.
        raise NotImplementedError("Complete Enemy.__init__().")

    def talk(self) -> None:
        """Print the default enemy introduction."""
        # TODO: Print a message using self.name.
        raise NotImplementedError("Complete Enemy.talk().")

    def attack(self) -> int:
        """Print an attack message and return this enemy's damage."""
        # TODO: Print with an f-string and return self.attack_damage.
        raise NotImplementedError("Complete Enemy.attack().")

    def special_move(self) -> str | None:
        """Return no message because a generic enemy has no special move."""
        # TODO: Return None. Subclasses will override this method.
        raise NotImplementedError("Complete Enemy.special_move().")


class SurveyDrone(Enemy):
    """Fast first encounter that can increase its attack damage."""

    def __init__(self):
        """Create a Survey Drone with 8 health and 2 attack damage."""
        # TODO: Pass the fixed name and values to Enemy through super().
        raise NotImplementedError("Complete SurveyDrone.__init__().")

    def talk(self) -> None:
        """Print a drone-specific warning."""
        # TODO: Override Enemy.talk() with a distinct message.
        raise NotImplementedError("Complete SurveyDrone.talk().")

    def special_move(self) -> str | None:
        """Have a 30% chance to gain 1 attack damage and return a message."""
        # TODO: Use random.random() < 0.30. Return None when it does not trigger.
        raise NotImplementedError("Complete SurveyDrone.special_move().")


class ReactorSentinel(Enemy):
    """Stronger second encounter that can repair itself."""

    def __init__(self):
        """Create a Reactor Sentinel with 14 health and 3 attack damage."""
        # TODO: Pass the fixed name and values to Enemy through super().
        raise NotImplementedError("Complete ReactorSentinel.__init__().")

    def talk(self) -> None:
        """Print a sentinel-specific warning."""
        # TODO: Override Enemy.talk() with a distinct message.
        raise NotImplementedError("Complete ReactorSentinel.talk().")

    def special_move(self) -> str | None:
        """Have a 25% chance to heal 2 points and return a message."""
        # TODO: Use random.random() < 0.25 and self.heal(2).
        # Return None when the move does not trigger.
        raise NotImplementedError("Complete ReactorSentinel.special_move().")
