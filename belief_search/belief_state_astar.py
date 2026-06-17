from queue import PriorityQueue

from common.node import Node

from common.puzzle_utils import (
    matrix_to_tuple,
    possible_move,
    do_action,
    remove_repetition,
    solution
)

from common.heuristic import (
    calc_belief_heuristic
)


# ========================================================
# BELIEF STATE UTILITIES
# ========================================================

def do_belief_action(belief_tuple, move):

    new_states = set()

    for state_tuple in belief_tuple:

        state_list = [list(row) for row in state_tuple]

        moves = possible_move(state_list)

        if move in moves:

            new_state = do_action(
                state_list,
                move
            )

            new_states.add(
                matrix_to_tuple(new_state)
            )

        else:

            new_states.add(
                matrix_to_tuple(state_list)
            )

    return tuple(sorted(new_states))


def check_belief_done(belief_tuple):

    goal_tuple = matrix_to_tuple(
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
    )

    return (
        len(belief_tuple) == 1
        and belief_tuple[0] == goal_tuple
    )


# ========================================================
# BELIEF STATE A*
# ========================================================

def belief_state_astar(initial_belief_tuple):

    start_node = Node(
        initial_belief_tuple,
        None,
        None,
        0
    )

    visited_nodes = 0

    if check_belief_done(start_node.state):
        return solution(start_node), visited_nodes

    frontier = PriorityQueue()

    counter = 0

    start_f = (
        0 +
        calc_belief_heuristic(
            initial_belief_tuple
        )
    )

    frontier.put(
        (
            start_f,
            counter,
            start_node
        )
    )

    explored = {
        initial_belief_tuple: 0
    }

    while not frontier.empty():

        if visited_nodes > 150000:
            return "Timeout", visited_nodes

        f_score, _, u = frontier.get()

        visited_nodes += 1

        if check_belief_done(u.state):
            return solution(u), visited_nodes

        for move in ["U", "D", "L", "R"]:

            if (
                u.move
                and remove_repetition(
                    move,
                    u.move
                )
            ):
                continue

            new_belief = do_belief_action(
                u.state,
                move
            )

            new_g = u.step + 1

            if (
                new_belief not in explored
                or new_g < explored[new_belief]
            ):

                explored[new_belief] = new_g

                child = Node(
                    new_belief,
                    u,
                    move,
                    new_g
                )

                child_f = (
                    new_g
                    + calc_belief_heuristic(
                        new_belief
                    )
                )

                counter += 1

                frontier.put(
                    (
                        child_f,
                        counter,
                        child
                    )
                )

    return None, visited_nodes