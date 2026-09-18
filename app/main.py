from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.calendar import router as calendar_router
from app.api.v1.endpoints.chat import router as chat_router
from app.api.v1.endpoints.users import router as users_router
from app.core.database import get_db
from app.core.error_handlers import (
    app_exception_handler,
    general_exception_handler,
    sqlalchemy_exception_handler,
    starlette_http_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import BaseAppException

app = FastAPI(
    title="BE-Espirit API", description="Backend API services for BE-Espirit"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Đăng ký các router
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(
    calendar_router, prefix="/api/v1/calendar", tags=["Calendar"]
)

# 2. Đăng ký các Global Exception Handlers
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(
    RequestValidationError, validation_exception_handler
)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(
    StarletteHTTPException, starlette_http_exception_handler
)
app.add_exception_handler(Exception, general_exception_handler)


# 3. Endpoint kiểm tra kết nối Database
@app.get("/db-check", tags=["Connected DB"])
async def db_check(
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        return {"database": "connected"}
    except Exception as e:
        raise BaseAppException(
            message=f"Database connection failed: {str(e)}", details=str(e)
        )