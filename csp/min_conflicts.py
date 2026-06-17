from collections import deque
import random

from common.node import Node

from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    solution
)

from common.heuristic import calc_heuristic

# ========================================================
# MIN-CONFLICTS CSP
# ========================================================

def min_conflicts_search(initial_state):

    current = Node(
        initial_state,
        None,
        None,
        0
    )

    visited_nodes = 0

    max_steps = 5000

    for _ in range(max_steps):

        visited_nodes += 1

        if check_done(current.state):
            return solution(current), visited_nodes

        best_neighbors = []

        best_conflict = float('inf')

        for move in possible_move(current.state):

            if (
                current.move
                and remove_repetition(
                    move,
                    current.move
                )
            ):
                continue

            new_state = do_action(
                current.state,
                move
            )

            conflicts = calc_heuristic(
                new_state
            )

            if conflicts < best_conflict:

                best_conflict = conflicts

                best_neighbors = [
                    (move, new_state)
                ]

            elif conflicts == best_conflict:

                best_neighbors.append(
                    (move, new_state)
                )

        if not best_neighbors:
            break

        move, new_state = random.choice(
            best_neighbors
        )

        current = Node(
            new_state,
            current,
            move,
            current.step + 1
        )

    return solution(current), visited_nodes