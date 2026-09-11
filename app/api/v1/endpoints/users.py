from fastapi import APIRouter, Depends, status, UploadFile, File

from app.api.deps import get_user_service, require_admin, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserAdminUpdateRequest, UserUpdateRequest
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


# 2. API GET /me (Lấy thông tin tài khoản đang đăng nhập)
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Lấy thông tin tài khoản đang đăng nhập"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thông tin cá nhân của người dùng hiện tại.
    """
    return current_user


# 3. API PUT /me (Cập nhật thông tin cá nhân người dùng hiện tại)
@router.put(
    "/me",
    response_model=UserResponse,
    summary="Cập nhật thông tin cá nhân của người dùng hiện tại"
)
async def update_my_profile(
    payload: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """
    Cập nhật thông tin cá nhân (Tên đăng nhập, Email, Mật khẩu, Avatar link) của người dùng hiện tại.
    """
    update_dict = payload.model_dump(exclude_unset=True)
    admin_payload = UserAdminUpdateRequest(**update_dict)
    return await user_service.update_user(user_id=current_user.id, payload=admin_payload, requesting_user=current_user)



# 4. API POST /me/avatar (Upload file ảnh đại diện lên Cloudinary)
@router.post(
    "/me/avatar",
    response_model=UserResponse,
    summary="Tải lên ảnh đại diện cho người dùng hiện tại qua Cloudinary"
)
async def upload_my_avatar(
    file: UploadFile = File(..., description="File ảnh đại diện (JPG, PNG, WEBP - tối đa 5MB)"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    """
    Tải file ảnh đại diện lên Cloudinary (tối đa 5MB, định dạng JPG/PNG/WEBP),
    tự động crop hình vuông 300x300 và lưu đường dẫn an toàn vào hồ sơ người dùng.
    """
    return await user_service.upload_avatar(user_id=current_user.id, file=file, requesting_user=current_user)



# 5. API GET /{id} (User thường xem chính mình, Admin xem bất kỳ ai)
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


# 6. API PATCH /{id} (User thường sửa chính mình trừ role, Admin sửa bất kỳ trường nào)
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


# 7. API DELETE /{id} (User thường xóa chính mình, Admin xóa bất kỳ ai)
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

