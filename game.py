"""
A Lextiles Solver
Author: Daniel Otto-Manzano
"""


import time
from coordinate import Coordinate
from swap import Swap
from board import Board

CHAR_TIME = .03
STR_TIME = .3

class Game:
    def __init__(self, letters, powerups, scores, swaps_left=3, min_word_length=3):
        self.board = Board(letters, powerups, scores)
        self.swaps_left = swaps_left
        self.min_word_length = min_word_length

    # ----------- UI Helpers -----------

    def typewrite_print(self, s, char_time=CHAR_TIME, str_time=STR_TIME):
        for ch in s:
            print(ch, end="", flush=True)
            time.sleep(char_time)
        time.sleep(str_time)
        print()

    def print_board(self):
        for row in self.board.letters:
            print(" ".join(cell if cell else "_" for cell in row))
        print()

    # ----------- Core Search w Swap -----------

    def best_move_with_swap(self, avoid):
        if self.swaps_left == 0:
            return Swap.identity(), self.board.best_move(avoid)

        swaps = self.board.possible_swaps()
        max_score = -1
        best_coords = []
        best_swap = Swap.identity()

        print("Checking swaps...")
        for swap in swaps:
            print(".", end="", flush=True)

            self.board.perform_swap(swap)
            coords = self.board.best_move(avoid)
            s = self.board.score(coords)
            self.board.perform_swap(swap)  # undo

            if s > max_score:
                max_score = s
                best_coords = coords
                best_swap = swap

        print("|")
        return best_swap, best_coords

    # ----------- Main Loop -----------

    def run(self):
        # self.typewrite_print("Hello, and welcome to the Lextiles Bot interface!")
        # self.typewrite_print("It appears that I've already been given the board state.")
        self.typewrite_print("Let's go!\n")

        avoid = []
        total_score = 0

        while True:
            self.print_board()
            swap, coords = self.best_move_with_swap(avoid)

            if not coords:
                break

            print(f"Score so far: {total_score}")
            print(f"Coords: {coords}")

            if swap:
                c1, c2 = swap.coord1, swap.coord2
                print(f"Swap coords: {c1} <-> {c2}")
                self.typewrite_print(
                    f"Swap {self.board[c1]} at {c1} with "
                    f"{self.board[c2]} at {c2}"
                )

            word = self.board.word_from_coords(coords, swap=swap)
            score = self.board.score(coords, swap=swap)
            self.typewrite_print(f"Play '{word}' for {score} points.\n")

            ans = input("Could you play this word? (Y/N) ").strip().lower()
            while ans not in ("y", "n"):
                ans = input("(Y/N) ").strip().lower()

            if ans == "n":
                self.typewrite_print("Alright, trying next best word.")
                avoid.append(word)
                continue

            if swap:
                self.swaps_left -= 1

            total_score += score
            self.board.play_word(coords, swap=swap)

        self.typewrite_print("No more words available.")
        self.typewrite_print(f"Solution total: {total_score} points!")
        self.typewrite_print("Ciao!")
