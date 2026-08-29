#!/bin/sh

# Ngắt script nếu gặp bất kỳ lỗi nào
set -e

echo "Chạy Database Migrations bằng Alembic..."
alembic upgrade head

echo "Khởi động FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
