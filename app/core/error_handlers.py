from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import BaseAppException


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Bắt và định dạng toàn bộ Custom Business Exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Bắt và định dạng lỗi kiểm tra dữ liệu của Pydantic (HTTP 422)."""
    details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []))
        details.append({
            "field": field,
            "issue": error.get("msg", ""),
            "type": error.get("type", "")
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Dữ liệu yêu cầu không hợp lệ.",
            "details": details
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Bắt và định dạng lỗi cơ sở dữ liệu SQLAlchemy."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "DATABASE_ERROR",
            "message": "Lỗi truy vấn cơ sở dữ liệu.",
            "details": str(exc)
        }
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Đồng nhất hóa định dạng lỗi mặc định của Starlette/FastAPI (như 404 Route Not Found)."""
    error_code_map = {
        404: "ROUTE_NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN"
    }
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": error_code,
            "message": exc.detail,
            "details": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Bắt các lỗi hệ thống bất ngờ khác (HTTP 500)."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "Đã xảy ra lỗi hệ thống bất ngờ.",
            "details": str(exc)
        }
    )
