# Codebase



---

## 🛠️ Cấu trúc thư mục dự án

```text
fastapi-app/
├── app/
│   ├── core/
│   │   ├── config.py       # Cấu hình nạp biến môi trường từ .env
│   │   └── database.py     # Thiết lập SQLAlchemy 2.0 AsyncEngine và dependency get_db
│   └── main.py             # Entrypoint của FastAPI với các router và endpoint mẫu
├── .env                    # Lưu cấu hình và credentials kết nối local (bị gitignore)
├── .env.example            # Bản mẫu cấu hình cho các thành viên khác
├── .gitignore              # Bỏ qua các file không cần thiết khi push Git
├── requirements.txt        # Danh sách thư viện phụ thuộc
└── README.md               # Hướng dẫn này
```

---

## Hướng dẫn cài đặt và chạy dự án (Local Setup)

Các thành viên dự án có thể làm theo các bước dưới đây để chạy dự án lần đầu:

### Bước 1: Yêu cầu chuẩn bị
* Máy tính đã cài đặt **Python >= 3.10**.
* Đang chạy MySQL Server (Ví dụ: Bật **Apache** và **MySQL** trên **XAMPP Control Panel** hoặc cài đặt MySQL Server local chạy ở port `3306`).
* Tạo sẵn một database trống trên MySQL (Ví dụ: tên là `test_db`).

---

### Bước 2: Thiết lập môi trường ảo (Virtual Environment)
Mở terminal tại thư mục gốc của dự án (`fastapi-app/`) và chạy lệnh:

**Trên Windows (cmd/PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Trên macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Bước 3: Cài đặt các thư viện cần thiết
Khi môi trường ảo đã được kích hoạt (có ký hiệu `(venv)` ở đầu dòng lệnh), tiến hành cài đặt thư viện:
```bash
pip install -r requirements.txt
```

---

### Bước 4: Tạo cấu hình file môi trường `.env`
1. Tạo một bản sao từ file `.env.example` đặt tên là `.env`:
   ```bash
   cp .env.example .env
   ```
2. Mở file `.env` vừa tạo và chỉnh sửa các tham số kết nối database phù hợp với môi trường local của bạn (Mặc định XAMPP không có mật khẩu root):
   ```env
   MYSQL_USER=root
   MYSQL_PASSWORD=
   MYSQL_SERVER=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_DB=test_db
   ```

---

### Bước 5: Khởi động ứng dụng
Khởi chạy Server phát triển local sử dụng Uvicorn:
```bash
uvicorn app.main:app --reload
```

Sau khi chạy thành công, server sẽ chạy tại địa chỉ: [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Danh sách Endpoints kiểm tra

* **Root Endpoint**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) - Kiểm tra xem Backend API có đang hoạt động hay không.
* **DB-Check Endpoint**: [http://127.0.0.1:8000/db-check](http://127.0.0.1:8000/db-check) - Kết nối thực tế tới MySQL Database để kiểm tra trạng thái hoạt động của DB connection. 
  * Nếu thành công: Trả về `{"database": "connected"}`.
  * Nếu thất bại: Trả về lỗi `500` kèm thông báo chi tiết lỗi kết nối.
