import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random
import copy
import math
from collections import deque
from queue import PriorityQueue
import sys

# Hệ điều hành thường giới hạn số lần gọi đệ quy (khoảng 1000) để chống tràn bộ nhớ (Stack Overflow).
# Thuật toán DFS, Backtracking, v.v. duyệt đồ thị rất sâu nên cần nới rộng giới hạn này lên 50000.
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
        self.state = state   # Ma trận 3x3 hiện tại (vd: [[1,2,3], [4,5,6], [7,8,0]])
        self.parent = parent # Node cha sinh ra Node này (dùng để dò ngược đường đi khi tìm thấy đích)
        self.move = move     # Hành động (U, D, L, R) đã làm để từ Node cha tạo ra Node này
        self.step = step     # Chi phí g(n): Tổng số bước đi tính từ Start đến Node này

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
    """Đích của trò chơi: Ma trận hoàn hảo có ô trống (0) ở cuối."""
    return matrix == [
        [1, 2, 3],
        [4, 5, 6], 
        [7, 8, 0]
    ]

def find_empty_position(matrix):
    """Duyệt mảng 2 chiều để tìm tọa độ (x, y) của ô trống có giá trị bằng 0."""
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
    """Tạo ra một cấu hình bảng mới sau khi trượt ô trống."""
    # BẮT BUỘC dùng deepcopy. Nếu chỉ gán (new = matrix), khi sửa new, matrix cũ cũng bị hỏng (lỗi tham chiếu).
    new_matrix = copy.deepcopy(matrix) 
    x, y = find_empty_position(new_matrix)
    
    # Kỹ thuật Swap (Hoán đổi giá trị) của Python: a, b = b, a
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
    """Dò ngược cây phả hệ: Từ Node Đích, truy ngược parent lên Node Start để lấy danh sách các bước đi."""
    result = []
    while node is not None:
        result.append(node)
        node = node.parent
    result.reverse() # Đảo ngược mảng để có đúng thứ tự Start -> Goal
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
    """Hàm Heuristic h(n) số 1: Đếm tổng số lượng các ô đang không nằm đúng vị trí của Đích."""
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
    """Sinh ra một ma trận ngẫu nhiên đảm bảo có thể giải được (Dùng cho nút Refresh)"""
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
        # Sinh xong phải kiểm tra xem có giải được không, và không được sinh ra ngay trạng thái Đích
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
            new_states.add(matrix_to_tuple(state_list)) # Nếu hướng đó bị đụng tường, ta dậm chân tại chỗ
    return tuple(sorted(new_states))

