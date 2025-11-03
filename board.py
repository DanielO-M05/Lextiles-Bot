from coordinate import Coordinate
from swap import Swap

class Board:

    MIN_WORD_LENGTH = 3

    def __init__(self, letters, powerups, scores, swaps_left, min_word_length):
        self.letters = letters
        self.powerups = powerups
        self.scores = scores
        self.swaps_left = swaps_left

    def best_move_with_swap(self):
        """Returns the swap and coordinates of the word with the maximum score on the board given a set of swaps.

        Args:
            None
        
        Returns:
            tuple[Swap, list[Coordinates]]: Swap and Coordinates list of the word with the maximum score given the board state.
        """
        if self.swaps_left == 0:
            return (Swap(), self.best_move()) # HACK

        swaps = make_swap_set()

        max_score = 0
        max_coords_found = []
        swap_to_make = Swap()


        for _ in range(len(swaps)):
            print(".", end="")

        print("|")

        for swap in swaps:
            print(".", end="", flush=True)
            perform_swap(swap)

            coords = self.best_move()

            if score(coords) > max_score:
                max_score = score(coords)
                max_coords_found = coords
                swap_to_make = swap

            perform_swap(swap) # unswap

        print("|")
        return (swap_to_make, max_coords_found)
    
    def best_move(self):
        """Returns the coordinates of the word with the maximum score on the board.

        Args:
            None

        Returns:
            list[Corordinate]: 0-indexed coordinates of the word with the maximum score given the board state.
        """
        max_score = -1
        max_coords_found = []
        
        for i in range(len(self.letters)):
            for j in range(len(letters[i])):
                if letters[i][j] == "": continue

                coords = max_coords([(i,j)], avoid)

                if score(coords) > max_score:
                    max_coords_found = coords
                    max_score = score(coords)

        return max_coords_found

