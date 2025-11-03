'''
A Lextiles Solver
Author: Daniel Otto-Manzano
'''

from english_prefix_trie import is_prefix, is_word
import time

from board import Board

# TODO: Format to docstrings
# TODO: Change dictionary to include more words (specifically plurals like "mobiles" or "apples")
# TODO: Wait coordinates should definitely be an object... what the hell is frozenset{tuple[int, int], tuple[int, int]}

# .07 and 7 are pretty good times, speeding up for debugging
CHAR_TIME = .03
STR_TIME = .3

# Constants for board dimensions
NUM_ROW = 6
NUM_COL = 6

# The minimum length for a valid word
MIN_WORD_LENGTH = 3

swaps_left = 3
count = 0

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

def talk(board):
    """Runs the program! Helps you solve the puzzle.

    Args:
        None: uses global state

    Returns:
        None: prints to terminal
    """
    typewrite_print("Hello, and welcome to the Lextiles Bot interface!")
    typewrite_print("It appears that I've already been given the board state.")
    typewrite_print("Let's go!")
    print()

    coords = []
    total_score = 0

    while True:

        board.grid_print(board.letters) # TODO I don't like this
        swap, coords = board.best_move_with_swap()
        if coords == []: break # No more words left

        print("Score: " + str(total_score))
        print("Coords " + str(coords))

        if swap:
            swap_coord1, swap_coord2 = swap
            print("Swap coords are " + str(swap_coord1) + " and " + str(swap_coord2))        
            typewrite_print("Swap " + board.word_from_coords([swap_coord1]) + " at coordinate " + str(swap_coord1) + " with " 
                            + board.word_from_coords([swap_coord2]) + " at coordinate " + str(swap_coord2))
            
        typewrite_print("Play " + board.word_from_coords(coords, swap=swap) + " for a score of " + str(board.score(coords, swap=swap)) + ".")
        print()

        ans = input("Press enter to continue. ").strip().lower()

        if swap: board.swaps_left -= 1 # TODO change to setter method

        total_score += board.score(coords, swap=swap)
        board.update_board(coords, swap=swap)

    typewrite_print("I couldn't find any words with this board.")
    typewrite_print("Congrats! We found a solution worth " + str(total_score) + " points!")
    typewrite_print("Ciao!")
      
def typewrite_print(str, char_time=CHAR_TIME, str_time=STR_TIME):
    """Prints to the screen with delay between characters

    Args:
        str (str): The string to be printed
        char_time, optional (float): The delay between characters
        str_time, optional (float): The delay after printing

    Returns:
        None: Prints to the terminal
    """
    for char in str:
        print(char, end="", flush=True)
        time.sleep(char_time)

    time.sleep(str_time) # Pause between statements
    print()

board = Board(letters, powerups, scores, swaps_left, MIN_WORD_LENGTH)

talk(board)