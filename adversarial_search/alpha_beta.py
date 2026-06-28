import copy
from common.node import Node
from common.puzzle_utils import (
    check_done,
    possible_move,
    do_action,
    matrix_to_tuple,
    remove_repetition
)
from common.heuristic import calc_manhattan

def utility(state):
    """
    Hàm tính giá trị tiện ích (Utility Function) của một trạng thái bảng.
    - Đích hoàn hảo được chấm 1000 điểm.
    - Các trạng thái khác được tính bằng số âm của tổng khoảng cách Manhattan.
    """
    if check_done(state):
        return 1000
    return -calc_manhattan(state)

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
        return utility(state)
        
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
        return utility(state)
        
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
