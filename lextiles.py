'''
A Lextiles Solver
Author: Daniel Otto-Manzano
'''

from english_prefix_trie import is_prefix, is_word

from wordfreq import zipf_frequency
import time

# TODO: Format to docstrings
# TODO: Change dictionary to include more words (specifically plurals like "mobiles" or "apples")
# BUG: in notes app, but swap set needs to be revised a little to avoid unnecessary swapping

# .07 and 7 are pretty good times, speeding up for debugging
CHAR_TIME = .03
STR_TIME = .3

# Constants for board dimensions
NUM_ROW = 6
NUM_COL = 6

# The minimum length for a valid word
MIN_WORD_LENGTH = 3

swaps_left = 3

# TODO: these scores are not fully updated, I don't know all of their values
scores = {
    "a": 2, "b": 6, "c": 7, "d": 5, "e": 2, "f": 10, "g": 5,
    "h": 10, "i": 2, "j": 16, "k": 14, "l": 3, "m": 8, "n": 2,
    "o": 2, "p": 9, "q": -1, "r": 2, "s": 4, "t": 3, "u": 2,
    "v": 12, "w": 12, "x": -1, "y": 12, "z": -1
}

# Note that throughout the run of the program, this board is mutated and restored
# So, this does introduce global state in some limited capacity
# If I feel like it later, I could just make this a constant and have copies be passed around in functions
# Note that as it stands, mutable variable letters is better for runtime because it avoids having to constantly make copies
# Functions are using letters all the time, so these deep copies may certainly add up
# I'm keeping it like this for now, but this a consideration for later to implement a better practice
letters = [
    ["e", "d", "i", "s", "e", "c"],
    ["t", "s", "r", "n", "e", "l"],
    ["d", "p", "e", "n", "y", "t"],
    ["e", "a", "e", "p", "t", "u"],
    ["i", "l", "n", "e", "p", "o"],
    ["a", "n", "r", "t", "m", "c"]
] # 6 by 6 grid of strings, either "" or the letter in the cell


powerups = [
    ["", "", "", "", "", ""],
    ["", "", "", "", "", ""],
    ["", "", "5", "", "", ""],
    ["", "", "", "dw", "", "ts"],
    ["", "", "15", "", "10", ""],
    ["", "", "", "tw", "", ""]
] # 6 by 6 grid of strings, either "" or the power up in the cell, eg "DS", "TL"

# We utilize a greedy approach
# First, we find the best possible word on the board, with no swaps
    # Note this is **not** guaranteed to find the best word, it uses heuristics to reduce the search space
    # It's not an easy calculation, but I want to say that brute force has many millions of possible paths
    # This is reduced because not all paths are words, but either way it still takes too long

# Lets the bot have a word with you
def talk():
    global swaps_left # HACK

    typewrite_print("Hello, and welcome to the Lextiles Bot interface!")
    typewrite_print("It appears that I've already been given the board state.")
    typewrite_print("Let's go!")
    print()

    avoid = []
    coords = []
    total_score = 0

    while True:

        grid_print(letters)
        swap, coords = best_move_with_swap(avoid=avoid)
        if coords == []: break

        print("Score: " + str(total_score))
        print("Coords " + str(coords))

        if swap:
            swap_coord1, swap_coord2 = swap
            print("Swap coords are " + str(swap_coord1) + " and " + str(swap_coord2))        
            typewrite_print("Swap " + word_from_coords([swap_coord1]) + " at coordinate " + str(swap_coord1) + " with " 
                            + word_from_coords([swap_coord2]) + " at coordinate " + str(swap_coord2))
            
            perform_swap(swap) # HACK Coords thing only works if you take into account the swap going on 
            typewrite_print("Play " + word_from_coords(coords) + " for a score of " + str(score(coords)) + ".")
            perform_swap(swap)
            print()
        else:
            typewrite_print("Play " + word_from_coords(coords) + " for a score of " + str(score(coords)) + ".")
            print()

        ans = input("Could you play this word? (Y/N)").strip().lower()
        while ans != "y" and ans != "n":
            ans = input("Could you play this word? (Y/N)").strip().lower()

        if ans == "n":
            typewrite_print("Alright, let's try the next best word.")
            perform_swap(swap) # HACK Coords thing only works if you take into account the swap going on 
            avoid.append(word_from_coords(coords))
            perform_swap(swap) # HACK Coords thing only works if you take into account the swap going on 
            continue

        if swap: swaps_left -= 1

        perform_swap(swap) # TODO should this be in update_board, it should be update_board(swap, coords)
        total_score += score(coords)
        update_board(coords)

    typewrite_print("I couldn't find any words with this board.")
    typewrite_print("Congrats! We found a solution worth " + str(total_score) + " points!")
    typewrite_print("Ciao!")

