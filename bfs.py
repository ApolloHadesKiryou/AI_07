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
def check(matrix):
    for i in range(4):
        for j in range(4):
            if matrix[i][j] == 1:
                return False
    
    return True

# Hàm kiểm tra có bị quay về vị trí của lần di chuyển trước đó
def check_action(move, pre_action):
    return (move == "U" and pre_action == "D") or (move == "D" and pre_action == "U") or (move == "L" and pre_action == "R") or (move == "R" and pre_action == "L")

def bfs(matrix, x, y, pre_move):
    

if __name__ == "__main__":
    matrix = create_matrix()

    x, y = create_pos()
    pre_action = ""
    for i in range(4):
            for j in range(4):
                print(matrix[i][j], end=" ")
            print()
    print(f"Start position: x = {x} | y = {y}")
    print()
    
    while True:
        if matrix[x][y] == 1:
            matrix[x][y] = 0
    
        moves = possible_moves(x, y)

        if pre_action != "":
            print(f"Previous action = {pre_action}")
        move = random.choice(moves)

        if pre_action == "":
            pre_action = move
        else:
            while check_action(move, pre_action):
                moves.remove(move)
                move = random.choice(moves)
        
        x, y = action(x, y, move)
        pre_action = move
        print(f"Action = {move}")

        for i in range(4):
            for j in range(4):
                print("x" if i == x and j == y else matrix[i][j], end=" ")
            print()
        print()

        if check(matrix):
            break