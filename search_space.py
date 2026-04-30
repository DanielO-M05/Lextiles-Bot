"""
search_space.py
---------------
Estimates the size of the Lextiles game tree by sampling branching factors
at each level of play and multiplying them together.

The purpose is to demonstrate why brute force search is intractable.

Methodology:
- At level 1, the branching factor is counted exactly (no sampling needed).
- At each subsequent level, we sample `estimate_samples` random moves from
  the current set of boards and count the average number of available moves
  on the resulting child boards. This gives a low-noise estimate of the
  branching factor at that level.
- Separately, we propagate only `propagate_samples` of those boards forward
  to the next level, keeping runtime manageable.
- These two parameters are independent: estimate_samples controls statistical
  accuracy; propagate_samples controls runtime.
- Note: the boards propagated forward are a subset of the boards used for
  estimation, introducing mild correlation between level estimates. This is
  acceptable for an order-of-magnitude blog-level estimate.

Assumptions:
- At most 1 swap per move (simplification of the true rules, noted in output).
- Swaps expand the move set rather than being counted as separate branches —
  i.e. the atomic decision is "which (optional-swap, word) pair do I play".
"""

import copy
import random
from collections import defaultdict
from board import Board
from swap import Swap
from solver_mcts import all_moves


# ── Helpers ───────────────────────────────────────────────────────────────────

def available_moves(board) -> list:
    """Return all (swap, coords) pairs available on the current board,
    including moves enabled by a single swap if swaps remain.

    Args:
        board (Board): The current board state.

    Returns:
        list[tuple[Swap, list[Coordinate]]]: All available (swap, coords) pairs.
    """
    moves = []

    for _, coords in all_moves(board):
        moves.append((Swap(), coords))

    if board.swaps_left > 0:
        for swap in board.make_swap_set():
            if not swap:
                continue
            board.perform_swap(swap)
            for _, coords in all_moves(board):
                moves.append((swap, coords))
            board.perform_swap(swap)  # unswap

    return moves


def _play_move(board, swap, coords) -> Board:
    """Return a new board with the given swap and move applied.

    Args:
        board (Board): The current board state. Not mutated.
        swap (Swap): The swap to apply.
        coords (list[Coordinate]): The word to play.

    Returns:
        Board: The resulting board state.
    """
    sim = copy.deepcopy(board)
    sim.perform_swap(swap)
    sim.update_board(coords)
    if swap:
        sim.swaps_left -= 1
    return sim


def _tiles_remaining(board) -> int:
    """Count non-empty tiles on the board."""
    return sum(
        1
        for i in range(board.NUM_ROWS)
        for j in range(board.NUM_COLS)
        if board.letters[i][j] != ""
    )


def _score_without_powerups(board, coords) -> int:
    """Return the raw letter score of a word, ignoring all powerups."""
    return sum(board.scores[board.letter_at(c)] for c in coords)


def _hits_powerup(board, coords) -> bool:
    """Return True if any tile in the word has a powerup."""
    return any(board.powerup_at(c) != "" for c in coords)


def _collect_level_stats(board_move_pairs, wl_list, sw_list, sr_list,
                         tc_list, su_list, ph_list):
    """Collect per-level statistics from a flat list of (board, swap, coords)
    triples and append one averaged entry to each accumulator list.

    Using a flat list means there is no per-board loop and no append/update
    ambiguity — this function is always called exactly once per level.

    Args:
        board_move_pairs (list[tuple[Board, Swap, list[Coordinate]]]): Sampled
            moves with their originating board, so scoring and powerup checks
            are always done against the correct board state.
        wl_list  : avg word length accumulator
        sw_list  : avg score with powerups accumulator
        sr_list  : avg score without powerups accumulator
        tc_list  : avg tiles remaining after move accumulator
        su_list  : swap usage rate accumulator
        ph_list  : powerup hit rate accumulator
    """
    if not board_move_pairs:
        return

    word_lengths = []
    scores_with  = []
    scores_raw   = []
    tiles_left   = []
    swap_used    = []
    powerup_hit  = []

    for board, swap, coords in board_move_pairs:
        word_lengths.append(len(coords))
        scores_with.append(board.score(coords))
        scores_raw.append(_score_without_powerups(board, coords))
        child = _play_move(board, swap, coords)
        tiles_left.append(_tiles_remaining(child))
        swap_used.append(1 if swap else 0)
        powerup_hit.append(1 if _hits_powerup(board, coords) else 0)

    wl_list.append(sum(word_lengths) / len(word_lengths))
    sw_list.append(sum(scores_with)  / len(scores_with))
    sr_list.append(sum(scores_raw)   / len(scores_raw))
    tc_list.append(sum(tiles_left)   / len(tiles_left))
    su_list.append(sum(swap_used)    / len(swap_used))
    ph_list.append(sum(powerup_hit)  / len(powerup_hit))


# ── Main estimator ────────────────────────────────────────────────────────────

