from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
from app.services.auth_service import AuthService

router = APIRouter()


# 1. API PUBLIC: Đăng ký tài khoản mới
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới"
)
async def register(
    payload: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Router nhận DTO đầu vào -> Chuyển giao logic xử lý cho AuthService -> Trả về UserResponse.
    """
    return await auth_service.register_user(payload)


# 2. API PUBLIC: Đăng nhập hệ thống
@router.post("/login", response_model=TokenResponse, summary="Đăng nhập hệ thống")
async def login(
    credentials: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Router nhận credentials -> Chuyển giao xác thực cho AuthService -> Trả về Token.
    """
    return await auth_service.authenticate_user(credentials)


# 3. API PRIVATE: Lấy thông tin tài khoản đang đăng nhập
@router.get("/me", response_model=UserResponse, summary="Lấy thông tin tài khoản đang đăng nhập")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    API này được khóa bằng Depends(get_current_user).
    Chỉ khi truyền đúng Bearer Token hợp lệ ở Header mới xem được dữ liệu.
    """
    return current_user


# 4. API PUBLIC: Quên mật khẩu (Yêu cầu gửi mail khôi phục)
@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Yêu cầu liên kết đặt lại mật khẩu"
)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Tiếp nhận yêu cầu khôi phục mật khẩu:
    - Phản hồi HTTP 200 tức thì (< 30ms).
    - Tác vụ gửi mail được thực thi ngầm qua BackgroundTasks.
    - Bảo mật chống tấn công dò quét email (Email Enumeration).
    """
    await auth_service.request_password_reset(payload.email, background_tasks)
    return MessageResponse(
        message="Nếu email tồn tại trên hệ thống, thư khôi phục đã được gửi."
    )


# 5. API PUBLIC: Đặt lại mật khẩu mới
@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Đặt lại mật khẩu với token"
)
async def reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Xác thực token và cập nhật mật khẩu mới. Token sẽ bị vô hiệu hóa ngay sau khi sử dụng.
    """
    await auth_service.reset_password(payload)
    return MessageResponse(
        message="Đặt lại mật khẩu thành công. Vui lòng đăng nhập bằng mật khẩu mới."
    )