from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class Coordinate:
    """Immutable coordinate on the Lextiles board."""
    row: int
    col: int

    def __iter__(self):
        """Allow unpacking like a tuple: row, col = coord"""
        yield self.row
        yield self.col

    def __add__(self, other):
        """Coordinate-wise addition, e.g., coord + (1, -1)."""
        if isinstance(other, tuple) and len(other) == 2:
            return Coordinate(self.row + other[0], self.col + other[1])
        raise TypeError("Can only add (row_offset, col_offset) tuples to Coordinate.")

    def in_bounds(self, num_rows: int, num_cols: int) -> bool:
        """Check if coordinate is within given bounds."""
        return 0 <= self.row < num_rows and 0 <= self.col < num_cols

    def __str__(self):
        return f"({self.row}, {self.col})"

    def __repr__(self):
        return f"Coordinate({self.row}, {self.col})"
