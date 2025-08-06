# Web Automation Tool based on Pixel Coordinates

Đây là một công cụ tự động hóa web được xây dựng bằng Python và Playwright, được thiết kế để thực hiện các tương tác với giao diện web thông qua tọa độ pixel cụ thể thay vì các selector truyền thống.

## Các tính năng chính

- [cite_start]**Điều khiển bằng tọa độ**: Thực hiện click, nhập liệu và các hành động khác tại vị trí (x, y) chính xác. [cite: 6]
- [cite_start]**Chuẩn hóa Viewport**: Tự động đặt kích thước cửa sổ trình duyệt về một kích thước cố định (ví dụ: 1920x1080) để đảm bảo tọa độ nhất quán trên mọi máy tính. [cite: 50, 60]
- [cite_start]**Quản lý phiên bằng Cookie**: Tự động lưu cookie sau khi đăng nhập và tải lại trong các lần chạy tiếp theo để bỏ qua bước đăng nhập. [cite: 18]
- [cite_start]**Quy trình làm việc có thể cấu hình**: Toàn bộ các bước tự động hóa được định nghĩa trong một tệp `workflows/config.yaml` dễ đọc. [cite: 81]
- [cite_start]**Hỗ trợ Headless**: Có khả năng chạy ở chế độ nền (headless) để triển khai trên máy chủ. [cite: 32]

## Hướng dẫn cài đặt

1.  **Clone a repository:**
    ```bash
    git clone <your-repo-url>
    cd web-automation-tool
    ```

2.  **Cài đặt các thư viện Python:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Cài đặt trình duyệt cho Playwright (chỉ cần làm lần đầu):**
    ```bash
    playwright install chromium
    ```

## Cách sử dụng

1.  **Chỉnh sửa tệp cấu hình `workflows/config.yaml`:**
    * Cấu hình `settings` để chọn trình duyệt, chế độ `headless`, và kích thước `viewport` mong muốn.
    * Trong `authentication`, chỉ định đường dẫn đến tệp cookie của bạn.
    * Trong `workflow`, định nghĩa các bước bạn muốn tự động hóa. Tìm tọa độ (x, y) bằng cách sử dụng các công cụ dành cho nhà phát triển của trình duyệt hoặc các tiện ích mở rộng.

2.  **Đặt các tệp cần upload (nếu có):**
    * Đặt các tệp bạn muốn upload vào thư mục `uploads/`.

3.  **Chạy ứng dụng:**
    ```bash
    python main.py
    ```

Hệ thống sẽ khởi chạy trình duyệt, thực hiện các bước trong quy trình, và lưu cookie hoặc ảnh chụp màn hình vào các thư mục tương ứng.

## Giải thích cấu trúc tệp `config.yaml`

- **`settings`**: Cài đặt toàn cục.
  - `headless`: `true` để chạy ẩn, `false` để hiển thị giao diện đồ họa.
  - [cite_start]`viewport`: Kích thước cửa sổ trình duyệt chuẩn để đảm bảo tọa độ chính xác. [cite: 88]
- **`authentication`**: Quản lý phiên.
  - `enabled`: `true` nếu bạn muốn sử dụng chức năng lưu/tải cookie.
  - [cite_start]`profile_path`: Nơi lưu trữ tệp cookie. [cite: 93]
- **`workflow`**: Danh sách các hành động.
  - `action`: Tên của hành động (ví dụ: `goto`, `click`, `type`, `upload`, `wait`, `screenshot`, `save_cookies`).
  - `params`: Các tham số cần thiết cho hành động đó.
  - `description`: Mô tả bước để dễ dàng theo dõi log.