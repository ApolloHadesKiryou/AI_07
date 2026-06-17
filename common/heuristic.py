from common.puzzle_utils import matrix_to_tuple


GOAL_STATE = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]


# ======================================================
# MISPLACED TILES
# ======================================================

def calc_heuristic(matrix):
    """
    Đếm số ô sai vị trí.
    """

    count = 0

    for i in range(3):
        for j in range(3):

            if (
                matrix[i][j] != 0 and
                matrix[i][j] != GOAL_STATE[i][j]
            ):
                count += 1

    return count


# ======================================================
# MANHATTAN DISTANCE
# ======================================================

def calc_manhattan(matrix):
    """
    Manhattan Distance.
    """

    distance = 0

    for i in range(3):
        for j in range(3):

            value = matrix[i][j]

            if value != 0:

                goal_row = (value - 1) // 3
                goal_col = (value - 1) % 3

                distance += (
                    abs(i - goal_row)
                    +
                    abs(j - goal_col)
                )

    return distance


# ======================================================
# BELIEF STATE HEURISTIC
# ======================================================

def calc_belief_heuristic(belief_tuple):
    """
    Heuristic cho Sensorless Search.
    """

    max_h = 0

    for state_tuple in belief_tuple:

        matrix = [list(row) for row in state_tuple]

        h = calc_manhattan(matrix)

        if h > max_h:
            max_h = h

    return max_h