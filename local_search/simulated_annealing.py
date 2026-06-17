import math
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


def simulated_annealing(initial_state):

    current_node = Node(initial_state, None, None, 0)

    visited_nodes = 0

    temperature = 100.0

    min_temperature = 0.001

    alpha = 0.99

    while temperature > min_temperature:

        visited_nodes += 1

        if check_done(current_node.state):
            return solution(current_node), visited_nodes

        moves = possible_move(current_node.state)

        valid_moves = [
            m for m in moves
            if not (
                current_node.move and
                remove_repetition(m, current_node.move)
            )
        ]

        if not valid_moves:
            valid_moves = moves

        chosen_move = random.choice(valid_moves)

        new_state = do_action(
            current_node.state,
            chosen_move
        )

        next_node = Node(
            new_state,
            current_node,
            chosen_move,
            current_node.step + 1
        )

        delta = (
            calc_manhattan(next_node.state)
            -
            calc_manhattan(current_node.state)
        )

        if delta < 0:

            current_node = next_node

        else:

            probability = math.exp(
                -delta / temperature
            )

            if random.random() < probability:
                current_node = next_node

        temperature *= alpha

    return solution(current_node), visited_nodes