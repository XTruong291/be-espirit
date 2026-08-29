# PROJECT RULES & ARCHITECTURE GUIDELINES

## 1. Core Stack & Versions
- Language & Framework: Python / FastAPI
- Database: MySQL
- Package Manager: pip

## 2. Architecture & Code Boundaries
- Kiến trúc áp dụng: Layered Architecture
- Không tự ý thêm thư viện mới (dependency) khi chưa có sự đồng ý.

## 3. Workflow Protocol (Bắt buộc với Agent)
- KHÔNG BAO GIỜ tự ý sửa/xóa nhiều file cùng lúc khi chưa trình bày Kế hoạch (Action Plan).
- Trước khi thực hiện: Liệt kê danh sách file tác động + lý do.
- Sau khi thực hiện: Tự chạy lệnh test/lint và báo cáo kết quả.