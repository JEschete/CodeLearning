"""LPDA antenna sub-package."""

from .lpda import LPDAntenna
from .. import register

register(LPDAntenna())
