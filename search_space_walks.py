"""
search_space_random_walk.py
---------------------------
Estimates the size of the Lextiles game tree using 100 independent random
game simulations (Monte Carlo random walks).

This is an alternative to the fan-out approach in search_space.py. Rather
than expanding a tree of board states level by level, we simulate N complete
games by choosing moves uniformly at random at each step. At each level, the
branching factor is estimated as the average number of available moves across
all paths still alive at that depth.

Advantages over fan-out:
- Samples are fully independent — no correlation between levels
- Simpler to reason about and implement
- Natural handling of variable game length (terminated paths drop out)

Potential disadvantages:
- Random walks may cluster in unrepresentative regions of the game tree,
  especially if early random choices lead to unusually sparse boards
- Fewer samples at deep levels as paths terminate, increasing variance there

See search_space.py for the fan-out approach. Both are order-of-magnitude
estimates suitable for illustrating why brute force is intractable. Refer to
the literature on game tree complexity (e.g. Browne et al. 2012, "A Survey of
Monte Carlo Tree Search Methods") for a more rigorous treatment.

Assumptions:
- At most 1 swap per move (simplification of the true rules, noted in output).
- Swaps expand the move set rather than being counted as separate branches.
"""

import copy
import random
from collections import defaultdict
from board import Board
from swap import Swap
from solver_mcts import all_moves
from search_space import available_moves, _play_move, _tiles_remaining, \
    _score_without_powerups, _hits_powerup, _collect_level_stats


