from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.chat_repository import ChatRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.ai_service import AIService
from app.services.chat_service import ChatService
from app.services.storage_service import StorageService
from app.core.exceptions import ForbiddenException

# Chuyển từ OAuth2PasswordBearer sang HTTPBearer để dán trực tiếp Token trên Swagger UI
security_scheme = HTTPBearer()


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency provider cho UserRepository."""
    return UserRepository(db)


def get_chat_repository(db: AsyncSession = Depends(get_db)) -> ChatRepository:
    """Dependency provider cho ChatRepository."""
    return ChatRepository(db)


def get_ai_service() -> AIService:
    """Dependency provider cho AIService (Mock AI Service)."""
    return AIService()


def get_storage_service() -> StorageService:
    """Dependency provider cho StorageService (Cloudinary)."""
    return StorageService()


def get_chat_service(
    chat_repo: ChatRepository = Depends(get_chat_repository),
    ai_service: AIService = Depends(get_ai_service),
) -> ChatService:
    """Dependency provider cho ChatService."""
    return ChatService(chat_repo=chat_repo, ai_service=ai_service)


def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    """Dependency provider cho AuthService."""
    return AuthService(user_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    storage_service: StorageService = Depends(get_storage_service),
) -> UserService:
    """Dependency provider cho UserService."""
    return UserService(user_repo=user_repo, storage_service=storage_service)




async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Dependency lấy thông tin User hiện tại đang đăng nhập.
    Tự động trích xuất token từ Bearer Header và gọi AuthService xác thực.
    """
    return await auth_service.get_current_user_from_token(credentials.credentials)


class RoleChecker:
    """
    Dependency Guard dùng để kiểm tra quyền hạn (Role) của User đăng nhập.
    """
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise ForbiddenException("Bạn không có quyền truy cập tài nguyên này.")
        return current_user


# Tạo sẵn instance guard cho quyền Admin
require_admin = RoleChecker(["admin"])