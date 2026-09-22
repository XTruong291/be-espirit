from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.user import (
    SendOTPRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VerifyOTPRequest,
)
from app.services.auth_service import AuthService


# Schema phản hồi chung cho các API thông báo
class MessageResponse(BaseModel):
    message: str
    status: str = "success"


router = APIRouter()


# 1. API PUBLIC: Đăng ký tài khoản mới (Yêu cầu Email đã verify OTP)
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Router nhận DTO đầu vào -> Chuyển giao logic xử lý cho AuthService -> Trả về UserResponse.

    Lưu ý: Email trong payload bắt buộc phải trải qua bước xác thực OTP thành công trước đó.
    """
    return await auth_service.register_user(payload)


# 2. API PUBLIC: Đăng nhập hệ thống
@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập hệ thống",
)
async def login(
    credentials: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Router nhận credentials -> Chuyển giao xác thực cho AuthService -> Trả về Token."""
    return await auth_service.authenticate_user(credentials)


# 3. API PRIVATE: Lấy thông tin tài khoản đang đăng nhập
@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin tài khoản đang đăng nhập",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """API này được khóa bằng Depends(get_current_user).

    Chỉ khi truyền đúng Bearer Token hợp lệ ở Header mới xem được dữ liệu.
    """
    return current_user


# 4. API PUBLIC: Gửi mã OTP qua Gmail
@router.post(
    "/send-otp",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Gửi mã OTP qua Gmail",
)
async def send_otp(
    payload: SendOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Tạo mã OTP 6 số và gửi qua Gmail.

    Kiểm tra Email hợp lệ (MX record) và áp dụng cooldown 60s chống spam.
    """
    result = await auth_service.send_otp(payload.email)
    return MessageResponse(message=result["message"])


# 5. API PUBLIC: Xác thực mã OTP
@router.post(
    "/verify-otp",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Xác thực mã OTP",
)
async def verify_otp(
    payload: VerifyOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Xác nhận mã OTP do người dùng nhập.

    Nếu chính xác và trong hạn 5 phút, đánh dấu email đã được xác thực thành công.
    """
    result = await auth_service.verify_otp(payload.email, payload.code)
    return MessageResponse(
        message=result["message"],
        status=result.get("status", "success"),
    )