def check_belief_done(belief_tuple):
    """Thành công của môi trường mù là khi tất cả các khả năng đều chập lại thành 1 Trạng thái Đích duy nhất."""
    goal_tuple = matrix_to_tuple([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
    return len(belief_tuple) == 1 and belief_tuple[0] == goal_tuple

def get_close_belief_states():
    """Tạo 3 trạng thái xuất phát cho bài toán Sensorless (Cách đích ngẫu nhiên 3-5 bước)."""
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
    """Hàm heuristic cho môi trường mù: Lấy giá trị lớn nhất (Max) trong số các khoảng cách Manhattan."""
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
    
    frontier = deque([node]) # deque (Double Ended Queue) chạy cực nhanh cho BFS
    explored = {matrix_to_tuple(node.state)}
    
    while frontier:
        u = frontier.popleft() # Bốc node cũ nhất ra (Lan tỏa theo các lớp ngang)
        visited_nodes += 1
        for move in possible_move(u.state):
            if u.move and remove_repetition(move, u.move): continue
            new_state = do_action(u.state, move)
            state_tuple = matrix_to_tuple(new_state)
            
            if state_tuple not in explored: # Nếu chưa duyệt thì nhét vào Queue
                child = Node(new_state, u, move, u.step + 1)
                if check_done(child.state): return solution(child), visited_nodes
                frontier.append(child)
                explored.add(state_tuple)
    return None, visited_nodes

def dfs(initial_state):
    """Depth-First Search (Duyệt theo chiều sâu). Dùng Stack (vào sau ra trước). Nhược điểm: Dễ đi lạc vào nhánh vô tận, ko tối ưu."""
    node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(node.state): return solution(node), visited_nodes
    
    frontier = [node] # List Python bản chất hoạt động như Stack
    explored = {matrix_to_tuple(node.state)}
    
    while frontier:
        # Ngăn thuật toán DFS treo máy tính vì cắm đầu đi vào đường hầm sâu vô cực
        if visited_nodes > 30000: return "Timeout", visited_nodes 
        
        u = frontier.pop() # Lấy node mới nhất vừa cất vào ra đi tiếp (Cắm đầu đi sâu 1 nhánh)
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
    """Depth-Limited Search: Chính là DFS nhưng cài thêm rào cản độ sâu 'limit'. Gặp rào cản thì tự quay đầu."""
    frontier = [node]
    visited_nodes = 0
    while frontier:
        u = frontier.pop()
        visited_nodes += 1
        if check_done(u.state): return solution(u), visited_nodes
        
        if u.step < limit: # Chỉ sinh thêm con nếu chưa chạm tới giới hạn (limit)
            for move in possible_move(u.state):
                if u.move and remove_repetition(move, u.move): continue
                child = Node(do_action(u.state, move), u, move, u.step + 1)
                frontier.append(child)
    return None, visited_nodes

def ids(initial_state):
    """Iterative Deepening Search: Dùng vòng lặp mở rộng dần limit của DLS. Tốn CPU lặp lại nhưng siêu tiết kiệm RAM so với BFS."""
    root_node = Node(initial_state, None, None, 0)
    total_visited = 0
    for depth in range(25): # Lặp độ sâu từ 0 đến 24
        res, visited = dls(root_node, depth) 
        total_visited += visited
        if res: return res, total_visited # Tìm thấy kết quả ở tầng nào thì dừng luôn
    return None, total_visited

def ucs(initial_state):
    """Uniform Cost Search (Duyệt theo chi phí cực tiểu). Luôn chọn Node có g(n) (số bước) thấp nhất để đi."""
    root_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    if check_done(root_node.state): return solution(root_node), visited_nodes
    
    frontier = PriorityQueue() # Hàng đợi ưu tiên tự động sắp xếp lại Node nào có step nhỏ lên đầu
    frontier.put((root_node.step, root_node)) 
    explored = {matrix_to_tuple(root_node.state)}
    
    while not frontier.empty():
        _, u = frontier.get() # Lấy ra node có chi phí rẻ nhất hiện tại
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
    """Greedy Best-First Search (Tìm kiếm Tham Lam). Luôn chọn Node có khoảng cách tới đích ngắn nhất h(n). Nhanh nhưng không ưu việt."""
    start_node = Node(initial_state, None, None, 0)
    frontier = [start_node]
    reached = []
    visited_nodes = 0
    while len(frontier) > 0:
        # Bốc Node có h(n) (calc_heuristic) THẤP NHẤT ra khỏi Frontier
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
    """A* Search (Ngôi sao sáng của thuật toán AI). Chọn node theo f(n) = g(n) + h(n). Đảm bảo luôn tìm ra đường tối ưu tuyệt đối."""
    start_node = Node(initial_state, None, None, 0)
    frontier = [start_node]
    reached = []
    visited_nodes = 0
    while len(frontier) > 0:
        # Bốc Node có f(n) = step (g) + calc_heuristic (h) THẤP NHẤT
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
            
            # Kỹ thuật cập nhật đồ thị phức tạp của A*: Nếu tìm thấy đường đi mới TỐT HƠN tới 1 node cũ -> Cập nhật đường
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
    """Iterative Deepening A* (IDA*). Sự lai tạo hoàn hảo: Dùng độ sâu lặp (như IDS) nhưng rào cản cắt tỉa lại dựa trên f-score (như A*)."""
    root = Node(initial_state, None, None, 0)
    threshold = calc_heuristic(root.state) # Ngưỡng cắt tỉa ban đầu
    visited_nodes = [0] 
    
    def search(node, g, bound):
        visited_nodes[0] += 1
        f = g + calc_heuristic(node.state)
        # Nếu f_score của đường này vượt quá ngưỡng cho phép -> Hủy đường
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
        threshold = t # Cập nhật ngưỡng (bound) lỏng dần ra qua từng vòng lặp

# ------------------------------------------------------------------------------
# 3.3. CÁC THUẬT TOÁN TỐI ƯU CỤC BỘ (LOCAL SEARCH)
# Nhóm này không quan tâm đường đi. Chỉ đứng tại chỗ nhìn xung quanh, thấy nước nào "gần đích hơn" thì nhảy tới. Rất dễ bị kẹt (Local Maximum).
# ------------------------------------------------------------------------------

def simple_hill_climbing(initial_state):
    """Simple Hill Climbing (Leo đồi cơ bản). Đứng tại chỗ quay đầu 4 hướng, thấy hướng nào tốt hơn hiện tại thì BƯỚC NGAY hướng đó."""
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
            if neighbor_h < current_h: # Dừng ngay khi thấy 1 thằng con tốt hơn mình
                current_node = Node(new_state, current_node, move, current_node.step + 1)
                found_better = True
                break
        if not found_better: return solution(current_node), visited_nodes # Kẹt đỉnh đồi (Local Maximum)

def steepest_ascent_hill_climbing(initial_state):
    """Steepest Ascent (Leo dốc nhất). Tương tự cái trên nhưng KHÔNG BƯỚC NGAY. Quét đánh giá TẤT CẢ hàng xóm, xong mới chọn hướng tốt NHẤT."""
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
            if neighbor_h < best_h: # Quét hết để lưu lại thằng con tốt nhất (Best)
                best_h = neighbor_h
                best_neighbor = Node(new_state, current_node, move, current_node.step + 1)
        if best_neighbor is None: return solution(current_node), visited_nodes
        current_node = best_neighbor

def stochastic_hill_climbing(initial_state):
    """Stochastic Hill Climbing (Leo đồi ngẫu nhiên). Tập hợp TẤT CẢ hàng xóm tốt hơn mình vào 1 mảng, rồi bốc thăm chọn ngẫu nhiên 1 cái."""
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
    """Random Restart. Khi leo đồi bị kẹt, hệ thống sinh ra ma trận mới tinh bắt đầu lại từ đầu (tối đa 50 lần). Rất hiệu quả để thoát kẹt."""
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
            if best_neighbor is None: break  # Bị kẹt đỉnh -> Break While để For bên ngoài nhảy Restart
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
        
        # Delta: Sự chênh lệch chất lượng. Delta Âm là tốt, Delta Dương là bước đi Tồi
        delta = calc_manhattan(next_node.state) - calc_manhattan(current_node.state)
        
        if delta < 0: # Bước đi TỐT HƠN -> Luôn luôn chọn
            current_node = next_node
        else:
            p = math.exp(-delta / T) # Hàm mũ tính Xác suất p (0->1) chấp nhận nước đi tồi
            if random.random() < p: current_node = next_node
        T = alpha * T
    return solution(current_node), visited_nodes

def local_beam_search(initial_state):
    """Local Beam Search. Dùng một chùm (K = 3) trạng thái cùng đi tìm đường. Nếu 1 trạng thái tìm thấy khu vực tốt, các trạng thái khác dồn tụ lại khu vực đó."""
    k = 3
    visited_nodes = 0
    current_state_set = [Node(initial_state, None, None, 0)]
    for _ in range(k - 1): # Khởi tạo K trạng thái khác nhau
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
                
        if not neighbor_states: return solution(current_state_set[0]), visited_nodes
        for neighbor in neighbor_states:
            if check_done(neighbor.state): return solution(neighbor), visited_nodes
            
        # Sắp xếp toàn bộ rổ hàng xóm lấy được
        neighbor_states.sort(key=lambda node: calc_manhattan(node.state))
        current_state_set = neighbor_states[:k] # Cắt phéng đồ thị, CHỈ DUY TRÌ đúng K trạng thái tinh hoa nhất đi tiếp.

# ------------------------------------------------------------------------------
# 3.4. CÁC TÁC NHÂN PHẢN XẠ (REFLEX AGENT)
# Trí tuệ cấp độ thấp nhất. Không cần tìm kiếm cây/đồ thị, chỉ đưa ra hành động dựa trên cảm nhận tức thì.
# ------------------------------------------------------------------------------

def simple_reflex(initial_state):
    """Simple Reflex Agent. Tác nhân phản xạ đơn giản: Không có bộ nhớ. Đi lung tung hú họa hi vọng trúng đích."""
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
    """Model-based Reflex Agent. Tác nhân phản xạ có mô hình: Khôn hơn một chút là có 'Model' nhớ lại lịch sử tránh dẫm lại đường lùi."""
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
        if state_tuple in path: return "failure" # Phát hiện vòng lặp
        
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
            plan_s = or_search(s_node.state, path, s_node) # Lấy rẽ nhánh từ OR Search
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
    """Backtracking CSP: Tìm kiếm quay lui. Thử điền số vào từng ô, nếu vi phạm luật thì xóa đi thử số khác."""
    visited_nodes = [0]
    
    variables = [(i, j) for i in range(3) for j in range(3)] # 9 Biến: Tọa độ 9 ô vuông
    goal_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    def is_consistent(var, value, assignment):
        """Luật (Constraint): Số điền không được trùng lặp và phải bằng giá trị Goal."""
        if value in assignment.values(): return False
        if value != goal_matrix[var[0]][var[1]]: return False
        return True

    def recursive_backtracking(assignment):
        visited_nodes[0] += 1
        if visited_nodes[0] > 30000: return "Timeout"

        if len(assignment) == len(variables): return assignment # Đã điền xong cả 9 ô

        var = next(v for v in variables if v not in assignment) # Bốc 1 biến (ô vuông) trống

        for value in range(9): # Miền giá trị (Domain): Thử gán các số từ 0 đến 8
            if is_consistent(var, value, assignment):
                assignment[var] = value # Thỏa mãn thì gán
                result = recursive_backtracking(assignment) # Đệ quy để điền ô tiếp theo
                if result != "failure" and result != "Timeout": return result
                del assignment[var] # Đi vào ngõ cụt thì xóa gán (Quay lui - Backtrack)
        return "failure"

    result_assignment = recursive_backtracking({})

    if result_assignment == "Timeout": return "Timeout", visited_nodes[0]
    elif result_assignment != "failure":
        # Chuyển đổi ngược Dictionary Assignment về lại mảng 2D cho GUI đọc
        final_matrix = [[0]*3 for _ in range(3)]
        for (i, j), val in result_assignment.items(): final_matrix[i][j] = val
        start_node = Node(initial_state, None, "Start", 0)
        goal_node = Node(final_matrix, start_node, "Teleport (CSP Backtrack)", 1)
        return [start_node, goal_node], visited_nodes[0]
    return None, visited_nodes[0]

def forward_checking_search(initial_state):
    """Forward Checking CSP: Thông minh hơn Backtrack. Khi vừa điền 1 ô, nó quét xóa luôn các số tương tự ở ô khác (Nhìn trước 1 bước)."""
    visited_nodes = [0]
    variables = [(i, j) for i in range(3) for j in range(3)]
    goal_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    # Domains: Mỗi biến lúc đầu có trọn vẹn 9 sự lựa chọn [0..8]
    domains = {v: list(range(9)) for v in variables}

    def is_consistent(var, value, assignment):
        if value in assignment.values(): return False
        if value != goal_matrix[var[0]][var[1]]: return False
        return True

    def apply_forward_checking(var, value, current_domains, assignment):
        """Kỹ thuật tỉa cành Forward Checking: Thu hẹp Domain của các ô chưa xét."""
        removed = []
        for unassigned_var in variables:
            if unassigned_var not in assignment:
                if value in current_domains[unassigned_var]:
                    current_domains[unassigned_var].remove(value) # Xóa giá trị trùng lặp
                    removed.append((unassigned_var, value)) # Ghi sổ để sau nhỡ sai còn biết đường Khôi phục
                if not current_domains[unassigned_var]:
                    return "failure", removed # Cắt nhánh! 1 ô nào đó hết giá trị điền -> Nhánh sai chắc
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
                    current_domains[v].append(val) # Trả lại các lựa chọn đã lỡ tay xóa
                del assignment[var]
        return "failure"

    result_assignment = forward_check({}, domains)

    if result_assignment == "Timeout": return "Timeout", visited_nodes[0]
    elif result_assignment != "failure":
        final_matrix = [[0]*3 for _ in range(3)]
        for (i, j), val in result_assignment.items(): final_matrix[i][j] = val
        start_node = Node(initial_state, None, "Start", 0)
        goal_node = Node(final_matrix, start_node, "Teleport (Forward Checking)", 1)
        return [start_node, goal_node], visited_nodes[0]
    return None, visited_nodes[0]

def min_conflicts_search(initial_state):
    """Min Conflicts CSP: Khởi tạo bảng đầy rẫy lỗi (số lung tung). Sau đó liên tục tìm các ô đang vi phạm lỗi và sửa chúng lại để giảm lỗi."""
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
            conflicts = calc_heuristic(new_state) # Dùng hàm đếm ô sai (h) thay cho bộ đếm xung đột CSP

            # Cập nhật xem hướng đi nào giảm được Mức độ Xung đột (lỗi vi phạm) nhiều nhất
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
    """AC-3 (Arc Consistency) CSP: Phép màu toán học đồ thị. Loại bỏ mọi nhánh sai, thu hẹp Miền giá trị cho tới khi chỉ còn lại đúng kết quả đích."""
    visited_nodes = 0
    domains = {}
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    # Nạp ma trận Đích vào Domains (AC-3 sẽ dựa vào đây để lọc giá trị đúng nhất)
    for i in range(3):
        for j in range(3):
            domains[(i, j)] = {goal[i][j]}

    # Queue lưu giữ các cặp Đỉnh-Cung (Arc) đồ thị
    queue = deque([(xi, xj) for xi in domains for xj in domains if xi != xj])

    def remove_inconsistent_values(xi, xj):
        removed = False
        for x in list(domains[xi]):
            if not any(x != y for y in domains[xj]):
                domains[xi].remove(x)
                removed = True
        return removed

    # Động cơ cốt lõi của AC-3: Quét liên tục các Cung
    while queue:
        visited_nodes += 1
        xi, xj = queue.popleft()
        if remove_inconsistent_values(xi, xj):
            for xk in domains:
                if xk != xi and xk != xj:
                    queue.append((xk, xi)) # Nếu cập nhật domain, thêm lại cung hàng xóm vào xử lý tiếp

    # Khởi tạo ma trận kết quả sau khi AC-3 đã làm sạch Domain
    solved = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            if len(domains[(i, j)]) != 1:
                return None, visited_nodes # Domain rỗng -> Vô nghiệm
            solved[i][j] = next(iter(domains[(i, j)]))

    if check_done(solved):
        start_node = Node(initial_state, None, "Start", 0)
        goal_node = Node(solved, start_node, "AC-3 Teleport", 1)
        return [start_node, goal_node], visited_nodes

    return None, visited_nodes

# ==============================================================================
# 4. GIAO DIỆN ĐỒ HỌA (GUI) SỬ DỤNG LIBRALY TKINTER
# ==============================================================================
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle AI Solver - Pro Edition")
        self.root.geometry("1100x750") 
        self.root.configure(bg="#F4F6F9") 
        
        # Các cờ (Flags) trạng thái điều khiển luồng hoạt ảnh
        self.is_animating = False 
        self.is_paused = False
        self.is_cancelled = False
        
        title_lbl = tk.Label(root, text="Hệ Thống Trí Tuệ Nhân Tạo 8-Puzzle", font=("Segoe UI", 24, "bold"), bg="#F4F6F9", fg="#2C3E50")
        title_lbl.pack(pady=(20, 10))
        
        main_frame = tk.Frame(root, bg="#F4F6F9")
        main_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(main_frame, bg="#F4F6F9") 
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        tk.Label(left_frame, text="Ma Trận Đầu Vào (0-8)", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#34495E").pack(anchor="w", pady=(0, 10))
        
        # Khung chứa ma trận lưới (Grid) 3x3
        board_container = tk.Frame(left_frame, bg="#BDC3C7", bd=5, relief="raised", padx=5, pady=5)
        board_container.pack(pady=5)
        board_frame = tk.Frame(board_container, bg="#2C3E50")
        board_frame.pack()
        
        self.entries = [] # Mảng 2 chiều chứa 9 ô Nhập dữ liệu (tk.Entry)
        for i in range(3):
            row_entries = []
            for j in range(3):
                e = tk.Entry(board_frame, width=3, font=("Consolas", 36, "bold"), justify="center", bg="#ECF0F1", fg="#2980B9", relief="flat")
                e.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(e)
            self.entries.append(row_entries)
            
        tk.Label(left_frame, text="Chọn Thuật Toán AI", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#34495E").pack(anchor="w", pady=(25, 5))

        self.algo_var = tk.StringVar(value="BFS")
        
        # Danh sách Toàn bộ 20 Thuật toán hiển thị trên Hộp chọn
        algos = ["BFS", "DFS", "IDS", "UCS", "Greedy Search", "A* Search", 
                 "IDA*", "Simple Hill Climbing", "Steepest-Ascent Hill Climbing", 
                 "Stochastic Hill Climbing", "Random Restart Hill Climbing", "Local Beam Search",
                 "Simulated Annealing", "Simple Reflex", "Model-based Reflex", "Sensorless (Belief State)",
                 "AND-OR Graph Search", "Backtracking CSP", "Forward Checking CSP", "AC-3 CSP", "Min-Conflicts CSP"]
        
        style = ttk.Style()
        style.theme_use('clam')
        self.algo_cb = ttk.Combobox(left_frame, textvariable=self.algo_var, values=algos, state="readonly", width=25, font=("Segoe UI", 13))
        self.algo_cb.pack(anchor="w", pady=5)
            
        tk.Label(left_frame, text="Chế Độ Hiển Thị", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#34495E").pack(anchor="w", pady=(15, 5))
        self.display_mode_var = tk.StringVar(value="In từ từ (Hoạt ảnh)")
        modes = ["In từ từ (Hoạt ảnh)", "In tức thì (Tất cả)"]
        self.display_cb = ttk.Combobox(left_frame, textvariable=self.display_mode_var, values=modes, state="readonly", width=25, font=("Segoe UI", 13))
        self.display_cb.pack(anchor="w", pady=5)

        # Cụm các nút điều khiển
        btn_frame = tk.Frame(left_frame, bg="#F4F6F9")
        btn_frame.pack(pady=30, fill=tk.X)
        self.btn_new = tk.Button(btn_frame, text="🔄 Tạo Bài Mới", command=self.new_puzzle, font=("Segoe UI", 12, "bold"), bg="#0D47A1", fg="black", activebackground="#1565C0", activeforeground="black", relief="flat", cursor="hand2", pady=8)
        self.btn_new.pack(fill=tk.X, pady=5)
        self.btn_search = tk.Button(btn_frame, text="▶ Bắt Đầu Giải", command=self.search, font=("Segoe UI", 12, "bold"), bg="#1B5E20", fg="black", activebackground="#2E7D32", activeforeground="black", relief="flat", cursor="hand2", pady=8)
        self.btn_search.pack(fill=tk.X, pady=5)
        self.btn_pause = tk.Button(btn_frame, text="⏸ Tạm Dừng", command=self.toggle_pause, font=("Segoe UI", 12, "bold"), bg="#E65100", fg="black", activebackground="#EF6C00", activeforeground="black", disabledforeground="#555555", relief="flat", cursor="hand2", pady=8, state=tk.DISABLED)
        self.btn_pause.pack(fill=tk.X, pady=5)
        self.btn_cancel = tk.Button(btn_frame, text="⏹ Hủy Bỏ", command=self.cancel_animation, font=("Segoe UI", 12, "bold"), bg="#B71C1C", fg="black", activebackground="#C62828", activeforeground="black", disabledforeground="#555555", relief="flat", cursor="hand2", pady=8, state=tk.DISABLED)
        self.btn_cancel.pack(fill=tk.X, pady=5)
        
        right_frame = tk.Frame(main_frame, bg="#F4F6F9") 
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Console Output:", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#34495E").pack(anchor="w", pady=(0, 5))
        
        # Màn hình Log Console (Nơi in ra các bước đi và bảng mô phỏng text)
        self.txt_log = scrolledtext.ScrolledText(right_frame, font=("Consolas", 13), bg="#1E1E1E", fg="#D4D4D4", insertbackground="white", relief="flat", padx=10, pady=10)
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        
        # Thiết lập các thẻ màu (Tags) cho màn hình Log
        self.txt_log.tag_configure("highlight", foreground="#F1C40F", font=("Consolas", 13, "bold"))
        self.txt_log.tag_configure("success", foreground="#2ECC71", font=("Consolas", 13, "bold"))
        self.txt_log.tag_configure("error", foreground="#E74C3C", font=("Consolas", 13, "bold"))
        self.txt_log.tag_configure("info", foreground="#3498DB")

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
        self.log("> Hệ thống đã tạo một bài toán mới sẵn sàng...\n", "info")

    def toggle_pause(self):
        """Kích hoạt/Tắt cờ Tạm dừng. Hàm animate_steps sẽ bắt cờ này để quyết định có chạy dòng lệnh in tiếp theo không."""
        if not self.is_animating: return
        if not self.is_paused:
            self.is_paused = True
            self.btn_pause.config(text="▶ Tiếp Tục", bg="#1B5E20", fg="white")
            self.log("\n[!] ĐÃ TẠM DỪNG MÔ PHỎNG...\n", "highlight")
        else:
            self.is_paused = False
            self.btn_pause.config(text="⏸ Tạm Dừng", bg="#E65100", fg="white")
            self.log("[!] TIẾP TỤC CHẠY...\n", "info")

    def cancel_animation(self):
        if self.is_animating:
            self.is_cancelled = True

    def reset_controls(self):
        """Mở khóa/Khóa các nút bấm tương tác khi Animation dừng lại/chạy lại."""
        self.is_animating = False
        self.is_paused = False
        self.is_cancelled = False
        self.btn_search.config(state=tk.NORMAL)
        self.btn_new.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED, text="⏸ Tạm Dừng", bg="#E65100", fg="white")
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
        self.log(f"• Số lượng Node đã mở rộng : {explored_count}\n")
        self.log(f"• Tổng số bước đã di chuyển: {len(steps)-1}\n")
        
        if is_success:
            self.log(f"• Trạng thái cuối: ", "info")
            self.log("GIẢI THÀNH CÔNG\n", "success")
        else:
            self.log(f"• Trạng thái cuối: ", "info")
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
        self.log(f"> Đang khởi chạy thuật toán: {algo}...\n", "highlight")
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
                    self.log("> Trạng thái vô nghiệm. Yêu cầu nhập lại!\n", "error")
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
            self.log("> Quá tải bộ nhớ. Thuật toán đã buộc dừng an toàn.\n", "error")
            messagebox.showwarning("Quá tải", f"Đã quét {visited_nodes} trạng thái nhưng dừng để tránh đơ máy.")
        elif result is None:    # Kịch bản 2: Không tìm thấy đường
            self.log("> Thuật toán không thể tìm ra kết quả.\n", "error")
            messagebox.showinfo("Thất bại", f"Không tìm được lời giải sau {visited_nodes} vòng lặp/kiểm tra.")
        else:                   # Kịch bản 3: Có kết quả mảng Node -> Giao cho Animation chạy in ra chữ
            self.is_animating = True 
            self.btn_search.config(state=tk.DISABLED) 
            self.btn_new.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self.btn_cancel.config(state=tk.NORMAL)
            
            self.log(f"> Tìm kiếm hoàn tất! Bắt đầu in kết quả:\n", "success")
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