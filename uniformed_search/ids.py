from common.node import Node
from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    solution
)


def dls(node, limit):

    frontier = [node]

    visited_nodes = 0

    while frontier:

        current = frontier.pop()

        visited_nodes += 1

        if check_done(current.state):
            return solution(current), visited_nodes

        if current.step < limit:

            for move in possible_move(current.state):

                if current.move and remove_repetition(move, current.move):
                    continue

                child = Node(
                    do_action(current.state, move),
                    current,
                    move,
                    current.step + 1
                )

                frontier.append(child)

    return None, visited_nodes


def ids(initial_state):

    root = Node(initial_state, None, None, 0)

    total_visited = 0

    for depth in range(25):

        result, visited = dls(root, depth)

        total_visited += visited

        if result:
            return result, total_visited

    return None, total_visited