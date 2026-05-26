import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import copy
from collections import deque
from queue import PriorityQueue

# LỚP DỮ LIỆU NODE SỬ DỤNG CHO CÁC THUẬT TOÁN ĐỒ THỊ
class Node:
    def __init__(self, state, parent, move, step):
        self.state = state
        self.parent = parent
        self.move = move
        self.step = step # Chi phí g(n) dùng cho UCS

    def __lt__(self, other):
        return self.step < other.step

# CÁC HÀM LOGIC CHUNG
def check_done(matrix):
    return matrix == [
        [1, 2, 3],
        [4, 5, 6], 
        [7, 8, 0]
    ]

def find_empty_position(matrix):
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return i, j
            
    return -1, -1

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
    return ((move == "U" and pre_move == "D") or 
            (move == "D" and pre_move == "U") or
            (move == "L" and pre_move == "R") or 
            (move == "R" and pre_move == "L"))

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

def check_solvable(matrix):
    arr = [val for row in matrix for val in row if val != 0]

    inversions = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])

    return inversions % 2 == 0

# 6 THUẬT TOÁN TÌM KIẾM
def bfs(initial_state):
    node = Node(initial_state, None, None, 0)

    if check_done(node.state): 
        return solution(node)
    
    frontier = deque([node])
    explored = {matrix_to_tuple(node.state)}

    while frontier:
        u = frontier.popleft()
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): 
                continue

            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)

            if state_tuple not in explored:
                child = Node(new_state, u, move, u.step + 1)
                if check_done(child.state): 
                    return solution(child)
                
                frontier.append(child)
                explored.add(state_tuple)

    return None

def dfs(initial_state):
    node = Node(initial_state, None, None, 0)
    if check_done(node.state): 
        return solution(node)
    
    frontier = [node]
    explored = {matrix_to_tuple(node.state)}

    while frontier:
        if len(explored) > 30000: 
            return "Timeout" # Tránh đơ máy
        
        u = frontier.pop()

        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): 
                continue

            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)

            if state_tuple not in explored:
                child = Node(new_state, u, move, u.step + 1)

                if check_done(child.state): 
                    return solution(child)
                
                frontier.append(child)
                explored.add(state_tuple)

    return None

def dls(node, limit):
    frontier = [node]

    while frontier:
        u = frontier.pop()
        if check_done(u.state): 
            return solution(u)
        
        if u.step < limit:
            for move in possible_move(u.state):
                child = Node(do_action(u.state, move), u, move, u.step + 1)
                frontier.append(child)

    return None

def ids(initial_state):
    root_node = Node(initial_state, None, None, 0)

    for depth in range(20): # Tìm đến độ sâu 20
        res = dls(root_node, depth)
        if res: 
            return res
        
    return None

def ucs(initial_state):
    root_node = Node(initial_state, None, None, 0)

    if check_done(root_node.state): 
        return solution(root_node)
    
    frontier = PriorityQueue()
    frontier.put((root_node.step, root_node))
    explored = {matrix_to_tuple(root_node.state)}

    while not frontier.empty():
        _, u = frontier.get()
        if check_done(u.state): 
            return solution(u)
        
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): 
                continue

            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)

            if state_tuple not in explored:
                child = Node(new_state, u, move, u.step + 1)
                frontier.put((child.step, child))
                explored.add(state_tuple)

    return None

def simple_reflex(initial_state):
    current = copy.deepcopy(initial_state)
    history = [Node(current, None, None, 0)]
    pre_move = ""

    for step in range(1, 500): # Giới hạn bước
        if check_done(current): 
            return history
        
        moves = possible_move(current)
        valid_moves = [m for m in moves if not (pre_move and remove_repetition(m, pre_move))]

        if not valid_moves: 
            valid_moves = moves

        chosen_move = random.choice(valid_moves)
        current = do_action(current, chosen_move)
        history.append(Node(current, None, chosen_move, step))
        pre_move = chosen_move

    return None

def model_based_reflex(initial_state):
    current = copy.deepcopy(initial_state)
    history = [Node(current, None, None, 0)]
    pre_move = ""

    for step in range(1, 500):
        # Điểm đích của bài toán mẫu Model-based
        if check_done(current): 
            return history
        
        moves = possible_move(current)
        opposite_moves = [m for m in moves if pre_move and remove_repetition(m, pre_move)]

        for m in opposite_moves:
            if len(moves) > 1: 
                moves.remove(m)

        chosen_move = random.choice(moves)
        current = do_action(current, chosen_move)
        history.append(Node(current, None, chosen_move, step))
        pre_move = chosen_move

    return None

