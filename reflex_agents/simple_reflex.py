from common.node import Node

from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition
)

import copy
import random


# ========================================================
# SIMPLE REFLEX AGENT
# ========================================================

def simple_reflex(initial_state):

    current = copy.deepcopy(initial_state)

    history = [
        Node(current, None, None, 0)
    ]

    pre_move = ""

    for step in range(1, 500):

        if check_done(current):
            return history, step

        moves = possible_move(current)

        valid_moves = [
            m for m in moves
            if not (
                pre_move and
                remove_repetition(m, pre_move)
            )
        ]

        if not valid_moves:
            valid_moves = moves

        chosen_move = random.choice(valid_moves)

        current = do_action(
            current,
            chosen_move
        )

        history.append(
            Node(
                current,
                None,
                chosen_move,
                step
            )
        )

        pre_move = chosen_move

    return None, 500
