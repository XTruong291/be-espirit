from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
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