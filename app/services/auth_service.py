import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.exceptions import DuplicateException, UnauthorizedException
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest

# Bộ nhớ tạm lưu mã OTP (Hết hạn sau 5 phút)
otp_db = {}
OTP_EXPIRE_SECONDS = 300


class AuthService:
    """Tầng Service chứa toàn bộ logic nghiệp vụ liên quan đến xác thực (Auth),

    kiểm tra dữ liệu đầu vào và gọi Tầng Repository để tương tác DB.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # ==================== TÍNH NĂNG XÁC THỰC OTP GMAIL ====================

    async def send_otp(self, email: str) -> dict:
        """Tạo mã OTP 6 số ngẫu nhiên và gửi qua Gmail."""
        otp_code = str(random.randint(100000, 999999))
        expires_at = time.time() + OTP_EXPIRE_SECONDS

        # 1. Lưu mã OTP cùng thời gian hết hạn vào RAM
        otp_db[email] = {"code": otp_code, "expires_at": expires_at}

        # 2. Cấu hình nội dung Email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{otp_code}] Mã xác minh địa chỉ Email"
        msg["From"] = settings.SENDER_EMAIL
        msg["To"] = email

        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #333;">Xác minh địa chỉ Email</h2>
            <p>Mã OTP của bạn là:</p>
            <h1 style="color: #007bff; letter-spacing: 4px;">{otp_code}</h1>
            <p>Mã này có hiệu lực trong <b>5 phút</b>. Vui lòng không chia sẻ mã cho bất kỳ ai.</p>
        </div>
        """
        msg.attach(MIMEText(html_content, "html"))

        # 3. Kết nối Server Gmail SMTP để gửi thư
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                server.sendmail(settings.SENDER_EMAIL, email, msg.as_string())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể gửi email xác thực: {str(e)}",
            )

        return {"message": f"Mã xác nhận đã được gửi thành công tới {email}"}

    async def verify_otp(self, email: str, code: str) -> dict:
        """Xác minh mã OTP do người dùng nhập vào."""
        record = otp_db.get(email)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email này chưa yêu cầu mã xác thực hoặc mã đã bị hủy.",
            )

        if time.time() > record["expires_at"]:
            del otp_db[email]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã OTP đã hết hạn (quá 5 phút). Vui lòng yêu cầu mã mới.",
            )

        if record["code"] != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mã xác thực không chính xác! Vui lòng kiểm tra lại.",
            )

        # Nhập đúng -> Xóa mã khỏi RAM và chấp nhận thành công
        del otp_db[email]
        return {
            "status": "success",
            "message": "Xác thực Gmail thành công! Email hợp lệ.",
        }

    # ==================== LUỒNG XÁC THỰC TÀI KHOẢN CŨ ====================

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
            hashed_password=get_password_hash(payload.password),
        )

        # 3. Lưu vào DB thông qua Repository
        return await self.user_repo.create(new_user)

    async def authenticate_user(
        self, credentials: UserLoginRequest
    ) -> TokenResponse:
        """Logic Đăng nhập và tạo JWT Access Token."""
        # 1. Tìm user theo username
        user = await self.user_repo.get_by_username(credentials.username)

        # 2. Xác thực tài khoản và mật khẩu
        if not user or not verify_password(
            credentials.password, user.hashed_password
        ):
            raise UnauthorizedException(
                "Tài khoản hoặc mật khẩu không chính xác."
            )

        # 3. Tạo access token
        access_token = create_access_token(
            subject=str(user.id), extra_data={"username": user.username}
        )

        return TokenResponse(access_token=access_token, token_type="bearer")

    async def get_current_user_from_token(self, token: str) -> User:
        """Logic giải mã Token và lấy thông tin người dùng đang đăng nhập."""
        # 1. Giải mã token
        payload = decode_access_token(token)
        if payload is None:
            raise UnauthorizedException(
                "Token không hợp lệ hoặc đã hết hạn."
            )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(
                "Token không hợp lệ hoặc đã hết hạn."
            )

        # 2. Tìm user trong DB thông qua Repository
        user = await self.user_repo.get_by_id(int(user_id))
        if user is None:
            raise UnauthorizedException(
                "Token không hợp lệ hoặc đã hết hạn."
            )

        return user
