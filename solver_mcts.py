"""
solver_mcts.py
--------------
Monte Carlo solver for Lextiles.
Improves on the greedy approach by simulating complete game rollouts
to evaluate the long-term value of each candidate move.

Design notes:
- Swaps are only considered at the real decision step, not inside rollouts.
  This keeps rollout cost manageable. The bias is symmetric across all
  candidates, so comparisons between them remain meaningful.
- Rollouts use the greedy policy (board.best_move) as the playout policy.
  This gives low-variance estimates at the cost of some speed.
"""

import copy
from coordinate import Coordinate
from english_prefix_trie import is_prefix, is_word
from swap import Swap
from solver_base import SolverBase


class MCTSSolver(SolverBase):

    def __init__(self, n_candidates: int = 10, n_rollouts: int = 50):
        self.n_candidates = n_candidates
        self.n_rollouts = n_rollouts

    def __str__(self) -> str:
        return f"MCTSSolver(n_candidates={self.n_candidates}, n_rollouts={self.n_rollouts})"

    def choose_move(self, board, verbose=True):
        """Choose the best move using Monte Carlo rollouts.

        For each of the top-N candidate words (by immediate score), simulate
        n_rollouts complete games from the resulting board state and average
        the total scores. The candidate with the highest average total is chosen.

        Swaps are considered at this real decision step only — not inside rollouts.

        Args:
            board (Board): The current board state.
            verbose (bool): If True, prints per-candidate rollout progress.

        Returns:
            tuple[Swap, list[Coordinate]]:
                The swap to make (identity Swap if none) and the coordinates
                of the chosen word. Returns (Swap(), []) if no moves available.
        """
        # ── 1. Build candidate list ───────────────────────────────────────────
        # Each entry: (immediate_score, swap, coords)
        candidates = []

        # Candidates without any swap
        for score, coords in all_moves(board)[:self.n_candidates]:
            candidates.append((score, Swap(), coords))

        # Candidates with each possible swap (if swaps remain)
        if board.swaps_left > 0:
            for swap in board.make_swap_set():
                if not swap:
                    continue  # skip identity, already covered above
                board.perform_swap(swap)
                for score, coords in all_moves(board)[:self.n_candidates]:
                    candidates.append((score, swap, coords))
                board.perform_swap(swap)  # unswap — restore board state

            # Re-sort and keep only the top n_candidates overall
            candidates.sort(key=lambda x: x[0], reverse=True)
            candidates = candidates[:self.n_candidates]

        if not candidates:
            return (Swap(), [])

        if verbose:
            print(f"\nEvaluating {len(candidates)} candidates × {self.n_rollouts} rollouts...")

        # ── 2. Evaluate each candidate via rollouts ───────────────────────────
        best_avg = -1
        best_swap = Swap()
        best_coords = []

        for idx, (immediate_score, swap, coords) in enumerate(candidates):
            if verbose:
                word = board.word_from_coords(coords, swap=swap)
                print(f"  [{idx+1}/{len(candidates)}] "
                      f"swap={swap} word={word!r} "
                      f"immediate={immediate_score}", end=" → ", flush=True)

            total_future = 0

            for _ in range(self.n_rollouts):
                sim = copy.deepcopy(board)
                sim.swaps_left = 0  # rollouts don't use swaps

                # Pre-apply the swap manually so update_board receives no swap
                # arg — avoids any risk of double-application since update_board
                # calls perform_swap internally.
                sim.perform_swap(swap)
                sim.update_board(coords)

                total_future += rollout(sim)

            avg = immediate_score + total_future / self.n_rollouts

            if verbose:
                print(f"avg total = {avg:.1f}")

            if avg > best_avg:
                best_avg = avg
                best_swap = swap
                best_coords = coords

        if verbose:
            print(f"\n→ Chosen: swap={best_swap} "
                  f"word={board.word_from_coords(best_coords, swap=best_swap)!r} "
                  f"avg={best_avg:.1f}\n")

        return (best_swap, best_coords)


class GreedySolver(SolverBase):

    def __str__(self) -> str:
        return "GreedySolver"

    def choose_move(self, board, verbose=True):
        """Thin wrapper around the existing board.best_move_with_swap().

        Args:
            board (Board): The current board state.
            verbose (bool): Unused — greedy produces no solver-level output.

        Returns:
            tuple[Swap, list[Coordinate]]: The swap and coords of the best
                immediate move.
        """
        return board.best_move_with_swap()


# ── Module-level helpers (used by MCTSSolver and available for other solvers) ──

def all_moves(board) -> list:
    """Return all valid words on the board as (score, coords) pairs, sorted
    descending by score.

    Args:
        board (Board): The current board state.

    Returns:
        list[tuple[int, list[Coordinate]]]: All (score, coords) pairs, best first.
    """
    results = []

    for i in range(board.NUM_ROWS):
        for j in range(board.NUM_COLS):
            coord = Coordinate(i, j)
            if board.letter_at(coord) == "":
                continue
            _collect_moves(board, [coord], results)

    results.sort(key=lambda x: x[0], reverse=True)
    return results


def _collect_moves(board, coords: list, results: list) -> None:
    """Recursive DFS that appends every valid word reachable from coords
    to results.

    Args:
        board (Board): The current board state.
        coords (list[Coordinate]): The path built so far.
        results (list): Accumulator — (score, coords) pairs appended here.
    """
    word = board.word_from_coords(coords)
    last_coord = coords[-1]

    if len(coords) >= board.MIN_WORD_LENGTH and is_word(word):
        results.append((board.score(coords), list(coords)))

    for i_off in range(-1, 2):
        for j_off in range(-1, 2):
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


def rollout(board) -> int:
    """Simulate a complete game from the given board state using the greedy
    policy (no swaps), and return the total score achieved.

    Args:
        board (Board): The board state to roll out from. Not mutated — we
                       work on a deep copy internally.

    Returns:
        int: Total score of the simulated game.
    """
    sim = copy.deepcopy(board)
    sim.swaps_left = 0
    total = 0

    while True:
        coords = sim.best_move()
        if not coords:
            break
        total += sim.score(coords)
        sim.update_board(coords)

    return total