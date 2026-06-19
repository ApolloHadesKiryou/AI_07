# AI_07 - Artificial Intelligence Search Algorithms

## Giới thiệu

**AI_07** là repository phục vụ cho môn học **Trí tuệ nhân tạo (Artificial Intelligence)** của lớp **AI_07**.

Dự án tập trung vào việc cài đặt, minh họa và so sánh các thuật toán tìm kiếm thường gặp trong AI thông qua bài toán **8-Puzzle**, kết hợp với giao diện đồ họa giúp trực quan hóa quá trình tìm kiếm và lời giải.

Repository được xây dựng nhằm mục đích:

* Học tập và nghiên cứu các thuật toán tìm kiếm AI.
* Minh họa hoạt động của từng thuật toán trên cùng một bài toán.
* So sánh hiệu năng giữa các thuật toán.
* Lưu trữ báo cáo và tài liệu thực hành theo từng buổi học.

---

## Nội dung repository

### 1. Chương trình tổng hợp

Thư mục chính chứa chương trình tích hợp:

* Giao diện đồ họa (GUI).
* Bài toán 8-Puzzle.
* Danh sách các thuật toán tìm kiếm.
* Hiển thị đường đi lời giải.
* Thống kê số bước, số node đã duyệt và thời gian thực thi.

---

### 2. Các nhóm thuật toán

Các thuật toán được tổ chức theo từng nhóm để thuận tiện cho việc học tập và nghiên cứu.

#### Nhóm Uninformed Search (Tìm kiếm không có thông tin)

* Breadth First Search (BFS)
* Depth First Search (DFS)
* Iterative Deepening DFS (IDS)
* Uniform Cost Search (UCS)

#### Nhóm Informed Search (Tìm kiếm có thông tin)

* Greedy Best First Search
* A*
* Iterative Deepening A* (IDA*)

#### Nhóm Local Search

* Hill Climbing
* Simulated Annealing
* Local Beam Search

#### Nhóm Adversarial Search

* Minimax
* Alpha-Beta Pruning
* Expectimax

#### Nhóm CSP (Constraint Satisfaction Problem)

* Backtracking Search
* Forward Checking
* AC-3
* Min-Conflicts

#### Nhóm Belief State / AND-OR Search

* AND-OR Graph Search
* Belief State Search

---

### 3. Báo cáo

Repository lưu trữ các báo cáo thực hành theo từng buổi học:

* Báo cáo lý thuyết.
* Mô tả thuật toán.

---

## Cấu trúc thư mục dự kiến

```text
AI_07/
│
├── 24110337_LyDongThinh : file main gồm code tổng
│
├── uninformed_search/
│   └── Các thuật toán tìm kiếm không thông tin
│
├── informed_search/
│   └── Các thuật toán tìm kiếm có thông tin
│
├── local_search/
│   └── Các thuật toán tìm kiếm cục bộ
│
├── adversarial_search/
│   └── Minimax, Alpha-Beta, Expectimax
│
├── csp/
│   └── Constraint Satisfaction Problems
│
├── belief_search/
│   └── Belief State và AND-OR Search
│
├── reports/
│   ├── Week_2_Session_1
│   ├── Week_2_Session_2
│   └── ...
│
└── README.md
```

---

## Công nghệ sử dụng

* Python 3
* Tkinter (GUI)
* Queue / Priority Queue
* Các cấu trúc dữ liệu phục vụ AI Search

---

## Bài toán minh họa

Toàn bộ thuật toán được minh họa trên bài toán **8-Puzzle**.

Mục tiêu là đưa trạng thái ban đầu về trạng thái đích bằng cách di chuyển ô trống theo các hướng hợp lệ:

```text
Trạng thái đích:

1 2 3
4 5 6
7 8 0
```

Trong đó `0` biểu diễn ô trống.

---

## Mục tiêu học tập

Thông qua dự án này, sinh viên có thể:

* Hiểu nguyên lý hoạt động của các thuật toán tìm kiếm AI.
* So sánh ưu nhược điểm của từng thuật toán.
* Thực hành xây dựng ứng dụng AI đơn giản bằng Python.
* Nắm được cách biểu diễn trạng thái và không gian tìm kiếm.
* Rèn luyện kỹ năng tổ chức dự án và viết báo cáo kỹ thuật.

---

## Thành viên

Repository được phát triển và sử dụng cho mục đích học tập của lớp **AI_07**.
