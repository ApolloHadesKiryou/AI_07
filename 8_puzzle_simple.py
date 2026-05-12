import random

def create_matrix():
    matrix = []

    values = [i for i in range(1, 10)]

    for i in range(3):
        row = []

        for j in range(3):
            num = random.choice(values)
            row.append(num)
            values.remove(num)

        matrix.append(row)

    return matrix
        
def find_position(matrix):
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 9:
                matrix[i][j] = 0
                return i, j
            
    

def possible_moves(x, y):
    moves = []

    if x < 2:
        moves.append("D")
    if x > 0:
        moves.append("U")
    if y < 2:
        moves.append("R")
    if y > 0:
        moves.append("L")
    
    return moves

def move(matrix, x, y, move):
    pass

def check(matrix):
    base = [
        [1, 2, 3],
        [6, 5, 4],
        [7, 8, 0]
    ]

    return matrix == base
def check_move(x, y, pre_x, pre_y, move):
    if move == "D":
        x += 1
    elif move == "U":
        x -= 1
    elif move == "R":
        y += 1
    else:
        y -= 1

    return x == pre_x and y == pre_y

def do_action(matrix, x, y, pre_x, pre_y, step):
    if check(matrix):
        return
    
    moves = possible_moves(x, y)
    pre_move = ""

    move = random.choice(moves)

    if pre_move == "":
        pre_move = move
    else:
        while check_move(x, y, pre_x, pre_y, move):
            moves.remove(move)
            move = random.choice(moves)
        
        pre_move = move

    if move == "D":
        matrix[x][y], matrix[x + 1][y] = matrix[x + 1][y], matrix[x][y]
        pre_x = x
        x += 1
    elif move == "U":
        matrix[x][y], matrix[x - 1][y] = matrix[x - 1][y], matrix[x][y]
        pre_x = x
        x -= 1
    elif move == "R":
        matrix[x][y], matrix[x][y + 1] = matrix[x][y + 1], matrix[x][y]
        pre_y = y
        y += 1
    else:
        matrix[x][y], matrix[x][y - 1] = matrix[x][y - 1], matrix[x][y]
        pre_y = y
        y -= 1

    for i in range(3):
        for j in range(3):
            print(matrix[i][j], end=" ")
        print()
    print(step)
    print()

    do_action(matrix, x, y, pre_x, pre_y)


if __name__ == "__main__":
    matrix = create_matrix()

    x, y = find_position(matrix)
    step = 1
    while not check(matrix):
    
        moves = possible_moves(x, y)
        pre_move = ""

        move = random.choice(moves)

        if pre_move == "":
            pre_move = move
        else:
            while check_move(x, y, pre_x, pre_y, move):
                moves.remove(move)
                move = random.choice(moves)
            
            pre_move = move

        if move == "D":
            matrix[x][y], matrix[x + 1][y] = matrix[x + 1][y], matrix[x][y]
            pre_x = x
            x += 1
        elif move == "U":
            matrix[x][y], matrix[x - 1][y] = matrix[x - 1][y], matrix[x][y]
            pre_x = x
            x -= 1
        elif move == "R":
            matrix[x][y], matrix[x][y + 1] = matrix[x][y + 1], matrix[x][y]
            pre_y = y
            y += 1
        else:
            matrix[x][y], matrix[x][y - 1] = matrix[x][y - 1], matrix[x][y]
            pre_y = y
            y -= 1

        for i in range(3):
            for j in range(3):
                print(matrix[i][j], end=" ")
            print()
        print(step)
        step += 1
        print()