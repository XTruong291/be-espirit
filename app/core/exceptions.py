from typing import Any, Optional


class BaseAppException(Exception):
    """Lớp Exception cơ sở cho toàn bộ ứng dụng."""
    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "Đã xảy ra lỗi hệ thống."

    def __init__(self, message: Optional[str] = None, details: Any = None):
        if message:
            self.message = message
        self.details = details
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    """Lỗi không tìm thấy tài nguyên (HTTP 404)."""
    status_code: int = 404
    error_code: str = "NOT_FOUND"
    message: str = "Tài nguyên không tìm thấy."


class BadRequestException(BaseAppException):
    """Lỗi yêu cầu không hợp lệ (HTTP 400)."""
    status_code: int = 400
    error_code: str = "BAD_REQUEST"
    message: str = "Yêu cầu không hợp lệ."


class UnauthorizedException(BaseAppException):
    """Lỗi không có quyền xác thực (HTTP 401)."""
    status_code: int = 401
    error_code: str = "UNAUTHORIZED"
    message: str = "Không được phép truy cập."


class ForbiddenException(BaseAppException):
    """Lỗi bị cấm truy cập tài nguyên (HTTP 403)."""
    status_code: int = 403
    error_code: str = "FORBIDDEN"
    message: str = "Bị cấm truy cập tài nguyên."


class DuplicateException(BaseAppException):
    """Lỗi trùng lặp tài nguyên (HTTP 400)."""
    status_code: int = 400
    error_code: str = "DUPLICATE_RESOURCE"
    message: str = "Tài nguyên đã tồn tại."