def estimate_search_space_random_walk(
    board,
    n_walks: int = 100,
) -> int:
    """Estimate the game tree size using independent random game simulations.

    Simulates n_walks complete games by choosing moves uniformly at random
    at each step. At each level, records the branching factor and gameplay
    statistics across all paths still alive.

    Args:
        board (Board): The starting board state. Not mutated.
        n_walks (int): Number of independent random games to simulate.

    Returns:
        int: The estimated total number of game sequences.
    """
    print("=" * 60)
    print("SEARCH SPACE ESTIMATION (random walk method)")
    print("=" * 60)
    print(f"Assumption: at most 1 swap per move (simplification).")
    print(f"Number of random walks: {n_walks}")
    print(f"Note: samples are fully independent — no cross-level correlation.")
    print()

    # Each walk is a board state, alive until no moves remain
    walks = [copy.deepcopy(board) for _ in range(n_walks)]

    # Per-level accumulators — same structure as search_space.py
    level_branching   = []
    level_word_length = []
    level_score_with  = []
    level_score_raw   = []
    level_tile_cover  = []
    level_swap_used   = []
    level_powerup_hit = []

    game_lengths = defaultdict(int)  # level -> count of walks that ended here
    level = 1

    while walks:
        # ── Get available moves for each alive walk ───────────────────────────
        walk_moves = [(w, available_moves(w)) for w in walks]

        # Separate terminated walks from alive ones
        alive   = [(w, moves) for w, moves in walk_moves if moves]
        dead    = [(w, moves) for w, moves in walk_moves if not moves]

        for _ in dead:
            game_lengths[level - 1] += 1

        if not alive:
            print(f"Level {level:>2}: all walks terminated.")
            break

        # ── Branching factor at this level ────────────────────────────────────
        branch_counts = [len(moves) for _, moves in alive]
        avg_branching = sum(branch_counts) / len(branch_counts)

        exact_tag = " (exact)" if level == 1 else f"  ({len(alive)} walks alive)"
        print(f"Level {level:>2}: avg branching factor = {avg_branching:>8.1f}{exact_tag}")

        level_branching.append(avg_branching)

        # ── Collect stats from this level's moves ─────────────────────────────
        # Pick one random move per walk for stats (the same move we'll play)
        chosen = [(w, *random.choice(moves)) for w, moves in alive]  # (board, swap, coords)
        _collect_level_stats(
            chosen,
            level_word_length, level_score_with, level_score_raw,
            level_tile_cover, level_swap_used, level_powerup_hit
        )

        # ── Advance each walk by its chosen move ──────────────────────────────
        walks = [_play_move(w, s, c) for w, s, c in chosen]

        level += 1

    # Any walks still alive at loop exit finished here
    for _ in walks:
        game_lengths[level - 1] += 1

    # ── Search space estimate ─────────────────────────────────────────────────
    print()
    print("-" * 60)
    print("Running product (search space estimate):")
    running = 1
    for i, avg in enumerate(level_branching):
        running *= avg
        print(f"  After level {i+1:>2}: {running:>25,.0f}")

    magnitude = len(str(int(running))) - 1
    print("-" * 60)
    print(f"Estimated search space: ~{running:,.0f}")
    print(f"                      = ~10^{magnitude} sequences")

    # ── Gameplay stats ────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("GAMEPLAY STATISTICS (from random walks)")
    print("=" * 60)

    print("\nGame length distribution (words played before board exhausted):")
    total_games = sum(game_lengths.values())
    if total_games > 0:
        for length in sorted(game_lengths):
            count = game_lengths[length]
            pct = 100 * count / total_games
            bar = "█" * int(pct / 2)
            print(f"  {length:>2} words: {count:>3} games ({pct:5.1f}%) {bar}")
    else:
        print("  (no complete games sampled)")

    print("\nPer-level statistics:")
    print(f"  {'Level':>5}  {'Walks':>5}  {'Branching':>10}  {'Word len':>8}  "
          f"{'Score(raw)':>10}  {'Score(+pu)':>10}  "
          f"{'Tiles left':>10}  {'Swap used':>9}  {'Powerup hit':>11}")
    print("  " + "-" * 93)

    alive_count = n_walks
    for i in range(len(level_branching)):
        # Approximate alive count — decrements by games that ended at this level
        alive_count -= game_lengths.get(i, 0)
        br = f"{level_branching[i]:.1f}"
        wl = f"{level_word_length[i]:.1f}" if i < len(level_word_length) else "—"
        sw = f"{level_score_with[i]:.1f}"  if i < len(level_score_with)  else "—"
        sr = f"{level_score_raw[i]:.1f}"   if i < len(level_score_raw)   else "—"
        tc = f"{level_tile_cover[i]:.1f}"  if i < len(level_tile_cover)  else "—"
        su = f"{level_swap_used[i]*100:.1f}%"   if i < len(level_swap_used)   else "—"
        ph = f"{level_powerup_hit[i]*100:.1f}%" if i < len(level_powerup_hit) else "—"

        print(f"  {i+1:>5}  {alive_count:>5}  {br:>10}  {wl:>8}  {sr:>10}  {sw:>10}  "
              f"{tc:>10}  {su:>9}  {ph:>11}")

    print()
    print("=" * 60)

    return int(running)


if __name__ == "__main__":
    scores = {
        "a": 2, "b": 6, "c": 7, "d": 5, "e": 2, "f": 10, "g": 5,
        "h": 10, "i": 2, "j": 16, "k": 14, "l": 3, "m": 8, "n": 2,
        "o": 2, "p": 9, "q": 22, "r": 2, "s": 4, "t": 3, "u": 2,
        "v": 12, "w": 12, "x": 18, "y": 12, "z": 20
    }
    letters = [
        ["o", "t", "g", "h", "t", "y"],
        ["n", "i", "u", "n", "c", "r"],
        ["s", "v", "g", "l", "c", "q"],
        ["o", "a", "i", "a", "h", "a"],
        ["o", "s", "f", "m", "c", "i"],
        ["i", "n", "e", "i", "n", "e"]
    ]
    powerups = [
        ["", "", "", "", "", ""],
        ["", "", "", "", "", ""],
        ["", "", "ds", "", "", ""],
        ["", "", "", "ts", "", "15"],
        ["", "", "tw", "", "10", ""],
        ["", "", "", "dl", "", ""]
    ]
    board = Board(letters, powerups, scores, 3, 3)
    estimate_search_space_random_walk(board, n_walks=10)