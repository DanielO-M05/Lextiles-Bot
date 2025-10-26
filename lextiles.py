'''
A Lextiles Solver
Author: Daniel Otto-Manzano
'''

from english_prefix_trie import is_prefix

from wordfreq import zipf_frequency

# Make this whole thing a class

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

# Description: finds the best word on the board
# Params: none
# Returns: the coordinate sequence (arr[tuple(x,y)]) of the best word
def best():
    max_score = -1
    max_coords_found = []
    for i in range(len(letters)):
        for j in range(len(letters[i])):
            # We assume there is at least one valid powerup for our heuristic
            # if letters[i][j] == "" or powerups[i][j] == "": continue
            if letters[i][j] == "": continue

            coords = max_coords([(i,j)], i, j)

            if score(word_from_coords(coords)) > max_score:
                max_coords_found = coords
                max_score = score(word_from_coords(coords))

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
        return cur_word_coords
    else: # Check if the word can be extended
        for i_off in range(-1, 2):
            for j_off in range(-1, 2):
                x, y = i + i_off, j + j_off

                # Make sure path is valid
                if not in_bounds(x, y) or (x,y) in coords: continue
                t_word = word_from_coords(coords) + letters[x][y]
                if not is_prefix(t_word): continue

                if is_prefix(t_word) or is_word(t_word):
                    t_coords = coords + [(x,y)]
                    p_coords = max_coords(t_coords, x, y)

                    if score(word_from_coords(p_coords)) > score(word_from_coords(cur_word_coords)):
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
# Params: a string
# Returns: The score of the word
def score(word):
    score = 0
    for i in range(len(word)):
        score += scores[word[i]]

    return score

coords = best()
print(coords)
print(word_from_coords(coords))