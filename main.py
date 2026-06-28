import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random
import copy
import math
from collections import deque
from queue import PriorityQueue
import sys

# Tăng giới hạn đệ quy để tránh lỗi Stack Overflow khi duyệt sâu
sys.setrecursionlimit(50000)

# ========================================================
# 1. LỚP DỮ LIỆU NODE SỬ DỤNG CHO CÁC THUẬT TOÁN ĐỒ THỊ
# ========================================================
class Node:
    """
    Class Node đại diện cho một 'nút' trên cây tìm kiếm. 
    Mỗi Node lưu trữ trạng thái hiện tại và lịch sử để tạo thành đường đi.
    """
    def __init__(self, state, parent, move, step):
        self.state = state   # Trạng thái ma trận hiện tại
        self.parent = parent # Node cha
        self.move = move     # Hành động di chuyển
        self.step = step     # Số bước đi từ trạng thái đầu

    def __lt__(self, other):
        """
        Hàm Magic (Less Than - <): Dạy cho cấu trúc PriorityQueue biết cách so sánh 2 Node.
        Khi đưa vào hàng đợi ưu tiên, Node nào có chi phí (step) nhỏ hơn sẽ được đẩy lên đầu.
        """
        return self.step < other.step

# ========================================================
# 2. CÁC HÀM LOGIC CHUNG CHO BÀI TOÁN 8-PUZZLE
# ========================================================

def check_done(matrix):
    """Trạng thái đích của bài toán"""
    return matrix == [
        [1, 2, 3],
        [4, 5, 6], 
        [7, 8, 0]
    ]

def find_empty_position(matrix):
    """Tìm tọa độ ô trống (giá trị 0)"""
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return i, j
    return -1, -1

def possible_move(matrix):
    """
    Dựa vào tọa độ của số 0 để biết nó có thể trượt đi đâu (Không được trượt ra ngoài rìa).
    Trả về mảng chứa các ký tự Hướng có thể đi: U (Up), D (Down), L (Left), R (Right).
    """
    moves = []
    x, y = find_empty_position(matrix)
    if x < 2: moves.append("D") # Chưa ở đáy -> Xuống được
    if x > 0: moves.append("U") # Chưa ở đỉnh -> Lên được
    if y < 2: moves.append("R") # Chưa ở sát phải -> Sang Phải được
    if y > 0: moves.append("L") # Chưa ở sát trái -> Sang Trái được
    return moves

def remove_repetition(move, pre_move):
    """
    Hàm tối ưu cây tìm kiếm: Tránh hành động đi lùi vô nghĩa.
    Nếu Node cha vừa đi Lên (U) thì Node con không nên đi Xuống (D) để quay về chỗ cũ.
    """
    return ((move == "U" and pre_move == "D") or 
            (move == "D" and pre_move == "U") or
            (move == "L" and pre_move == "R") or 
            (move == "R" and pre_move == "L"))

def do_action(matrix, move):
    """Thực hiện di chuyển ô trống"""
    # BẮT BUỘC dùng deepcopy. Nếu chỉ gán (new = matrix), khi sửa new, matrix cũ cũng bị hỏng (lỗi tham chiếu).
    new_matrix = copy.deepcopy(matrix) 
    x, y = find_empty_position(new_matrix)
    
    # 
    if move == "U": new_matrix[x][y], new_matrix[x - 1][y] = new_matrix[x - 1][y], new_matrix[x][y]
    elif move == "D": new_matrix[x][y], new_matrix[x + 1][y] = new_matrix[x + 1][y], new_matrix[x][y]
    elif move == "L": new_matrix[x][y], new_matrix[x][y - 1] = new_matrix[x][y - 1], new_matrix[x][y]
    elif move == "R": new_matrix[x][y], new_matrix[x][y + 1] = new_matrix[x][y + 1], new_matrix[x][y]
    
    return new_matrix

def matrix_to_tuple(matrix):
    """
    Chuyển List of Lists (Mảng 2 chiều) thành Tuple of Tuples.
    Lý do: Trong Python, List là mutable (có thể thay đổi) -> Không thể dùng làm Khóa (Key) cho Set/Dictionary.
    Tuple là immutable (Bất biến) -> Dùng để nhét vào tập hợp 'explored' (đánh dấu đã duyệt) cực nhanh.
    """
    return tuple(tuple(row) for row in matrix)

def solution(node):
    """Truy vết đường đi từ đích về xuất phát"""
    result = []
    while node is not None:
        result.append(node)
        node = node.parent
    result.reverse() # Đảo ngược thứ tự để có đường đi từ Start đến Goal
    return result

def check_solvable(matrix):
    """
    Toán học của 8-Puzzle: Đếm 'Số nghịch thế' (Inversions).
    Nghịch thế là khi số lớn đứng trước số bé trong mảng 1 chiều.
    Nếu tổng nghịch thế là số CHẴN -> Trò chơi giải được. Số LẺ -> Trò chơi vô nghiệm.
    """
    arr = [val for row in matrix for val in row if val != 0] # Duỗi ma trận 2D thành mảng 1D, bỏ số 0
    inversions = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
    return inversions % 2 == 0

def calc_heuristic(matrix):
    """Đếm số ô sai vị trí so với trạng thái đích"""
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    count = 0
    for i in range(3):
        for j in range(3):
            if matrix[i][j] != 0 and matrix[i][j] != goal[i][j]:
                count += 1
    return count

def calc_manhattan(matrix):
    """
    Hàm Heuristic h(n) số 2: Khoảng cách Manhattan (Khoảng cách đường chim bay theo ô vuông).
    Tính tổng số bước tối thiểu mà MỖI Ô cần phải đi để về đúng vị trí (bỏ qua vật cản).
    Thông minh hơn Heuristic đếm ô sai.
    """
    distance = 0
    for i in range(3):
        for j in range(3):
            val = matrix[i][j]
            if val != 0:
                target_row = (val - 1) // 3 # Công thức toán học tìm Tọa độ Hàng Đích
                target_col = (val - 1) % 3  # Công thức toán học tìm Tọa độ Cột Đích
                distance += abs(i - target_row) + abs(j - target_col)
    return distance

def get_random_solvable_state():
    """Sinh trạng thái ngẫu nhiên có thể giải được"""
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
        # 
        if check_solvable(matrix) and not check_done(matrix):
            return matrix

# --- LOGIC RIÊNG CHO MÔI TRƯỜNG MÙ (SENSORLESS BELIEF STATE) ---
def do_belief_action(belief_tuple, move):
    """
    Trong môi trường mù, ta không biết mình đang ở ma trận nào.
    Nên 1 hành động phải được áp dụng cho TẤT CẢ các ma trận có thể (Belief state).
    """
    new_states = set()
    for state_tuple in belief_tuple:
        state_list = [list(row) for row in state_tuple]
        moves = possible_move(state_list)
        if move in moves:
            new_state = do_action(state_list, move)
            new_states.add(matrix_to_tuple(new_state))
        else:
            new_states.add(matrix_to_tuple(state_list)) # Nếu hành động không hợp lệ, giữ nguyên trạng thái
    return tuple(sorted(new_states))

def check_belief_done(belief_tuple):
    """Kiểm tra belief state đạt đến đích"""
    goal_tuple = matrix_to_tuple([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
    return len(belief_tuple) == 1 and belief_tuple[0] == goal_tuple

def get_close_belief_states():
    """Sinh belief state khởi đầu ngẫu nhiên cách đích từ 3 đến 5 bước"""
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    goal_tuple = matrix_to_tuple(goal)
    states = set()
    while len(states) < 3:
        curr = copy.deepcopy(goal)
        num_moves = random.randint(3, 5) 
        pre_move = None
        for _ in range(num_moves): 
            moves = possible_move(curr)
            valid_moves = [m for m in moves if not (pre_move and remove_repetition(m, pre_move))]
            if not valid_moves: valid_moves = moves
            chosen_move = random.choice(valid_moves)
            curr = do_action(curr, chosen_move)
            pre_move = chosen_move
        curr_tuple = matrix_to_tuple(curr)
        if curr_tuple != goal_tuple: 
            states.add(curr_tuple)
    return tuple(states)

def calc_belief_heuristic(belief_tuple):
    """Tính heuristic cho belief state (khoảng cách Manhattan lớn nhất)"""
    max_h = 0
    for state_tuple in belief_tuple:
        state_list = [list(row) for row in state_tuple]
        h = calc_manhattan(state_list) 
        if h > max_h:
            max_h = h
    return max_h

# ------------------------------------------------------------------------------
# 3.1. CÁC THUẬT TOÁN TÌM KIẾM MÙ (UNINFORMED SEARCH)
# Nhóm này không dùng não (không có hàm đánh giá). Chỉ dò đường dựa trên luật cơ bản.
# ------------------------------------------------------------------------------

def bfs(initial_state):
    """Breadth-First Search (Duyệt theo chiều rộng). Dùng Queue (vào trước ra trước). Ưu điểm: Chắc chắn tìm đường ngắn nhất."""
    node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(node.state): return solution(node), visited_nodes
    
    frontier = deque([node]) # 
    explored = {matrix_to_tuple(node.state)}
    
    while frontier:
        u = frontier.popleft() # Lấy node ở đầu hàng đợi
        visited_nodes += 1
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): continue
            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)
            
            if state_tuple not in explored: # 
                child = Node(new_state, u, move, u.step + 1)
                if check_done(child.state): return solution(child), visited_nodes
                frontier.append(child)
                explored.add(state_tuple)
    return None, visited_nodes

