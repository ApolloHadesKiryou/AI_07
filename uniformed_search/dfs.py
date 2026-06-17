from common.node import Node
from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    matrix_to_tuple,
    remove_repetition,
    solution
)


def dfs(initial_state):

    root = Node(initial_state, None, None, 0)

    visited_nodes = 0

    if check_done(root.state):
        return solution(root), visited_nodes

    frontier = [root]

    explored = {matrix_to_tuple(root.state)}

    while frontier:

        if visited_nodes > 30000:
            return "Timeout", visited_nodes

        current = frontier.pop()

        visited_nodes += 1

        for move in possible_move(current.state):

            if current.move and remove_repetition(move, current.move):
                continue

            new_state = do_action(current.state, move)

            state_tuple = matrix_to_tuple(new_state)

            if state_tuple not in explored:

                child = Node(
                    new_state,
                    current,
                    move,
                    current.step + 1
                )

                if check_done(child.state):
                    return solution(child), visited_nodes

                frontier.append(child)

                explored.add(state_tuple)

    return None, visited_nodes