from datetime import datetime
from typing import Optional
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.future import select
# pyrefly: ignore [missing-import]
from sqlalchemy import or_

from app.models.user import User


class UserRepository:
    """
    Tầng Data Access (Repository) chịu trách nhiệm tương tác trực tiếp với cơ sở dữ liệu cho model User.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Tìm user theo ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Tìm user theo Tên đăng nhập."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Tìm user theo Email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_username_or_email(self, username: str, email: str) -> Optional[User]:
        """Tìm user theo Username hoặc Email."""
        result = await self.db.execute(
            select(User).where(or_(User.username == username, User.email == email))
        )
        return result.scalars().first()

    async def create(self, user: User) -> User:
        """Tạo mới một User trong DB."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lấy danh sách tất cả người dùng kèm phân trang."""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def update(self, user: User, update_data: dict) -> User:
        """Cập nhật các trường thông tin của User."""
        for key, value in update_data.items():
            setattr(user, key, value)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Xóa hoàn toàn một User khỏi DB."""
        await self.db.delete(user)
        await self.db.commit()

    async def get_by_reset_token(self, token_hash: str) -> Optional[User]:
        """Tìm user dựa trên chuỗi hash của reset token."""
        result = await self.db.execute(
            select(User).where(User.reset_token == token_hash)
        )
        return result.scalars().first()

    async def save_reset_token(
        self,
        user: User,
        token_hash: str,
        expires_at: datetime,
        request_time: datetime
    ) -> User:
        """Lưu token đặt lại mật khẩu và cập nhật thời gian yêu cầu gần nhất."""
        user.reset_token = token_hash
        user.reset_expires_at = expires_at
        user.last_reset_request = request_time
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password_and_clear_token(
        self,
        user: User,
        new_hashed_password: str
    ) -> User:
        """Cập nhật mật khẩu mới và hủy bỏ token (Single-use token)."""
        user.hashed_password = new_hashed_password
        user.reset_token = None
        user.reset_expires_at = None
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

