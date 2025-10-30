from coordinate import Coordinate
from swap import Swap

from english_prefix_trie import is_prefix, is_word
from wordfreq import zipf_frequency

class Board:
    def __init__(self, letters: list[list[str]], powerups: list[list[str]], scores: dict[str, int], min_word_length=3):
        self.letters = [row[:] for row in letters]   # copy grid
        self.powerups = [row[:] for row in powerups]
        self.scores = dict(scores)
        self.num_rows = len(letters)
        self.num_cols = len(letters[0]) if letters else 0
        self.min_word_length = min_word_length

    def __getitem__(self, coord: Coordinate) -> str:
        return self.letters[coord.row][coord.col]

    def powerup(self, coord: Coordinate) -> str:
        return self.powerups[coord.row][coord.col]

    def in_bounds(self, coord: Coordinate) -> bool:
        return 0 <= coord.row < self.num_rows and 0 <= coord.col < self.num_cols
    
    def word_from_coords(self, coords, swap=Swap.identity()):
        self.perform_swap(swap)
        word = ""
        for coord in coords:
            word += self[coord]
        self.perform_swap(swap)
        return word

    def score(self, coords, swap=Swap.identity()):
        if not coords:
            return 0
        
        self.perform_swap(swap)

        score = 0
        mult = 1

        for coord in coords:
            ch = self[coord]
            if ch == "":
                raise RuntimeError("Empty tile in coords")

            score += self.scores[ch]

            pu = self.powerup(coord)
            if pu == "ds": score *= 2
            elif pu == "ts": score *= 3
            elif pu == "dw": mult *= 2
            elif pu == "tw": mult *= 3
            elif pu == "dl": score += self.scores[ch]
            elif pu == "tl": score += self.scores[ch] * 2
            elif pu.isdigit(): score += int(pu)

        self.perform_swap(swap)

        return score * mult
    
    def best_move(self, avoid=[]):
        """
        Returns the coordinates of the highest-scoring word on the board,
        excluding any words in `avoid`.
        """
        best_score = -1
        best_coords: list[Coordinate] = []

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.letters[row][col] == "":
                    continue

                start_coord = Coordinate(row, col)
                candidate = self.max_coords([start_coord], avoid)
                candidate_score = self.score(candidate)

                if candidate_score > best_score:
                    best_coords = candidate
                    best_score = candidate_score

        return best_coords

    def max_coords(self, coords: list[Coordinate], avoid=[]):
        """
        Returns the best-scoring word obtainable by extending the given coordinate path.

        Args:
            coords (list[Coordinate]): Coordinates of the current word path.
            avoid (list[str] | None): Words that should not count as valid results.

        Returns:
            list[Coordinate]: Coordinates of the best word found.
        """
        last_coord = coords[-1]
        current_word = self.word_from_coords(coords)
        best_coords: list[Coordinate] = []

        # If current is a valid completed word, track it
        if (is_word(current_word)
            and current_word not in avoid
            and len(coords) >= self.min_word_length):
            best_coords = coords

        # Try extending by adjacent tiles (-1 to +1 in both directions)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue

                next_coord = last_coord + (dx, dy)

                # Bounds, visited, blank tile check
                if (not next_coord.in_bounds(self.num_rows, self.num_cols)
                    or next_coord in coords
                    or self.letters[next_coord.row][next_coord.col] == ""):
                    continue

                next_word = current_word + self.letters[next_coord.row][next_coord.col]

                # Extend only if it's a valid prefix
                if is_prefix(next_word):
                    candidate = self.max_coords(coords + [next_coord], avoid)

                    if (self.score(candidate) > self.score(best_coords)
                        and self.word_from_coords(candidate) not in avoid):
                        best_coords = candidate

        return best_coords


    # put these 2 into one function
    def swap(self, c1: Coordinate, c2: Coordinate):
        self.letters[c1.row][c1.col], self.letters[c2.row][c2.col] = \
            self.letters[c2.row][c2.col], self.letters[c1.row][c1.col]

    def perform_swap(self, swap: Swap):
        if swap:
            self.swap(swap.coord1, swap.coord2)

    def possible_swaps(self) -> list[Swap]:
        swaps = set()

        for r in range(self.num_rows):
            for c in range(self.num_cols):
                coord = Coordinate(r, c)
                if self.letters[r][c] == "":
                    continue

                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        new = Coordinate(nr, nc)
                        if not new.in_bounds(self.num_rows, self.num_cols):
                            continue
                        if self.letters[nr][nc] == "":
                            continue
                        if self.letters[nr][nc] == self.letters[r][c]:
                            continue

                        swaps.add(Swap(coord, new))

        return [Swap.identity()] + list(swaps) # NOTE We are putting the identity set first so that in case of a tie, the case with no swap is put in first

    def play_word(self, coords: list[Coordinate], swap=Swap.identity()):
        """Clear letters and collapse board."""
        self.perform_swap(swap)

        # remove letters
        for r, c in coords:
            self.letters[r][c] = ""

        self._collapse_down()
        self._collapse_right()

    def _collapse_down(self):
        """Row collapse down."""
        # Iterate through each column
        for i in range(self.num_cols):
            new_col = []  # Array of letters in a column, will be shifted down

            # Get all non-empty values in the column, bottom to top
            for j in range(self.num_rows):
                if self.letters[self.num_rows - j - 1][i] != "":
                    new_col.append(self.letters[self.num_rows - j - 1][i])

            # Put new column in bottom
            for j in range(len(new_col)):
                self.letters[self.num_rows - j - 1][i] = new_col[j]

            # Put blanks on top
            for j in range(self.num_rows - len(new_col)):
                self.letters[j][i] = ""


    def _collapse_right(self):
        """Column collapse to the right."""
        cols_with_tiles = [c for c in range(self.num_cols) if self.letters[self.num_rows-1][c] != ""]
        cur = self.num_cols - 1

        # move non-empty cols to the right
        for c in reversed(cols_with_tiles):
            for r in range(self.num_rows):
                self.letters[r][cur] = self.letters[r][c]
            cur -= 1

        # blank any remaining left columns
        for c in range(cur + 1):
            for r in range(self.num_rows):
                self.letters[r][c] = ""

    def print_board(self, pad=" "):
        for row in self.letters:
            print([cell if cell != "" else pad for cell in row])