def dfs(initial_state):
    """Thuật toán tìm kiếm theo chiều sâu (DFS)"""
    node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(node.state): return solution(node), visited_nodes
    
    frontier = [node] # List Python bản chất hoạt động như Stack
    explored = {matrix_to_tuple(node.state)}
    
    while frontier:
        # Giới hạn số node duyệt để tránh timeout/tràn bộ nhớ
        if visited_nodes > 30000: return "Timeout", visited_nodes 
        
        u = frontier.pop() # Lấy node ở đỉnh ngăn xếp
        visited_nodes += 1
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): continue
            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)
            
            if state_tuple not in explored:
                child = Node(new_state, u, move, u.step + 1)
                if check_done(child.state): return solution(child), visited_nodes
                frontier.append(child)
                explored.add(state_tuple)
    return None, visited_nodes

def dls(node, limit):
    """Thuật toán DFS giới hạn độ sâu (DLS)"""
    frontier = [node]
    visited_nodes = 0
    while frontier:
        u = frontier.pop()
        visited_nodes += 1
        if check_done(u.state): return solution(u), visited_nodes
        
        if u.step < limit: # 
            for move in possible_move(u.state):
                if u.move and remove_repetition(move, u.move): continue
                child = Node(do_action(u.state, move), u, move, u.step + 1)
                frontier.append(child)
    return None, visited_nodes

def ids(initial_state):
    """Thuật toán tìm kiếm sâu dần (IDS)"""
    root_node = Node(initial_state, None, None, 0)
    total_visited = 0
    for depth in range(25): # Lặp độ sâu từ 0 đến 24
        res, visited = dls(root_node, depth) 
        total_visited += visited
        if res: return res, total_visited # 
    return None, total_visited

def ucs(initial_state):
    """Thuật toán tìm kiếm chi phí đồng nhất (UCS)"""
    root_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(root_node.state): return solution(root_node), visited_nodes
    
    frontier = PriorityQueue() # 
    frontier.put((root_node.step, root_node)) 
    explored = {matrix_to_tuple(root_node.state)}
    
    while not frontier.empty():
        _, u = frontier.get() # 
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

# ------------------------------------------------------------------------------
# 3.2. CÁC THUẬT TOÁN TÌM KIẾM CÓ THÔNG TIN (INFORMED SEARCH)
# Nhóm này sử dụng hàm đánh giá Heuristic h(n) để "đánh hơi" xem đích nằm ở đâu.
# ------------------------------------------------------------------------------

def greedy_search(initial_state):
    """Thuật toán tìm kiếm tham lam (Greedy Search)"""
    start_node = Node(initial_state, None, None, 0)
    frontier = [start_node]
    reached = []
    visited_nodes = 0
    while len(frontier) > 0:
        # Lấy node có heuristic nhỏ nhất
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
            if not in_frontier and not in_reached: frontier.append(m)
    return None, visited_nodes

def a_star_search(initial_state):
    """Thuật toán tìm kiếm A*"""
    start_node = Node(initial_state, None, None, 0)
    frontier = [start_node]
    reached = []
    visited_nodes = 0
    while len(frontier) > 0:
        # Lấy node có f(n) nhỏ nhất
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
            
            # Cập nhật đường đi nếu tìm thấy chi phí tốt hơn
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

def ida_star(initial_state):
    """Thuật toán tìm kiếm IDA*"""
    root = Node(initial_state, None, None, 0)
    threshold = calc_heuristic(root.state) # Ngưỡng cắt tỉa ban đầu
    visited_nodes = [0] 
    
    def search(node, g, bound):
        visited_nodes[0] += 1
        f = g + calc_heuristic(node.state)
        # Cắt nhánh nếu f vượt quá ngưỡng
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
        threshold = t # Cập nhật ngưỡng giới hạn f

# ------------------------------------------------------------------------------
# 3.3. CÁC THUẬT TOÁN TỐI ƯU CỤC BỘ (LOCAL SEARCH)
# Nhóm này không quan tâm đường đi. Chỉ đứng tại chỗ nhìn xung quanh, thấy nước nào "gần đích hơn" thì nhảy tới. Rất dễ bị kẹt (Local Maximum).
# ------------------------------------------------------------------------------

def simple_hill_climbing(initial_state):
    """Thuật toán leo đồi đơn giản (Simple Hill Climbing)"""
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
            if neighbor_h < current_h: # 
                current_node = Node(new_state, current_node, move, current_node.step + 1)
                found_better = True
                break
        if not found_better: return solution(current_node), visited_nodes # 

def steepest_ascent_hill_climbing(initial_state):
    """Thuật toán leo đồi dốc nhất (Steepest-Ascent Hill Climbing)"""
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
            if neighbor_h < best_h: # 
                best_h = neighbor_h
                best_neighbor = Node(new_state, current_node, move, current_node.step + 1)
        if best_neighbor is None: return solution(current_node), visited_nodes
        current_node = best_neighbor

def stochastic_hill_climbing(initial_state):
    """Thuật toán leo đồi ngẫu nhiên (Stochastic Hill Climbing)"""
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
        if not better_neighbors: return solution(current_node), visited_nodes 
        current_node = random.choice(better_neighbors)

def random_restart_hill_climbing(initial_state):
    """Thuật toán leo đồi khởi động lại ngẫu nhiên (Random Restart)"""
    max_restart = 50 
    visited_nodes = 0
    for i in range(max_restart):
        current_matrix = initial_state if i == 0 else get_random_solvable_state()
        current_node = Node(current_matrix, None, f"Lượt {i+1}" if i > 0 else None, 0)
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
            if best_neighbor is None: break  # 
            current_node = best_neighbor
    return None, visited_nodes

def simulated_annealing(initial_state):
    """
    Simulated Annealing (Luyện kim tự nhiên). Giải quyết điểm yếu chết người của Hill Climbing bằng cách: 
    Thỉnh thoảng cho phép đi những nước TỒI TỆ (h(n) tăng) để bật ra khỏi thung lũng cục bộ. Càng về sau xác suất chấp nhận nước tồi càng giảm.
    """
    current_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    T = 100.0      # Nhiệt độ ban đầu (Càng nóng càng đi loạn)
    T_min = 0.001  # Nhiệt độ tối thiểu để dừng
    alpha = 0.99   # Hệ số làm lạnh (Hạ nhiệt độ qua mỗi vòng)
    while T > T_min:
        visited_nodes += 1
        if check_done(current_node.state): return solution(current_node), visited_nodes
        moves = possible_move(current_node.state)
        valid_moves = [m for m in moves if not (current_node.move and remove_repetition(m, current_node.move))]
        if not valid_moves: valid_moves = moves
        
        chosen_move = random.choice(valid_moves)
        new_state = do_action(current_node.state, chosen_move)
        next_node = Node(new_state, current_node, chosen_move, current_node.step + 1)
        
        # 
        delta = calc_manhattan(next_node.state) - calc_manhattan(current_node.state)
        
        if delta < 0: # 
            current_node = next_node
        else:
            p = math.exp(-delta / T) # 
            if random.random() < p: current_node = next_node
        T = alpha * T
    return solution(current_node), visited_nodes

def local_beam_search(initial_state):
    """Thuật toán tìm kiếm chùm cục bộ (Local Beam Search)"""
    k = 3
    visited_nodes = 0
    current_state_set = [Node(initial_state, None, None, 0)]
    for _ in range(k - 1): # 
        rand_matrix = get_random_solvable_state()
        current_state_set.append(Node(rand_matrix, None, "Khoi tao ngau nhien", 0))
        
    while True:
        neighbor_states = []
        for state_node in current_state_set:
            visited_nodes += 1
            for move in possible_move(state_node.state):
                if state_node.move and remove_repetition(move, state_node.move): continue
                new_state = do_action(state_node.state, move)
                neighbor_states.append(Node(new_state, state_node, move, state_node.step + 1))
                
        if not neighbor_states: return solution(current_state_set[0]), visited_nodes
        for neighbor in neighbor_states:
            if check_done(neighbor.state): return solution(neighbor), visited_nodes
            
        # Sắp xếp toàn bộ rổ hàng xóm lấy được
        neighbor_states.sort(key=lambda node: calc_manhattan(node.state))
        current_state_set = neighbor_states[:k] # Giữ lại K trạng thái tốt nhất

