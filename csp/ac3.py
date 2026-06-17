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
# AC-3 CSP
# ========================================================

def ac3_search(initial_state):

    visited_nodes = 0

    domains = {}

    goal = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]

    for i in range(3):
        for j in range(3):
            domains[(i, j)] = {
                goal[i][j]
            }

    queue = deque(
        [
            (xi, xj)
            for xi in domains
            for xj in domains
            if xi != xj
        ]
    )

    def remove_inconsistent_values(
        xi,
        xj
    ):

        removed = False

        for x in list(domains[xi]):

            if not any(
                x != y
                for y in domains[xj]
            ):
                domains[xi].remove(x)
                removed = True

        return removed

    while queue:

        visited_nodes += 1

        xi, xj = queue.popleft()

        if remove_inconsistent_values(
            xi,
            xj
        ):

            for xk in domains:

                if (
                    xk != xi
                    and xk != xj
                ):
                    queue.append((xk, xi))

    solved = [
        [0] * 3
        for _ in range(3)
    ]

    for i in range(3):
        for j in range(3):

            if len(domains[(i, j)]) != 1:
                return None, visited_nodes

            solved[i][j] = next(
                iter(domains[(i, j)])
            )

    if check_done(solved):

        start_node = Node(
            initial_state,
            None,
            "Start",
            0
        )

        goal_node = Node(
            solved,
            start_node,
            "AC-3 Teleport",
            1
        )

        return [
            start_node,
            goal_node
        ], visited_nodes

    return None, visited_nodes