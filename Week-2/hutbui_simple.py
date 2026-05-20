import random

def create_matrix():
    matrix = []

    for i in range(4):
        row = []
        for j in range(4):
            row.append(random.randint(0, 1))
        matrix.append(row)

    return matrix

def create_pos():
    x = random.randint(0, 3)
    y = random.randint(0, 3)

    return x, y

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

def move(x, y, move):
    if move == "D":
        x += 1
    elif move == "U":
        x -= 1
    elif move == "R":
        y += 1
    else:
        y -= 1
    
    print(move)

    return x, y

def check(matrix):
    for i in range(4):
        for j in range(4):
            if matrix[i][j] == 1:
                return False
    
    return True

def do_action(matrix, x, y):
    if matrix[x][y] == 1:
        matrix[x][y] = 0
    
    moves = possible_moves(x, y)

    action = random.choice(moves)

    x, y = move(x, y, action)

    for i in range(4):
        for j in range(4):
            print(matrix[i][j], end=" ")
        print()
    print()

    if check(matrix):
        return

    do_action(matrix, x, y)

if __name__ == "__main__":
    matrix = create_matrix()

    x, y = create_pos()

    print(f"Start position: x = {x} | y = {y}")

    do_action(matrix, x, y)