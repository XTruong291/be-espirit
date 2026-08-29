from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.core.exceptions import DuplicateException, UnauthorizedException


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
