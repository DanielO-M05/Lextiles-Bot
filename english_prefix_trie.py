"""
english_prefix_trie.py
----------------------
Builds or loads a MARISA trie of English words (from wordfreq)
and provides a fast prefix and word-checking function.
"""

import os
import marisa_trie
from wordfreq import top_n_list

TRIE_PATH = os.path.join(os.path.dirname(__file__), "english_words.trie")

def build_trie():
    """Build the trie from wordfreq's English word list and save it to disk."""
    print("Building trie from wordfreq word list...")
    # You can adjust n for coverage vs. memory use (e.g., 50_000 or 100_000)
    word_list = [w.lower() for w in top_n_list("en", 100_000)]
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

# TODO Trie.has_keys_with_prefix is deprecated and will be removed in marisa_trie 0.8.0. Please use Trie.iterkeys instead.
def is_prefix(prefix: str) -> bool:
    """Return True if any English word starts with the given prefix."""
    prefix = prefix.lower().strip()
    return _trie.has_keys_with_prefix(prefix)

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
