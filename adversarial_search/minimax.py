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
    - Trạng thái Đích (Goal State) được gán giá trị tối đa là 1000 điểm.
    - Các trạng thái trung gian được gán giá trị âm tương đương khoảng cách Manhattan (-Manhattan Distance).
      Điều này khuyến khích thuật toán tìm đường ngắn nhất (do Manhattan distance càng nhỏ thì utility càng gần 0).
    """
    if check_done(state):
        return 1000
    return -calc_manhattan(state)

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
        return utility(state)
    
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
        return utility(state)
        
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
