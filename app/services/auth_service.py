<<<<<<< HEAD
import asyncio
=======
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf
import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
<<<<<<< HEAD

from app.core.config import settings
from app.core.exceptions import (
    BaseAppException,
    DuplicateException,
    UnauthorizedException,
)
=======
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.exceptions import DuplicateException, UnauthorizedException
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest

<<<<<<< HEAD
# Bộ nhớ tạm lưu mã OTP (Lưu trữ: code, expires_at, last_sent, attempts, is_verified)
otp_db = {}
OTP_EXPIRE_SECONDS = 300  # 5 phút
RESEND_COOLDOWN_SECONDS = 60  # 60 giây mới cho gửi lại
MAX_VERIFY_ATTEMPTS = 5  # Tối đa 5 lần nhập sai


class AuthService:
    """Tầng Service chứa toàn bộ logic nghiệp vụ liên quan đến xác thực (Auth)."""
=======
# Bộ nhớ tạm lưu mã OTP (Hết hạn sau 5 phút)
otp_db = {}
OTP_EXPIRE_SECONDS = 300


class AuthService:
    """Tầng Service chứa toàn bộ logic nghiệp vụ liên quan đến xác thực (Auth),

    kiểm tra dữ liệu đầu vào và gọi Tầng Repository để tương tác DB.
    """
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

<<<<<<< HEAD
    # --- HÀM PHỤ TRỢ: GỬI MAIL ĐỒNG BỘ NẰM TRONG THREAD RIÊNG ---
    def _send_email_sync(self, recipient: str, message: MIMEMultipart):
        """Chạy hàm gửi mail đồng bộ để tránh block Async Event Loop."""
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
            server.sendmail(settings.SENDER_EMAIL, recipient, message.as_string())

    # TÍNH NĂNG XÁC THỰC OTP EMAIL 

    async def send_otp(self, email: str) -> dict:
        """Tạo mã OTP 6 số ngẫu nhiên và gửi qua Gmail."""
        # 1. Kiểm tra xem Email đã tồn tại trong DB chưa
        existing_user = await self.user_repo.get_by_username_or_email(
            username="", email=email
        )
        if existing_user and existing_user.email == email:
            raise DuplicateException("Email này đã được sử dụng bởi tài khoản khác.")

        now = time.time()
        record = otp_db.get(email)

        # 2. Chống Spam (Cooldown 60s)
        if record and (now - record.get("last_sent_at", 0) < RESEND_COOLDOWN_SECONDS):
            remaining = int(RESEND_COOLDOWN_SECONDS - (now - record["last_sent_at"]))
            raise BaseAppException(
                message=f"Vui lòng đợi {remaining} giây trước khi yêu cầu mã mới.",
                status_code=400,
            )

        # 3. Tạo mã OTP mới
        otp_code = str(random.randint(100000, 999999))
        otp_db[email] = {
            "code": otp_code,
            "expires_at": now + OTP_EXPIRE_SECONDS,
            "last_sent_at": now,
            "attempts": 0,
            "is_verified": False,
        }

        # 4. Cấu hình nội dung Email
=======
    # ==================== TÍNH NĂNG XÁC THỰC OTP GMAIL ====================

    async def send_otp(self, email: str) -> dict:
        """Tạo mã OTP 6 số ngẫu nhiên và gửi qua Gmail."""
        otp_code = str(random.randint(100000, 999999))
        expires_at = time.time() + OTP_EXPIRE_SECONDS

        # 1. Lưu mã OTP cùng thời gian hết hạn vào RAM
        otp_db[email] = {"code": otp_code, "expires_at": expires_at}

        # 2. Cấu hình nội dung Email
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf
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

<<<<<<< HEAD
        # 5. Gửi thư không gây treo server 
        try:
            await asyncio.to_thread(self._send_email_sync, email, msg)
        except smtplib.SMTPRecipientsRefused:
            # Lỗi khi gửi tới địa chỉ không tồn tại thực sự trên hệ thống Gmail
            del otp_db[email]
            raise BaseAppException(
                message="Địa chỉ email không tồn tại hoặc không thể tiếp nhận thư.",
                status_code=400,
            )
        except Exception as e:
            raise BaseAppException(
                message=f"Không thể gửi email xác thực: {str(e)}",
                status_code=500,
=======
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
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf
            )

        return {"message": f"Mã xác nhận đã được gửi thành công tới {email}"}

    async def verify_otp(self, email: str, code: str) -> dict:
        """Xác minh mã OTP do người dùng nhập vào."""
        record = otp_db.get(email)

        if not record:
