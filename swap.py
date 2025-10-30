from dataclasses import dataclass
from coordinate import Coordinate
from typing import Optional

@dataclass(frozen=True)
class Swap:
    """Swap between two coordinates. Identity swap is falsy."""
    coord1: Optional[Coordinate]
    coord2: Optional[Coordinate]

    # Private singleton instance for identity
    _identity_instance = None

    def __bool__(self):
        """Falsy if this is the identity swap."""
        return self is not Swap.identity()

    def __repr__(self):
        if self is Swap.identity():
            return "Swap(identity)"
        return f"Swap({self.coord1}, {self.coord2})"

    @classmethod
    def identity(cls):
        """Return the singleton identity swap."""
        if cls._identity_instance is None:
            cls._identity_instance = cls(None, None)
        return cls._identity_instance
