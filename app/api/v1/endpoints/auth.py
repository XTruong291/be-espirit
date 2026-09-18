from fastapi import APIRouter, Depends, status

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

router = APIRouter()


# 1. API PUBLIC: Đăng ký tài khoản mới
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
    return await auth_service.register_user(payload)


# 2. API PUBLIC: Đăng nhập hệ thống
@router.post("/login", response_model=TokenResponse, summary="Đăng nhập hệ thống")
async def login(
    credentials: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.authenticate_user(credentials)


# 3. API PRIVATE: Lấy thông tin tài khoản đang đăng nhập
@router.get(
    "/me", response_model=UserResponse, summary="Lấy thông tin tài khoản"
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# 4. API PUBLIC: Gửi mã OTP qua Gmail
@router.post("/send-otp", summary="Gửi mã OTP qua Gmail")
async def send_otp(
    payload: SendOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.send_otp(payload.email)


# 5. API PUBLIC: Xác thực mã OTP
@router.post("/verify-otp", summary="Xác thực mã OTP")
async def verify_otp(
    payload: VerifyOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.verify_otp(payload.email, payload.code)