# ------------------------------------------------------------------------------
# 3.4. CÁC TÁC NHÂN PHẢN XẠ (REFLEX AGENT)
# Trí tuệ cấp độ thấp nhất. Không cần tìm kiếm cây/đồ thị, chỉ đưa ra hành động dựa trên cảm nhận tức thì.
# ------------------------------------------------------------------------------

def simple_reflex(initial_state):
    """Tác nhân phản xạ đơn giản (Simple Reflex)"""
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

def model_based_reflex(initial_state):
    """Tác nhân phản xạ có mô hình (Model-based Reflex)"""
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

# ------------------------------------------------------------------------------
# 3.5. TÌM KIẾM ĐỒ THỊ ĐẶC BIỆT & MÔI TRƯỜNG MÙ
# ------------------------------------------------------------------------------

def belief_state_astar(initial_belief_tuple):
    """
    Belief State A* (Giải thuật 8-Puzzle khi bịt mắt).
    Người chơi không nhìn thấy bảng hiện tại (Initial Belief là 1 tập nhiều ma trận).
    Dùng A* để áp dụng hành động đồng loạt lên toàn bộ tập niềm tin cho tới khi nó teo lại thành 1 trạng thái Đích duy nhất.
    """
    start_node = Node(initial_belief_tuple, None, None, 0)
    visited_nodes = 0
    if check_belief_done(start_node.state): 
        return solution(start_node), visited_nodes
        
    frontier = PriorityQueue()
    counter = 0 
    start_f = 0 + calc_belief_heuristic(initial_belief_tuple)
    frontier.put((start_f, counter, start_node))
    explored = {initial_belief_tuple: 0}

    while not frontier.empty():
        if visited_nodes > 150000: return "Timeout", visited_nodes 
        f_score, _, u = frontier.get() 
        visited_nodes += 1
        
        if check_belief_done(u.state): 
            return solution(u), visited_nodes
            
        for move in ["U", "D", "L", "R"]: 
            if u.move and remove_repetition(move, u.move): continue
            new_belief = do_belief_action(u.state, move)
            new_g = u.step + 1
            
            if new_belief not in explored or new_g < explored[new_belief]:
                explored[new_belief] = new_g
                child = Node(new_belief, u, move, new_g)
                child_f = new_g + calc_belief_heuristic(new_belief)
                counter += 1
                frontier.put((child_f, counter, child))
                
    return None, visited_nodes

def and_or_graph_search(initial_state):
    """
    AND-OR Graph Search. Mô phỏng tìm kiếm trong môi trường có rủi ro/đối thủ.
    - Nút OR: Bạn chọn đường đi (Lựa chọn của Agent).
    - Nút AND: Môi trường (hay đối thủ) quyết định hậu quả rẽ nhánh của bạn.
    Thuật toán trả về một Kế hoạch (Plan) xử lý triệt để mọi rủi ro thay vì 1 đường đi cố định.
    """
    visited_nodes = [0]
    
    def or_search(state, path, current_node):
        if visited_nodes[0] > 30000: return "Timeout"
        visited_nodes[0] += 1
        if check_done(state): return current_node
        
        state_tuple = matrix_to_tuple(state)
        if state_tuple in path: return "failure" # Tránh vòng lặp vô hạn
        
        for move in possible_move(state):
            if current_node.move and remove_repetition(move, current_node.move): continue
                
            new_state = do_action(state, move)
            child_node = Node(new_state, current_node, move, current_node.step + 1)
            result_states = [child_node]  # Khởi tạo danh sách kết quả cho nhánh AND
            plan = and_search(result_states, path + [state_tuple])
            
            if plan != "failure": return plan
        return "failure"

    def and_search(states, path):
        plans = {}
        for s_node in states:
            plan_s = or_search(s_node.state, path, s_node) # 
            if plan_s == "failure" or plan_s == "Timeout": return plan_s
            plans[matrix_to_tuple(s_node.state)] = plan_s
        return list(plans.values())[0]

    start_node = Node(initial_state, None, None, 0)
    result_node = or_search(initial_state, [], start_node)
    
    if result_node == "Timeout": return "Timeout", visited_nodes[0]
    elif result_node == "failure" or result_node is None: return None, visited_nodes[0]
    else: return solution(result_node), visited_nodes[0]

# ------------------------------------------------------------------------------
# 3.6. CÁC THUẬT TOÁN BÀI TOÁN THỎA MÃN RÀNG BUỘC (CSP - CONSTRAINT SATISFACTION)
# Lưu ý: Các thuật toán này không trượt (slide) các ô. Nó coi 8-Puzzle là bài toán:
# "Điền 9 con số từ 0->8 vào 9 ô vuông trống sao cho các số không trùng lặp và khớp vị trí đích."
# Do đó, nó sẽ DỊCH CHUYỂN TỨC THỜI tới kết quả.
# ------------------------------------------------------------------------------
    
def backtracking_search(initial_state):
    """Thuật toán CSP quay lui (Backtracking)"""
    visited_nodes = [0]
    
    variables = [(i, j) for i in range(3) for j in range(3)] # 9 Biến: Tọa độ 9 ô vuông
    goal_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    def is_consistent(var, value, assignment):
        """Kiểm tra tính hợp lệ ràng buộc"""
        if value in assignment.values(): return False
        if value != goal_matrix[var[0]][var[1]]: return False
        return True

    def recursive_backtracking(assignment):
        visited_nodes[0] += 1
        if visited_nodes[0] > 30000: return "Timeout"

        if len(assignment) == len(variables): return assignment # 

        var = next(v for v in variables if v not in assignment) # 

        for value in range(9): # 
            if is_consistent(var, value, assignment):
                assignment[var] = value # Thỏa mãn thì gán
                result = recursive_backtracking(assignment) # 
                if result != "failure" and result != "Timeout": return result
                del assignment[var] # 
        return "failure"

    result_assignment = recursive_backtracking({})

    if result_assignment == "Timeout": return "Timeout", visited_nodes[0]
    elif result_assignment != "failure":
        # Chuyển đổi ngược Dictionary Assignment về lại mảng 2D cho GUI đọc
        final_matrix = [[0]*3 for _ in range(3)]
        for (i, j), val in result_assignment.items(): final_matrix[i][j] = val
        start_node = Node(initial_state, None, "Start", 0)
        goal_node = Node(final_matrix, start_node, "CSP Backtrack", 1)
        return [start_node, goal_node], visited_nodes[0]
    return None, visited_nodes[0]

def forward_checking_search(initial_state):
    """Forward Checking CSP: Thông minh hơn Backtrack. Khi vừa điền 1 ô, nó quét xóa luôn các số tương tự ở ô khác (Nhìn trước 1 bước)."""
    visited_nodes = [0]
    variables = [(i, j) for i in range(3) for j in range(3)]
    goal_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    # Khởi tạo miền giá trị ban đầu
    domains = {v: list(range(9)) for v in variables}

    def is_consistent(var, value, assignment):
        if value in assignment.values(): return False
        if value != goal_matrix[var[0]][var[1]]: return False
        return True

    def apply_forward_checking(var, value, current_domains, assignment):
        """Thực hiện forward checking lọc miền giá trị"""
        removed = []
        for unassigned_var in variables:
            if unassigned_var not in assignment:
                if value in current_domains[unassigned_var]:
                    current_domains[unassigned_var].remove(value) # Xóa giá trị trùng lặp
                    removed.append((unassigned_var, value)) # 
                if not current_domains[unassigned_var]:
                    return "failure", removed # 
        return "success", removed

    def forward_check(assignment, current_domains):
        visited_nodes[0] += 1
        if visited_nodes[0] > 30000: return "Timeout"
        if len(assignment) == len(variables): return assignment

        var = next(v for v in variables if v not in assignment)

        for value in list(current_domains[var]):
            if is_consistent(var, value, assignment):
                assignment[var] = value
                
                status, removed_values = apply_forward_checking(var, value, current_domains, assignment)
                
                if status != "failure":
                    result = forward_check(assignment, current_domains)
                    if result != "failure" and result != "Timeout": return result
                
                for (v, val) in removed_values:
                    current_domains[v].append(val) # 
                del assignment[var]
        return "failure"

    result_assignment = forward_check({}, domains)

    if result_assignment == "Timeout": return "Timeout", visited_nodes[0]
    elif result_assignment != "failure":
        final_matrix = [[0]*3 for _ in range(3)]
        for (i, j), val in result_assignment.items(): final_matrix[i][j] = val
        start_node = Node(initial_state, None, "Start", 0)
        goal_node = Node(final_matrix, start_node, "Forward Checking", 1)
        return [start_node, goal_node], visited_nodes[0]
    return None, visited_nodes[0]