# Calls max coords with every swap permutation?
# Returns tuple (swap, coords) where swap is a set of coord tuples of form set{(a,b),(c,d)} and coords is a list of coords [(a,b), (c,d), ...]
def best_move_with_swap(avoid=[]):
    global swaps_left # HACK
    if swaps_left == 0:
        return (frozenset(), best_move(avoid)) # HACK

    swaps = make_swap_set()
    swaps.add(frozenset()) # swap set + identity swap (no swap) HACK this is a special case needed to be handled by perform swap

    max_score = 0
    max_coords_found = []
    swap_to_make = set()


    for _ in range(len(swaps)):
        print(".", end="")

    print("|")

    for swap in swaps:
        print(".", end="", flush=True)
        perform_swap(swap)

        coords = best_move(avoid)

        if score(coords) > max_score:
            max_score = score(coords)
            max_coords_found = coords
            swap_to_make = set(swap)

        perform_swap(swap) # unswap

    print("|")
    return (swap_to_make, max_coords_found)
        
# Prints like a typewriter
def typewrite_print(str, char_time=CHAR_TIME, str_time=STR_TIME):
    for char in str:
        print(char, end="", flush=True)
        time.sleep(char_time)

    time.sleep(str_time) # Pause between statements
    print()

def update_board(coords):

    for i in range(6):
        for j in range(6):
            if (i,j) in coords:
                letters[i][j] = ""

    collapse_down()
    collapse_right()

# TODO: test
def collapse_down():
    # Iterate through each column
    for i in range(NUM_COL):
        new_col = [] # Array of letters in a column, will be shifted down

        # Get all values in the column
        for j in range(NUM_ROW):
            if letters[NUM_ROW-j-1][i] != "":
                new_col.append(letters[NUM_ROW-j-1][i])

        # Put new column in bottom
        for j in range(len(new_col)):
            letters[NUM_ROW-j-1][i] = new_col[j]

        # Put blanks on top:
        for j in range(NUM_ROW-len(new_col)):
            letters[j][i] = ""

# TODO Test
# Prereq: We assume we have already collapsed all the columns down
def collapse_right():
    col_to_shift = [] # List of indices of non-empty cols 

    # Populate col_to_shift
    for i in range(NUM_COL - 1, -1, -1):
        if letters[NUM_ROW - 1][i] != "":
            col_to_shift.append(i)

    # Iterate through columns and put them as far right as possible
    cur_col = NUM_COL - 1
    for col in col_to_shift:
        for i in range(NUM_ROW):
            letters[i][cur_col] = letters[i][col]

        cur_col -= 1

    # Clear all the unneeded columns on the left side
    for i in range(NUM_COL-len(col_to_shift)):
        for j in range(NUM_ROW):
            letters[j][i] = ""

# Description: finds the best word on the board
# Params: optionally include words not to count
# Returns: the coordinate sequence (arr[tuple(x,y)]) of the best word
def best_move(avoid = []):
    max_score = -1
    max_coords_found = []
    for i in range(len(letters)):
        for j in range(len(letters[i])):
            if letters[i][j] == "": continue

            coords = max_coords([(i,j)], avoid)

            if score(coords) > max_score:
                max_coords_found = coords
                max_score = score(coords)

    return max_coords_found
      
