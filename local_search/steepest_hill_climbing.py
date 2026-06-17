from common.node import Node

from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    solution
)

from common.heuristic import calc_manhattan


def steepest_ascent_hill_climbing(initial_state):

    current_node = Node(initial_state, None, None, 0)

    visited_nodes = 0

    while True:

        visited_nodes += 1

        if check_done(current_node.state):
            return solution(current_node), visited_nodes

        current_h = calc_manhattan(current_node.state)

        best_neighbor = None
        best_h = current_h

        for move in possible_move(current_node.state):

            if current_node.move and remove_repetition(move, current_node.move):
                continue

            new_state = do_action(current_node.state, move)

            neighbor_h = calc_manhattan(new_state)

            if neighbor_h < best_h:

                best_h = neighbor_h

                best_neighbor = Node(
                    new_state,
                    current_node,
                    move,
                    current_node.step + 1
                )

        if best_neighbor is None:
            return solution(current_node), visited_nodes

        current_node = best_neighbor