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
# BACKTRACKING CSP
# ========================================================

def backtracking_search(initial_state):

    visited_nodes = [0]

    variables = [
        (i, j)
        for i in range(3)
        for j in range(3)
    ]

    goal_matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]

    def is_consistent(
        var,
        value,
        assignment
    ):

        if value in assignment.values():
            return False

        if value != goal_matrix[var[0]][var[1]]:
            return False

        return True

    def recursive_backtracking(assignment):

        visited_nodes[0] += 1

        if visited_nodes[0] > 30000:
            return "Timeout"

        if len(assignment) == len(variables):
            return assignment

        var = next(
            v for v in variables
            if v not in assignment
        )

        for value in range(9):

            if is_consistent(
                var,
                value,
                assignment
            ):

                assignment[var] = value

                result = recursive_backtracking(
                    assignment
                )

                if (
                    result != "failure"
                    and result != "Timeout"
                ):
                    return result

                del assignment[var]

        return "failure"

    result_assignment = recursive_backtracking({})

    if result_assignment == "Timeout":
        return "Timeout", visited_nodes[0]

    elif result_assignment != "failure":

        final_matrix = [
            [0] * 3
            for _ in range(3)
        ]

        for (i, j), val in result_assignment.items():
            final_matrix[i][j] = val

        start_node = Node(
            initial_state,
            None,
            "Start",
            0
        )

        goal_node = Node(
            final_matrix,
            start_node,
            "Teleport (CSP Backtrack)",
            1
        )

        return [
            start_node,
            goal_node
        ], visited_nodes[0]

    return None, visited_nodes[0]