<<<<<<< HEAD
            raise BaseAppException(
                message="Email này chưa yêu cầu mã xác thực hoặc mã đã bị hủy.",
                status_code=400,
            )

        # Kiểm tra hết hạn
        if time.time() > record["expires_at"]:
            del otp_db[email]
            raise BaseAppException(
                message="Mã OTP đã hết hạn (quá 5 phút). Vui lòng yêu cầu mã mới.",
                status_code=400,
            )

        # Kiểm tra giới hạn nhập sai (Brute-force protection)
        if record["attempts"] >= MAX_VERIFY_ATTEMPTS:
            del otp_db[email]
            raise BaseAppException(
                message="Bạn đã nhập sai quá 5 lần. Mã OTP này đã bị vô hiệu hóa.",
                status_code=400,
            )

        # Kiểm tra mã
        if record["code"] != code:
            record["attempts"] += 1
            remaining_attempts = MAX_VERIFY_ATTEMPTS - record["attempts"]
            raise BaseAppException(
                message=f"Mã xác thực không chính xác! Bạn còn {remaining_attempts} lần thử.",
                status_code=400,
            )

        # Nhập đúng -> Đánh dấu Email ĐÃ XÁC THỰC
        record["is_verified"] = True
        return {
            "status": "success",
            "message": "Xác thực Gmail thành công! Bạn có thể tiến hành đăng ký.",
        }

    #  CÁC LUỒNG XÁC THỰC TÀI KHOẢN 
=======
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
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf

    async def register_user(self, payload: UserRegisterRequest) -> User:
        """Logic Đăng ký người dùng mới (Yêu cầu phải Verify OTP trước)."""

        # 1. BẮT BỘC: Kiểm tra email đã qua bước xác thực OTP thành công chưa
        otp_record = otp_db.get(payload.email)
        if not otp_record or not otp_record.get("is_verified"):
            raise BaseAppException(
                message="Email chưa được xác thực qua OTP. Vui lòng xác thực email trước khi đăng ký.",
                status_code=400,
            )

        # 2. Kiểm tra username hoặc email đã tồn tại hay chưa
        existing_user = await self.user_repo.get_by_username_or_email(
            username=payload.username, email=payload.email
        )

        if existing_user:
            if existing_user.username == payload.username:
                raise DuplicateException("Tên đăng nhập đã tồn tại.")
            if existing_user.email == payload.email:
                raise DuplicateException("Email đã được sử dụng.")

        # 3. Tạo đối tượng User mới và mã hóa password
        new_user = User(
            username=payload.username,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
        )

        # 4. Lưu vào DB thông qua Repository
        created_user = await self.user_repo.create(new_user)

<<<<<<< HEAD
        # 5. Đăng ký thành công -> Xóa trạng thái OTP khỏi bộ nhớ
        if payload.email in otp_db:
            del otp_db[payload.email]

        return created_user

=======
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf
    async def authenticate_user(
        self, credentials: UserLoginRequest
    ) -> TokenResponse:
        """Logic Đăng nhập và tạo JWT Access Token."""
        user = await self.user_repo.get_by_username(credentials.username)

<<<<<<< HEAD
        if not user or not verify_password(
            credentials.password, user.hashed_password
        ):
            raise UnauthorizedException("Tài khoản hoặc mật khẩu không chính xác.")
=======
        # 2. Xác thực tài khoản và mật khẩu
        if not user or not verify_password(
            credentials.password, user.hashed_password
        ):
            raise UnauthorizedException(
                "Tài khoản hoặc mật khẩu không chính xác."
            )
>>>>>>> 3130b0cd266eba590f5f88c55633477c151efcbf

        access_token = create_access_token(
            subject=str(user.id), extra_data={"username": user.username}
        )

        return TokenResponse(access_token=access_token, token_type="bearer")

    async def get_current_user_from_token(self, token: str) -> User:
        """Logic giải mã Token và lấy thông tin người dùng đang đăng nhập."""
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

        user = await self.user_repo.get_by_id(int(user_id))
        if user is None:
            raise UnauthorizedException(
                "Token không hợp lệ hoặc đã hết hạn."
            )

        return user