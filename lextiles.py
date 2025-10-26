'''
A Lextiles Solver
Author: Daniel Otto-Manzano
'''

from english_prefix_trie import is_prefix

from wordfreq import zipf_frequency

# TODO: Make this whole thing a class
# TODO: Format to docstrings
# TODO: variables snake case and functions camel case?
# TODO: make trie from wordfreq and not nltk for consistency

WORD_POPULARITY = 1.5

# TODO: these scores are not fully updated, I don't know all of their values
scores = {
    "a": -1, "b": -1, "c": -1, "d": 5, "e": 2, "f": 10, "g": 5,
    "h": 10, "i": 2, "j": -1, "k": -1, "l": 3, "m": 8, "n": 2,
    "o": 2, "p": 9, "q": -1, "r": 2, "s": 4, "t": 3, "u": 2,
    "v": -1, "w": -1, "x": -1, "y": 12, "z": -1
}

letters = [
    ["o", "n", "i", "s", "t", "e"],
    ["e", "r", "v", "i", "t", "d"],
    ["h", "g", "n", "u", "h", "i"],
    ["i", "e", "y", "t", "n", "u"],
    ["m", "l", "t", "f", "s", "m"],
    ["e", "o", "n", "o", "p", "f"]
] # 6 by 6 grid of strings, either "" or the letter in the cell


powerups = [
    ["", "", "", "", "", ""],
    ["", "", "", "", "dw", ""],
    ["", "", "15", "", "", ""],
    ["", "", "", "10", "", "ts"],
    ["", "", "dl", "", "", ""],
    ["", "", "", "", "", ""]
] # 6 by 6 grid of strings, either "" or the power up in the cell, eg "DS", "TL"

# We utilize a greedy approach
# First, we find the best possible word on the board, with no swaps
    # Note this is **not** guaranteed to find the best word, it uses heuristics to reduce the search space
    # It's not an easy calculation, but I want to say that brute force has many millions of possible paths
    # This is reduced because not all paths are words, but either way it still takes too long

def solve():
    print(letters)
    coords = best_move()

    while coords != []:
        print(coords)
        print(word_from_coords(coords))
        print()

        update_board(coords)

        print(letters)

        coords = best_move()

def update_board(coords):

    for i in range(6):
        for j in range(6):
            if (i,j) in coords:
                letters[i][j] = ""

    print("before collapse")
    print(letters)

    collapse_down()
    collapse_right()

def collapse_down():
    for i in range(len(letters[0])):
        new_col = []

        for j in range(6):
            if letters[5-j][i] != "":
                new_col.append(letters[5-j][i])

        # Put new col in bottom
        for j in range(len(new_col)): # TODO change magic number 6 into ROW
            letters[5-j][i] = new_col[j]

        # Put blanks on top:
        for j in range(6-len(new_col)):
            letters[j][i] = ""

def collapse_right(): # TODO: all the const stuff + idk if this is right
    for i in range(5, 0, -1): # TODO: 5 = COL - 1
        offset = 0
        while letters[5][i-offset] == "":
            offset += 1

        for i in range(6-offset):
            for j in range(6):
                letters[j][5-i] = letters[j][5-offset-i]

    # Upate i in special manner?
    


# Description: finds the best word on the board
# Params: none
# Returns: the coordinate sequence (arr[tuple(x,y)]) of the best word
def best_move():
    max_score = -1
    max_coords_found = []
    for i in range(len(letters)):
        for j in range(len(letters[i])):
            if letters[i][j] == "": continue

            coords = max_coords([(i,j)], i, j)

            if score(coords) > max_score:
                max_coords_found = coords
                max_score = score(coords)

    return max_coords_found
      
# Note: should prob rename this to max_coords
# Description: Given a word in progress and the most recent index, return the coordinates of the maximum word, recursively
# Params: coords, row, col
# Returns: Coordinate sequence of the maximum word possible given parameters
def max_coords(coords, i, j):
    cur_word_coords = []

    if is_word(word_from_coords(coords)):
        cur_word_coords = coords

    if not is_prefix(word_from_coords(coords)):
        if word_from_coords(coords) == "thump": print("bruhhhh")
        return cur_word_coords
    else: # Check if the word can be extended
        for i_off in range(-1, 2):
            for j_off in range(-1, 2):
                x, y = i + i_off, j + j_off

                # Make sure path is valid
                if not in_bounds(x, y) or (x,y) in coords or letters[x][y] == "" : continue
                t_word = word_from_coords(coords) + letters[x][y]

                if is_prefix(t_word) or is_word(t_word):
                    t_coords = coords + [(x,y)]
                    p_coords = max_coords(t_coords, x, y)

                    if score(p_coords) > score(cur_word_coords):
                        cur_word_coords = p_coords

    return cur_word_coords


def is_word(s: str) -> bool:
    return zipf_frequency(s.lower(), 'en') > WORD_POPULARITY

# Params: x and y coordinate integers
# Returns: True if both in range [0,5], false otherwise
def in_bounds(x, y):
    return x >= 0 and x <= 5 and y >= 0 and y <= 5

# Params: coordinate sequence
# Returns: a string that corresponds to the letters in the coordinate positions
def word_from_coords(coords):
    word = ""

    for i in range(len(coords)):
        x, y = coords[i]
        word = word + letters[x][y]

    return word

# TODO: this function is wrong, because it **needs** to take in coords, not words, because powerups need coords
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
        elif powerups[x][y] == "5":
            score += 5
        elif powerups[x][y] == "10":
            score += 10
        elif powerups[x][y] == "15":
            score += 15
        
    return score * multiplier

# coords = best_move()
# print(coords)
# print(word_from_coords(coords))

solve()