def min_conflicts_search(initial_state):
    """Thuật toán CSP Min-Conflicts"""
    current = Node(initial_state, None, None, 0)
    visited_nodes = 0
    max_steps = 5000

    for _ in range(max_steps):
        visited_nodes += 1
        if check_done(current.state): 
            return solution(current), visited_nodes

        best_neighbors = []
        best_conflict = float('inf')

        for move in possible_move(current.state):
            if current.move and remove_repetition(move, current.move): continue
            new_state = do_action(current.state, move)
            conflicts = calc_heuristic(new_state) # 

            # 
            if conflicts < best_conflict:
                best_conflict = conflicts
                best_neighbors = [(move, new_state)]
            elif conflicts == best_conflict:
                best_neighbors.append((move, new_state))

        if not best_neighbors: break # Kẹt ngõ cụt cục bộ

        move, new_state = random.choice(best_neighbors)
        current = Node(new_state, current, move, current.step + 1)

    return solution(current), visited_nodes

def ac3_search(initial_state):
    """Thuật toán CSP Arc Consistency (AC-3)"""
    visited_nodes = 0
    domains = {}
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    # 
    for i in range(3):
        for j in range(3):
            domains[(i, j)] = {goal[i][j]}

    # 
    queue = deque([(xi, xj) for xi in domains for xj in domains if xi != xj])

    def remove_inconsistent_values(xi, xj):
        removed = False
        for x in list(domains[xi]):
            if not any(x != y for y in domains[xj]):
                domains[xi].remove(x)
                removed = True
        return removed

    # Quét các cung trong đồ thị
    while queue:
        visited_nodes += 1
        xi, xj = queue.popleft()
        if remove_inconsistent_values(xi, xj):
            for xk in domains:
                if xk != xi and xk != xj:
                    queue.append((xk, xi)) # 

    # 
    solved = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if len(domains[(i, j)]) != 1:
                return None, visited_nodes # Domain rỗng -> Vô nghiệm
            solved[i][j] = next(iter(domains[(i, j)]))

    if check_done(solved):
        start_node = Node(initial_state, None, "Start", 0)
        goal_node = Node(solved, start_node, "AC-3", 1)
        return [start_node, goal_node], visited_nodes

    return None, visited_nodes

# ------------------------------------------------------------------------------
# 3.7. CÁC THUẬT TOÁN ĐỐI KHÁNG & XÁC SUẤT (ADVERSARIAL & EXPECTIMAX SEARCH)
# ------------------------------------------------------------------------------

def adversarial_utility(state):
    """
    Hàm tính giá trị tiện ích (Utility Function) của một trạng thái bảng.
    - Trạng thái Đích (Goal State) được gán giá trị tối đa là 1000 điểm.
    - Các trạng thái trung gian được gán giá trị âm tương đương khoảng cách Manhattan (-Manhattan Distance).
      Điều này khuyến khích thuật toán tìm đường ngắn nhất (do Manhattan distance càng nhỏ thì utility càng gần 0).
    """
    if check_done(state):
        return 1000
    return -calc_manhattan(state)

# --- MINIMAX ---
def minimax_decision(state, depth, visited_nodes):
    """
    Hàm đưa ra quyết định nước đi tốt nhất từ trạng thái hiện tại bằng thuật toán Minimax.
    - Duyệt qua toàn bộ nước đi hợp lệ của ô trống.
    - Gọi hàm min_value cho trạng thái con để lấy giá trị tối thiểu mà đối thủ có thể ép ta nhận.
    - Trả về nước đi đem lại giá trị lớn nhất (tốt nhất cho Agent).
    """
    best_move = None
    best_value = -float('inf')
    
    # Lặp qua tất cả các hướng đi có thể (U, D, L, R)
    for move in possible_move(state):
        next_state = do_action(state, move)
        # Giả lập đối thủ (MIN) sẽ đi nước tiếp theo ở cấp độ sâu tiếp theo (depth - 1)
        value = min_value(next_state, depth - 1, visited_nodes)
        # Lựa chọn nước đi tối đa hóa giá trị
        if value > best_value:
            best_value = value
            best_move = move
            
    return best_move

def max_value(state, depth, visited_nodes):
    """
    Hàm tính giá trị tối đa (phục vụ cho lượt đi của Agent - MAX).
    - Tăng bộ đếm số nút đã duyệt (visited_nodes) lên 1.
    - Nếu chạm giới hạn độ sâu (depth == 0) hoặc đạt trạng thái đích, trả về giá trị tiện ích (utility).
    - Ngược lại, duyệt các nước đi khả dĩ và chọn giá trị cực đại trả về từ lượt của đối thủ (min_value).
    """
    visited_nodes[0] += 1
    # Điều kiện dừng đệ quy
    if depth == 0 or check_done(state):
        return adversarial_utility(state)
    
    v = -float('inf')
    for move in possible_move(state):
        next_state = do_action(state, move)
        # MAX tìm cách tối đa hóa giá trị lấy được từ các nút MIN con
        v = max(v, min_value(next_state, depth - 1, visited_nodes))
    return v

def min_value(state, depth, visited_nodes):
    """
    Hàm tính giá trị tối thiểu (phục vụ cho lượt đi của Đối thủ - MIN).
    - Tăng bộ đếm số nút đã duyệt (visited_nodes) lên 1.
    - Nếu chạm giới hạn độ sâu hoặc đạt trạng thái đích, trả về giá trị tiện ích (utility).
    - Ngược lại, duyệt các nước đi khả dĩ và chọn giá trị cực tiểu trả về từ lượt của Agent (max_value).
    """
    visited_nodes[0] += 1
    # Điều kiện dừng đệ quy
    if depth == 0 or check_done(state):
        return adversarial_utility(state)
        
    v = float('inf')
    for move in possible_move(state):
        next_state = do_action(state, move)
        # MIN tìm cách tối thiểu hóa giá trị của MAX bằng cách chọn nước đi tệ nhất cho MAX
        v = min(v, max_value(next_state, depth - 1, visited_nodes))
    return v

def minimax_search(initial_state):
    """
    Mô phỏng toàn bộ tiến trình chơi game 8-puzzle giữa MAX (Tác nhân AI) và MIN (Đối thủ phá hoại).
    - MAX sử dụng Minimax để tính toán nước đi thông minh nhất.
    - MIN sử dụng chiến thuật phá hoại bằng cách chọn nước đi ngẫu nhiên hoặc tối đa hóa khoảng cách Manhattan.
    - Quá trình chạy lặp tối đa 100 bước, trả về danh sách lịch sử các trạng thái (history) để vẽ giao diện hoạt ảnh.
    """
    visited_nodes = [0]
    history = []
    
    # Khởi tạo trạng thái ban đầu của bảng
    current_state = copy.deepcopy(initial_state)
    current_node = Node(current_state, None, None, 0)
    history.append(current_node)
    
    step = 0
    max_steps = 100
    # Tập hợp lưu các trạng thái đã đi qua nhằm phát hiện và tránh rơi vào vòng lặp vô hạn
    executed_states = {matrix_to_tuple(current_state)}
    
    while step < max_steps:
        # Nếu đã đạt đến trạng thái đích, dừng mô phỏng và trả về đường đi thành công
        if check_done(current_state):
            return history, visited_nodes[0]
            
        # --- Lượt của MAX (Tác nhân AI) ---
        # Chọn nước đi tối ưu nhất bằng Minimax ở độ sâu 3
        best_move = minimax_decision(current_state, depth=3, visited_nodes=visited_nodes)
        if not best_move:
            break
            
        next_state = do_action(current_state, best_move)
        
        # Cơ chế phòng ngừa vòng lặp: Nếu nước đi tối ưu dẫn đến trạng thái đã đi qua,
        # thuật toán sẽ chuyển sang chọn nước đi chưa từng đi qua có khoảng cách Manhattan nhỏ nhất.
        if matrix_to_tuple(next_state) in executed_states:
            moves = possible_move(current_state)
            unvisited_moves = [m for m in moves if matrix_to_tuple(do_action(current_state, m)) not in executed_states]
            if unvisited_moves:
                best_move = min(unvisited_moves, key=lambda m: calc_manhattan(do_action(current_state, m)))
                next_state = do_action(current_state, best_move)
                
        current_state = next_state
        executed_states.add(matrix_to_tuple(current_state))
        # Ghi nhận bước đi của Agent
        current_node = Node(current_state, current_node, f"{best_move} (MAX)", step + 1)
        history.append(current_node)
        step += 1
        
        if check_done(current_state):
            return history, visited_nodes[0]
            
        # --- Lượt của MIN (Đối thủ cản trở) ---
        # Đối thủ tìm cách di chuyển ô trống để phá hoại, ưu tiên nước đi tăng Manhattan distance
        moves = possible_move(current_state)
        # Loại trừ nước đi nghịch đảo ngay lập tức để tránh rung lắc tại chỗ vô ích
        valid_moves = [m for m in moves if not remove_repetition(m, best_move)]
        if not valid_moves:
            valid_moves = moves
            
        # Đối thủ chọn nước đi làm tăng Manhattan distance nhiều nhất (giá trị MAX nhận được là nhỏ nhất)
        opponent_move = max(valid_moves, key=lambda m: calc_manhattan(do_action(current_state, m)))
        current_state = do_action(current_state, opponent_move)
        executed_states.add(matrix_to_tuple(current_state))
        # Ghi nhận bước đi phá hoại của đối thủ
        current_node = Node(current_state, current_node, f"{opponent_move} (MIN)", step + 1)
        history.append(current_node)
        step += 1
        
    return history, visited_nodes[0]

