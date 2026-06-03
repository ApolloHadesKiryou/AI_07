import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random
import copy
from collections import deque
from queue import PriorityQueue

# 1. LỚP DỮ LIỆU NODE SỬ DỤNG CHO CÁC THUẬT TOÁN ĐỒ THỊ
class Node:
    def __init__(self, state, parent, move, step):
        self.state = state
        self.parent = parent
        self.move = move
        self.step = step # Chi phí g(n) dùng cho UCS và A*

    def __lt__(self, other):
        return self.step < other.step

# 2. CÁC HÀM LOGIC CHUNG

# Kiểm tra xem ma trận hiện tại đã khớp với ma trận đích (Goal) chưa
def check_done(matrix):
    return matrix == [
        [1, 2, 3],
        [4, 5, 6], 
        [7, 8, 0]
    ]

# Tìm tọa độ hàng (i) và cột (j) của ô trống (số 0)
def find_empty_position(matrix):
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return i, j
    return -1, -1

# Kiểm tra xem ô trống có thể di chuyển theo những hướng nào
def possible_move(matrix):
    moves = []
    x, y = find_empty_position(matrix)
    if x < 2: moves.append("D") # Nếu chưa ở hàng cuối -> có thể đi Xuống (Down)
    if x > 0: moves.append("U") # Nếu chưa ở hàng đầu -> có thể đi Lên (Up)
    if y < 2: moves.append("R") # Nếu chưa ở cột cuối -> có thể đi Phải (Right)
    if y > 0: moves.append("L") # Nếu chưa ở cột đầu -> có thể đi Trái (Left)
    return moves

# Ngăn thuật toán đi lùi (tránh bị lặp vô hạn). Ví dụ: vừa đi Lên (U) xong thì không được đi Xuống (D) ngay.
def remove_repetition(move, pre_move):
    return ((move == "U" and pre_move == "D") or 
            (move == "D" and pre_move == "U") or
            (move == "L" and pre_move == "R") or 
            (move == "R" and pre_move == "L"))

# Tạo ra ma trận mới sau khi thực hiện 1 bước đi (tráo đổi vị trí số 0 và số kề cạnh)
def do_action(matrix, move):
    new_matrix = copy.deepcopy(matrix) # Bắt buộc phải deepcopy để không làm hỏng ma trận gốc của Node cha
    x, y = find_empty_position(new_matrix)
    if move == "U": new_matrix[x][y], new_matrix[x - 1][y] = new_matrix[x - 1][y], new_matrix[x][y]
    elif move == "D": new_matrix[x][y], new_matrix[x + 1][y] = new_matrix[x + 1][y], new_matrix[x][y]
    elif move == "L": new_matrix[x][y], new_matrix[x][y - 1] = new_matrix[x][y - 1], new_matrix[x][y]
    elif move == "R": new_matrix[x][y], new_matrix[x][y + 1] = new_matrix[x][y + 1], new_matrix[x][y]
    return new_matrix

# Chuyển ma trận (List of Lists) thành Tuple. 
# Lý do: Kiểu List có thể thay đổi (mutable) nên không thể đưa vào tập hợp Set() (explored). Tuple thì được.
def matrix_to_tuple(matrix):
    return tuple(tuple(row) for row in matrix)

# Khi tìm thấy đích, dùng hàm này dò ngược theo thuộc tính parent để lấy ra toàn bộ đường đi từ Start -> Goal
def solution(node):
    result = []
    while node is not None:
        result.append(node)
        node = node.parent
    result.reverse() # Đảo ngược lại để có mảng theo đúng thứ tự từ Start tới Goal
    return result

# Hàm toán học: Kiểm tra xem đề bài sinh ra có khả năng giải được không (Dựa vào số nghịch thế - inversions)
# Số nghịch thế chẵn -> giải được. Lẻ -> Vô nghiệm. Ngăn thuật toán chạy vô cực.
def check_solvable(matrix):
    arr = [val for row in matrix for val in row if val != 0] # Dàn ma trận thành mảng 1 chiều, bỏ qua số 0
    inversions = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
    return inversions % 2 == 0

