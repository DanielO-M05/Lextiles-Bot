"""
solver_base.py
--------------
Abstract base class for Lextiles solvers.
All solvers must implement choose_move(board), which returns a
(Swap, list[Coordinate]) tuple.
"""

from abc import ABC, abstractmethod
from board import Board
from swap import Swap


class SolverBase(ABC):

    @abstractmethod
    def choose_move(self, board: Board, verbose: bool = True) -> tuple[Swap, list]:
        """Return the swap and coordinates of the chosen move.

        Args:
            board (Board): The current board state. Must not be mutated.
            verbose (bool): If True, solvers may print progress information.
                            If False, solvers must produce no output.

        Returns:
            tuple[Swap, list[Coordinate]]: The swap to make (identity Swap if
                none) and the coordinates of the chosen word. Return
                (Swap(), []) if no moves are available.
        """
        ...

    @abstractmethod
    def __str__(self) -> str:
        """Human-readable name of the solver, used in logging and comparison."""
        ...