from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from fastapi import BackgroundTasks

from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.schemas.auth import ResetPasswordRequest
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.core.exceptions import DuplicateException, UnauthorizedException, BadRequestException
from app.utils.email_sender import send_reset_password_email


class AuthService:
    """
    Tầng Service chứa toàn bộ logic nghiệp vụ liên quan đến xác thực (Auth),
    kiểm tra dữ liệu đầu vào và gọi Tầng Repository để tương tác DB.
    """
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, payload: UserRegisterRequest) -> User:
        """Logic Đăng ký người dùng mới."""
        # 1. Kiểm tra username hoặc email đã tồn tại hay chưa
        existing_user = await self.user_repo.get_by_username_or_email(
            username=payload.username, email=payload.email
        )
        
        if existing_user:
            if existing_user.username == payload.username:
                raise DuplicateException("Tên đăng nhập đã tồn tại.")
            if existing_user.email == payload.email:
                raise DuplicateException("Email đã được sử dụng.")

        # 2. Tạo đối tượng User mới và mã hóa password
        new_user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=get_password_hash(payload.password)
        )

        # 3. Lưu vào DB thông qua Repository
        return await self.user_repo.create(new_user)

    async def authenticate_user(self, credentials: UserLoginRequest) -> TokenResponse:
        """Logic Đăng nhập và tạo JWT Access Token."""
        # 1. Tìm user theo username
        user = await self.user_repo.get_by_username(credentials.username)

        # 2. Xác thực tài khoản và mật khẩu
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise UnauthorizedException("Tài khoản hoặc mật khẩu không chính xác.")

        # 3. Tạo access token
        access_token = create_access_token(
            subject=str(user.id),
            extra_data={"username": user.username}
        )

        return TokenResponse(access_token=access_token, token_type="bearer")

    async def get_current_user_from_token(self, token: str) -> User:
        """Logic giải mã Token và lấy thông tin người dùng đang đăng nhập."""
        # 1. Giải mã token
        payload = decode_access_token(token)
        if payload is None:
            raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn.")

        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn.")

        # 2. Tìm user trong DB thông qua Repository
        user = await self.user_repo.get_by_id(int(user_id))
        if user is None:
            raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn.")

        return user

    @staticmethod
    def _hash_token(token: str) -> str:
        """Băm token thô sang chuỗi SHA-256 an toàn trước khi lưu vào DB."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def request_password_reset(self, email: str, background_tasks: BackgroundTasks) -> None:
        """
        Nghiệp vụ Quên mật khẩu:
        - Kiểm tra user theo email (Nếu không có, return im lặng để chống Email Enumeration).
        - Kiểm tra giãn cách yêu cầu (Rate Limit 2 phút).
        - Sinh token an toàn, lưu hash vào DB và đẩy task gửi mail vào BackgroundTasks.
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Email không tồn tại -> Return âm thầm, không ném lỗi (chống Email Enumeration Attack)
            return

        now = datetime.now(timezone.utc)

        # Kiểm tra Rate Limiting (chống spam SMTP)
        if user.last_reset_request:
            last_req = (
                user.last_reset_request.replace(tzinfo=timezone.utc)
                if user.last_reset_request.tzinfo is None
                else user.last_reset_request
            )
            if (now - last_req) < timedelta(minutes=settings.RESET_PASSWORD_COOLDOWN_MINUTES):
                # Chưa hết thời gian chờ 2 phút -> Bỏ qua gửi email để chống spam
                return

        # Tạo token thô ngẫu nhiên 32 bytes (URL-safe string)
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = now + timedelta(minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)

        # Lưu token hash và cập nhật last_reset_request vào DB
        await self.user_repo.save_reset_token(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at,
            request_time=now,
        )

        # Đẩy tác vụ gửi email vào BackgroundTasks (Non-blocking)
        background_tasks.add_task(send_reset_password_email, user.email, raw_token)

    async def reset_password(self, payload: ResetPasswordRequest) -> None:
        """
        Nghiệp vụ Đặt lại mật khẩu:
        - Xác minh token qua SHA-256 hash.
        - Kiểm tra hạn sử dụng (15 phút).
        - Cập nhật mật khẩu mới và xóa token (Single-use).
        """
        token_hash = self._hash_token(payload.token)
        user = await self.user_repo.get_by_reset_token(token_hash)

        if not user or not user.reset_expires_at:
            raise BadRequestException("Liên kết đặt lại mật khẩu không hợp lệ hoặc đã được sử dụng.")

        now = datetime.now(timezone.utc)
        expires_at = (
            user.reset_expires_at.replace(tzinfo=timezone.utc)
            if user.reset_expires_at.tzinfo is None
            else user.reset_expires_at
        )

        if now > expires_at:
            raise BadRequestException("Liên kết đặt lại mật khẩu đã hết hạn. Vui lòng yêu cầu lại.")

        # Băm mật khẩu mới và xóa token (Single-use)
        new_hashed_pwd = get_password_hash(payload.new_password)
        await self.user_repo.update_password_and_clear_token(user, new_hashed_pwd)