# Hàm Heuristic h(n) 1: Đếm số ô sai vị trí (Dùng cho Greedy, A*, IDA*)
def calc_heuristic(matrix):
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    count = 0
    for i in range(3):
        for j in range(3):
            if matrix[i][j] != 0 and matrix[i][j] != goal[i][j]:
                count += 1
    return count

# Hàm Heuristic h(n) 2: Khoảng cách Manhattan (Dùng cho các thuật toán Climbing & Beam)
def calc_manhattan(matrix):
    distance = 0
    for i in range(3):
        for j in range(3):
            val = matrix[i][j]
            if val != 0:
                target_row = (val - 1) // 3
                target_col = (val - 1) % 3
                distance += abs(i - target_row) + abs(j - target_col)
    return distance

# Hàm phụ trợ sinh ma trận ngẫu nhiên giải được
def get_random_solvable_state():
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
            return matrix

# 3. 14 THUẬT TOÁN TÌM KIẾM

# Breadth-First Search (Tìm kiếm theo chiều rộng)
def bfs(initial_state):
    node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(node.state): return solution(node), visited_nodes
    
    frontier = deque([node]) 
    explored = {matrix_to_tuple(node.state)}

    while frontier:
        u = frontier.popleft() 
        visited_nodes += 1
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): continue
            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)
            if state_tuple not in explored: 
                child = Node(new_state, u, move, u.step + 1)
                if check_done(child.state): 
                    return solution(child), visited_nodes
                frontier.append(child)
                explored.add(state_tuple)
    return None, visited_nodes

# Depth-First Search (Tìm kiếm theo chiều sâu)
def dfs(initial_state):
    node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(node.state): return solution(node), visited_nodes
    
    frontier = [node] 
    explored = {matrix_to_tuple(node.state)}

    while frontier:
        if visited_nodes > 30000: return "Timeout", visited_nodes 
        u = frontier.pop() 
        visited_nodes += 1
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): continue
            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)
            if state_tuple not in explored:
                child = Node(new_state, u, move, u.step + 1)
                if check_done(child.state): 
                    return solution(child), visited_nodes
                frontier.append(child)
                explored.add(state_tuple)
    return None, visited_nodes

# Depth-Limited Search (Thành phần phụ trợ của IDS) - Tìm theo chiều sâu nhưng có giới hạn (limit)
def dls(node, limit):
    frontier = [node]
    visited_nodes = 0
    while frontier:
        u = frontier.pop()
        visited_nodes += 1
        if check_done(u.state): return solution(u), visited_nodes
        if u.step < limit: 
            for move in possible_move(u.state):
                if u.move and remove_repetition(move, u.move): continue
                child = Node(do_action(u.state, move), u, move, u.step + 1)
                frontier.append(child)
    return None, visited_nodes

# Iterative Deepening Search (Tìm kiếm sâu dần)
def ids(initial_state):
    root_node = Node(initial_state, None, None, 0)
    total_visited = 0
    for depth in range(25): 
        res, visited = dls(root_node, depth) 
        total_visited += visited
        if res: return res, total_visited
    return None, total_visited

# Uniform Cost Search (Tìm kiếm chi phí đồng nhất)
def ucs(initial_state):
    root_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(root_node.state): return solution(root_node), visited_nodes
    
    frontier = PriorityQueue() 
    frontier.put((root_node.step, root_node)) 
    explored = {matrix_to_tuple(root_node.state)}

    while not frontier.empty():
        _, u = frontier.get()
        visited_nodes += 1
        if check_done(u.state): return solution(u), visited_nodes
        
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): continue
            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)
            if state_tuple not in explored:
                child = Node(new_state, u, move, u.step + 1)
                frontier.put((child.step, child)) 
                explored.add(state_tuple)
    return None, visited_nodes

