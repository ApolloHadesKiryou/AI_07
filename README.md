# AI Search Algorithms - 8-Puzzle Solver

## Giới thiệu

Repository này lưu trữ mã nguồn cho dự án môn học **Trí tuệ nhân tạo (Artificial Intelligence)**. Dự án tập trung vào việc cài đặt, minh họa và so sánh các thuật toán tìm kiếm phổ biến trong AI thông qua bài toán **8-Puzzle**, kết hợp với giao diện đồ họa trực quan (GUI) hiển thị quá trình tìm kiếm và các bước giải chi tiết.

### Mục tiêu của dự án:
* Cài đặt và mô phỏng trực quan các thuật toán tìm kiếm AI trên cùng một bài toán cơ sở.
* So sánh hiệu năng thực tế (số bước đi, số trạng thái đã mở rộng/duyệt) giữa các giải thuật.
* Tổ chức mã nguồn khoa học, tự chủ và hỗ trợ chạy độc lập từ một tệp duy nhất để thuận tiện cho việc đánh giá.

---

## Các nhóm thuật toán hỗ trợ (Tổng số 23 thuật toán)

Chương trình tích hợp toàn bộ các nhóm thuật toán sau:

### 1. Nhóm Tìm kiếm mù (Uninformed Search)
* Breadth-First Search (BFS)
* Depth-First Search (DFS)
* Iterative Deepening Search (IDS)
* Uniform Cost Search (UCS)

### 2. Nhóm Tìm kiếm có thông tin (Informed Search)
* Greedy Best-First Search
* A* Search
* Iterative Deepening A* (IDA*)

### 3. Nhóm Tìm kiếm tối ưu cục bộ (Local Search)
* Hill Climbing (Simple, Steepest-Ascent, Stochastic, Random Restart)
* Simulated Annealing
* Local Beam Search

### 4. Nhóm Tìm kiếm đối kháng & Xác suất (Adversarial & Expectimax Search)
* Minimax
* Alpha-Beta Pruning
* Expectimax

### 5. Nhóm Bài toán thỏa mãn ràng buộc (CSP)
* Backtracking
* Forward Checking
* Arc Consistency (AC-3)
* Min-Conflicts

### 6. Nhóm Môi trường mù & Đồ thị đặc biệt
* Belief State Search (Belief A*)
* AND-OR Graph Search
* Tác nhân phản xạ (Simple Reflex, Model-based Reflex)

---

## Cấu trúc thư mục thực tế

```text
Tri tue nhan tao/
│
├── main.py                     # Chương trình chính tích hợp giao diện GUI và 23 thuật toán (chạy độc lập)
│
├── uniformed_search/           # Các thuật toán tìm kiếm không thông tin (BFS, DFS, IDS, UCS)
│   ├── bfs.py
│   ├── dfs.py
│   ├── ids.py
│   └── ucs.py
│
├── informed_search/            # Các thuật toán tìm kiếm có thông tin (Greedy, A*, IDA*)
│   ├── a_star.py
│   ├── greedy_search.py
│   └── ida_star.py
│
├── local_search/               # Các thuật toán tìm kiếm cục bộ và tối ưu hóa
│   ├── simple_hill_climbing.py
│   ├── steepest_hill_climbing.py
│   ├── stochastic_hill_climbing.py
│   ├── random_restart.py
│   ├── simulated_annealing.py
│   └── local_beam.py
│
├── adversarial_search/         # Các thuật toán đối kháng và trò chơi (Minimax, Alpha-Beta, Expectimax)
│   ├── minimax.py
│   ├── alpha_beta.py
│   └── expectimax.py
│
├── csp/                        # Các thuật toán thỏa mãn ràng buộc
│   ├── backtracking.py
│   ├── forward_checking.py
│   ├── ac3.py
│   └── min_conflicts.py
│
├── belief_search/              # Belief State và AND-OR Search
│   ├── belief_state_astar.py
│   └── and_or_graph_search.py
│
├── reflex_agents/              # Tác nhân phản xạ đơn giản và có mô hình
│   ├── simple_reflex.py
│   └── model_based_reflex.py
│
├── common/                     # Tiện ích chung cho 8-Puzzle
│   ├── node.py
│   ├── puzzle_utils.py
│   └── heuristic.py
│
├── reports/                    # Báo cáo thực hành từng buổi học
│   └── ...
│
└── README.md
```

---

## Công nghệ sử dụng

* **Ngôn ngữ**: Python 3
* **Giao diện**: Thư viện Tkinter (GUI mặc định của Python)
* **Cấu trúc dữ liệu**: Queue, Priority Queue, Deque, Dict/Set Hashable

---

## Bài toán minh họa

Dự án sử dụng bài toán **8-Puzzle** làm mô hình mẫu. Mục tiêu là đưa ma trận 3x3 ban đầu về cấu hình đích bằng các bước trượt ô trống (ký hiệu là `0`):

```text
Trạng thái đích:
1  2  3
4  5  6
7  8  0
```

---

## Hướng dẫn sử dụng

### Chạy chương trình chính (GUI tích hợp đầy đủ):
Để khởi chạy ứng dụng GUI mô phỏng trực quan tất cả 23 thuật toán trên, chỉ cần thực thi duy nhất tệp `main.py`:
```bash
python main.py
```
*Lưu ý: Tệp `main.py` được thiết kế tự chủ hoàn toàn, không phụ thuộc vào bất kỳ tệp cục bộ nào ngoài các thư viện mặc định của Python.*