# GIAO DIỆN ĐỒ HỌA (GUI)
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Solver")
        
        # Tiêu đề
        tk.Label(root, text="Chương trình 8 Puzzle", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Khung chính
        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # === BÊN TRÁI ===
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 1. Các entry nhập số
        tk.Label(left_frame, text="Nhập ma trận (0-8):").pack(anchor="w")
        grid_frame = tk.Frame(left_frame)
        grid_frame.pack(pady=5)
        
        self.entries = []
        for i in range(3):
            row_entries = []

            for j in range(3):
                e = tk.Entry(grid_frame, width=3, font=("Arial", 20), justify="center")
                e.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(e)

            self.entries.append(row_entries)
            
        # 2. Chọn thuật toán
        tk.Label(left_frame, text="Chọn thuật toán:").pack(anchor="w", pady=(10, 0))
        self.algo_var = tk.StringVar(value="BFS")
        algos = ["BFS", "DFS", "IDS", "UCS", "Simple Reflex", "Model-based Reflex"]
        
        for algo in algos:
            tk.Radiobutton(left_frame, text=algo, variable=self.algo_var, value=algo).pack(anchor="w")
            
        # 3. Các nút bấm
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Tạo bài mới (New)", command=self.new_puzzle, width=15).pack(pady=2)
        tk.Button(btn_frame, text="Tìm kiếm (Search)", command=self.search, width=15).pack(pady=2)
        
        # === BÊN PHẢI ===
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Kết quả các bước chạy:").pack(anchor="w")
        self.txt_log = scrolledtext.ScrolledText(right_frame, width=40, height=20, font=("Consolas", 10))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # Khởi tạo dữ liệu ngẫu nhiên ban đầu
        self.new_puzzle()

    def get_matrix(self):
        # Đọc ma trận từ các ô Entry
        matrix = []
        try:
            for i in range(3):
                row = []
                for j in range(3):
                    val = int(self.entries[i][j].get())
                    row.append(val)
                matrix.append(row)
            return matrix
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng chỉ nhập số!")
            return None

    def new_puzzle(self):
        # Sinh ma trận ngẫu nhiên có lời giải
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
                break
        
        # Cập nhật lên Entry
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(matrix[i][j]))

        self.txt_log.delete('1.0', tk.END)

    def print_steps(self, steps):
        # In các bước ra Text Area
        self.txt_log.delete('1.0', tk.END)

        for i, node in enumerate(steps):
            move_str = node.move if node.move else "Bắt đầu"
            self.txt_log.insert(tk.END, f"Bước {i} - Nước đi: {move_str}\n")
            for row in node.state:
                self.txt_log.insert(tk.END, "  " + "  ".join(str(x) if x != 0 else "_" for x in row) + "\n")

            self.txt_log.insert(tk.END, "-" * 20 + "\n")

        self.txt_log.see(tk.END)
        messagebox.showinfo("Hoàn thành", f"Đã tìm thấy đường đi trong {len(steps)-1} bước!")

    def search(self):
        # Khởi động tìm kiếm
        matrix = self.get_matrix()
        if not matrix: return
        
        algo = self.algo_var.get()
        if algo in ["BFS", "DFS", "IDS", "UCS"] and not check_solvable(matrix):
            messagebox.showwarning("Cảnh báo", "Trạng thái này không có lời giải tiêu chuẩn!")
            return
            
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.insert(tk.END, f"Đang chạy thuật toán {algo}...\n")
        self.root.update()
        
        result = None
        if algo == "BFS": 
            result = bfs(matrix)
        elif algo == "DFS": 
            result = dfs(matrix)
        elif algo == "IDS": 
            result = ids(matrix)
        elif algo == "UCS": 
            result = ucs(matrix)
        elif algo == "Simple Reflex": 
            result = simple_reflex(matrix)
        elif algo == "Model-based Reflex": 
            result = model_based_reflex(matrix)
        
        if result == "Timeout":
            messagebox.showwarning("Quá tải", "DFS đi quá sâu, đã dừng để tránh đơ máy.")
        elif result is None:
            messagebox.showinfo("Thất bại", "Không tìm được lời giải hoặc đã đạt giới hạn vòng lặp.")
        else:
            self.print_steps(result)

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()