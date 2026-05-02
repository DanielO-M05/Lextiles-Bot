"""
A Lextiles Solver
Author: Daniel Otto-Manzano
"""
from english_prefix_trie import is_prefix, is_word
import time
from solver_mcts import GreedySolver, MCTSSolver
from board import Board
from search_space import estimate_search_space

# .07 and 7 are pretty good times, speeding up for debugging
CHAR_TIME = .03
STR_TIME = .3

# The minimum length for a valid word
MIN_WORD_LENGTH = 3

scores = {
    "a": 2, "b": 6, "c": 7, "d": 5, "e": 2, "f": 10, "g": 5,
    "h": 10, "i": 2, "j": 16, "k": 14, "l": 3, "m": 8, "n": 2,
    "o": 2, "p": 9, "q": 22, "r": 2, "s": 4, "t": 3, "u": 2,
    "v": 12, "w": 12, "x": 18, "y": 12, "z": 20
}

letters = [
    ["s", "g", "o", "i", "n", "d"],
    ["v", "t", "n", "l", "o", "e"],
    ["j", "d", "l", "c", "t", "p"],
    ["x", "e", "r", "e", "r", "e"],
    ["t", "m", "a", "h", "g", "a"],
    ["s", "e", "l", "y", "a", "g"]
]

powerups = [
    ["", "", "", "", "", ""],
    ["", "", "", "", "", ""],
    ["", "", "10", "", "", ""],
    ["", "", "", "ts", "", "dw"],
    ["", "", "dl", "", "tw", ""],
    ["", "", "", "5", "", ""]
]

def talk(board, solver, verbose=True):
    """Runs the program! Helps you solve the puzzle.

    Args:
        board (Board): The board to solve.
        solver (SolverBase): The solver to use.
        verbose (bool): If True, uses typewriter printing and prompts for
                        input between moves. If False, prints moves
                        automatically without pausing.

    Returns:
        int: The total score achieved.
    """
    def out(s):
        """Print a line, typewriter-style if verbose, plain if not."""
        if verbose:
            typewrite_print(s)
        else:
            print(s)

    out("Hello, and welcome to the Lextiles Bot interface!")
    out("It appears that I've already been given the board state.")
    out("Let's go!")
    print()

    total_score = 0
    move_number = 1

    while True:
        board.grid_print(board.letters)
        swap, coords = solver.choose_move(board, verbose=verbose)

        if coords == []:
            break

        word = board.word_from_coords(coords, swap=swap)
        move_score = board.score(coords, swap=swap)

        print(f"Move {move_number} | Running score: {total_score}")
        print(f"Coords: {coords}")

        if swap:
            swap_coord1, swap_coord2 = swap
            out(f"Swap {board.word_from_coords([swap_coord1])} at {swap_coord1}"
                f" with {board.word_from_coords([swap_coord2])} at {swap_coord2}")

        out(f"Play '{word}' for a score of {move_score}.")
        print()

        if verbose:
            input("Press enter to continue. ").strip().lower()

        if swap:
            board.swaps_left -= 1  # TODO change to setter method
        total_score += move_score
        board.update_board(coords, swap=swap)
        move_number += 1

    out(f"I couldn't find any words with this board.")
    out(f"Congrats! We found a solution worth {total_score} points!")
    if verbose:
        out("Ciao!")

    return total_score


def typewrite_print(str, char_time=CHAR_TIME, str_time=STR_TIME):
    """Prints to the screen with delay between characters.

    Args:
        str (str): The string to be printed.
        char_time (float): The delay between characters.
        str_time (float): The delay after printing.
    """
    for char in str:
        print(char, end="", flush=True)
        time.sleep(char_time)
    time.sleep(str_time)
    print()


solver = MCTSSolver(n_candidates=10, n_rollouts=50)
board = Board(letters, powerups, scores, 3, MIN_WORD_LENGTH)

# estimate_search_space(board, samples_per_level=5)
talk(board, solver, verbose=True)