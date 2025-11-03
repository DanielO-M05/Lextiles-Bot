from coordinate import Coordinate
from swap import Swap

from english_prefix_trie import is_prefix, is_word


class Board:

    def __init__(self, letters, powerups, scores, swaps_left, min_word_length):
        self.letters = [row[:] for row in letters]   # copy grid
        self.powerups = [row[:] for row in powerups]
        self.scores = dict(scores)
        self.swaps_left = swaps_left
        self.NUM_ROWS = len(letters)
        self.NUM_COLS = len(letters[0]) if letters else 0
        self.MIN_WORD_LENGTH = min_word_length

    def letter_at(self, coord: Coordinate) -> str:
        return self.letters[coord.row][coord.col]

    def powerup_at(self, coord: Coordinate) -> str:
        return self.powerups[coord.row][coord.col]
    
    def best_move_with_swap(self):
        """Returns the swap and coordinates of the word with the maximum score on the board given a set of swaps.

        Args:
            None
        
        Returns:
            tuple[Swap, list[Coordinates]]: Swap and Coordinates list of the word with the maximum score given the board state.
        """
        if self.swaps_left == 0:
            return (Swap(), self.best_move()) # HACK

        swaps = self.make_swap_set()

        max_score = 0
        max_coords_found = []
        swap_to_make = Swap()


        for _ in range(len(swaps)):
            print(".", end="")

        print("|")

        for swap in swaps:
            print(".", end="", flush=True)
            self.perform_swap(swap)

            coords = self.best_move()

            if self.score(coords) > max_score:
                max_score = self.score(coords)
                max_coords_found = coords
                swap_to_make = swap

            self.perform_swap(swap) # unswap

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
                coord = Coordinate(i, j)
                if self.letter_at(coord) == "": continue

                coords = self.max_coords([coord])

                if self.score(coords) > max_score:
                    max_coords_found = coords
                    max_score = self.score(coords)

        return max_coords_found
    
       
    def max_coords(self, coords):
        """Returns the coordinates of the word with the maximum starting with the coordinates provided, except for any words specified.

        Args:
            coords (list[Coordinate]): Coordinates of the word so far.

        Returns:
            list[tuple[int, int]]: Coordinates of the word with the maximum score given the provided coorinates and global board state.
        """
        # TODO this function can be optimized if the trie is updated so words arent prefixes of themselves, because then the extension check can run conditionally
        last_coord = coords[-1] # The most recent coordinate
        max_word_coords = [] # The coordinates of the word found so far with the maximum score

        if is_word(self.word_from_coords(coords)) and len(coords) >= self.MIN_WORD_LENGTH:
            max_word_coords = coords

        # See if word can be extended
        for i_off in range(-1, 2):
            for j_off in range(-1, 2):
                next_coord = last_coord + (i_off, j_off)

                # Make sure path is valid
                if not next_coord.in_bounds(self.NUM_ROWS, self.NUM_COLS) or next_coord in coords or self.letter_at(next_coord) == "" : continue
                t_word = self.word_from_coords(coords) + self.letter_at(next_coord) # t is for temp, the set of letters we are temporarily considering

                if is_prefix(t_word): # If this temporary word is a prefix or word, make the recursive call
                    t_coords = coords + [next_coord]
                    p_coords = self.max_coords(t_coords)

                    if self.score(p_coords) > self.score(max_word_coords):
                        max_word_coords = p_coords

        return max_word_coords
    

    def word_from_coords(self, coords, swap=Swap()):
        """Returns the word represented by a set of coordinates on the board, optionally first performing a swap.

        Args:
            coords (list[tuple[int, int]]): 0-indexed coordinates (row, col) of the word on the board.
            swap (frozenset{tuple[int,int], tuple[int,int]}): 0-indexed coordinates (row, col) of the coordinates to be swapped before calculation.

        Returns:
            str: The word represented by the swap and set of coordinates on the board.
        """
        self.perform_swap(swap)
        word = ""

        for i in range(len(coords)):
            coord = coords[i]
            word = word + self.letter_at(coord)

        self.perform_swap(swap) # Return board state to normal
        return word
    
    
    def score(self, coords, swap=Swap()):
        """Returns the score of a word represented by a set of coordinates on the board, optionally first performing a swap.

        Args:
            coords (list[Coordinate]): Coordinates of the word on the board.
            swap (Swap): Swap to be swapped before calculation.

        Returns:
            int: The score of the word

        Raises:
            RuntimeError: If one of the coordinates does not have a letter. 
        """
        if coords == []: return 0

        self.perform_swap(swap)

        score = 0
        multiplier = 1

        for coord in coords:

            if self.letter_at(coord) == "": 
                raise RuntimeError("It's so over. One of the coordinates is empty.")

            score += self.scores[self.letter_at(coord)]

            # Check for powerup
            if self.powerup_at(coord) == "ds":
                score *= 2
            elif self.powerup_at(coord) == "ts":
                score *= 3
            elif self.powerup_at(coord) == "dw":
                multiplier *= 2
            elif self.powerup_at(coord) == "tw":
                multiplier *= 3
            elif self.powerup_at(coord) == "dl":
                score += self.scores[self.letter_at(coord)]
            elif self.powerup_at(coord) == "tl":
                score += self.scores[self.letter_at(coord)] * 2
            elif self.powerup_at(coord) == "5":
                score += 5
            elif self.powerup_at(coord) == "10":
                score += 10
            elif self.powerup_at(coord) == "15":
                score += 15

        self.perform_swap(swap) # unswap
            
        return score * multiplier

    def perform_swap(self, swap):
        """Mutate the board to represent the result of a swap.

        Args:
            swap (Swap): Swap to be swapped.

        Returns:
            None: This function mutates letters
        """
        # Handle identity swap
        if not swap:
            return 
        
        coord1, coord2 = swap
        row1, col1 = coord1
        row2, col2 = coord2

        temp = self.letters[row1][col1]
        self.letters[row1][col1] = self.letters[row2][col2]
        self.letters[row2][col2] = temp


    def make_swap_set(self):
        """Returns a list of swap that are the coordinates of all unique possible swaps given the board state.

        Args:
            None

        Returns:
            list[Swap]: The list of Swaps of all unique possible swaps given the board state.

        """
        swaps = set()
        for i in range(self.NUM_ROWS):
            for j in range(self.NUM_COLS):
                for i_off, j_off in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                    coord1 = Coordinate(i, j)
                    coord2 = coord1 + (i_off, j_off)

                    if not coord2.in_bounds(self.NUM_ROWS, self.NUM_COLS) or self.letter_at(coord1) == "" or self.letter_at(coord2) == "" or self.letter_at(coord1) == self.letter_at(coord2): continue

                    swap = Swap((coord1, coord2))
                    swaps.add(swap) # Valid swap, add it

        swaps = list(swaps)
        swaps.insert(0, Swap()) # NOTE We are putting the identity set first so that in case of a tie, the case with no swap is put in first
        print(swaps)
        return swaps
    

    def grid_print(self, grid, padding=" "):
        """Prints a grid with some padding to make it look nice.

        Args:
            grid (list[list[strings]]): The grid to be printed.
            padding, optional (str): The string to pad the grid with.

        Returns:
            None: This function prints to the terminal.
        """
        grid_copy = [["" for _ in range(len(grid[i]))] for i in range(len(grid))]
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if self.letters[i][j] == "":
                    grid_copy[i][j] = padding
                else:
                    grid_copy[i][j] = self.letters[i][j]

        for i in range(len(grid_copy)):
            print(grid_copy[i])

    def update_board(self, coords, swap=Swap()):
        """Mutates letters to reflect a word being played, with an optional swap before it. 

        Args:
            coords (list[tuple[int, int]]): Coordinates of the word being played.

        Returns:
            None: mutates letters
        """
        self.perform_swap(swap)
        for i in range(6):
            for j in range(6):
                coord = Coordinate(i, j)
                if coord in coords:
                    self.letters[i][j] = ""

        self.collapse_down()
        self.collapse_right()

    def collapse_down(self):
        """Mutates letters to move letters down

        Args:
            None: mutates letters

        Returns:
            None: mutates letters
        """
        # Iterate through each column
        for i in range(self.NUM_COLS):
            new_col = [] # Array of letters in a column, will be shifted down

            # Get all values in the column
            for j in range(self.NUM_ROWS):
                if self.letters[self.NUM_ROWS-j-1][i] != "":
                    new_col.append(self.letters[self.NUM_ROWS-j-1][i])

            # Put new column in bottom
            for j in range(len(new_col)):
                self.letters[self.NUM_ROWS-j-1][i] = new_col[j]

            # Put blanks on top:
            for j in range(self.NUM_ROWS-len(new_col)):
                self.letters[j][i] = ""

    def collapse_right(self):
        """Mutates the global board to move columns to the right where there are gaps

        Args:
            None: mutates global board state, assumed to have already been collapsed down.

        Returns:
            None: mutates global board state
        """
        col_to_shift = [] # List of indices of non-empty cols 

        # Populate col_to_shift
        for i in range(self.NUM_COLS - 1, -1, -1):
            if self.letters[self.NUM_ROWS - 1][i] != "":
                col_to_shift.append(i)

        # Iterate through columns and put them as far right as possible
        cur_col = self.NUM_COLS - 1
        for col in col_to_shift:
            for i in range(self.NUM_ROWS):
                self.letters[i][cur_col] = self.letters[i][col]

            cur_col -= 1

        # Clear all the unneeded columns on the left side
        for i in range(self.NUM_COLS-len(col_to_shift)):
            for j in range(self.NUM_ROWS):
                self.letters[j][i] = ""




