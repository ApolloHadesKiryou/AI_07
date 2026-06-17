class Node:
    """
    Node dùng chung cho toàn bộ thuật toán 8-Puzzle.
    """

    def __init__(self, state, parent=None, move=None, step=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.step = step

    def __lt__(self, other):
        """
        Cho phép PriorityQueue so sánh Node.
        """
        return self.step < other.step