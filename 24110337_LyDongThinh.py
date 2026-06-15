import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import random
import copy
import math
from collections import deque
from queue import PriorityQueue
import sys

# Nới rộng giới hạn đệ quy của Python từ 1000 lên 50000
sys.setrecursionlimit(50000)

# ========================================================
# 1. LỚP DỮ LIỆU NODE SỬ DỤNG CHO CÁC THUẬT TOÁN ĐỒ THỊ
# ========================================================
class Node:
    def __init__(self, state, parent, move, step):
        self.state = state
        self.parent = parent
        self.move = move
        self.step = step # Chi phí g(n) dùng cho UCS và A*

    def __lt__(self, other):
        return self.step < other.step

# ========================================================
# 2. CÁC HÀM LOGIC CHUNG
# ========================================================

def check_done(matrix):
    """Kiểm tra xem ma trận hiện tại đã khớp với ma trận đích (Goal) chưa"""
    return matrix == [
        [1, 2, 3],
        [4, 5, 6], 
        [7, 8, 0]
    ]

def find_empty_position(matrix):
    """Tìm tọa độ hàng (i) và cột (j) của ô trống (số 0)"""
    for i in range(3):
        for j in range(3):
            if matrix[i][j] == 0:
                return i, j
    return -1, -1


def possible_move(matrix):
    """Kiểm tra xem ô trống có thể di chuyển theo những hướng nào"""
    moves = []
    x, y = find_empty_position(matrix)
    if x < 2: moves.append("D") # Nếu chưa ở hàng cuối -> có thể đi Xuống (Down)
    if x > 0: moves.append("U") # Nếu chưa ở hàng đầu -> có thể đi Lên (Up)
    if y < 2: moves.append("R") # Nếu chưa ở cột cuối -> có thể đi Phải (Right)
    if y > 0: moves.append("L") # Nếu chưa ở cột đầu -> có thể đi Trái (Left)
    return moves

def remove_repetition(move, pre_move):
    """Ngăn thuật toán đi lùi (tránh bị lặp vô hạn). Ví dụ: vừa đi Lên (U) xong thì không được đi Xuống (D) ngay."""
    return ((move == "U" and pre_move == "D") or 
            (move == "D" and pre_move == "U") or
            (move == "L" and pre_move == "R") or 
            (move == "R" and pre_move == "L"))

def do_action(matrix, move):
    """Tạo ra ma trận mới sau khi thực hiện 1 bước đi (tráo đổi vị trí số 0 và số kề cạnh)"""
    new_matrix = copy.deepcopy(matrix) # Bắt buộc phải deepcopy để không làm hỏng ma trận gốc của Node cha
    x, y = find_empty_position(new_matrix)
    if move == "U": new_matrix[x][y], new_matrix[x - 1][y] = new_matrix[x - 1][y], new_matrix[x][y]
    elif move == "D": new_matrix[x][y], new_matrix[x + 1][y] = new_matrix[x + 1][y], new_matrix[x][y]
    elif move == "L": new_matrix[x][y], new_matrix[x][y - 1] = new_matrix[x][y - 1], new_matrix[x][y]
    elif move == "R": new_matrix[x][y], new_matrix[x][y + 1] = new_matrix[x][y + 1], new_matrix[x][y]
    return new_matrix

def matrix_to_tuple(matrix):
    """
    Chuyển ma trận (List of Lists) thành Tuple. 
    Lý do: Kiểu List có thể thay đổi (mutable) nên không thể đưa vào tập hợp Set() (explored). Tuple thì được.
    """
    return tuple(tuple(row) for row in matrix)

def solution(node):
    """Khi tìm thấy đích, dùng hàm này dò ngược theo thuộc tính parent để lấy ra toàn bộ đường đi từ Start -> Goal"""
    result = []
    while node is not None:
        result.append(node)
        node = node.parent
    result.reverse() # Đảo ngược lại để có mảng theo đúng thứ tự từ Start tới Goal
    return result

def check_solvable(matrix):
    """
    Hàm toán học: Kiểm tra xem đề bài sinh ra có khả năng giải được không (Dựa vào số nghịch thế - inversions)
    Số nghịch thế chẵn -> giải được. Lẻ -> Vô nghiệm. Ngăn thuật toán chạy vô cực.
    """
    arr = [val for row in matrix for val in row if val != 0] # Dàn ma trận thành mảng 1 chiều, bỏ qua số 0
    inversions = sum(1 for i in range(len(arr)) for j in range(i + 1, len(arr)) if arr[i] > arr[j])
    return inversions % 2 == 0