# --- ALPHA-BETA PRUNING ---
def alpha_beta_decision(state, depth, visited_nodes):
    """
    Hàm chọn nước đi tốt nhất cho Agent sử dụng thuật toán cắt tỉa Alpha-Beta.
    - Alpha đại diện cho giá trị lớn nhất mà người chơi MAX (Agent) chắc chắn đạt được.
    - Beta đại diện cho giá trị nhỏ nhất mà đối thủ MIN chắc chắn có thể ép MAX nhận.
    - Trả về nước đi tối ưu nhất giúp tối đa hóa điểm số của MAX.
    """
    best_move = None
    best_value = -float('inf')
    alpha = -float('inf')
    beta = float('inf')
    
    for move in possible_move(state):
        next_state = do_action(state, move)
        # Giả lập đối thủ phản công ở độ sâu tiếp theo với khoảng giá trị cắt tỉa [alpha, beta]
        value = min_value_ab(next_state, depth - 1, alpha, beta, visited_nodes)
        if value > best_value:
            best_value = value
            best_move = move
        # Cập nhật alpha cho các nhánh duyệt sau
        alpha = max(alpha, best_value)
            
    return best_move

def max_value_ab(state, depth, alpha, beta, visited_nodes):
    """
    Hàm tính toán giá trị lớn nhất với cơ chế cắt tỉa nhánh (MAX Node).
    - Tăng bộ đếm visited_nodes.
    - Duyệt qua các nút con: Nếu giá trị v lớn hơn hoặc bằng beta, lập tức cắt nhánh (prune)
      bởi vì đối thủ MIN ở tầng trên sẽ không bao giờ cho phép ta đi vào nhánh này.
    """
    visited_nodes[0] += 1
    if depth == 0 or check_done(state):
        return adversarial_utility(state)
        
    v = -float('inf')
    for move in possible_move(state):
        next_state = do_action(state, move)
        v = max(v, min_value_ab(next_state, depth - 1, alpha, beta, visited_nodes))
        # Cắt tỉa nhánh beta (Beta Cut-off)
        if v >= beta:
            return v
        # Cập nhật giá trị alpha tốt nhất
        alpha = max(alpha, v)
    return v

def min_value_ab(state, depth, alpha, beta, visited_nodes):
    """
    Hàm tính toán giá trị nhỏ nhất với cơ chế cắt tỉa nhánh (MIN Node).
    - Tăng bộ đếm visited_nodes.
    - Duyệt qua các nút con: Nếu giá trị v nhỏ hơn hoặc bằng alpha, lập tức cắt nhánh (prune)
      bởi vì Agent MAX ở tầng trên sẽ không bao giờ chọn đi vào nhánh này.
    """
    visited_nodes[0] += 1
    if depth == 0 or check_done(state):
        return adversarial_utility(state)
        
    v = float('inf')
    for move in possible_move(state):
        next_state = do_action(state, move)
        v = min(v, max_value_ab(next_state, depth - 1, alpha, beta, visited_nodes))
        # Cắt tỉa nhánh alpha (Alpha Cut-off)
        if v <= alpha:
            return v
        # Cập nhật giá trị beta tốt nhất của đối thủ
        beta = min(beta, v)
    return v

def alpha_beta_search(initial_state):
    """
    Mô phỏng trò chơi 8-puzzle sử dụng tìm kiếm đối kháng cắt tỉa Alpha-Beta.
    - Nhờ có cắt tỉa, ta có thể tăng độ sâu tìm kiếm (depth = 4) giúp Agent nhìn xa hơn
      và đưa ra nước đi hiệu quả hơn so với Minimax thông thường mà không tốn nhiều CPU.
    """
    visited_nodes = [0]
    history = []
    
    current_state = copy.deepcopy(initial_state)
    current_node = Node(current_state, None, None, 0)
    history.append(current_node)
    
    step = 0
    max_steps = 100
    executed_states = {matrix_to_tuple(current_state)}
    
    while step < max_steps:
        if check_done(current_state):
            return history, visited_nodes[0]
            
        # --- Lượt của MAX (Agent) ---
        # Gọi quyết định nước đi tối ưu ở độ sâu 4
        best_move = alpha_beta_decision(current_state, depth=4, visited_nodes=visited_nodes)
        if not best_move:
            break
            
        next_state = do_action(current_state, best_move)
        
        # Tránh rơi vào vòng lặp trạng thái cũ
        if matrix_to_tuple(next_state) in executed_states:
            moves = possible_move(current_state)
            unvisited_moves = [m for m in moves if matrix_to_tuple(do_action(current_state, m)) not in executed_states]
            if unvisited_moves:
                best_move = min(unvisited_moves, key=lambda m: calc_manhattan(do_action(current_state, m)))
                next_state = do_action(current_state, best_move)
                
        current_state = next_state
        executed_states.add(matrix_to_tuple(current_state))
        current_node = Node(current_state, current_node, f"{best_move} (MAX)", step + 1)
        history.append(current_node)
        step += 1
        
        if check_done(current_state):
            return history, visited_nodes[0]
            
        # --- Lượt của MIN (Đối thủ phá hoại) ---
        moves = possible_move(current_state)
        valid_moves = [m for m in moves if not remove_repetition(m, best_move)]
        if not valid_moves:
            valid_moves = moves
            
        opponent_move = max(valid_moves, key=lambda m: calc_manhattan(do_action(current_state, m)))
        current_state = do_action(current_state, opponent_move)
        executed_states.add(matrix_to_tuple(current_state))
        current_node = Node(current_state, current_node, f"{opponent_move} (MIN)", step + 1)
        history.append(current_node)
        step += 1
        
    return history, visited_nodes[0]

# --- EXPECTIMAX ---
def expectimax_decision(state, depth, visited_nodes):
    """
    Hàm chọn nước đi tốt nhất cho Agent sử dụng thuật toán Expectimax.
    - Duyệt qua các hướng đi khả dĩ của ô trống.
    - Gọi hàm exp_value đại diện cho nút cơ hội (Chance Node) của môi trường.
    - Trả về nước đi giúp tối đa hóa giá trị kỳ vọng (Expected Value).
    """
    best_move = None
    best_value = -float('inf')
    
    for move in possible_move(state):
        next_state = do_action(state, move)
        # Tính giá trị trung bình kỳ vọng từ các phản ứng ngẫu nhiên của môi trường
        value = exp_value(next_state, depth - 1, visited_nodes)
        if value > best_value:
            best_value = value
            best_move = move
            
    return best_move

def max_value_exp(state, depth, visited_nodes):
    """
    Hàm tính giá trị tối đa của tác nhân tại nút MAX trong Expectimax.
    - Tự tăng bộ đếm visited_nodes.
    - Chọn nước đi tối đa hóa giá trị kỳ vọng trả về từ nút cơ hội.
    """
    visited_nodes[0] += 1
    if depth == 0 or check_done(state):
        return adversarial_utility(state)
        
    v = -float('inf')
    for move in possible_move(state):
        next_state = do_action(state, move)
        v = max(v, exp_value(next_state, depth - 1, visited_nodes))
    return v

