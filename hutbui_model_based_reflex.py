import random


# Hàm khởi tạo ma trận 4x4 random
def create_matrix():
    matrix = []

    for i in range(4):
        row = []
        for j in range(4):
            row.append(random.randint(0, 1))
        matrix.append(row)

    return matrix


# Hàm khởi tạo vị trí máy hút bụi ban đầu
def create_pos():
    x = random.randint(0, 3)
    y = random.randint(0, 3)

    return x, y


# Hàm trả về list các hướng có thể di chuyển
def possible_moves(x, y):
    moves = []

    if x < 3:
        moves.append("D")
    if x > 0:
        moves.append("U")
    if y < 3:
        moves.append("R")
    if y > 0:
        moves.append("L")

    return moves


# Hàm di chuyển vị trí máy hút bụi
def action(x, y, move):
    if move == "D":
        x += 1
    elif move == "U":
        x -= 1
    elif move == "R":
        y += 1
    else:
        y -= 1

    return x, y


# Hàm kiểm tra đã hết bụi hay chưa
def check_done(matrix):
    for i in range(4):
        for j in range(4):
            if matrix[i][j] == 1:
                return False

    return True


# Hàm kiểm tra có bị quay về vị trí trước đó
def check_action(move, pre_action):
    return (
        (move == "U" and pre_action == "D") or
        (move == "D" and pre_action == "U") or
        (move == "L" and pre_action == "R") or
        (move == "R" and pre_action == "L")
    )


# Hàm chọn hướng di chuyển
def choose_move(matrix, visited, x, y, moves):
    best_move = None
    best_visit = 999

    for move in moves:
        nx, ny = action(x, y, move)

        # Nếu có bụi -> ưu tiên tuyệt đối
        if matrix[nx][ny] == 1:
            return move

        # Chọn ô ít đi qua nhất
        if visited[nx][ny] < best_visit:
            best_visit = visited[nx][ny]
            best_move = move

    return best_move


if __name__ == "__main__":

    matrix = create_matrix()

    # Ma trận lưu số lần đã ghé
    visited = [[0 for _ in range(4)] for _ in range(4)]

    x, y = create_pos()

    pre_action = ""

    step = 1

    print("Initial matrix:")
    for i in range(4):
        for j in range(4):
            print(matrix[i][j], end=" ")
        print()

    print(f"\nStart position: x = {x} | y = {y}\n")

    while True:

        print(f"Step = {step}")

        # Đánh dấu đã ghé ô này
        visited[x][y] += 1

        # Hút bụi
        if matrix[x][y] == 1:
            matrix[x][y] = 0

        # Kiểm tra hoàn thành
        if check_done(matrix):
            print("DONE!")
            break

        moves = possible_moves(x, y)

        # Không cho quay đầu ngay lập tức
        if pre_action != "":
            moves = [
                move for move in moves
                if not check_action(move, pre_action)
            ]

        # Chọn hướng đi
        move = choose_move(matrix, visited, x, y, moves)

        # Di chuyển
        x, y = action(x, y, move)

        pre_action = move

        print(f"Action = {move}")

        print("Matrix:")

        for i in range(4):
            for j in range(4):
                if i == x and j == y:
                    print("X", end=" ")
                else:
                    print(matrix[i][j], end=" ")
            print()

        print("\nVisited:")

        for row in visited:
            print(row)

        print()

        step += 1