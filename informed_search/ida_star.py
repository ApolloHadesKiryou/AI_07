from common.node import Node
from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    solution
)

from common.heuristic import calc_heuristic


def ida_star(initial_state):

    root = Node(initial_state, None, None, 0)

    threshold = calc_heuristic(root.state)

    visited_nodes = [0]

    def search(node, g, bound):

        visited_nodes[0] += 1

        f = g + calc_heuristic(node.state)

        if f > bound:
            return None, f

        if check_done(node.state):
            return node, "FOUND"

        minimum = float("inf")

        for move in possible_move(node.state):

            if node.move and remove_repetition(move, node.move):
                continue

            new_state = do_action(node.state, move)

            child = Node(
                new_state,
                node,
                move,
                g + 1
            )

            result_node, value = search(
                child,
                g + 1,
                bound
            )

            if value == "FOUND":
                return result_node, "FOUND"

            if value < minimum:
                minimum = value

        return None, minimum

    while True:

        result_node, value = search(
            root,
            0,
            threshold
        )

        if value == "FOUND":
            return solution(result_node), visited_nodes[0]

        if value == float("inf"):
            return None, visited_nodes[0]

        threshold = value