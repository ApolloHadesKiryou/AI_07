from common.node import Node
from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    matrix_to_tuple,
    remove_repetition,
    solution
)

from common.heuristic import calc_heuristic


def greedy_search(initial_state):

    start_node = Node(initial_state, None, None, 0)

    frontier = [start_node]

    reached = []

    visited_nodes = 0

    while frontier:

        current = min(
            frontier,
            key=lambda node: calc_heuristic(node.state)
        )

        visited_nodes += 1

        if check_done(current.state):
            return solution(current), visited_nodes

        frontier.remove(current)

        reached.append(current)

        for move in possible_move(current.state):

            if current.move and remove_repetition(move, current.move):
                continue

            new_state = do_action(current.state, move)

            child = Node(
                new_state,
                current,
                move,
                current.step + 1
            )

            in_frontier = any(
                matrix_to_tuple(child.state)
                ==
                matrix_to_tuple(node.state)
                for node in frontier
            )

            in_reached = any(
                matrix_to_tuple(child.state)
                ==
                matrix_to_tuple(node.state)
                for node in reached
            )

            if not in_frontier and not in_reached:
                frontier.append(child)

    return None, visited_nodes