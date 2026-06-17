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
# FORWARD CHECKING CSP
# ========================================================

def forward_checking_search(initial_state):

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

    domains = {
        v: list(range(9))
        for v in variables
    }

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

    def apply_forward_checking(
        var,
        value,
        current_domains,
        assignment
    ):

        removed = []

        for unassigned_var in variables:

            if unassigned_var not in assignment:

                if value in current_domains[unassigned_var]:

                    current_domains[
                        unassigned_var
                    ].remove(value)

                    removed.append(
                        (
                            unassigned_var,
                            value
                        )
                    )

                if not current_domains[unassigned_var]:
                    return "failure", removed

        return "success", removed

    def forward_check(
        assignment,
        current_domains
    ):

        visited_nodes[0] += 1

        if visited_nodes[0] > 30000:
            return "Timeout"

        if len(assignment) == len(variables):
            return assignment

        var = next(
            v for v in variables
            if v not in assignment
        )

        for value in list(current_domains[var]):

            if is_consistent(
                var,
                value,
                assignment
            ):

                assignment[var] = value

                status, removed_values = apply_forward_checking(
                    var,
                    value,
                    current_domains,
                    assignment
                )

                if status != "failure":

                    result = forward_check(
                        assignment,
                        current_domains
                    )

                    if (
                        result != "failure"
                        and result != "Timeout"
                    ):
                        return result

                for (v, val) in removed_values:
                    current_domains[v].append(val)

                del assignment[var]

        return "failure"

    result_assignment = forward_check(
        {},
        domains
    )

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
            "Teleport (Forward Checking)",
            1
        )

        return [
            start_node,
            goal_node
        ], visited_nodes[0]

    return None, visited_nodes[0]