# Tetris Dual & AI Bot 🧱

Một phiên bản mở rộng của trò chơi xếp hình Tetris kinh điển, được phát triển bằng Python và thư viện đồ họa Pygame. Project được thiết kế linh hoạt với hệ thống tính điểm combo, giao diện mượt mà và đặc biệt là tích hợp Trí tuệ Nhân tạo (A.I) có khả năng tự động chơi ở trình độ cao.

Đồ án môn học - Ngành Trí tuệ nhân tạo - Trường Đại học Công nghệ Thông tin (UIT).

## 🚀 Các tính năng chính (Features)

- **1 Player Mode (Solo):** Chế độ sinh tồn cổ điển. Hệ thống tính điểm theo combo, cơ chế Hold (Giữ gạch), Ghost Piece (Bóng mờ rơi) và Next Queue (Xem trước gạch).
- **2 Player Mode (Local PvP):** Chế độ đối kháng chia đôi màn hình (Split-screen) trên cùng một máy tính. Hai người chơi sử dụng bộ phím độc lập (WASD và Phím Mũi tên).
- **1 VS Bot (PvE):** Người chơi thi đấu trực tiếp với máy. Hệ thống Bot được chia làm 3 cấp độ:
  - **EASY (Tập sự):** Thuật toán Tham lam (Greedy), ưu tiên phá hàng ngay lập tức nhưng cẩu thả với tương lai.
  - **HARD (Cao thủ):** Ứng dụng hàm đánh giá (Heuristic Evaluation) để giữ lưới gọn gàng, phạt nặng các lỗ hổng. Tầm nhìn Lookahead 1 khối.
  - **GOD (Siêu AI):** Thuật toán Beam Search mạnh mẽ. Mở rộng tầm nhìn lên 2 khối (Lookahead = 2, Beam Width = 12) để setup combo và tránh bẫy cục bộ.
- **Hệ thống Media:** Âm thanh SFX và BGM được quản lý tập trung. Hỗ trợ UI thanh trượt âm lượng kéo thả tương tác mượt mà.
