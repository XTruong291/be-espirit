from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserAdminUpdateRequest
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, ForbiddenException, DuplicateException


class UserService:
    """
    Tầng Service chứa các logic nghiệp vụ liên quan đến quản lý thông tin User chung.
    """
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lấy danh sách tất cả người dùng (Admin)."""
        return await self.user_repo.get_all(skip=skip, limit=limit)

    async def get_user_by_id(self, user_id: int, requesting_user: User) -> User:
        """Lấy thông tin chi tiết một người dùng."""
        # Phân quyền: User thường chỉ được xem chính mình, Admin xem được tất cả
        if requesting_user.role != "admin" and requesting_user.id != user_id:
            raise ForbiddenException("Bạn không có quyền truy cập tài nguyên này.")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Không tìm thấy người dùng.")
        return user

    async def update_user(self, user_id: int, payload: UserAdminUpdateRequest, requesting_user: User) -> User:
        """Cập nhật thông tin người dùng."""
        target_user = await self.user_repo.get_by_id(user_id)
        if not target_user:
            raise NotFoundException("Không tìm thấy người dùng.")

        # 1. Phân quyền cập nhật
        if requesting_user.role != "admin":
            # User thường chỉ được phép sửa thông tin của chính mình
            if requesting_user.id != user_id:
                raise ForbiddenException("Bạn không có quyền sửa thông tin người dùng này.")
            # User thường không được tự ý sửa đổi role (chỉ chặn nếu giá trị mới khác với vai trò hiện tại)
            if payload.role is not None and payload.role != target_user.role:
                raise ForbiddenException("Bạn không có quyền thay đổi vai trò.")

        # 2. Chuẩn bị dữ liệu cập nhật
        update_data = payload.model_dump(exclude_unset=True)

        # Xử lý đổi tên đăng nhập: kiểm tra trùng lặp với tài khoản khác
        if "username" in update_data:
            new_username = update_data["username"]
            # Chỉ check nếu tên mới khác tên hiện tại của target_user
            if new_username != target_user.username:
                existing_username_user = await self.user_repo.get_by_username(new_username)
                if existing_username_user and existing_username_user.id != user_id:
                    raise DuplicateException("Tên đăng nhập đã tồn tại.")

        # Xử lý đổi password: băm mật khẩu mới
        if "password" in update_data:
            new_password = update_data.pop("password")
            if new_password: # Chỉ băm nếu mật khẩu mới không rỗng
                update_data["hashed_password"] = get_password_hash(new_password)

        # Xử lý đổi email: kiểm tra trùng lặp email với tài khoản khác
        if "email" in update_data:
            new_email = update_data["email"]
            # Chỉ check nếu email mới khác với email hiện tại của target_user
            if new_email != target_user.email:
                existing_email_user = await self.user_repo.get_by_email(new_email)
                if existing_email_user and existing_email_user.id != user_id:
                    raise DuplicateException("Email đã được sử dụng bởi tài khoản khác.")

        # 3. Gọi repository thực thi
        return await self.user_repo.update(target_user, update_data)

    async def delete_user(self, user_id: int, requesting_user: User) -> None:
        """Xóa tài khoản người dùng."""
        target_user = await self.user_repo.get_by_id(user_id)
        if not target_user:
            raise NotFoundException("Không tìm thấy người dùng.")

        # Phân quyền: User thường chỉ được xóa chính mình, Admin xóa được bất kỳ ai
        if requesting_user.role != "admin" and requesting_user.id != user_id:
            raise ForbiddenException("Bạn không có quyền xóa người dùng này.")

        # Thực thi xóa
        await self.user_repo.delete(target_user)
