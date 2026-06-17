import copy
import random


# ======================================================
# GOAL TEST
# ======================================================

GOAL_STATE = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]


def check_done(matrix):
    return matrix == GOAL_STATE


# ======================================================
# POSITION
# ======================================================

def find_empty_position(matrix):
    """
    Tìm vị trí ô trống (0)
    """

    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return i, j

    return -1, -1


# ======================================================
# MOVES
# ======================================================

def possible_move(matrix):
    """
    Trả về danh sách hành động hợp lệ.
    """

    moves = []

    x, y = find_empty_position(matrix)

    if x < 2:
        moves.append("D")

    if x > 0:
        moves.append("U")

    if y < 2:
        moves.append("R")

    if y > 0:
        moves.append("L")

    return moves


def remove_repetition(move, pre_move):
    """
    Tránh đi ngược ngay lập tức.
    """

    return (
        (move == "U" and pre_move == "D") or
        (move == "D" and pre_move == "U") or
        (move == "L" and pre_move == "R") or
        (move == "R" and pre_move == "L")
    )


# ======================================================
# ACTION
# ======================================================

def do_action(matrix, move):

    new_matrix = copy.deepcopy(matrix)

    x, y = find_empty_position(new_matrix)

    if move == "U":
        new_matrix[x][y], new_matrix[x - 1][y] = (
            new_matrix[x - 1][y],
            new_matrix[x][y]
        )

    elif move == "D":
        new_matrix[x][y], new_matrix[x + 1][y] = (
            new_matrix[x + 1][y],
            new_matrix[x][y]
        )

    elif move == "L":
        new_matrix[x][y], new_matrix[x][y - 1] = (
            new_matrix[x][y - 1],
            new_matrix[x][y]
        )

    elif move == "R":
        new_matrix[x][y], new_matrix[x][y + 1] = (
            new_matrix[x][y + 1],
            new_matrix[x][y]
        )

    return new_matrix


# ======================================================
# HASHABLE STATE
# ======================================================

def matrix_to_tuple(matrix):
    """
    Chuyển list 2 chiều thành tuple để dùng trong set/dict.
    """

    return tuple(tuple(row) for row in matrix)


# ======================================================
# SOLUTION PATH
# ======================================================

def solution(node):
    """
    Truy vết đường đi từ Goal -> Start.
    """

    result = []

    while node is not None:
        result.append(node)
        node = node.parent

    result.reverse()

    return result


# ======================================================
# SOLVABLE CHECK
# ======================================================

def check_solvable(matrix):
    """
    Kiểm tra trạng thái có giải được hay không.
    """

    arr = []

    for row in matrix:
        for value in row:
            if value != 0:
                arr.append(value)

    inversions = 0

    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inversions += 1

    return inversions % 2 == 0


# ======================================================
# RANDOM STATE
# ======================================================

def get_random_solvable_state():

    while True:

        values = list(range(9))

        matrix = []

        for i in range(3):

            row = []

            for j in range(3):

                num = random.choice(values)

                row.append(num)

                values.remove(num)

            matrix.append(row)

        if check_solvable(matrix) and not check_done(matrix):
            return matrix