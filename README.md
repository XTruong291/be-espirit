# BE-Espirit - Backend API

> **BE-Espirit** là hệ thống Backend API phục vụ cho nền tảng Trợ lý Tâm linh & Thờ cúng (E-Spirit), được xây dựng trên nền tảng **FastAPI**, **SQLAlchemy 2.0 (Async)** và **MySQL**. Dự án cung cấp hệ thống xác thực người dùng, phân quyền, quản lý hội thoại/chatbot thông minh, tiện ích Lịch Âm - Dương theo thiên văn Việt Nam và kiến trúc mở sẵn sàng tích hợp các mô hình AI/RAG thực tế.

---

## 🚀 Công nghệ sử dụng (Tech Stack)

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) - Hiệu năng cao, hỗ trợ bất đồng bộ (Asynchronous) hoàn chỉnh.
- **ORM & Database Access**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) kết hợp [aiomysql](https://github.com/aio-libs/aiomysql) cho truy vấn MySQL Non-blocking.
- **Data Validation & Serialization**: [Pydantic V2](https://docs.pydantic.dev/) & `pydantic-settings`.
- **Database Migration**: [Alembic](https://alembic.sqlalchemy.org/) - Tự động hóa cập nhật lược đồ cơ sở dữ liệu.
- **Bảo mật & Xác thực**: [PyJWT](https://pyjwt.readthedocs.io/) (JSON Web Tokens) & [bcrypt](https://pypi.org/project/bcrypt/) (băm mật khẩu).
- **Thuật toán Thiên văn**: Cài đặt trực tiếp thuật toán Hồ Ngọc Đức cho Âm lịch Việt Nam (UTC+7 - `Asia/Ho_Chi_Minh`), tính toán thuần túy trên RAM.
- **Containerization & Deployment**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) (MySQL 8.0, phpMyAdmin, FastAPI Service).

---

## 📁 Cấu trúc thư mục (Project Architecture)

Dự án áp dụng mô hình kiến trúc phân lớp chuẩn (Layered Architecture / Clean Architecture), tách biệt rõ ràng giữa Data Access, Business Logic, Utilities và API Controller:

```text
fastapi-app/
├── alembic/                         # Cấu hình và các file migration lịch sử cơ sở dữ liệu
│   ├── versions/                    # Các file migration (users, chat_sessions, chat_messages, ...)
│   └── env.py                       # Cấu hình môi trường chạy migration bất đồng bộ
├── app/
│   ├── api/                         # Tầng Router & Dependency Injection
│   │   ├── deps.py                  # Dependencies (Database session, Auth, Service & Repository providers)
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py          # API Đăng ký, Đăng nhập, Token
│   │           ├── users.py         # API Quản lý thông tin cá nhân & Admin quản lý users
│   │           ├── chat.py          # API Quản lý phiên chat (Sessions) & Tin nhắn (Messages)
│   │           └── calendar.py      # API Lịch Âm - Dương, Giờ Hoàng Đạo, Chuyển đổi 2 chiều
│   ├── core/                        # Cấu hình nền tảng ứng dụng
│   │   ├── config.py                # Nạp biến môi trường từ .env
│   │   ├── database.py              # Async Engine, sessionmaker và get_db generator
│   │   ├── exceptions.py            # Hệ thống Custom Exceptions (BaseAppException, NotFound, Forbidden, ...)
│   │   └── error_handlers.py        # Global Exception Handlers chuẩn hóa JSON Response
│   ├── models/                      # SQLAlchemy ORM Models
│   │   ├── user.py                  # Model User & Base Declarative
│   │   └── chat.py                  # Model ChatSession & ChatMessage (Cascade delete, ForeignKeys, Indexes)
│   ├── repositories/                # Tầng Data Access Layer (CRUD cơ sở dữ liệu)
│   │   ├── user_repository.py       # Truy vấn bảng users
│   │   └── chat_repository.py       # Truy vấn bảng chat_sessions và chat_messages
│   ├── schemas/                     # Pydantic V2 Schemas (Data Transfer Objects - DTOs)
│   │   ├── user.py                  # Schemas cho User Request / Response
│   │   ├── chat.py                  # Schemas cho Chat Session & Message Request / Response
│   │   └── calendar.py              # Schemas cho Lịch Âm - Dương & Giờ Hoàng Đạo
│   ├── services/                    # Tầng Nghiệp vụ (Business Logic Layer)
│   │   ├── auth_service.py          # Logic xác thực, mã hóa mật khẩu, sinh/giải mã JWT token
│   │   ├── user_service.py          # Logic quản lý tài khoản người dùng
│   │   ├── ai_service.py            # Mock AI Service giả lập câu trả lời tâm linh/thờ cúng
│   │   └── chat_service.py          # Logic phiên chat, kiểm tra quyền sở hữu, an toàn transaction
│   ├── utils/                       # Các module tiện ích dùng chung
│   │   └── lunar_calendar.py        # Core Engine thuật toán Âm Dương Hồ Ngọc Đức (Múi giờ Asia/Ho_Chi_Minh)
│   └── main.py                      # FastAPI App Entrypoint, CORS, Exception Handlers & Routers
├── .env                             # File biến môi trường thực tế (bị gitignore)
├── .env.example                     # File mẫu biến môi trường
├── .dockerignore                    # Danh sách file loại trừ khi build Docker
├── Dockerfile                       # Cấu hình đóng gói ứng dụng (python:3.11-slim)
├── docker-compose.yaml              # Cấu hình chạy cụm Services (API, MySQL 8.0, phpMyAdmin)
├── entrypoint.sh                    # Script tự động chạy migration trước khi khởi chạy server
├── requirements.txt                 # Danh sách các thư viện Python
└── README.md                        # Tài liệu hướng dẫn dự án
```

---

## ✨ Các tính năng chính (Key Features)

### 1. Xác thực & Phân quyền (Authentication & Authorization)
- Đăng ký (`Register`), Đăng nhập (`Login`) cấp `access_token` định dạng JWT Bearer.
- Phân quyền theo vai trò (`user`, `admin`), bảo vệ các tài nguyên nhạy cảm thông qua `RoleChecker`.
- Đổi thông tin cá nhân (username, email, password) và Admin quản lý vai trò của người dùng.

### 2. Quản lý Hội thoại / Trợ lý Tâm linh (Chatbot & Conversations)
- **Quản lý Phiên trò chuyện (Chat Sessions)**: Tạo phiên mới, lấy danh sách theo thời gian cập nhật mới nhất, xóa phiên.
- **Bảo mật sở hữu (Anti-IDOR)**: Kiểm tra quyền sở hữu phiên chat; trả về `404 Not Found` nếu truy cập phiên của người khác để chống dò quét ID.
- **Tự động đặt tiêu đề**: Tự động trích xuất 30 ký tự đầu của tin nhắn đầu tiên để cập nhật tiêu đề cho phiên trò chuyện.
- **An toàn Transaction**: Lưu và cam kết (commit) tin nhắn của người dùng trước khi gọi AI service nhằm tránh mất dữ liệu nếu AI gặp sự cố.
- **Mock AI Service (`AIService`)**: Phản hồi giả lập các chủ đề tâm linh/thờ cúng (văn khấn, thắp hương, mâm cúng, phong thủy bàn thờ), thiết kế độc lập sẵn sàng tích hợp LLM/RAG thực tế.

### 3. Lịch Âm - Dương & Tiện ích Ngày Lễ Tâm Linh (Lunar Calendar)
- **Thuật toán thiên văn Hồ Ngọc Đức (UTC+7)**: Tính toán thuần túy trên RAM với độ chính xác tuyệt đối, không phụ thuộc API bên thứ 3.
- **Múi giờ Việt Nam (`Asia/Ho_Chi_Minh`)**: Đảm bảo đồng nhất thời gian thực tế ngay cả khi container Docker chạy múi giờ UTC.
- **Chuyển đổi 2 chiều**: Chuyển đổi linh hoạt giữa Dương lịch và Âm lịch (hỗ trợ cờ tháng nhuận).
- **Can Chi & Giờ Hoàng Đạo**: Tính toán Can Chi Năm, Tháng, Ngày và 12 canh giờ âm lịch (Giờ Tý: 23:00 - 01:00) phân loại 6 giờ Hoàng Đạo và 6 giờ Hắc Đạo kèm tên sao trực nhật.
- **Gợi ý Tâm linh & Sự kiện**: Tự động nhận diện ngày Mồng Một, ngày Rằm, các ngày lễ truyền thống (Tết, Rằm tháng Giêng, Hàn Thực, Phật Đản, Đoan Ngọ, Vu Lan, Trung Thu, Táo Quân, Tất Niên) kèm lời nhắc tâm linh thích hợp.
- **Tối ưu hiệu năng**: API Lịch Tháng (`/month`) lặp tính 30 ngày thuần trên RAM với latency dưới **1ms**.
- **Tích hợp Chatbot AI**: Cung cấp helper `get_lunar_context_for_prompt()` bơm sẵn ngày âm dương hiện tại vào System Prompt của Chatbot AI.

### 4. Cấu hình & Trải nghiệm lập trình
- **CORS Middleware**: Mở rộng cho phép Frontend / Mobile App kết nối dễ dàng.
- **Chuẩn hóa lỗi (Global Error Format)**: Mọi lỗi nghiệp vụ và hệ thống đều trả về cấu trúc JSON đồng nhất `{ "success": false, "error_code": "...", "message": "..." }`.
- **API Documentation**: Tự động sinh Swagger UI tại `/docs` và ReDoc tại `/redoc`.
- **Database Healthcheck**: Endpoint `/db-check` kiểm tra kết nối trực tiếp đến MySQL.

---

## 🛠️ Hướng dẫn cài đặt & Khởi chạy

### Cách 1: Khởi chạy nhanh bằng Docker Compose (Khuyến nghị)

Docker Compose sẽ tự động khởi tạo MySQL 8.0, phpMyAdmin, tự động chạy migration Alembic và bật server API.

1. **Chuẩn bị file `.env`**:
   ```bash
   cp .env.example .env
   ```
2. **Khởi chạy bằng Docker Compose**:
   ```bash
   docker compose up --build -d
   ```
3. **Truy cập các dịch vụ**:
   - **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **phpMyAdmin**: [http://localhost:8080](http://localhost:8080) (User: `root`, Password: `123456`)
   - **Database Check**: [http://localhost:8000/db-check](http://localhost:8000/db-check)

---

### Cách 2: Khởi chạy trực tiếp trên môi trường Local (Python Virtualenv)

#### Bước 1: Yêu cầu chuẩn bị
- **Python >= 3.10**
- **MySQL Server** (qua XAMPP, MySQL Installer hoặc Docker MySQL) chạy tại port `3306`.
- Tạo sẵn một cơ sở dữ liệu trống trên MySQL (ví dụ: `e_spirit_db` hoặc `test_db`).

#### Bước 2: Tạo môi trường ảo & cài đặt thư viện
- **Trên Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```
- **Trên macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

#### Bước 3: Cấu hình file `.env`
Tạo file `.env` từ `.env.example` và cập nhật thông tin kết nối MySQL:
```env
MYSQL_USER=root
MYSQL_PASSWORD=[PASSWORD]
MYSQL_SERVER=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=e_spirit_db
SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
```

#### Bước 4: Chạy Database Migration
Áp dụng các bảng dữ liệu mới nhất vào cơ sở dữ liệu:
```bash
alembic upgrade head
```

#### Bước 5: Khởi động Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Truy cập tài liệu API tại: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## 📌 Danh sách API Endpoints chính

| Nhóm | Method | Endpoint | Mô tả | Yêu cầu Auth |
| :--- | :--- | :--- | :--- | :---: |
| **System** | `GET` | `/db-check` | Kiểm tra trạng thái kết nối MySQL Database | Public |
| **Auth** | `POST` | `/api/v1/auth/register` | Đăng ký tài khoản người dùng mới | Public |
| **Auth** | `POST` | `/api/v1/auth/login` | Đăng nhập và nhận JWT Access Token | Public |
| **Users** | `GET` | `/api/v1/users/me` | Lấy thông tin tài khoản đang đăng nhập | Bearer Token |
| **Users** | `PUT` | `/api/v1/users/me` | Cập nhật thông tin cá nhân (username, email, pass) | Bearer Token |
| **Users** | `GET` | `/api/v1/users/` | Danh sách tất cả người dùng (Phân trang) | Admin |
| **Users** | `PUT` | `/api/v1/users/{user_id}` | Cập nhật thông tin & vai trò người dùng bất kỳ | Admin |
| **Chat** | `GET` | `/api/v1/chat/sessions` | Lấy danh sách các phiên chat của user | Bearer Token |
| **Chat** | `POST` | `/api/v1/chat/sessions` | Tạo một phiên trò chuyện mới | Bearer Token |
| **Chat** | `GET` | `/api/v1/chat/sessions/{id}/messages` | Lấy toàn bộ lịch sử tin nhắn trong phiên chat | Bearer Token |
| **Chat** | `POST` | `/api/v1/chat/sessions/{id}/messages` | Gửi tin nhắn và nhận phản hồi từ AI Assistant | Bearer Token |
| **Chat** | `DELETE` | `/api/v1/chat/sessions/{id}` | Xóa phiên trò chuyện kèm toàn bộ tin nhắn | Bearer Token |
| **Calendar** | `GET` | `/api/v1/calendar/today` | Lấy chi tiết âm - dương ngày hiện tại (múi giờ UTC+7) | Public |
| **Calendar** | `GET` | `/api/v1/calendar/convert-solar` | Chuyển đổi ngày Dương lịch tùy chọn sang Âm lịch | Public |
| **Calendar** | `GET` | `/api/v1/calendar/convert-lunar` | Chuyển đổi ngày Âm lịch tùy chọn sang Dương lịch | Public |
| **Calendar** | `GET` | `/api/v1/calendar/month` | Dữ liệu lịch toàn bộ một tháng cho Calendar Grid | Public |
| **Calendar** | `GET` | `/api/v1/calendar/auspicious-hours` | Tra cứu chi tiết 12 canh giờ (Hoàng/Hắc Đạo) trong ngày | Public |
