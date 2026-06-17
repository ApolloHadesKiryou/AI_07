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


def local_beam_search(initial_state):

    k = 3

    visited_nodes = 0

    current_states = [
        Node(initial_state, None, None, 0)
    ]

    for _ in range(k - 1):

        current_states.append(
            Node(
                get_random_solvable_state(),
                None,
                "Random Start",
                0
            )
        )

    while True:

        neighbors = []

        for state_node in current_states:

            visited_nodes += 1

            for move in possible_move(state_node.state):

                if state_node.move and remove_repetition(move, state_node.move):
                    continue

                new_state = do_action(
                    state_node.state,
                    move
                )

                neighbors.append(
                    Node(
                        new_state,
                        state_node,
                        move,
                        state_node.step + 1
                    )
                )

        if not neighbors:
            return solution(current_states[0]), visited_nodes

        for node in neighbors:

            if check_done(node.state):
                return solution(node), visited_nodes

        neighbors.sort(
            key=lambda node:
            calc_manhattan(node.state)
        )

        current_states = neighbors[:k]