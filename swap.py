from dataclasses import dataclass
from coordinate import Coordinate
from typing import Optional, Tuple

@dataclass(frozen=True)
class Swap:
    coords: Optional[Tuple[Coordinate, Coordinate]] = None

    def __post_init__(self):
        if self.coords is not None:
            if not (isinstance(self.coords, tuple) and len(self.coords) == 2):
                raise ValueError("coords must be a tuple of two Coordinates")
            a, b = self.coords
            if not all(isinstance(x, Coordinate) for x in (a, b)):
                raise TypeError("coords must contain Coordinate objects")

    def __bool__(self):
        return self.coords is not None
    
    def __iter__(self):
        if self.coords is None:
            return iter((None, None))
        return iter(self.coords)
    
    def __eq__(self, other):
        if not isinstance(other, Swap):
            return False
        if self.coords is None or other.coords is None:
            return self.coords is other.coords  # identity comparison for None
        return frozenset(self.coords) == frozenset(other.coords) # Order doesn't matter

    def __hash__(self):
        if self.coords is None:
            return hash(None)
        return hash(frozenset(self.coords)) # Order doesn't matter
    
    def __str__(self):
        if not self:
            return "Swap(identity)"
        return f"({self.coords[0]}, {self.coords[1]})" 

    def __repr__(self):
        if not self:
            return "Swap(identity)"
        return f"Swap({self.coords[0]}, {self.coords[1]})"
