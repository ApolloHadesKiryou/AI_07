import random

from common.node import Node

from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    solution
)

from common.heuristic import calc_manhattan


def stochastic_hill_climbing(initial_state):

    current_node = Node(initial_state, None, None, 0)

    visited_nodes = 0

    while True:

        visited_nodes += 1

        if check_done(current_node.state):
            return solution(current_node), visited_nodes

        current_h = calc_manhattan(current_node.state)

        better_neighbors = []

        for move in possible_move(current_node.state):

            if current_node.move and remove_repetition(move, current_node.move):
                continue

            new_state = do_action(current_node.state, move)

            neighbor_h = calc_manhattan(new_state)

            if neighbor_h < current_h:

                better_neighbors.append(
                    Node(
                        new_state,
                        current_node,
                        move,
                        current_node.step + 1
                    )
                )

        if not better_neighbors:
            return solution(current_node), visited_nodes

        current_node = random.choice(better_neighbors)