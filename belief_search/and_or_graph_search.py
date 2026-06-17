from common.node import Node

from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    remove_repetition,
    matrix_to_tuple,
    solution
)


def and_or_graph_search(initial_state):

    visited_nodes = [0]

    def or_search(
        state,
        path,
        current_node
    ):

        if visited_nodes[0] > 30000:
            return "Timeout"

        visited_nodes[0] += 1

        if check_done(state):
            return current_node

        state_tuple = matrix_to_tuple(state)

        if state_tuple in path:
            return "failure"

        for move in possible_move(state):

            if (
                current_node.move
                and remove_repetition(
                    move,
                    current_node.move
                )
            ):
                continue

            new_state = do_action(
                state,
                move
            )

            child_node = Node(
                new_state,
                current_node,
                move,
                current_node.step + 1
            )

            result_states = [child_node]

            plan = and_search(
                result_states,
                path + [state_tuple]
            )

            if plan != "failure":
                return plan

        return "failure"

    def and_search(
        states,
        path
    ):

        plans = {}

        for s_node in states:

            plan_s = or_search(
                s_node.state,
                path,
                s_node
            )

            if (
                plan_s == "failure"
                or plan_s == "Timeout"
            ):
                return plan_s

            plans[
                matrix_to_tuple(
                    s_node.state
                )
            ] = plan_s

        return list(plans.values())[0]

    start_node = Node(
        initial_state,
        None,
        None,
        0
    )

    result_node = or_search(
        initial_state,
        [],
        start_node
    )

    if result_node == "Timeout":
        return "Timeout", visited_nodes[0]

    elif (
        result_node == "failure"
        or result_node is None
    ):
        return None, visited_nodes[0]

    else:
        return (
            solution(result_node),
            visited_nodes[0]
        )