def exp_value(state, depth, visited_nodes):
    """
    Hàm tính toán giá trị trung bình kỳ vọng tại nút Cơ hội (Chance Node).
    - Giả định môi trường sẽ thực hiện ngẫu nhiên một nước đi với xác suất đồng đều.
    - Trả về tổng trung bình của tất cả các giá trị nhận được từ các nút con.
    """
    visited_nodes[0] += 1
    if depth == 0 or check_done(state):
        return adversarial_utility(state)
        
    moves = possible_move(state)
    if not moves:
        return adversarial_utility(state)
        
    total_val = 0
    prob = 1.0 / len(moves)
    for move in moves:
        next_state = do_action(state, move)
        total_val += prob * max_value_exp(next_state, depth - 1, visited_nodes)
    return total_val

def expectimax_search(initial_state):
    visited_nodes = [0]
    history = []
    
    current_state = copy.deepcopy(initial_state)
    current_node = Node(current_state, None, None, 0)
    history.append(current_node)
    
    step = 0
    max_steps = 100
    executed_states = {matrix_to_tuple(current_state)}
    
    while step < max_steps:
        if check_done(current_state):
            return history, visited_nodes[0]
            
        # Lượt của MAX (Agent)
        best_move = expectimax_decision(current_state, depth=3, visited_nodes=visited_nodes)
        if not best_move:
            break
            
        next_state = do_action(current_state, best_move)
        
        if matrix_to_tuple(next_state) in executed_states:
            moves = possible_move(current_state)
            unvisited_moves = [m for m in moves if matrix_to_tuple(do_action(current_state, m)) not in executed_states]
            if unvisited_moves:
                best_move = min(unvisited_moves, key=lambda m: calc_manhattan(do_action(current_state, m)))
                next_state = do_action(current_state, best_move)
                
        current_state = next_state
        executed_states.add(matrix_to_tuple(current_state))
        current_node = Node(current_state, current_node, f"{best_move} (MAX)", step + 1)
        history.append(current_node)
        step += 1
        
        if check_done(current_state):
            return history, visited_nodes[0]
            
        # Lượt của môi trường (Chance)
        moves = possible_move(current_state)
        valid_moves = [m for m in moves if not remove_repetition(m, best_move)]
        if not valid_moves:
            valid_moves = moves
            
        chance_move = random.choice(valid_moves)
        current_state = do_action(current_state, chance_move)
        executed_states.add(matrix_to_tuple(current_state))
        current_node = Node(current_state, current_node, f"{chance_move} (Chance)", step + 1)
        history.append(current_node)
        step += 1
        
    return history, visited_nodes[0]

