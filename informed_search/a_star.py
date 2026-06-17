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


def a_star_search(initial_state):

    start_node = Node(initial_state, None, None, 0)

    frontier = [start_node]

    reached = []

    visited_nodes = 0

    while frontier:

        current = min(
            frontier,
            key=lambda node:
            node.step + calc_heuristic(node.state)
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

            node_in_frontier = next(
                (
                    node for node in frontier
                    if matrix_to_tuple(node.state)
                    ==
                    matrix_to_tuple(new_state)
                ),
                None
            )

            node_in_reached = next(
                (
                    node for node in reached
                    if matrix_to_tuple(node.state)
                    ==
                    matrix_to_tuple(new_state)
                ),
                None
            )

            g_new = current.step + 1

            if node_in_reached:

                if g_new < node_in_reached.step:

                    reached.remove(node_in_reached)

                    node_in_reached.step = g_new
                    node_in_reached.parent = current
                    node_in_reached.move = move

                    frontier.append(node_in_reached)

            elif node_in_frontier:

                if g_new < node_in_frontier.step:

                    node_in_frontier.step = g_new
                    node_in_frontier.parent = current
                    node_in_frontier.move = move

            else:

                child = Node(
                    new_state,
                    current,
                    move,
                    g_new
                )

                frontier.append(child)

    return None, visited_nodes