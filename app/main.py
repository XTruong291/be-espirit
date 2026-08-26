from fastapi import FastAPI, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy import text
from app.core.database import get_db
from app.api.v1.endpoints.auth import router as auth_router
from app.api.deps import get_current_user  # Import hàm xác thực người dùng
from app.models.user import User            # Import model User

app = FastAPI(
    title="BE-Espirit API",
    description="Backend API services for BE-Espirit"
)

# 1. Đăng ký các router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])

# 2. Trang chủ Welcome
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to BE-Espirit API Services"}

# 3. Endpoint kiểm tra kết nối Database (Đã khóa - Yêu cầu đăng nhập)
@app.get("/db-check", tags=["Health Check"])
async def db_check(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Khóa API bằng Bearer Token
):
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        return {"database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )