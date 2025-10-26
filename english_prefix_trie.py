"""
english_prefix_trie.py
----------------------
Builds or loads a MARISA trie of English words (from nltk.corpus.words)
and provides a fast prefix-checking function.
"""

import os
import marisa_trie
import nltk
from nltk.corpus import words

TRIE_PATH = os.path.join(os.path.dirname(__file__), "english_words.trie")

def build_trie():
    """Build the trie from NLTK's word list and save it to disk."""
    print("Downloading NLTK word list (if not already downloaded)...")
    nltk.download("words", quiet=True)

    print("Building trie from word list...")
    word_list = [w.lower() for w in words.words()]
    trie = marisa_trie.Trie(word_list)

    print(f"Saving trie to {TRIE_PATH} ...")
    trie.save(TRIE_PATH)
    print("Trie built and saved successfully.")
    return trie

def load_trie():
    """Load the trie from disk, or build it if it doesn't exist."""
    if not os.path.exists(TRIE_PATH):
        return build_trie()
    return marisa_trie.Trie().load(TRIE_PATH)

# Lazy-load the trie once at import time
_trie = load_trie()

def is_prefix(prefix: str) -> bool:
    """
    Return True if any English word starts with the given prefix.
    Example:
        >>> is_prefix("ac")
        True
        >>> is_prefix("yx")
        False
    """
    prefix = prefix.lower().strip()
    return _trie.has_keys_with_prefix(prefix)

if __name__ == "__main__":
    # Test example
    test_words = ["ac", "act", "yx", "zebr"]
    for t in test_words:
        print(f"{t!r} -> {is_prefix(t)}")
