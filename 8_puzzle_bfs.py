import random
from collections import deque
import copy


# Node dùng để lưu trạng thái hiện tại
class Node:
    def __init__(self, state, parent, move, step):
        self.state = state      # Ma trận hiện tại
        self.parent = parent    # Node cha
        self.move = move        # Hành động đã thực hiện
        self.step = step        # Số bước


# Tạo ma trận random 3x3
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


# Kiểm tra đã đạt trạng thái đích chưa
def check_done(matrix):
    result = [
        [1, 2, 3],
        [6, 5, 4],
        [7, 8, 0]
    ]

    return matrix == result


# Tìm vị trí ô trống
def find_empty_position(matrix):
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return i, j


# Lấy các hướng di chuyển hợp lệ
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


# Tránh đi ngược lại bước trước
def remove_repetition(move, pre_move):

    return (
        (move == "U" and pre_move == "D") or
        (move == "D" and pre_move == "U") or
        (move == "L" and pre_move == "R") or
        (move == "R" and pre_move == "L")
    )


# Thực hiện hành động
def do_action(matrix, move):

    # Copy ma trận để tránh sửa trực tiếp state cũ
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


# Chuyển ma trận sang tuple để lưu vào set
def matrix_to_tuple(matrix):
    return tuple(tuple(row) for row in matrix)


# Truy vết đường đi từ node đích về node gốc
def solution(node):

    result = []

    while node is not None:
        result.append(node)

        node = node.parent

    # Đảo ngược để in từ đầu -> cuối
    result.reverse()

    return result


# Thuật toán BFS
def bfs(node, frontier, explored):

    # Nếu trạng thái đầu đã là đích
    if check_done(node.state):
        return solution(node)

    # Đưa node đầu vào hàng đợi
    frontier.append(node)

    # Đánh dấu đã thăm
    explored.add(matrix_to_tuple(node.state))

    # Khi frontier còn phần tử
    while frontier:

        # BFS lấy phần tử đầu hàng đợi
        u = frontier.popleft()

        # Lấy các hướng di chuyển
        moves = possible_move(u.state)

        for move in moves:

            # Tránh đi ngược lại
            if u.move is not None:
                if remove_repetition(move, u.move):
                    continue

            # Tạo trạng thái mới
            new_state = do_action(u.state, move)

            state_tuple = matrix_to_tuple(new_state)

            # Nếu chưa thăm
            if state_tuple not in explored:

                # Tạo node con
                child = Node(
                    new_state,
                    u,
                    move,
                    u.step + 1
                )

                # Nếu là đích
                if check_done(child.state):
                    return solution(child)

                # Thêm vào frontier
                frontier.append(child)

                # Đánh dấu đã thăm
                explored.add(state_tuple)

    return "Failure"


# In ma trận
def print_matrix(matrix):

    for row in matrix:
        print(row)

    print()


if __name__ == "__main__":

    matrix = create_matrix()

    print("Trang thai ban dau:\n")

    print_matrix(matrix)

    node = Node(matrix, None, None, 0)

    # Queue cho BFS
    frontier = deque()

    # Set lưu trạng thái đã thăm
    explored = set()

    result = bfs(node, frontier, explored)

    if result == "Failure":
        print("Khong tim thay loi giai")

    else:

        print("====== KET QUA ======\n")

        for node in result:

            print("Move:", node.move)
            print("Step:", node.step)

            print_matrix(node.state)