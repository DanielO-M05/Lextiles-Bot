from coordinate import Coordinate
from swap import Swap

from english_prefix_trie import is_prefix, is_word


class Board:

    

    def __init__(self, letters, powerups, scores, swaps_left, min_word_length):
        self.letters = letters
        self.powerups = powerups
        self.scores = scores
        self.swaps_left = swaps_left
        self.NUM_ROWS = len(letters)
        self.NUM_COLS = len(letters[0]) if letters else 0
        self.MIN_WORD_LENGTH = min_word_length

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
            for j in range(len(self.letters[i])):
                if self.letters[i][j] == "": continue

                coords = max_coords([(i,j)])

                if score(coords) > max_score:
                    max_coords_found = coords
                    max_score = score(coords)

        return max_coords_found
    
       
    def max_coords(self, coords, avoid = []):
        """Returns the coordinates of the word with the maximum starting with the coordinates provided, except for any words specified.

        Args:
            coords (list[Coordinate]): Coordinates of the word so far.

        Returns:
            list[tuple[int, int]]: Coordinates of the word with the maximum score given the provided coorinates and global board state.
        """
        # TODO this function can be optimized if the trie is updated so words arent prefixes of themselves, because then the extension check can run conditionally
        last_coord = coords[-1] # The most recent coordinate
        max_word_coords = [] # The coordinates of the word found so far with the maximum score

        if is_word(word_from_coords(coords)) and word_from_coords(coords) not in avoid and len(coords) >= self.MIN_WORD_LENGTH:
            max_word_coords = coords

        # See if word can be extended
        for i_off in range(-1, 2):
            for j_off in range(-1, 2):
                next_coord = last_coord + (i_off, j_off)

                # Make sure path is valid
                if not next_coord.in_bounds(self.NUM_ROWS, self.NUM_COLS) or next_coord in coords or self.letters[next_coord] == "" : continue
                t_word = word_from_coords(coords) + letters[x][y] # t is for temp, the set of letters we are temporarily considering

                if is_prefix(t_word): # If this temporary word is a prefix or word, make the recursive call
                    t_coords = coords + [(x,y)]
                    p_coords = max_coords(t_coords, avoid)

                    if score(p_coords) > score(max_word_coords) and word_from_coords(p_coords) not in avoid:
                        max_word_coords = p_coords

        return max_word_coords


