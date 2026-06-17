from common.node import Node

from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    solution,
    get_random_solvable_state
)

from common.heuristic import calc_manhattan


def random_restart_hill_climbing(initial_state):

    max_restart = 50

    visited_nodes = 0

    for i in range(max_restart):

        current_state = (
            initial_state
            if i == 0
            else get_random_solvable_state()
        )

        current_node = Node(
            current_state,
            None,
            f"Restart {i + 1}" if i > 0 else None,
            0
        )

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
                break

            current_node = best_neighbor

    return None, visited_nodes