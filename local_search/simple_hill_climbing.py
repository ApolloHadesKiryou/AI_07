from common.node import Node

from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    solution
)

from common.heuristic import calc_manhattan


def simple_hill_climbing(initial_state):

    current_node = Node(initial_state, None, None, 0)

    visited_nodes = 0

    while True:

        visited_nodes += 1

        if check_done(current_node.state):
            return solution(current_node), visited_nodes

        current_h = calc_manhattan(current_node.state)

        found_better = False

        for move in possible_move(current_node.state):

            if current_node.move and remove_repetition(move, current_node.move):
                continue

            new_state = do_action(current_node.state, move)

            neighbor_h = calc_manhattan(new_state)

            if neighbor_h < current_h:

                current_node = Node(
                    new_state,
                    current_node,
                    move,
                    current_node.step + 1
                )

                found_better = True
                break

        if not found_better:
            return solution(current_node), visited_nodes