def estimate_search_space(
    board,
    estimate_samples: int = 10,
    propagate_samples: int = 4
) -> int:
    """Estimate the total number of distinct game sequences (leaf nodes in the
    game tree) by sampling branching factors at each level of play.

    Prints a summary table of branching factors per level, a final estimate
    of the total search space size, and a set of gameplay statistics collected
    from the sampled games.

    Args:
        board (Board): The starting board state. Not mutated.
        estimate_samples (int): How many random moves to sample at each level
                                when estimating the branching factor.
        propagate_samples (int): How many child boards to generate per board
                                 at each level. Board count grows as
                                 propagate_samples^depth. Controls runtime.

    Returns:
        int: The estimated total number of game sequences.
    """
    print("=" * 60)
    print("SEARCH SPACE ESTIMATION")
    print("=" * 60)
    print(f"Assumption: at most 1 swap per move (simplification).")
    print(f"Estimate samples per level : {estimate_samples}")
    print(f"Propagate samples per level: {propagate_samples}")
    print(f"Note: propagated boards are a subset of estimated boards,")
    print(f"      introducing mild correlation between level estimates.")
    print()

    level_branching   = []
    level_word_length = []
    level_score_with  = []
    level_score_raw   = []
    level_tile_cover  = []
    level_swap_used   = []
    level_powerup_hit = []

    game_lengths = defaultdict(int)  # level -> count of games ending here

    current_boards = [copy.deepcopy(board)]
    level = 1

    while True:

        # ── Level 1: exact branching count ───────────────────────────────────
        if level == 1:
            moves = available_moves(current_boards[0])
            branching_factor = len(moves)
            print(f"Level {level:>2}: branching factor = {branching_factor:>8,d}  (exact)")

            if branching_factor == 0:
                print("          No moves available — game ends immediately.")
                game_lengths[0] += 1
                break

            level_branching.append(float(branching_factor))

            # Sample for stats — flat list of (board, swap, coords)
            sampled = random.sample(moves, min(estimate_samples, len(moves)))
            _collect_level_stats(
                [(current_boards[0], s, c) for s, c in sampled],
                level_word_length, level_score_with, level_score_raw,
                level_tile_cover, level_swap_used, level_powerup_hit
            )

            # Propagate forward
            prop = random.sample(moves, min(propagate_samples, len(moves)))
            current_boards = [_play_move(current_boards[0], s, c) for s, c in prop]

        # ── Level 2+: sampled branching count ────────────────────────────────
        else:
            # Build flat pool of (board, swap, coords) across all current boards
            pool = []
            for b in current_boards:
                for swap, coords in available_moves(b):
                    pool.append((b, swap, coords))

            # Track exhausted boards
            exhausted = sum(1 for b in current_boards if not available_moves(b))
            if exhausted:
                game_lengths[level - 1] += exhausted

            if not pool:
                print(f"Level {level:>2}: no moves available — game ends here.")
                break

            # Sample for branching factor estimate
            sampled = random.sample(pool, min(estimate_samples, len(pool)))
            child_counts = [
                len(available_moves(_play_move(b, s, c)))
                for b, s, c in sampled
            ]

            avg_branching = sum(child_counts) / len(child_counts)
            print(f"Level {level:>2}: avg branching factor = {avg_branching:>8.1f}"
                  f"  (estimated from {len(sampled)} samples"
                  f" across {len(current_boards)} board(s))")

            if avg_branching == 0:
                print(f"          No moves available on average — game ends here.")
                game_lengths[level - 1] += len(current_boards)
                break

            level_branching.append(avg_branching)

            # Collect stats from the same sample — already (board, swap, coords)
            _collect_level_stats(
                sampled,
                level_word_length, level_score_with, level_score_raw,
                level_tile_cover, level_swap_used, level_powerup_hit
            )

            # Propagate forward — fan out each current board into up to
            # propagate_samples children, so board count grows as
            # propagate_samples^depth rather than staying flat.
            next_boards = []
            for b in current_boards:
                b_moves = [(s, c) for bb, s, c in pool if bb is b]
                if not b_moves:
                    continue
                chosen = random.sample(b_moves, min(propagate_samples, len(b_moves)))
                next_boards.extend(_play_move(b, s, c) for s, c in chosen)
            current_boards = next_boards

        level += 1

    # Any boards still alive at loop exit are finished games
    for _ in current_boards:
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
    print("GAMEPLAY STATISTICS (from sampled games)")
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
    print(f"  {'Level':>5}  {'Branching':>10}  {'Word len':>8}  "
          f"{'Score(raw)':>10}  {'Score(+pu)':>10}  "
          f"{'Tiles left':>10}  {'Swap used':>9}  {'Powerup hit':>11}")
    print("  " + "-" * 85)

    for i in range(len(level_branching)):
        br = f"{level_branching[i]:.1f}"
        wl = f"{level_word_length[i]:.1f}" if i < len(level_word_length) else "—"
        sw = f"{level_score_with[i]:.1f}"  if i < len(level_score_with)  else "—"
        sr = f"{level_score_raw[i]:.1f}"   if i < len(level_score_raw)   else "—"
        tc = f"{level_tile_cover[i]:.1f}"  if i < len(level_tile_cover)  else "—"
        su = f"{level_swap_used[i]*100:.1f}%"   if i < len(level_swap_used)   else "—"
        ph = f"{level_powerup_hit[i]*100:.1f}%" if i < len(level_powerup_hit) else "—"

        print(f"  {i+1:>5}  {br:>10}  {wl:>8}  {sr:>10}  {sw:>10}  "
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
    estimate_search_space(board, estimate_samples=10, propagate_samples=3)