# Greedy Best-First Search (Tìm kiếm Tham Lam)
def greedy_search(initial_state):
    start_node = Node(initial_state, None, None, 0)
    frontier = [start_node]
    reached = []
    visited_nodes = 0

    while len(frontier) > 0:
        n = min(frontier, key=lambda node: calc_heuristic(node.state))
        visited_nodes += 1
        if check_done(n.state): return solution(n), visited_nodes
            
        frontier.remove(n)
        reached.append(n)
        
        for move in possible_move(n.state):
            if n.move and remove_repetition(move, n.move): continue
            m_state = do_action(n.state, move)
            m = Node(m_state, n, move, n.step + 1)
            
            in_frontier = any(matrix_to_tuple(m.state) == matrix_to_tuple(x.state) for x in frontier)
            in_reached = any(matrix_to_tuple(m.state) == matrix_to_tuple(x.state) for x in reached)
            
            if not in_frontier and not in_reached:
                frontier.append(m)
    return None, visited_nodes

# Thuật toán A* (A-Star) - Tối ưu và thông minh nhất
def a_star_search(initial_state):
    start_node = Node(initial_state, None, None, 0)
    frontier = [start_node]
    reached = []
    visited_nodes = 0

    while len(frontier) > 0:
        n = min(frontier, key=lambda node: node.step + calc_heuristic(node.state))
        visited_nodes += 1
        if check_done(n.state): return solution(n), visited_nodes
            
        frontier.remove(n)
        reached.append(n)
        
        for move in possible_move(n.state):
            if n.move and remove_repetition(move, n.move): continue
            m_state = do_action(n.state, move)
            
            node_in_frontier = next((x for x in frontier if matrix_to_tuple(x.state) == matrix_to_tuple(m_state)), None)
            node_in_reached = next((x for x in reached if matrix_to_tuple(x.state) == matrix_to_tuple(m_state)), None)
            g_new_m = n.step + 1 
            
            if node_in_reached is not None:
                if g_new_m < node_in_reached.step:
                    reached.remove(node_in_reached)
                    node_in_reached.step = g_new_m
                    node_in_reached.parent = n
                    node_in_reached.move = move
                    frontier.append(node_in_reached) 
            elif node_in_frontier is not None:
                if g_new_m < node_in_frontier.step:
                    node_in_frontier.step = g_new_m
                    node_in_frontier.parent = n
                    node_in_frontier.move = move
            else:
                m = Node(m_state, n, move, g_new_m)
                frontier.append(m)
    return None, visited_nodes

# Iterative Deepening A* (IDA*) - Kết hợp giới hạn chiều sâu của IDS và hàm f(n) của A*
def ida_star(initial_state):
    root = Node(initial_state, None, None, 0)
    threshold = calc_heuristic(root.state)
    visited_nodes = [0] 

    def search(node, g, bound):
        visited_nodes[0] += 1
        f = g + calc_heuristic(node.state)
        if f > bound: return None, f
        if check_done(node.state): return node, "FOUND"
        
        min_val = float('inf')
        for move in possible_move(node.state):
            if node.move and remove_repetition(move, node.move): continue
            new_state = do_action(node.state, move)
            child = Node(new_state, node, move, g + 1)
            result_node, t = search(child, g + 1, bound)
            if t == "FOUND": return result_node, "FOUND"
            if t < min_val: min_val = t
        return None, min_val

    while True:
        result_node, t = search(root, 0, threshold)
        if t == "FOUND": return solution(result_node), visited_nodes[0]
        if t == float('inf'): return None, visited_nodes[0] 
        threshold = t 

# Simple Hill Climbing (Leo đồi đơn giản / First-choice)
def simple_hill_climbing(initial_state):
    current_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    while True:
        visited_nodes += 1
        if check_done(current_node.state): return solution(current_node), visited_nodes
        
        current_h = calc_manhattan(current_node.state)
        found_better = False
        for move in possible_move(current_node.state):
            if current_node.move and remove_repetition(move, current_node.move): continue
            new_state = do_action(current_node.state, move)
            neighbor_h = calc_manhattan(new_state)
            if neighbor_h < current_h:
                current_node = Node(new_state, current_node, move, current_node.step + 1)
                found_better = True
                break
        if not found_better:
            return solution(current_node), visited_nodes

