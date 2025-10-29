"""
english_prefix_trie.py
----------------------
Builds or loads a MARISA trie of English words from a JSON file
and provides fast prefix and word-checking functions.
"""

import os
import json
import marisa_trie

TRIE_PATH = os.path.join(os.path.dirname(__file__), "english_words.trie")
WORDLIST_JSON_PATH = os.path.join(os.path.dirname(__file__), "wordList.json")


def build_trie():
    """Build the trie from wordList.json and save it to disk."""
    print(f"Building trie from {WORDLIST_JSON_PATH} ...")
    with open(WORDLIST_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract just the words and lowercase them
    word_list = [entry["word"].lower() for entry in data if "word" in entry]
    trie = marisa_trie.Trie(word_list)

    print(f"Saving trie to {TRIE_PATH} ...")
    trie.save(TRIE_PATH)
    print("Trie built and saved successfully.")
    return trie


def load_trie():
    """Load the trie from disk, or build it if it doesn't exist."""
    if not os.path.exists(TRIE_PATH):
        return build_trie()
    trie = marisa_trie.Trie()
    trie.load(TRIE_PATH)
    return trie


# Lazy-load the trie once at import time
_trie = load_trie()


def is_prefix(prefix: str) -> bool:
    """Return True if any English word starts with the given prefix."""
    prefix = prefix.lower().strip()
    return any(_trie.iterkeys(prefix))


def is_word(word: str) -> bool:
    """Return True if the given string is an exact English word."""
    word = word.lower().strip()
    return word in _trie


if __name__ == "__main__":
    # Test examples
    test_prefixes = ["pp", "act", "zebr", "mobile", "acetylsalicylic", "apple"]
    for t in test_prefixes:
        print(f"is_prefix({t!r}) -> {is_prefix(t)}")

    test_words = ["pp", "ppd", "apple", "zxq", "mobiles", "apples", "acetylsalicylic", "elapsed"]
    for t in test_words:
        print(f"is_word({t!r}) -> {is_word(t)}")
