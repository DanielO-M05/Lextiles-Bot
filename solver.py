"""
solver.py
---------
Monte Carlo solver for Lextiles.
Improves on the greedy approach by simulating complete game rollouts
to evaluate the long-term value of each candidate move.
"""

import copy
import random
from board import Board
from swap import Swap


# ── Helpers ───────────────────────────────────────────────────────────────────

def all_moves(board: Board) -> list:
    """Return all valid words on the board as (score, coords) pairs, sorted
    descending by score.

    This is like best_move but collects every valid word instead of just
    the maximum.

    Args:
        board (Board): The current board state.

    Returns:
        list[tuple[int, list[Coordinate]]]: All (score, coords) pairs, best first.
    """
    results = []

    for i in range(board.NUM_ROWS):
        for j in range(board.NUM_COLS):
            coord = board.__class__  # just need Coordinate — import below
            from coordinate import Coordinate
            coord = Coordinate(i, j)
            if board.letter_at(coord) == "":
                continue
            _collect_moves(board, [coord], results)

    # Deduplicate by frozenset of coords (same tiles, different order = same word
    # is impossible in a path-based game, but keep it tidy anyway)
    seen = set()
    unique = []
    for score, coords in results:
        key = tuple(coords)
        if key not in seen:
            seen.add(key)
            unique.append((score, coords))

    unique.sort(key=lambda x: x[0], reverse=True)
    return unique


def _collect_moves(board: Board, coords: list, results: list) -> None:
    """Recursive DFS that appends every valid word reachable from coords to results.

    Args:
        board (Board): The current board state.
        coords (list[Coordinate]): The path built so far.
        results (list): Accumulator — (score, coords) pairs are appended here.
    """
    from english_prefix_trie import is_prefix, is_word

    word = board.word_from_coords(coords)
    last_coord = coords[-1]

    if len(coords) >= board.MIN_WORD_LENGTH and is_word(word):
        results.append((board.score(coords), list(coords)))

    for i_off in range(-1, 2):
        for j_off in range(-1, 2):
            from coordinate import Coordinate
            next_coord = last_coord + (i_off, j_off)

            if (
                not next_coord.in_bounds(board.NUM_ROWS, board.NUM_COLS)
                or next_coord in coords
                or board.letter_at(next_coord) == ""
            ):
                continue

            t_word = word + board.letter_at(next_coord)
            if is_prefix(t_word):
                _collect_moves(board, coords + [next_coord], results)


# ── Rollout ───────────────────────────────────────────────────────────────────

def rollout(board: Board) -> int:
    """Simulate a complete game from the given board state using the greedy
    policy (no swaps), and return the total score achieved.

    The board is not mutated — we work on a deep copy.

    Args:
        board (Board): The board state to roll out from.

    Returns:
        int: Total score of the simulated game.
    """
    sim = copy.deepcopy(board)
    sim.swaps_left = 0  # No swaps during rollouts (see design notes in solver)
    total = 0

    while True:
        coords = sim.best_move()
        if not coords:
            break
        total += sim.score(coords)
        sim.update_board(coords)

    return total


# ── Monte Carlo move selection ────────────────────────────────────────────────

def monte_carlo_move(board: Board, n_candidates: int = 10, n_rollouts: int = 50):
    """Choose the best move using Monte Carlo rollouts.

    For each of the top-N candidate words (by immediate score), simulate
    n_rollouts complete games from the resulting board state and average the
    total scores. The candidate whose average total score is highest is chosen.

    Swaps are considered only at this real decision step, not inside rollouts.

    Args:
        board (Board): The current board state.
        n_candidates (int): How many candidate words to evaluate.
        n_rollouts (int): How many rollout simulations per candidate.

    Returns:
        tuple[Swap, list[Coordinate]]:
            The swap to make (identity Swap if none) and the coordinates of
            the chosen word. Returns (Swap(), []) if no moves are available.
    """
    # ── 1. Build candidate list, optionally with swaps ────────────────────────
    candidates = []  # list of (immediate_score, swap, coords)

    # Candidates without any swap
    for score, coords in all_moves(board)[:n_candidates]:
        candidates.append((score, Swap(), coords))

    # Candidates with each possible swap (if swaps remain)
    if board.swaps_left > 0:
        swaps = board.make_swap_set()
        for swap in swaps:
            if not swap:
                continue  # skip identity, already covered above
            board.perform_swap(swap)
            for score, coords in all_moves(board)[:n_candidates]:
                candidates.append((score, swap, coords))
            board.perform_swap(swap)  # unswap

        # Re-sort combined list and keep top n_candidates
        candidates.sort(key=lambda x: x[0], reverse=True)
        candidates = candidates[:n_candidates]

    if not candidates:
        return (Swap(), [])

    print(f"\nEvaluating {len(candidates)} candidates × {n_rollouts} rollouts...")

    # ── 2. Evaluate each candidate via rollouts ───────────────────────────────
    best_avg = -1
    best_swap = Swap()
    best_coords = []

    for idx, (immediate_score, swap, coords) in enumerate(candidates):
        print(f"  [{idx+1}/{len(candidates)}] "
              f"swap={swap} word={board.word_from_coords(coords, swap=swap)!r} "
              f"immediate={immediate_score}", end=" → ", flush=True)

        total_future = 0

        for _ in range(n_rollouts):
            sim = copy.deepcopy(board)
            sim.swaps_left = 0  # rollouts don't use swaps

            # Apply the swap and play the candidate word on the simulation
            sim.perform_swap(swap)
            sim.update_board(coords)  # note: board already swapped in sim

            total_future += rollout(sim)

        avg = immediate_score + total_future / n_rollouts
        print(f"avg total = {avg:.1f}")

        if avg > best_avg:
            best_avg = avg
            best_swap = swap
            best_coords = coords

    print(f"\n→ Chosen: swap={best_swap} "
          f"word={board.word_from_coords(best_coords, swap=best_swap)!r} "
          f"avg={best_avg:.1f}\n")

    return (best_swap, best_coords)