# Steepest-Ascent Hill Climbing (Leo đồi dốc nhất / Tốt nhất)
def steepest_ascent_hill_climbing(initial_state):
    current_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    while True:
        visited_nodes += 1
        if check_done(current_node.state): return solution(current_node), visited_nodes
        
        current_h = calc_manhattan(current_node.state)
        best_neighbor = None
        best_h = current_h
        for move in possible_move(current_node.state):
            if current_node.move and remove_repetition(move, current_node.move): continue
            new_state = do_action(current_node.state, move)
            neighbor_h = calc_manhattan(new_state)
            if neighbor_h < best_h:
                best_h = neighbor_h
                best_neighbor = Node(new_state, current_node, move, current_node.step + 1)
        if best_neighbor is None:
            return solution(current_node), visited_nodes
        current_node = best_neighbor

# Stochastic Hill Climbing (Leo đồi ngẫu nhiên)
def stochastic_hill_climbing(initial_state):
    current_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    while True:
        visited_nodes += 1
        if check_done(current_node.state): return solution(current_node), visited_nodes
        
        current_h = calc_manhattan(current_node.state)
        better_neighbors = []
        for move in possible_move(current_node.state):
            if current_node.move and remove_repetition(move, current_node.move): continue
            new_state = do_action(current_node.state, move)
            neighbor_h = calc_manhattan(new_state)
            if neighbor_h < current_h:
                better_neighbors.append(Node(new_state, current_node, move, current_node.step + 1))
        if not better_neighbors:
            return solution(current_node), visited_nodes 
        current_node = random.choice(better_neighbors)

# Random Restart Hill Climbing (Leo đồi khởi động lại ngẫu nhiên)
def random_restart_hill_climbing(initial_state):
    max_restart = 50 
    visited_nodes = 0
    for i in range(max_restart):
        current_matrix = initial_state if i == 0 else get_random_solvable_state()
        current_node = Node(current_matrix, None, f"Restart Lượt {i+1}" if i > 0 else None, 0)
        while True:
            visited_nodes += 1
            if check_done(current_node.state): return solution(current_node), visited_nodes
            
            current_h = calc_manhattan(current_node.state)
            best_neighbor = None
            best_h = current_h
            for move in possible_move(current_node.state):
                if current_node.move and remove_repetition(move, current_node.move): continue
                new_state = do_action(current_node.state, move)
                neighbor_h = calc_manhattan(new_state)
                if neighbor_h < best_h:
                    best_h = neighbor_h
                    best_neighbor = Node(new_state, current_node, move, current_node.step + 1)
            if best_neighbor is None:
                break 
            current_node = best_neighbor
    return None, visited_nodes

# Local Beam Search (Tìm kiếm chùm cục bộ)
def local_beam_search(initial_state):
    k = 3
    visited_nodes = 0
    current_state_set = [Node(initial_state, None, None, 0)]
    for _ in range(k - 1):
        rand_matrix = get_random_solvable_state()
        current_state_set.append(Node(rand_matrix, None, "Random Start", 0))
        
    while True:
        neighbor_states = []
        for state_node in current_state_set:
            visited_nodes += 1
            for move in possible_move(state_node.state):
                if state_node.move and remove_repetition(move, state_node.move): continue
                new_state = do_action(state_node.state, move)
                neighbor_states.append(Node(new_state, state_node, move, state_node.step + 1))
        if not neighbor_states:
            return solution(current_state_set[0]), visited_nodes
            
        for neighbor in neighbor_states:
            if check_done(neighbor.state):
                return solution(neighbor), visited_nodes
                
        neighbor_states.sort(key=lambda node: calc_manhattan(node.state))
        current_state_set = neighbor_states[:k]

# Phản xạ đơn giản (Đi lung tung ngẫu nhiên, không thèm nhớ quá khứ xa)
def simple_reflex(initial_state):
    current = copy.deepcopy(initial_state)
    history = [Node(current, None, None, 0)]
    pre_move = ""
    for step in range(1, 500): 
        if check_done(current): return history, step
        moves = possible_move(current)
        valid_moves = [m for m in moves if not (pre_move and remove_repetition(m, pre_move))]
        if not valid_moves: valid_moves = moves
        chosen_move = random.choice(valid_moves)
        current = do_action(current, chosen_move)
        history.append(Node(current, None, chosen_move, step))
        pre_move = chosen_move
    return None, 500

