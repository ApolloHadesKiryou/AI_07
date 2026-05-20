import tkinter as tk
from tkinter import messagebox
import random
import copy

# ==========================================
# CÁC HÀM VÀ LỚP LOGIC CỐT LÕI (DFS)
# ==========================================

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
    if x < 2: moves.append("D")
    if x > 0: moves.append("U")
    if y < 2: moves.append("R")
    if y > 0: moves.append("L")
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

def dfs(node, frontier, explored):
    if check_done(node.state):
        return solution(node)
    
    frontier.append(node)
    explored.add(matrix_to_tuple(node.state))
    
    while frontier:
        u = frontier.pop()
        moves = possible_move(u.state)
        
        for move in moves:
            if u.move is not None:
                if remove_repetition(move, u.move):
                    continue
            
            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)
            
            if state_tuple not in explored:
                child = Node(new_state, u, move, u.step + 1)
                
                if check_done(child.state):
                    return solution(child)
                
                frontier.append(child)
                explored.add(state_tuple)
                
    return "Failure"

# ==========================================
# LỚP GIAO DIỆN ĐỒ HỌA TKINTER
# ==========================================

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver (Thuật toán DFS)")
        self.matrix = self.create_matrix()
        
        # Khung chứa ma trận
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)
        
        # Lưới các ô vuông (Labels)
        self.tiles = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.tiles[i][j] = tk.Label(self.frame, text="", font=("Helvetica", 32, "bold"), 
                                            width=4, height=2, borderwidth=2, relief="groove")
                self.tiles[i][j].grid(row=i, column=j, padx=5, pady=5)
        
        # Nhãn hiển thị trạng thái
        self.status_label = tk.Label(self.root, text="Sẵn sàng", font=("Helvetica", 14))
        self.status_label.pack(pady=10)
        
        # Khung chứa nút bấm
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(pady=10)
        
        self.solve_btn = tk.Button(self.btn_frame, text="Giải tự động (DFS)", font=("Helvetica", 12), command=self.solve)
        self.solve_btn.grid(row=0, column=0, padx=10)
        
        self.new_btn = tk.Button(self.btn_frame, text="Tạo bài mới", font=("Helvetica", 12), command=self.new_game)
        self.new_btn.grid(row=0, column=1, padx=10)
        
        self.update_ui()

    def create_matrix(self):
        value = [i for i in range(9)]
        matrix = []
        for i in range(3):
            row = []
            for j in range(3):
                num = random.choice(value)
                row.append(num)
                value.remove(num)
            matrix.append(row)
        return matrix

    def update_ui(self):
        for i in range(3):
            for j in range(3):
                val = self.matrix[i][j]
                if val == 0:
                    self.tiles[i][j].config(text="", bg="#d3d3d3")
                else:
                    self.tiles[i][j].config(text=str(val), bg="#ffb6c1") # Đổi sang màu hồng nhạt để phân biệt với bản BFS

    def new_game(self):
        self.matrix = self.create_matrix()
        self.update_ui()
        self.status_label.config(text="Sẵn sàng", fg="black")
        self.solve_btn.config(state=tk.NORMAL)

    def solve(self):
        self.solve_btn.config(state=tk.DISABLED)
        self.new_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Đang tìm kiếm (DFS có thể mất thời gian lâu hơn)...")
        self.root.update()
        
        # Thiết lập DFS
        node = Node(self.matrix, None, None, 0)
        frontier = []
        explored = set()
        
        result = dfs(node, frontier, explored)
        
        if result == "Failure":
            messagebox.showinfo("Kết quả", "Không tìm thấy lời giải cho trạng thái này!")
            self.solve_btn.config(state=tk.NORMAL)
            self.new_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Không có lời giải", fg="red")
        else:
            # Tốc độ chạy animation (DFS thường tìm ra đường đi rất dài, nên giảm thời gian chờ xuống 100ms)
            self.animate_solution(result, delay=100)

    def animate_solution(self, steps, index=0, delay=100):
        if index < len(steps):
            self.matrix = steps[index].state
            self.update_ui()
            
            move_text = steps[index].move if steps[index].move else "Bắt đầu"
            self.status_label.config(text=f"Bước: {steps[index].step} | Nước đi: {move_text} | Tổng: {len(steps)-1} bước")
            
            self.root.after(delay, self.animate_solution, steps, index + 1, delay)
        else:
            self.solve_btn.config(state=tk.NORMAL)
            self.new_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Đã hoàn thành!", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.resizable(False, False)
    root.mainloop()