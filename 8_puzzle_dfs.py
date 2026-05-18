import random
import copy


class Node:
    def __init__(self, state, parent, move, step):
        self.state = state
        self.parent = parent
        self.move = move
        self.step = step


def create_matrix():
    matrix = []

    value = [i for i in range(9)]

    for i in range(3):
        row = []

        for j in range(3):
            num = random.choice(value)

            row.append(num)

            value.remove(num)

        matrix.append(row)

    return matrix


def check_done(matrix):
    result = [
        [1, 2, 3],
        [6, 5, 4],
        [7, 8, 0]
    ]

    return matrix == result


def find_empty_position(matrix):
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return i, j


def possible_move(matrix):
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

    return (
        (move == "U" and pre_move == "D") or
        (move == "D" and pre_move == "U") or
        (move == "L" and pre_move == "R") or
        (move == "R" and pre_move == "L")
    )


def do_action(matrix, move):

    new_matrix = copy.deepcopy(matrix)

    x, y = find_empty_position(new_matrix)

    if move == "U":
        new_matrix[x][y], new_matrix[x - 1][y] = new_matrix[x - 1][y], new_matrix[x][y]

    elif move == "D":
        new_matrix[x][y], new_matrix[x + 1][y] = new_matrix[x + 1][y], new_matrix[x][y]

    elif move == "L":
        new_matrix[x][y], new_matrix[x][y - 1] = new_matrix[x][y - 1], new_matrix[x][y]

    elif move == "R":
        new_matrix[x][y], new_matrix[x][y + 1] = new_matrix[x][y + 1], new_matrix[x][y]

    return new_matrix


def matrix_to_tuple(matrix):
    return tuple(tuple(row) for row in matrix)


def solution(node):

    result = []

    while node is not None:
        result.append(node)

        node = node.parent

    result.reverse()

    return result


# Thuật toán DFS
def dfs(node, frontier, explored):

    # Nếu node đầu là đích
    if check_done(node.state):
        return solution(node)

    # Đưa node đầu vào stack
    frontier.append(node)

    # Đánh dấu đã thăm
    explored.add(matrix_to_tuple(node.state))

    while frontier:

        # DFS lấy phần tử cuối stack
        u = frontier.pop()

        moves = possible_move(u.state)

        for move in moves:

            # Tránh đi ngược lại
            if u.move is not None:
                if remove_repetition(move, u.move):
                    continue

            # Sinh trạng thái mới
            new_state = do_action(u.state, move)

            state_tuple = matrix_to_tuple(new_state)

            # Nếu chưa thăm
            if state_tuple not in explored:

                child = Node(
                    new_state,
                    u,
                    move,
                    u.step + 1
                )

                # Nếu tìm thấy đích
                if check_done(child.state):
                    return solution(child)

                # Thêm vào stack
                frontier.append(child)

                # Đánh dấu đã thăm
                explored.add(state_tuple)

    return "Failure"


def print_matrix(matrix):

    for row in matrix:
        print(row)

    print()


if __name__ == "__main__":

    matrix = create_matrix()

    print("Trang thai ban dau:\n")

    print_matrix(matrix)

    node = Node(matrix, None, None, 0)

    # Stack cho DFS
    frontier = []

    explored = set()

    result = dfs(node, frontier, explored)

    if result == "Failure":
        print("Khong tim thay loi giai")

    else:

        print("====== KET QUA ======\n")

        for node in result:

            print("Move:", node.move)
            print("Step:", node.step)

            print_matrix(node.state)