# Phản xạ dựa trên mô hình (Thông minh hơn tí: Có xu hướng đi tránh lặp lại đường cũ)
def model_based_reflex(initial_state):
    current = copy.deepcopy(initial_state)
    history = [Node(current, None, None, 0)]
    pre_move = ""
    for step in range(1, 500):
        if check_done(current): return history, step
        moves = possible_move(current)
        opposite_moves = [m for m in moves if pre_move and remove_repetition(m, pre_move)]
        for m in opposite_moves:
            if len(moves) > 1: moves.remove(m)
        chosen_move = random.choice(moves)
        current = do_action(current, chosen_move)
        history.append(Node(current, None, chosen_move, step))
        pre_move = chosen_move
    return None, 500

# 4. GIAO DIỆN ĐỒ HỌA (GUI) NÂNG CẤP KÍCH THƯỚC
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Solver")
        self.root.geometry("1000x750") 
        self.is_animating = False 
        
        tk.Label(root, text="Chương trình 8 Puzzle", font=("Arial", 22, "bold")).pack(pady=15)
        
        main_frame = tk.Frame(root)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(main_frame) 
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        tk.Label(left_frame, text="Nhập ma trận (0-8):", font=("Arial", 14)).pack(anchor="w", pady=5)
        grid_frame = tk.Frame(left_frame)
        grid_frame.pack(pady=10)
        
        self.entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                e = tk.Entry(grid_frame, width=3, font=("Arial", 40, "bold"), justify="center")
                e.grid(row=i, column=j, padx=5, pady=5)
                row_entries.append(e)
            self.entries.append(row_entries)
            
        tk.Label(left_frame, text="Chọn thuật toán:", font=("Arial", 14)).pack(anchor="w", pady=(20, 5))

        self.algo_var = tk.StringVar(value="BFS")
        algos = ["BFS", "DFS", "IDS", "UCS", "Greedy Search", "A* Search", 
                 "IDA*", "Simple Hill Climbing", "Steepest-Ascent Hill Climbing", 
                 "Stochastic Hill Climbing", "Random Restart Hill Climbing", "Local Beam Search",
                 "Simple Reflex", "Model-based Reflex"]
        self.algo_cb = ttk.Combobox(left_frame, textvariable=self.algo_var, values=algos, state="readonly", width=25, font=("Arial", 14))
        self.algo_cb.pack(anchor="w", pady=5)
            
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=30)
        
        self.btn_new = tk.Button(btn_frame, text="Tạo bài mới", command=self.new_puzzle, width=20, font=("Arial", 14), height=2)
        self.btn_new.pack(pady=5)
        
        self.btn_search = tk.Button(btn_frame, text="Tìm kiếm", command=self.search, width=20, font=("Arial", 14), height=2)
        self.btn_search.pack(pady=5)
        
        right_frame = tk.Frame(main_frame) 
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(right_frame, text="Kết quả các bước chạy:", font=("Arial", 14)).pack(anchor="w", pady=5)
        
        self.txt_log = scrolledtext.ScrolledText(right_frame, width=50, height=25, font=("Consolas", 14))
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        self.new_puzzle() 

    def get_matrix(self):
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
        if self.is_animating: return 
        matrix = get_random_solvable_state()
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(matrix[i][j]))
        self.txt_log.delete('1.0', tk.END) 

    # Đệ quy tạo hiệu ứng in từ từ
    def animate_steps(self, steps, current_index, explored_count):
        if current_index < len(steps): 
            node = steps[current_index]
            move_str = node.move if node.move else "Bắt đầu"
            
            self.txt_log.insert(tk.END, f"Bước {current_index} - Nước đi: {move_str}\n")
            for row in node.state:
                self.txt_log.insert(tk.END, "    " + "    ".join(str(x) if x != 0 else "_" for x in row) + "\n")
            self.txt_log.insert(tk.END, "-" * 30 + "\n")
            self.txt_log.see(tk.END) 
            
            self.root.after(300, self.animate_steps, steps, current_index + 1, explored_count)
        else: # Nếu đã in xong tất cả các bước
            moves = [node.move for node in steps if node.move and not node.move.startswith("Restart") and not node.move.startswith("Random")]
            move_sequence = " -> ".join(moves) if moves else "Không có hành động"
            
            # Kiểm tra xem trạng thái cuối cùng có thực sự là đích hay không
            is_success = check_done(steps[-1].state)
            
            self.txt_log.insert(tk.END, f"\n[ KẾT QUẢ TỔNG QUÁT ]\n")
            self.txt_log.insert(tk.END, f"• Số lần duyệt (đã xét): {explored_count} trạng thái\n")
            self.txt_log.insert(tk.END, f"• Tổng số bước đã đi: {len(steps)-1}\n")
            
            if is_success:
                self.txt_log.insert(tk.END, f"• Trạng thái: GIẢI THÀNH CÔNG\n")
            else:
                self.txt_log.insert(tk.END, f"• Trạng thái: THẤT BẠI - BỊ KẸT (LOCAL MAXIMUM/MINIMUM)\n")
                
            self.txt_log.insert(tk.END, f"• Chuỗi hành động: \n  {move_sequence}\n\n")
            self.txt_log.see(tk.END)
            
            self.is_animating = False
            self.btn_search.config(state=tk.NORMAL)
            self.btn_new.config(state=tk.NORMAL)
            
            # Hiển thị thông báo popup tương ứng
            if is_success:
                messagebox.showinfo("Hoàn thành", "Đã mô phỏng xong các bước tới đích!")
            else:
                messagebox.showwarning("Bị kẹt", "Thuật toán đã dừng lại vì đạt cực trị cục bộ (Local Minimum).\nKhông thể tới đích!")

    def search(self):
        if self.is_animating: return
        
        matrix = self.get_matrix()
        if not matrix: return
        
        algo = self.algo_var.get()
        if not check_solvable(matrix):
            messagebox.showwarning("Cảnh báo", "Trạng thái này không có lời giải tiêu chuẩn!")
            return
            
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.insert(tk.END, f"Đang tính toán thuật toán {algo}...\n")
        self.root.update() 
        
        result = None
        visited_nodes = 0
        
        if algo == "BFS": result, visited_nodes = bfs(matrix)
        elif algo == "DFS": result, visited_nodes = dfs(matrix)
        elif algo == "IDS": result, visited_nodes = ids(matrix)
        elif algo == "UCS": result, visited_nodes = ucs(matrix)
        elif algo == "Greedy Search": result, visited_nodes = greedy_search(matrix)
        elif algo == "A* Search": result, visited_nodes = a_star_search(matrix)
        elif algo == "IDA*": result, visited_nodes = ida_star(matrix)
        elif algo == "Simple Hill Climbing": result, visited_nodes = simple_hill_climbing(matrix)
        elif algo == "Steepest-Ascent Hill Climbing": result, visited_nodes = steepest_ascent_hill_climbing(matrix)
        elif algo == "Stochastic Hill Climbing": result, visited_nodes = stochastic_hill_climbing(matrix)
        elif algo == "Random Restart Hill Climbing": result, visited_nodes = random_restart_hill_climbing(matrix)
        elif algo == "Local Beam Search": result, visited_nodes = local_beam_search(matrix)
        elif algo == "Simple Reflex": result, visited_nodes = simple_reflex(matrix)
        elif algo == "Model-based Reflex": result, visited_nodes = model_based_reflex(matrix)
        
        self.txt_log.delete('1.0', tk.END) 
        
        if result == "Timeout":
            messagebox.showwarning("Quá tải", f"Đã duyệt {visited_nodes} trạng thái nhưng dừng để tránh đơ máy.")
        elif result is None:
            messagebox.showinfo("Thất bại", f"Không tìm được lời giải sau {visited_nodes} lần duyệt.")
        else:
            self.is_animating = True 
            self.btn_search.config(state=tk.DISABLED) 
            self.btn_new.config(state=tk.DISABLED)
            
            self.txt_log.insert(tk.END, f"Đã tính xong, bắt đầu in các bước:\n{'='*40}\n\n")
            self.animate_steps(result, 0, visited_nodes) 

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()