# ==============================================================================
# 4. GIAO DIỆN ĐỒ HỌA (GUI) SỬ DỤNG LIBRALY TKINTER
# ==============================================================================
class GUI:
    """
    Lớp GUI quản lý giao diện người dùng dựa trên thư viện Tkinter.
    Hỗ trợ hiển thị lưới ma trận 8-Puzzle, chọn thuật toán và hiển thị các bước giải.
    """
    def __init__(self, root):
        self.root = root
        # Đặt tiêu đề cho cửa sổ ứng dụng
        self.root.title("8 Puzzle AI Solver - Pro Edition")
        # Định kích thước cửa sổ chính: rộng 1100px, cao 750px
        self.root.geometry("1100x750") 
        # Sử dụng màu nền tối sang trọng: #0F172A (Slate 900)
        self.root.configure(bg="#0F172A") 
        
        # Các cờ (Flags) trạng thái điều khiển luồng hoạt ảnh
        self.is_animating = False # Cờ xác định xem hoạt ảnh mô phỏng có đang chạy không
        self.is_paused = False    # Cờ xác định xem hoạt ảnh có đang tạm dừng không
        self.is_cancelled = False # Cờ xác định xem tiến trình mô phỏng đã bị hủy chưa
        
        # Tiêu đề chính của ứng dụng với màu Sky Blue phát sáng (#38BDF8)
        title_lbl = tk.Label(root, text="Hệ Thống Trí Tuệ Nhân Tạo 8-Puzzle", font=("Segoe UI", 24, "bold"), bg="#0F172A", fg="#38BDF8")
        title_lbl.pack(pady=(20, 10))
        
        # Khung chứa chính (Main Frame) bao quát toàn bộ nội dung dưới tiêu đề
        main_frame = tk.Frame(root, bg="#0F172A")
        main_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
        
        # Cột bên trái: Dành cho nhập liệu ma trận đầu vào, chọn thuật toán và các nút điều khiển
        left_frame = tk.Frame(main_frame, bg="#0F172A") 
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Nhãn tiêu đề cho lưới ma trận nhập vào
        tk.Label(left_frame, text="Ma Trận Đầu Vào (0-8)", font=("Segoe UI", 14, "bold"), bg="#0F172A", fg="#E2E8F0").pack(anchor="w", pady=(0, 10))
        
        # Khung chứa ma trận lưới (Grid) 3x3 với thiết kế phẳng (flat), màu Slate 800 (#1E293B)
        board_container = tk.Frame(left_frame, bg="#1E293B", bd=3, relief="flat", padx=8, pady=8)
        board_container.pack(pady=5)
        board_frame = tk.Frame(board_container, bg="#1E293B")
        board_frame.pack()
        
        # Tạo lưới 3x3 ô nhập dữ liệu (Entry)
        self.entries = [] # Mảng 2 chiều chứa 9 đối tượng tk.Entry để người dùng điền số
        for i in range(3):
            row_entries = []
            for j in range(3):
                # Mỗi ô nhập liệu được thiết kế màu nền sáng tương phản (#F8FAFC) và chữ màu đen tối (#0F172A)
                # để đảm bảo khả năng đọc tốt nhất dưới bất kỳ độ sáng nào trên mọi HĐH kể cả macOS.
                # Khi click chọn, viền của ô sẽ chuyển sang màu xanh dương sáng (#3B82F6).
                e = tk.Entry(board_frame, width=3, font=("Consolas", 36, "bold"), justify="center", 
                             bg="#F8FAFC", fg="#0F172A", relief="flat", insertbackground="#0F172A",
                             highlightthickness=1, highlightbackground="#CBD5E1", highlightcolor="#3B82F6")
                e.grid(row=i, column=j, padx=4, pady=4)
                row_entries.append(e)
            self.entries.append(row_entries)
            
        # Nhãn chọn thuật toán tìm kiếm
        tk.Label(left_frame, text="Chọn Thuật Toán AI", font=("Segoe UI", 14, "bold"), bg="#0F172A", fg="#E2E8F0").pack(anchor="w", pady=(25, 5))

        self.algo_var = tk.StringVar(value="BFS")
        
        # Danh sách toàn bộ 23 thuật toán được tích hợp sẵn
        algos = ["BFS", "DFS", "IDS", "UCS", "Greedy Search", "A* Search", 
                 "IDA*", "Simple Hill Climbing", "Steepest-Ascent Hill Climbing", 
                 "Stochastic Hill Climbing", "Random Restart Hill Climbing", "Local Beam Search",
                 "Simulated Annealing", "Simple Reflex", "Model-based Reflex", "Sensorless (Belief State)",
                 "AND-OR Graph Search", "Minimax", "Alpha-Beta Pruning", "Expectimax",
                 "Backtracking CSP", "Forward Checking CSP", "AC-3 CSP", "Min-Conflicts CSP"]
        
        # Cấu hình phong cách thiết kế Combobox có độ tương phản cao (chữ đen, nền trắng) để giải quyết lỗi mờ chữ trên macOS
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", 
                        fieldbackground="white", 
                        background="#E2E8F0", 
                        foreground="black", 
                        bordercolor="#CBD5E1", 
                        arrowcolor="#0F172A")
        
        # Hộp chọn thuật toán (Combobox)
        self.algo_cb = ttk.Combobox(left_frame, textvariable=self.algo_var, values=algos, state="readonly", width=25, font=("Segoe UI", 13))
        self.algo_cb.pack(anchor="w", pady=5)
            
        # Nhãn chọn chế độ hiển thị kết quả
        tk.Label(left_frame, text="Chế Độ Hiển Thị", font=("Segoe UI", 14, "bold"), bg="#0F172A", fg="#E2E8F0").pack(anchor="w", pady=(15, 5))
        self.display_mode_var = tk.StringVar(value="In từ từ (Hoạt ảnh)")
        modes = ["In từ từ (Hoạt ảnh)", "In tức thì (Tất cả)"]
        self.display_cb = ttk.Combobox(left_frame, textvariable=self.display_mode_var, values=modes, state="readonly", width=25, font=("Segoe UI", 13))
        self.display_cb.pack(anchor="w", pady=5)

        # Cụm các nút điều khiển chính
        btn_frame = tk.Frame(left_frame, bg="#0F172A")
        btn_frame.pack(pady=20, fill=tk.X)
        
        # Các nút bấm bên dưới sử dụng fg="black" (chữ màu đen) để hiển thị sắc nét trên nền nút mặc định màu sáng của macOS.
        # Nút "Tạo Bài Mới": Màu xanh lam (Royal Blue)
        self.btn_new = tk.Button(btn_frame, text="Tạo Bài Mới", command=self.new_puzzle, font=("Segoe UI", 12, "bold"), 
                                 bg="#2563EB", fg="black", activebackground="#1D4ED8", activeforeground="black", relief="flat", cursor="hand2", pady=8)
        self.btn_new.pack(fill=tk.X, pady=4)
        
        # Nút "Bắt Đầu Giải": Màu xanh lá cây (Emerald Green)
        self.btn_search = tk.Button(btn_frame, text="Bắt Đầu Giải", command=self.search, font=("Segoe UI", 12, "bold"), 
                                    bg="#10B981", fg="black", activebackground="#059669", activeforeground="black", relief="flat", cursor="hand2", pady=8)
        self.btn_search.pack(fill=tk.X, pady=4)
        
        # Nút "Tạm Dừng / Tiếp Tục": Màu cam ấm (Amber Yellow)
        self.btn_pause = tk.Button(btn_frame, text="Tạm Dừng", command=self.toggle_pause, font=("Segoe UI", 12, "bold"), 
                                   bg="#D97706", fg="black", activebackground="#B45309", activeforeground="black", disabledforeground="#6B7280", relief="flat", cursor="hand2", pady=8, state=tk.DISABLED)
        self.btn_pause.pack(fill=tk.X, pady=4)
        
        # Nút "Hủy Bỏ": Màu đỏ tươi (Red)
        self.btn_cancel = tk.Button(btn_frame, text="Hủy Bỏ", command=self.cancel_animation, font=("Segoe UI", 12, "bold"), 
                                    bg="#EF4444", fg="black", activebackground="#DC2626", activeforeground="black", disabledforeground="#6B7280", relief="flat", cursor="hand2", pady=8, state=tk.DISABLED)
        self.btn_cancel.pack(fill=tk.X, pady=4)
        
        # Nút "Thoát Chương Trình": Màu xám đậm (Slate Gray)
        self.btn_exit = tk.Button(btn_frame, text="Thoát Chương Trình", command=self.exit_app, font=("Segoe UI", 12, "bold"),
                                  bg="#4B5563", fg="black", activebackground="#374151", activeforeground="black", relief="flat", cursor="hand2", pady=8)
        self.btn_exit.pack(fill=tk.X, pady=4)
        
        # Cột bên phải: Chứa màn hình Log để hiển thị kết quả và các bước giải chi tiết
        right_frame = tk.Frame(main_frame, bg="#0F172A") 
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Console Output:", font=("Segoe UI", 14, "bold"), bg="#0F172A", fg="#E2E8F0").pack(anchor="w", pady=(0, 5))
        
        # Màn hình Log Console (Nơi in ra các bước đi và mô phỏng dạng text)
        self.txt_log = scrolledtext.ScrolledText(right_frame, font=("Consolas", 13), bg="#1E293B", fg="#F1F5F9", insertbackground="white", relief="flat", padx=12, pady=12)
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        
        # Thiết lập màu sắc hiển thị cho các thẻ Log đặc biệt
        self.txt_log.tag_configure("highlight", foreground="#F59E0B", font=("Consolas", 13, "bold")) # Màu cam cho hành động hiện tại
        self.txt_log.tag_configure("success", foreground="#34D399", font=("Consolas", 13, "bold"))   # Màu xanh lá cây khi tìm thấy đích
        self.txt_log.tag_configure("error", foreground="#F87171", font=("Consolas", 13, "bold"))     # Màu đỏ cho thông báo lỗi/bị kẹt
        self.txt_log.tag_configure("info", foreground="#60A5FA")                                     # Màu xanh dương cho thông tin hệ thống
 
        self.new_puzzle() # Tự động tạo bảng random lúc vừa bật App

    def log(self, text, tag=None):
        """Hàm hỗ trợ chèn văn bản (Kèm định dạng màu tag) vào màn hình Log bên phải."""
        self.txt_log.insert(tk.END, text, tag)
        self.txt_log.see(tk.END) # Tự động cuộn chuột (scroll) xuống dòng cuối cùng

    def get_matrix(self):
        """Đọc và ép kiểu dữ liệu từ 9 ô tk.Entry người dùng nhập thành ma trận Mảng 2 Chiều."""
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
            messagebox.showerror("Lỗi Nhập Liệu", "Vui lòng chỉ nhập các số nguyên từ 0 đến 8!")
            return None

    def new_puzzle(self):
        """Xóa ma trận cũ, gọi hàm sinh ma trận có nghiệm và cập nhật lên 9 ô Input."""
        if self.is_animating: return 
        matrix = get_random_solvable_state()
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(matrix[i][j]))
        self.txt_log.delete('1.0', tk.END)
        self.log("Hệ thống đã tạo một bài toán mới sẵn sàng...\n", "info")

    def toggle_pause(self):
        """
        Hàm xử lý sự kiện Tạm dừng / Tiếp tục quá trình mô phỏng hoạt ảnh.
        Bấm nút này sẽ thay đổi trạng thái của cờ self.is_paused, 
        giúp tạm ngắt việc cập nhật khung hiển thị mà không làm mất tiến trình hiện tại.
        """
        # Nếu hoạt ảnh không chạy thì không làm gì cả
        if not self.is_animating: return
        
        # Nếu đang chạy -> chuyển sang Tạm dừng
        if not self.is_paused:
            self.is_paused = True
            # Đổi nhãn nút thành "Tiếp Tục" và chuyển màu nút sang xanh lá cây (Emerald Green) để gợi ý người dùng bấm chạy tiếp
            # Đặt fg="black" để đảm bảo chữ hiển thị rõ ràng trên macOS vốn có nút nền sáng
            self.btn_pause.config(text="Tiếp Tục", bg="#10B981", fg="black")
            self.log("\n[!] ĐÃ TẠM DỪNG MÔ PHỎNG...\n", "highlight")
        # Nếu đang tạm dừng -> quay lại Tiếp tục chạy
        else:
            self.is_paused = False
            # Đổi nhãn nút lại thành "Tạm Dừng" và khôi phục màu cam hổ phách (Amber Yellow) với chữ màu đen
            self.btn_pause.config(text="Tạm Dừng", bg="#D97706", fg="black")
            self.log("[!] TIẾP TỤC CHẠY...\n", "info")

    def cancel_animation(self):
        """
        Hàm hủy bỏ tiến trình mô phỏng đang chạy.
        Gán cờ self.is_cancelled = True để hàm animate_steps nhận diện và ngắt đệ quy.
        """
        if self.is_animating:
            self.is_cancelled = True

    def exit_app(self):
        """
        Hàm xử lý thoát ứng dụng một cách an toàn.
        Đảm bảo hủy hoạt ảnh đang chạy để giải phóng tài nguyên trước khi đóng hoàn toàn cửa sổ.
        """
        if self.is_animating:
            self.is_cancelled = True
        self.root.destroy()

    def reset_controls(self):
        """
        Hàm khôi phục trạng thái ban đầu của các nút bấm điều khiển trên giao diện.
        Được gọi khi hoạt ảnh kết thúc, bị hủy hoặc xảy ra lỗi.
        """
        self.is_animating = False
        self.is_paused = False
        self.is_cancelled = False
        # Mở khóa các nút chính
        self.btn_search.config(state=tk.NORMAL)
        self.btn_new.config(state=tk.NORMAL)
        # Khóa nút Tạm dừng và Hủy bỏ, đồng thời đặt lại nhãn và màu sắc chuẩn của nút Tạm dừng là chữ màu đen
        self.btn_pause.config(state=tk.DISABLED, text="Tạm Dừng", bg="#D97706", fg="black")
        self.btn_cancel.config(state=tk.DISABLED)

    def animate_steps(self, steps, current_index, explored_count):
        """
        Trái tim của hệ thống Mô phỏng (Animation)
        Dùng kỹ thuật đệ quy giao diện (root.after) để tránh bị đơ (freeze/Not Responding) main thread Tkinter.
        """
        if self.is_cancelled:
            self.log(f"\n[X] ĐÃ HỦY THEO YÊU CẦU NGƯỜI DÙNG\n", "error")
            self.reset_controls()
            messagebox.showwarning("Đã Dừng", "Tiến trình mô phỏng đã bị người dùng hủy!")
            return

        if self.is_paused:
            # Nếu đang Pause, đệ quy gọi lại hàm với độ trễ 100ms mà KHÔNG TĂNG current_index -> Đứng yên tại chỗ
            self.root.after(100, self.animate_steps, steps, current_index, explored_count)
            return

        mode = self.display_mode_var.get()

        # NẾU CHỌN IN TỨC THÌ (TẤT CẢ) - Dùng vòng lặp for bung thẳng luôn
        if mode == "In tức thì (Tất cả)":
            for idx in range(current_index, len(steps)):
                if self.is_cancelled: 
                    self.log(f"\n[X] ĐÃ HỦY...\n", "error")
                    self.reset_controls()
                    return
                
                node = steps[idx]
                move_str = node.move if node.move else "Trạng thái bắt đầu"
                self.log(f"Bước {idx} - Hành động: {move_str}\n", "highlight")
                
                if isinstance(node.state[0][0], tuple): # Xử lý in danh sách ma trận Tập niềm tin của Sensorless
                    self.log(f"  [Tập niềm tin: {len(node.state)} trạng thái có thể xảy ra]\n", "error")
                    for s_idx, matrix_tuple in enumerate(node.state):
                        self.log(f"    + Trạng thái {s_idx+1}:\n")
                        for row in matrix_tuple:
                            self.log("        " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
                else: # In ma trận bình thường
                    for row in node.state:
                        self.log("    " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
                    self.update_grid_ui(node.state) # CẬP NHẬT TRỰC QUAN LƯỚI ENTRY BÊN TRÁI
                
                self.log("-" * 35 + "\n")
            
            # Chạy xong For -> Hiện Tổng kết
            self._print_final_summary(steps, explored_count)
            return

        # NẾU CHỌN IN TỪ TỪ (HOẠT ẢNH) - Chỉ in 1 bước rồi root.after nhường RAM cho App thở.
        if current_index < len(steps):
            node = steps[current_index]
            move_str = node.move if node.move else "Trạng thái bắt đầu"
            self.log(f"Bước {current_index} - Hành động: {move_str}\n", "highlight")
            
            if isinstance(node.state[0][0], tuple):
                self.log(f"  [Tập niềm tin: {len(node.state)} trạng thái có thể xảy ra]\n", "error")
                for s_idx, matrix_tuple in enumerate(node.state):
                    self.log(f"    + Trạng thái {s_idx+1}:\n")
                    for row in matrix_tuple:
                        self.log("        " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
            else:
                for row in node.state:
                    self.log("    " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
                self.update_grid_ui(node.state) 
            
            self.log("-" * 35 + "\n")
            # Set timeout 300ms sau sẽ gọi đệ quy hàm này chạy tiếp với current_index + 1
            self.root.after(300, self.animate_steps, steps, current_index + 1, explored_count)
        else:
            self._print_final_summary(steps, explored_count)

    def _print_final_summary(self, steps, explored_count):
        """In tổng kết chuỗi đường đi và phán quyết (Giải Cứu Thành Công / Bị Kẹt Cục Bộ)"""
        moves = [node.move for node in steps if node.move and not node.move.startswith("Restart") and not node.move.startswith("Random")]
        move_sequence = " -> ".join(moves) if moves else "Không có hành động"
        
        if isinstance(steps[-1].state[0][0], tuple):
            is_success = check_belief_done(steps[-1].state)
        else:
            is_success = check_done(steps[-1].state) # Kiểm tra Node cuối cùng có phải Đích không
        
        self.log(f"\n===== KẾT QUẢ TỔNG QUÁT =====\n", "info")
        self.log(f"Số lượng Node đã mở rộng : {explored_count}\n")
        self.log(f"Tổng số bước đã di chuyển: {len(steps)-1}\n")
        
        if is_success:
            self.log(f"Trạng thái cuối: ", "info")
            self.log("GIẢI THÀNH CÔNG\n", "success")
        else:
            self.log(f"Trạng thái cuối: ", "info")
            self.log("THẤT BẠI - BỊ KẸT\n", "error")
            
        self.log(f"• Chuỗi đường đi:\n  {move_sequence}\n\n")
        
        self.reset_controls()
        if is_success:
            messagebox.showinfo("Hoàn Thành", "Đã mô phỏng xong đường đi tới đích!")
        else:
            messagebox.showwarning("Cảnh Báo", "Thuật toán đã dừng do rơi vào cực trị cục bộ hoặc hết thời gian!")

    def search(self):
        """
        Khối động cơ điều phối: Nhận tín hiệu từ Button -> Chọn Thuật toán tương ứng -> Tính toán chạy -> Đẩy cho Animation.
        """
        if self.is_animating: return
        algo = self.algo_var.get()
        
        self.txt_log.delete('1.0', tk.END)
        self.log(f"Đang khởi chạy thuật toán: {algo}...\n", "highlight")
        self.root.update() 
        
        result = None
        visited_nodes = 0
        
        try:
            # Nhánh Môi Trường Mù cần Khởi tạo Node riêng (Tuple 3 Ma trận ngẫu nhiên)
            if algo == "Sensorless (Belief State)":
                belief_start = get_close_belief_states()
                result, visited_nodes = belief_state_astar(belief_start)
            else:
                matrix = self.get_matrix()
                if not matrix: return
                
                # Check Toán học: Có những ma trận bẩm sinh không thể xếp lại được. Ngăn thuật toán chạy vô tận.
                if not check_solvable(matrix):
                    self.log("Trạng thái vô nghiệm. Yêu cầu nhập lại!\n", "error")
                    messagebox.showwarning("Vô Nghiệm", "Ma trận này thuộc nhóm không thể giải (Inversions lẻ)!")
                    return
                
                # --- PHÂN LUỒNG 20 THUẬT TOÁN ---
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
                elif algo == "Simulated Annealing": result, visited_nodes = simulated_annealing(matrix)
                elif algo == "Simple Reflex": result, visited_nodes = simple_reflex(matrix)
                elif algo == "Model-based Reflex": result, visited_nodes = model_based_reflex(matrix)
                elif algo == "AND-OR Graph Search": result, visited_nodes = and_or_graph_search(matrix)
                elif algo == "Minimax": result, visited_nodes = minimax_search(matrix)
                elif algo == "Alpha-Beta Pruning": result, visited_nodes = alpha_beta_search(matrix)
                elif algo == "Expectimax": result, visited_nodes = expectimax_search(matrix)
                elif algo == "Backtracking CSP": result, visited_nodes = backtracking_search(matrix)
                elif algo == "Forward Checking CSP": result, visited_nodes = forward_checking_search(matrix)
                elif algo == "AC-3 CSP": result, visited_nodes = ac3_search(matrix)
                elif algo == "Min-Conflicts CSP": result, visited_nodes = min_conflicts_search(matrix)
                
        except RecursionError:
            # XỬ LÝ LỖI TRÀN BỘ NHỚ: DFS và Backtrack có thể cắm đầu xuống quá sâu gây Memory Leak cho Python.
            self.log("\n[X] LỖI: VƯỢT QUÁ GIỚI HẠN ĐỆ QUY!\n", "error")
            self.log("> Cây tìm kiếm quá sâu, hệ thống đã buộc dừng để bảo vệ bộ nhớ.\n", "info")
            messagebox.showerror("Tràn Đệ Quy (Recursion Error)", "Độ sâu đệ quy đã vượt qua giới hạn an toàn của Python.\nThuật toán bị buộc dừng để tránh treo máy!")
            self.reset_controls()
            return

        self.txt_log.delete('1.0', tk.END) 
        
        # Xử lý Hậu quả tính toán: Kết quả sẽ rơi vào 1 trong 3 kịch bản
        if result == "Timeout": # Kịch bản 1: Quét quá lâu/quá rộng
            self.log("Quá tải bộ nhớ. Thuật toán đã buộc dừng an toàn.\n", "error")
            messagebox.showwarning("Quá tải", f"Đã quét {visited_nodes} trạng thái nhưng dừng để tránh đơ máy.")
        elif result is None:    # Kịch bản 2: Không tìm thấy đường
            self.log("Thuật toán không thể tìm ra kết quả.\n", "error")
            messagebox.showinfo("Thất bại", f"Không tìm được lời giải sau {visited_nodes} vòng lặp/kiểm tra.")
        else:                   # Kịch bản 3: Có kết quả mảng Node -> Giao cho Animation chạy in ra chữ
            self.is_animating = True 
            self.btn_search.config(state=tk.DISABLED) 
            self.btn_new.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self.btn_cancel.config(state=tk.NORMAL)
            
            self.log(f"Tìm kiếm hoàn tất! Bắt đầu in kết quả:\n", "success")
            self.log("=" * 45 + "\n\n")
            self.animate_steps(result, 0, visited_nodes)

    def update_grid_ui(self, matrix):
        """Cập nhật các ô Entry trên giao diện để Lưới 3x3 bên trái luôn khớp với dữ liệu Console bên phải"""
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(matrix[i][j]))
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()