def calc_heuristic(matrix):
    """Hàm Heuristic h(n) 1: Đếm số ô sai vị trí (Dùng cho Greedy, A*, IDA*)"""
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    count = 0
    for i in range(3):
        for j in range(3):
            if matrix[i][j] != 0 and matrix[i][j] != goal[i][j]:
                count += 1
    return count

def calc_manhattan(matrix):
    """Hàm Heuristic h(n) 2: Khoảng cách Manhattan (Dùng cho các thuật toán Climbing & Beam)"""
    distance = 0
    for i in range(3):
        for j in range(3):
            val = matrix[i][j]
            if val != 0:
                target_row = (val - 1) // 3
                target_col = (val - 1) % 3
                distance += abs(i - target_row) + abs(j - target_col)
    return distance

def get_random_solvable_state():
    """Hàm phụ trợ sinh ma trận ngẫu nhiên giải được"""
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

# --- LOGIC RIÊNG CHO MÔI TRƯỜNG MÙ (SENSORLESS BELIEF STATE) ---
def do_belief_action(belief_tuple, move):
    """Duyệt và áp dụng hành động lên tất cả trạng thái trong Belief State."""
    new_states = set()
    for state_tuple in belief_tuple:
        state_list = [list(row) for row in state_tuple]
        moves = possible_move(state_list)
        if move in moves:
            new_state = do_action(state_list, move)
            new_states.add(matrix_to_tuple(new_state))
        else:
            new_states.add(matrix_to_tuple(state_list)) # Đụng tường -> Ma trận giữ nguyên
    return tuple(sorted(new_states))

