"""Phased Array antenna type — element × array factor."""

from .. import register
from .array_antenna import PhasedArrayAntenna

register(PhasedArrayAntenna())
