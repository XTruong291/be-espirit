# Sử dụng python:3.11-slim làm base image tối ưu
FROM python:3.11-slim

# Thiết lập biến môi trường ngăn Python ghi file bytecode (.pyc) và buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt dependencies hệ thống cần thiết để build các python package (aiomysql/cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt dependencies Python trước để tận dụng cache layer của Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào thư mục làm việc
COPY . .

# Đảm bảo file entrypoint.sh có quyền thực thi trong container
RUN chmod +x entrypoint.sh

# Cấu hình cổng chạy mặc định của container
EXPOSE 8000

# Chỉ định Entrypoint script chạy khởi động
ENTRYPOINT ["./entrypoint.sh"]