def check_belief_done(belief_tuple):
    """Kiểm tra xem tập niềm tin đã thu gọn về duy nhất 1 trạng thái Đích chưa."""
    goal_tuple = matrix_to_tuple([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
    return len(belief_tuple) == 1 and belief_tuple[0] == goal_tuple

def get_close_belief_states():
    """Sinh 3 trạng thái xuất phát cách đích từ 3 đến 5 bước, loại trừ đi lùi lặp lại nước."""
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
    """Tính toán giá trị Heuristic Max bằng khoảng cách Manhattan cho Belief State."""
    max_h = 0
    for state_tuple in belief_tuple:
        state_list = [list(row) for row in state_tuple]
        h = calc_manhattan(state_list) # Sử dụng khoảng cách Manhattan
        if h > max_h:
            max_h = h
    return max_h


# ==============================================================================
# 3. 16 THUẬT TOÁN TÌM KIẾM AI
# ==============================================================================
# 3.1. Các thuật toán tìm kiếm mù (Uninformed Search)
def bfs(initial_state):
    """Breadth-First Search (Duyệt theo chiều rộng, dùng Queue)"""
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
                if check_done(child.state): return solution(child), visited_nodes
                frontier.append(child)
                explored.add(state_tuple)
    return None, visited_nodes

def dfs(initial_state):
    """Depth-First Search (Duyệt theo chiều sâu, dùng Stack)"""
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
                if check_done(child.state): return solution(child), visited_nodes
                frontier.append(child)
                explored.add(state_tuple)
    return None, visited_nodes

def dls(node, limit):
    """Depth-Limited Search (Thành phần hỗ trợ cho IDS, dừng sâu ở limit)"""
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

def ids(initial_state):
    """Iterative Deepening Search (Duyệt sâu dần, kết hợp ưu điểm của BFS và DFS)"""
    root_node = Node(initial_state, None, None, 0)
    total_visited = 0
    for depth in range(25): 
        res, visited = dls(root_node, depth) 
        total_visited += visited
        if res: return res, total_visited
    return None, total_visited

def ucs(initial_state):
    """Uniform Cost Search (Duyệt theo chi phí g(n) thấp nhất, dùng PriorityQueue)"""
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

# 3.2. Các thuật toán tìm kiếm có thông tin (Informed Search)
def greedy_search(initial_state):
    """Greedy Best-First Search (Tham lam, chỉ chọn node có h(n) nhỏ nhất)"""
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
            if not in_frontier and not in_reached: frontier.append(m)
    return None, visited_nodes

def a_star_search(initial_state):
    """A* Search (Tối ưu nhất, cân bằng g(n) + h(n))"""
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

def ida_star(initial_state):
    """Iterative Deepening A* (IDA* - Kết hợp giới hạn nhớ của IDS và thông minh của A*)"""
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

# 3.3. Các thuật toán tối ưu cục bộ (Local Search)
def simple_hill_climbing(initial_state):
    """Simple Hill Climbing (Dừng lại ngay khi tìm thấy 1 hàng xóm tốt hơn)"""
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
        if not found_better: return solution(current_node), visited_nodes

def steepest_ascent_hill_climbing(initial_state):
    """Steepest Ascent Hill Climbing (Đánh giá TẤT CẢ hàng xóm, chọn cái tốt nhất)"""
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
        if best_neighbor is None: return solution(current_node), visited_nodes
        current_node = best_neighbor

def stochastic_hill_climbing(initial_state):
    """Stochastic Hill Climbing (Chọn ngẫu nhiên 1 trong số các hàng xóm tốt hơn)"""
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
    """Random Restart Hill Climbing (Khởi động lại nếu bị kẹt cực trị cục bộ)"""
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
            if best_neighbor is None: break 
            current_node = best_neighbor
    return None, visited_nodes

def simulated_annealing(initial_state):
    """Simulated Annealing (Luyện kim tự nhiên - Chấp nhận rủi ro lùi bước để thoát kẹt)"""
    current_node = Node(initial_state, None, None, 0)
    visited_nodes = 0
    T = 100.0      # Nhiệt độ ban đầu
    T_min = 0.001  # Nhiệt độ tối thiểu để dừng
    alpha = 0.99   # Tốc độ làm lạnh
    while T > T_min:
        visited_nodes += 1
        if check_done(current_node.state): return solution(current_node), visited_nodes
        moves = possible_move(current_node.state)
        valid_moves = [m for m in moves if not (current_node.move and remove_repetition(m, current_node.move))]
        if not valid_moves: valid_moves = moves
        chosen_move = random.choice(valid_moves)
        new_state = do_action(current_node.state, chosen_move)
        next_node = Node(new_state, current_node, chosen_move, current_node.step + 1)
        delta = calc_manhattan(next_node.state) - calc_manhattan(current_node.state)
        if delta < 0:
            current_node = next_node
        else:
            p = math.exp(-delta / T) # Xác suất p chấp nhận nước đi tồi
            if random.random() < p: current_node = next_node
        T = alpha * T
    return solution(current_node), visited_nodes

def local_beam_search(initial_state):
    """Local Beam Search (Giữ lại k trạng thái tốt nhất mỗi vòng)"""
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
        if not neighbor_states: return solution(current_state_set[0]), visited_nodes
        for neighbor in neighbor_states:
            if check_done(neighbor.state): return solution(neighbor), visited_nodes
        neighbor_states.sort(key=lambda node: calc_manhattan(node.state))
        current_state_set = neighbor_states[:k] # Cắt chùm, chỉ lấy K phần tử tốt nhất

# 3.4. Các thuật toán tác nhân phản xạ (Reflex Agent)
def simple_reflex(initial_state):
    """Simple Reflex Agent (Đi lung tung ngẫu nhiên, không thèm nhớ quá khứ)"""
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
    """Model-based Reflex Agent (Đi ngẫu nhiên nhưng có mô hình tránh đường cụt)"""
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

# --- THUẬT TOÁN CHO MÔI TRƯỜNG KHÔNG NHÌN THẤY (A* MANHATTAN) ---
def belief_state_astar(initial_belief_tuple):
    """Thuật toán A* sử dụng khoảng cách Manhattan (Hàm Heuristic Max) cho Tập niềm tin."""
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
    """AND-OR Graph Search (Tìm kiếm trên đồ thị AND-OR)"""
    visited_nodes = [0]
    
    def or_search(state, path, current_node):
        if visited_nodes[0] > 30000: 
            return "Timeout"
            
        visited_nodes[0] += 1
        
        if check_done(state):
            return current_node
        
        state_tuple = matrix_to_tuple(state)
        if state_tuple in path:
            return "failure"
        
        for move in possible_move(state):
            if current_node.move and remove_repetition(move, current_node.move):
                continue
                
            new_state = do_action(state, move)
            child_node = Node(new_state, current_node, move, current_node.step + 1)
            
            result_states = [child_node] 
            
            plan = and_search(result_states, path + [state_tuple])
            
            if plan != "failure":
                return plan
                
        return "failure"

    def and_search(states, path):
        plans = {}
        
        for s_node in states:
            plan_s = or_search(s_node.state, path, s_node)
            
            if plan_s == "failure" or plan_s == "Timeout":
                return plan_s
                
            plans[matrix_to_tuple(s_node.state)] = plan_s
        
        return list(plans.values())[0]

    start_node = Node(initial_state, None, None, 0)
    result_node = or_search(initial_state, [], start_node)
    
    if result_node == "Timeout":
        return "Timeout", visited_nodes[0]
    elif result_node == "failure" or result_node is None:
        return None, visited_nodes[0]
    else:
        return solution(result_node), visited_nodes[0]
    
# ==============================================================================
# 4. GIAO DIỆN ĐỒ HỌA (GUI)
# ==============================================================================
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle AI Solver - Pro Edition")
        self.root.geometry("1100x750") 
        self.root.configure(bg="#F4F6F9") 
        
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
        
        board_container = tk.Frame(left_frame, bg="#BDC3C7", bd=5, relief="raised", padx=5, pady=5)
        board_container.pack(pady=5)
        
        board_frame = tk.Frame(board_container, bg="#2C3E50")
        board_frame.pack()
        
        self.entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                e = tk.Entry(board_frame, width=3, font=("Consolas", 36, "bold"), justify="center", bg="#ECF0F1", fg="#2980B9", relief="flat")
                e.grid(row=i, column=j, padx=2, pady=2)
                row_entries.append(e)
            self.entries.append(row_entries)
            
        tk.Label(left_frame, text="Chọn Thuật Toán AI", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#34495E").pack(anchor="w", pady=(25, 5))

        self.algo_var = tk.StringVar(value="BFS")
        algos = ["BFS", "DFS", "IDS", "UCS", "Greedy Search", "A* Search", 
                 "IDA*", "Simple Hill Climbing", "Steepest-Ascent Hill Climbing", 
                 "Stochastic Hill Climbing", "Random Restart Hill Climbing", "Local Beam Search",
                 "Simulated Annealing", "Simple Reflex", "Model-based Reflex", "Sensorless (Belief State)",
                 "AND-OR Graph Search"]
        
        style = ttk.Style()
        style.theme_use('clam')
        self.algo_cb = ttk.Combobox(left_frame, textvariable=self.algo_var, values=algos, state="readonly", width=25, font=("Segoe UI", 13))
        self.algo_cb.pack(anchor="w", pady=5)
            
        tk.Label(left_frame, text="Chế Độ Hiển Thị", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#34495E").pack(anchor="w", pady=(15, 5))
        self.display_mode_var = tk.StringVar(value="In từ từ (Hoạt ảnh)")
        modes = ["In từ từ (Hoạt ảnh)", "In tức thì (Tất cả)"]
        self.display_cb = ttk.Combobox(left_frame, textvariable=self.display_mode_var, values=modes, state="readonly", width=25, font=("Segoe UI", 13))
        self.display_cb.pack(anchor="w", pady=5)

        btn_frame = tk.Frame(left_frame, bg="#F4F6F9")
        btn_frame.pack(pady=30, fill=tk.X)
        
        self.btn_new = tk.Button(btn_frame, text="🔄 Tạo Bài Mới", command=self.new_puzzle, 
                                 font=("Segoe UI", 12, "bold"), bg="#0D47A1", fg="black", 
                                 activebackground="#1565C0", activeforeground="black", 
                                 relief="flat", cursor="hand2", pady=8)
        self.btn_new.pack(fill=tk.X, pady=5)
        
        self.btn_search = tk.Button(btn_frame, text="▶ Bắt Đầu Giải", command=self.search, 
                                    font=("Segoe UI", 12, "bold"), bg="#1B5E20", fg="black", 
                                    activebackground="#2E7D32", activeforeground="black", 
                                    relief="flat", cursor="hand2", pady=8)
        self.btn_search.pack(fill=tk.X, pady=5)
        
        self.btn_pause = tk.Button(btn_frame, text="⏸ Tạm Dừng", command=self.toggle_pause, 
                                   font=("Segoe UI", 12, "bold"), bg="#E65100", fg="black", 
                                   activebackground="#EF6C00", activeforeground="black", 
                                   disabledforeground="#555555",
                                   relief="flat", cursor="hand2", pady=8, state=tk.DISABLED)
        self.btn_pause.pack(fill=tk.X, pady=5)
        
        self.btn_cancel = tk.Button(btn_frame, text="⏹ Hủy Bỏ", command=self.cancel_animation, 
                                    font=("Segoe UI", 12, "bold"), bg="#B71C1C", fg="black", 
                                    activebackground="#C62828", activeforeground="black", 
                                    disabledforeground="#555555",
                                    relief="flat", cursor="hand2", pady=8, state=tk.DISABLED)
        self.btn_cancel.pack(fill=tk.X, pady=5)
        
        right_frame = tk.Frame(main_frame, bg="#F4F6F9") 
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Console Output:", font=("Segoe UI", 14, "bold"), bg="#F4F6F9", fg="#34495E").pack(anchor="w", pady=(0, 5))
        
        self.txt_log = scrolledtext.ScrolledText(right_frame, font=("Consolas", 13), bg="#1E1E1E", fg="#D4D4D4", insertbackground="white", relief="flat", padx=10, pady=10)
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        
        self.txt_log.tag_configure("highlight", foreground="#F1C40F", font=("Consolas", 13, "bold"))
        self.txt_log.tag_configure("success", foreground="#2ECC71", font=("Consolas", 13, "bold"))
        self.txt_log.tag_configure("error", foreground="#E74C3C", font=("Consolas", 13, "bold"))
        self.txt_log.tag_configure("info", foreground="#3498DB")

        self.new_puzzle()

    def log(self, text, tag=None):
        self.txt_log.insert(tk.END, text, tag)
        self.txt_log.see(tk.END)

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
            messagebox.showerror("Lỗi Nhập Liệu", "Vui lòng chỉ nhập các số nguyên từ 0 đến 8!")
            return None

    def new_puzzle(self):
        if self.is_animating: return 
        matrix = get_random_solvable_state()
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(matrix[i][j]))
        self.txt_log.delete('1.0', tk.END)
        self.log("> Hệ thống đã tạo một bài toán mới sẵn sàng...\n", "info")

    def toggle_pause(self):
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
        self.is_animating = False
        self.is_paused = False
        self.is_cancelled = False
        self.btn_search.config(state=tk.NORMAL)
        self.btn_new.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED, text="⏸ Tạm Dừng", bg="#E65100", fg="white")
        self.btn_cancel.config(state=tk.DISABLED)

    def animate_steps(self, steps, current_index, explored_count):
        if self.is_cancelled:
            self.log(f"\n[X] ĐÃ HỦY THEO YÊU CẦU NGƯỜI DÙNG\n", "error")
            self.reset_controls()
            messagebox.showwarning("Đã Dừng", "Tiến trình mô phỏng đã bị người dùng hủy!")
            return

        if self.is_paused:
            self.root.after(100, self.animate_steps, steps, current_index, explored_count)
            return

        mode = self.display_mode_var.get()

        # NẾU CHỌN IN TỨC THÌ (TẤT CẢ)
        if mode == "In tức thì (Tất cả)":
            for idx in range(current_index, len(steps)):
                if self.is_cancelled: 
                    self.log(f"\n[X] ĐÃ HỦY...\n", "error")
                    self.reset_controls()
                    return
                
                node = steps[idx]
                move_str = node.move if node.move else "Trạng thái bắt đầu"
                self.log(f"Bước {idx} - Hành động: {move_str}\n", "highlight")
                
                if isinstance(node.state[0][0], tuple): # Xử lý Belief State
                    self.log(f"  [Tập niềm tin: {len(node.state)} trạng thái có thể xảy ra]\n", "error")
                    for s_idx, matrix_tuple in enumerate(node.state):
                        self.log(f"    + Trạng thái {s_idx+1}:\n")
                        for row in matrix_tuple:
                            self.log("        " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
                else: # Trạng thái bình thường
                    for row in node.state:
                        self.log("    " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
                    self.update_grid_ui(node.state) # CẬP NHẬT LƯỚI ENTRY
                
                self.log("-" * 35 + "\n")
            
            # Sau khi in hết vòng lặp, gọi in tổng kết
            self._print_final_summary(steps, explored_count)
            return

        # NẾU CHỌN IN TỪ TỪ (HOẠT ẢNH)
        if current_index < len(steps):
            node = steps[current_index]
            move_str = node.move if node.move else "Trạng thái bắt đầu"
            self.log(f"Bước {current_index} - Hành động: {move_str}\n", "highlight")
            
            if isinstance(node.state[0][0], tuple): # Xử lý Belief State
                self.log(f"  [Tập niềm tin: {len(node.state)} trạng thái có thể xảy ra]\n", "error")
                for s_idx, matrix_tuple in enumerate(node.state):
                    self.log(f"    + Trạng thái {s_idx+1}:\n")
                    for row in matrix_tuple:
                        self.log("        " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
            else: # Trạng thái bình thường
                for row in node.state:
                    self.log("    " + "   ".join(str(x) if x != 0 else "_" for x in row) + "\n")
                self.update_grid_ui(node.state) # CẬP NHẬT LƯỚI ENTRY
            
            self.log("-" * 35 + "\n")
            self.root.after(300, self.animate_steps, steps, current_index + 1, explored_count)
        else:
            self._print_final_summary(steps, explored_count)

    def _print_final_summary(self, steps, explored_count):
        """Hàm phụ trợ in phần kết luận (Tách ra để dùng chung cho cả 2 chế độ)"""
        moves = [node.move for node in steps if node.move and not node.move.startswith("Restart") and not node.move.startswith("Random")]
        move_sequence = " -> ".join(moves) if moves else "Không có hành động"
        
        if isinstance(steps[-1].state[0][0], tuple):
            is_success = check_belief_done(steps[-1].state)
        else:
            is_success = check_done(steps[-1].state)
        
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
        if self.is_animating: return
        algo = self.algo_var.get()
        
        self.txt_log.delete('1.0', tk.END)
        self.log(f"> Đang khởi chạy thuật toán: {algo}...\n", "highlight")
        self.root.update() 
        
        result = None
        visited_nodes = 0
        
        try:
            if algo == "Sensorless (Belief State)":
                belief_start = get_close_belief_states()
                result, visited_nodes = belief_state_astar(belief_start)
            else:
                matrix = self.get_matrix()
                if not matrix: return
                if not check_solvable(matrix):
                    self.log("> Trạng thái vô nghiệm. Yêu cầu nhập lại!\n", "error")
                    messagebox.showwarning("Vô Nghiệm", "Ma trận này thuộc nhóm không thể giải (Inversions lẻ)!")
                    return
                
                # Danh sách gọi các thuật toán
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
                
        except RecursionError:
            # XỬ LÝ KHI ĐỆ QUY QUÁ LỚN
            self.log("\n[X] LỖI: VƯỢT QUÁ GIỚI HẠN ĐỆ QUY!\n", "error")
            self.log("> Cây tìm kiếm quá sâu, hệ thống đã buộc dừng để bảo vệ bộ nhớ.\n", "info")
            messagebox.showerror("Tràn Đệ Quy (Recursion Error)", "Độ sâu đệ quy đã vượt qua giới hạn an toàn của Python.\nThuật toán bị buộc dừng để tránh treo máy!")
            self.reset_controls()
            return # Thoát hàm luôn, không chạy phần in kết quả bên dưới nữa

        self.txt_log.delete('1.0', tk.END) 
        
        if result == "Timeout":
            self.log("> Quá tải bộ nhớ. Thuật toán đã buộc dừng an toàn.\n", "error")
            messagebox.showwarning("Quá tải", f"Đã quét {visited_nodes} trạng thái nhưng dừng để tránh đơ máy.")
        elif result is None:
            self.log("> Thuật toán không thể tìm ra đường đi.\n", "error")
            messagebox.showinfo("Thất bại", f"Không tìm được lời giải sau {visited_nodes} lần duyệt.")
        else:
            self.is_animating = True 
            self.btn_search.config(state=tk.DISABLED) 
            self.btn_new.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)
            self.btn_cancel.config(state=tk.NORMAL)
            
            self.log(f"> Tìm kiếm hoàn tất! Bắt đầu in chuỗi mô phỏng:\n", "success")
            self.log("=" * 45 + "\n\n")
            self.animate_steps(result, 0, visited_nodes)

    def update_grid_ui(self, matrix):
        """Cập nhật các ô Entry trên giao diện khớp với ma trận hiện tại"""
        for i in range(3):
            for j in range(3):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(matrix[i][j]))
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()