# Description: Given a word in progress and the most recent index, return the coordinates of the maximum word, recursively
# Params: coords, row, col
# Returns: Coordinate sequence of the maximum word possible given parameters
def max_coords(coords, avoid = []):
    """Returns the coordinates of the word with the maximum score on the board, except for any words specified.

    Args:
        coords (list[tuple[int, int]]): 0-indexed coordinates (row, col) of the word so far.
        avoid (list[str]): Strings that should not count as valid words.

    Returns:
        list[tuple[int, int]]: 0-indexed coordinates (row, col) of the word with the maximum score given the board state.
    """
    i, j = coords[-1]
    cur_word_coords = []

    if is_word(word_from_coords(coords)) and word_from_coords(coords) not in avoid and len(coords) >= MIN_WORD_LENGTH:
        cur_word_coords = coords

    # See if word can be extended
    for i_off in range(-1, 2):
        for j_off in range(-1, 2):
            x, y = i + i_off, j + j_off

            # Make sure path is valid
            if not in_bounds(x, y) or (x,y) in coords or letters[x][y] == "" : continue
            t_word = word_from_coords(coords) + letters[x][y]

            if is_prefix(t_word) or is_word(t_word):
                t_coords = coords + [(x,y)]
                p_coords = max_coords(t_coords, avoid)

                if score(p_coords) > score(cur_word_coords) and word_from_coords(p_coords) not in avoid:
                    cur_word_coords = p_coords

    return cur_word_coords

# Params: x and y coordinate integers
# Returns: True if both in range [0,5], false otherwise
def in_bounds(x, y):
    return x >= 0 and x <= NUM_ROW - 1 and y >= 0 and y <= NUM_COL - 1

# Params: coordinate sequence
# Returns: a string that corresponds to the letters in the coordinate positions
def word_from_coords(coords):
    word = ""

    for i in range(len(coords)):
        x, y = coords[i]
        word = word + letters[x][y]

    return word

# Params: coordinate sequence
# Returns: The score of the word formed by the sequence
def score(coords):
    if coords == []: return 0

    score = 0
    multiplier = 1

    for i in range(len(coords)):
        x, y = coords[i]

        # HACK
        if letters[x][y] == "": return 0

        score += scores[letters[x][y]]

        # Check for powerup
        if powerups[x][y] == "ds":
            score *= 2
        elif powerups[x][y] == "ts":
            score *= 3
        elif powerups[x][y] == "dw":
            multiplier *= 2
        elif powerups[x][y] == "tw":
            multiplier *= 3
        elif powerups[x][y] == "dl":
            score += scores[letters[x][y]]
        elif powerups[x][y] == "tl":
            score += scores[letters[x][y]] * 2
        elif powerups[x][y] == "5":
            score += 5
        elif powerups[x][y] == "10":
            score += 10
        elif powerups[x][y] == "15":
            score += 15
        
    return score * multiplier

# Takes 2d grid of strings and displays it nicely
def grid_print(grid):
    # We're padding by one space, but we could make this variable
    grid_copy = [["" for _ in range(len(grid[i]))] for i in range(len(grid))]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if letters[i][j] == "":
                grid_copy[i][j] = " "
            else:
                grid_copy[i][j] = letters[i][j]

    for i in range(len(grid_copy)):
        print(grid_copy[i])

# Returns a set of frozensets of tuples that correspond to possible swaps
# So will be like: { {(a,b), (c,d)}, {(w,x), (y,z)} } meaning coords (a,b) swaps with (c,d) and (w,x) with (y,z)
# Note sets used because order doesn't matter in a swap
# There may be a faster way to do this, but n is small so it doesn't matter. 
    # Also, if I rly cared about speed, I could generate this once and just use it
def make_swap_set():
    swaps = set()
    for i in range(NUM_ROW):
        for j in range(NUM_COL):
            for i_off in range(-1, 2):
                for j_off in range(-1, 2):

                    x, y = i + i_off, j + j_off
                    if not in_bounds(x, y) or (x,y) == (i,j) or letters[x][y] == "" or letters[i][j] == "": continue

                    swap = frozenset([(i,j), (x,y)])
                    swaps.add(swap) # Valid swap, add it

    return swaps

# Mutates letters[][] and swaps the two coordinates given as a parameter of set{(a,b), (c,d)}
def perform_swap(swap):
    # Handle identity swap
    if not swap:
        return 
    
    coord1, coord2 = swap
    row1, col1 = coord1
    row2, col2 = coord2

    temp = letters[row1][col1]
    letters[row1][col1] = letters[row2][col2]
    letters[row2][col2] = temp

talk()
