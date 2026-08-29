from fastapi import APIRouter, Depends, status

from app.api.deps import get_user_service, require_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserAdminUpdateRequest
from app.services.user_service import UserService

router = APIRouter()


# 1. API GET / (Chỉ dành cho Admin)
@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Lấy danh sách toàn bộ người dùng (Chỉ Admin)"
)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service),
    admin_user: User = Depends(require_admin)
):
    """
    Lấy danh sách tất cả người dùng trong hệ thống.
    """
    return await user_service.get_all_users(skip=skip, limit=limit)


# 2. API GET /{id} (User thường xem chính mình, Admin xem bất kỳ ai)
@router.get(
    "/{id}",
    response_model=UserResponse,
    summary="Lấy thông tin chi tiết của người dùng"
)
async def get_user_by_id(
    id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin cá nhân của người dùng.
    """
    return await user_service.get_user_by_id(user_id=id, requesting_user=current_user)


# 3. API PATCH /{id} (User thường sửa chính mình trừ role, Admin sửa bất kỳ trường nào)
@router.patch(
    "/{id}",
    response_model=UserResponse,
    summary="Cập nhật thông tin người dùng"
)
async def update_user(
    id: int,
    payload: UserAdminUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật các trường thông tin (Tên đăng nhập, Email, Mật khẩu, vai trò) của người dùng.
    """
    return await user_service.update_user(user_id=id, payload=payload, requesting_user=current_user)


# 4. API DELETE /{id} (User thường xóa chính mình, Admin xóa bất kỳ ai)
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa tài khoản người dùng"
)
async def delete_user(
    id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """
    Xóa tài khoản người dùng khỏi hệ thống.
    """
    await user_service.delete_user(user_id=id, requesting_user=current_user)
    return None
