import tkinter as tk
from tkinter import messagebox
import random
import copy

# ==========================================
# CẤU TRÚC DỮ LIỆU VÀ CÁC HÀM CƠ BẢN
# ==========================================

class Node:
    def __init__(self, state, parent, move, step):
        self.state = state
        self.parent = parent
        self.move = move
        self.step = step # step chính là DEPTH của node trong cây tìm kiếm

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
    # function problem.Is-GOAL(node.STATE)
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

def solution(node):
    # Truy vết kết quả trả về một mảng các node từ gốc đến đích
    result = []
    while node is not None:
        result.append(node)
        node = node.parent
    result.reverse()
    return result

def is_cycle(node):
    # function IS-CYCLE(node)
    # Kiểm tra xem trạng thái hiện tại có bị lặp lại trong đường đi từ gốc đến node này không
    current_state = node.state
    parent = node.parent
    while parent is not None:
        if parent.state == current_state:
            return True
        parent = parent.parent
    return False

# ==========================================
# THUẬT TOÁN THEO MÃ GIẢ TRONG ẢNH
# ==========================================

def depth_limited_search(initial_node, limit):
    # function DEPTH-LIMITED-SEARCH(problem, l)
    
    # frontier <- a LIFO queue (stack) with NODE(problem.INITIAL)
    frontier = [initial_node] 
    
    # result <- failure
    result = "failure"
    
    # while not IS-EMPTY(frontier) do
    while frontier:
        # node <- POP(frontier)
        node = frontier.pop()
        
        # if problem.Is-GOAL(node.STATE) then return node
        if check_done(node.state):
            return solution(node)
            
        # if DEPTH(node) > l then
        if node.step > limit:
            # result <- cutoff
            result = "cutoff"
            
        # else if not IS-CYCLE(node) do
        elif not is_cycle(node):
            # Lấy các hướng di chuyển hợp lệ
            moves = possible_move(node.state)
            
            # for each child in EXPAND(problem, node) do
            for move in moves:
                new_state = do_action(node.state, move)
                child = Node(new_state, node, move, node.step + 1)
                
                # add child to frontier
                frontier.append(child)
                
    # return result
    return result

def iterative_deepening_search(initial_node, gui=None, max_depth=30):
    # function ITERATIVE-DEEPENING-SEARCH(problem)
    
    # for depth = 0 to vô cực do (ở đây giới hạn max_depth để tránh treo máy nếu vô nghiệm)
    for depth in range(max_depth + 1):
        
        # Cập nhật GUI để người dùng biết thuật toán đang chạy tới độ sâu nào
        if gui:
            gui.status_label.config(text=f"Đang tìm kiếm... Limit Depth = {depth}")
            gui.root.update()
            
        # result <- DEPTH-LIMITED-SEARCH(problem, depth)
        result = depth_limited_search(initial_node, depth)
        
        # if result != cutoff then return result
        if result != "cutoff":
            return result
            
    # return failure (nếu vượt quá max_depth mà vẫn chỉ ra cutoff hoặc failure)
    return "failure"

# ==========================================
# GIAO DIỆN ĐỒ HỌA TKINTER
# ==========================================

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver (Thuật toán IDS)")
        self.matrix = self.create_matrix()
        
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)
        
        self.tiles = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.tiles[i][j] = tk.Label(self.frame, text="", font=("Helvetica", 32, "bold"), 
                                            width=4, height=2, borderwidth=2, relief="groove")
                self.tiles[i][j].grid(row=i, column=j, padx=5, pady=5)
        
        self.status_label = tk.Label(self.root, text="Sẵn sàng", font=("Helvetica", 14))
        self.status_label.pack(pady=10)
        
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(pady=10)
        
        self.solve_btn = tk.Button(self.btn_frame, text="Giải tự động (IDS)", font=("Helvetica", 12), command=self.solve)
        self.solve_btn.grid(row=0, column=0, padx=10)
        
        self.new_btn = tk.Button(self.btn_frame, text="Tạo bài mới", font=("Helvetica", 12), command=self.new_game)
        self.new_btn.grid(row=0, column=1, padx=10)
        
        self.update_ui()

    def create_matrix(self):
        # Trạng thái ban đầu dễ để test IDS nhanh hơn (IDS chạy lâu với trạng thái quá khó)
        # Nếu muốn random hoàn toàn, bỏ comment dòng dưới và comment khối trạng thái tĩnh
        # return create_matrix() 
        return [
            [1, 2, 3],
            [6, 0, 4],
            [7, 5, 8]
        ]

    def update_ui(self):
        for i in range(3):
            for j in range(3):
                val = self.matrix[i][j]
                if val == 0:
                    self.tiles[i][j].config(text="", bg="#d3d3d3")
                else:
                    self.tiles[i][j].config(text=str(val), bg="#ffd700") # Màu vàng nổi bật cho bản IDS

    def new_game(self):
        self.matrix = create_matrix() # Random ván mới
        self.update_ui()
        self.status_label.config(text="Sẵn sàng", fg="black")
        self.solve_btn.config(state=tk.NORMAL)

    def solve(self):
        self.solve_btn.config(state=tk.DISABLED)
        self.new_btn.config(state=tk.DISABLED)
        
        initial_node = Node(self.matrix, None, None, 0)
        
        # Gọi IDS, truyền đối tượng GUI vào để cập nhật label hiển thị depth đang quét
        result = iterative_deepening_search(initial_node, gui=self, max_depth=30)
        
        if result == "failure" or result == "cutoff":
            messagebox.showinfo("Kết quả", "Không tìm thấy lời giải (Vượt quá giới hạn độ sâu)!")
            self.solve_btn.config(state=tk.NORMAL)
            self.new_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Không có lời giải", fg="red")
        else:
            self.animate_solution(result)

    def animate_solution(self, steps, index=0):
        if index < len(steps):
            self.matrix = steps[index].state
            self.update_ui()
            
            move_text = steps[index].move if steps[index].move else "Bắt đầu"
            self.status_label.config(text=f"Bước: {steps[index].step} | Nước đi: {move_text} | Tổng: {len(steps)-1} bước", fg="black")
            
            self.root.after(300, self.animate_solution, steps, index + 1)
        else:
            self.solve_btn.config(state=tk.NORMAL)
            self.new_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Đã hoàn thành!", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.resizable(False, False)
    root.mainloop()