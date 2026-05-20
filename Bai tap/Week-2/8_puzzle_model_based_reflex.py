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


def move(matrix, x, y, direction):

    if direction == "D":

        matrix[x][y], matrix[x + 1][y] = matrix[x + 1][y], matrix[x][y]

        x += 1

    elif direction == "U":

        matrix[x][y], matrix[x - 1][y] = matrix[x - 1][y], matrix[x][y]

        x -= 1

    elif direction == "R":

        matrix[x][y], matrix[x][y + 1] = matrix[x][y + 1], matrix[x][y]

        y += 1

    else:

        matrix[x][y], matrix[x][y - 1] = matrix[x][y - 1], matrix[x][y]

        y -= 1

    return x, y


def check(matrix):

    goal = [
        [1, 2, 3],
        [6, 5, 4],
        [7, 8, 0]
    ]

    return matrix == goal


def check_move(move, pre_move):

    return (
        (move == "U" and pre_move == "D") or
        (move == "D" and pre_move == "U") or
        (move == "L" and pre_move == "R") or
        (move == "R" and pre_move == "L")
    )


def print_matrix(matrix):

    for i in range(3):
        for j in range(3):
            print(matrix[i][j], end=" ")
        print()

    print()


if __name__ == "__main__":

    matrix = create_matrix()

    x, y = find_position(matrix)

    step = 1

    pre_move = ""

    print("START:")
    print_matrix(matrix)

    while not check(matrix):

        moves = possible_moves(x, y)

        if pre_move != "":

            opposite_moves = []

            for m in moves:

                if check_move(m, pre_move):
                    opposite_moves.append(m)

            for m in opposite_moves:

                if len(moves) > 1:
                    moves.remove(m)

        move_choice = random.choice(moves)

        x, y = move(matrix, x, y, move_choice)

        pre_move = move_choice

        print(f"STEP {step}")
        print(f"MOVE = {move_choice}")

        print_matrix(matrix)

        step += 1

    print("SOLVED!")