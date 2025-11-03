from dataclasses import dataclass
from coordinate import Coordinate
from typing import Optional, Tuple

@dataclass(frozen=True)
class Swap:
    coords: Optional[Tuple[Coordinate, Coordinate]]

    def __bool__(self):
        return self.coords is not None
    
    def __iter__(self):
        if self.coords is None:
            return iter((None, None))
        return iter(self.coords)
    
    def __str__(self):
        if not self:
            return "Swap(identity)"
        return f"({self.coords[0]}, {self.coords[1]})" 

    def __repr__(self):
        if not self:
            return "Swap(identity)"
        return f"Swap({self.coords[0]}, {self.coords[1]})"
