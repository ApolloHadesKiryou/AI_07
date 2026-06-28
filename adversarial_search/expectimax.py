import copy
import random
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
    Hàm giá trị tiện ích (Utility Function) của một trạng thái bảng.
    - Đích hoàn hảo được chấm 1000 điểm.
    - Các trạng thái khác được tính bằng số âm của tổng khoảng cách Manhattan.
    """
    if check_done(state):
        return 1000
    return -calc_manhattan(state)

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
        return utility(state)
        
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
        return utility(state)
        
    moves = possible_move(state)
    if not moves:
        return utility(state)
        
    total_val = 0
    # Tính xác suất phân bố đều cho mỗi nước đi hợp lệ
    prob = 1.0 / len(moves)
    for move in moves:
        next_state = do_action(state, move)
        # Tích lũy giá trị kỳ vọng (giá trị * xác suất)
        total_val += prob * max_value_exp(next_state, depth - 1, visited_nodes)
    return total_val

def expectimax_search(initial_state):
    """
    Mô phỏng trò chơi 8-puzzle giữa MAX (Tác nhân AI) và môi trường có tính ngẫu nhiên (Chance).
    - Agent tính toán nước đi tốt nhất bằng cách giả định môi trường phản ứng ngẫu nhiên (Expectimax).
    - Ở lượt của môi trường, một hướng đi ngẫu nhiên hợp lệ sẽ được chọn ngẫu nhiên hoàn toàn.
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
        best_move = expectimax_decision(current_state, depth=3, visited_nodes=visited_nodes)
        if not best_move:
            break
            
        next_state = do_action(current_state, best_move)
        
        # Tránh trạng thái đã đi qua nếu có thể
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
            
        # --- Lượt của Môi Trường (Chance) ---
        moves = possible_move(current_state)
        valid_moves = [m for m in moves if not remove_repetition(m, best_move)]
        if not valid_moves:
            valid_moves = moves
            
        # Chọn ngẫu nhiên hoàn toàn một hướng đi hợp lệ
        chance_move = random.choice(valid_moves)
        current_state = do_action(current_state, chance_move)
        executed_states.add(matrix_to_tuple(current_state))
        current_node = Node(current_state, current_node, f"{chance_move} (Chance)", step + 1)
        history.append(current_node)
        step += 1
        
    return history, visited_nodes[0]
