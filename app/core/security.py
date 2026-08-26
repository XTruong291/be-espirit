from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
import jwt

from app.core.config import settings  # Lấy SECRET_KEY và ALGORITHM từ config dự án


def get_password_hash(password: str) -> str:
    """
    Băm mật khẩu thô thành chuỗi mã hóa bcrypt an toàn.
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    So sánh mật khẩu thô người dùng nhập vào với chuỗi hash trong Database.
    """
    try:
        password_byte_enc = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_byte_enc, hashed_password_bytes)
    except Exception:
        return False


def create_access_token(
    subject: str | Any, 
    extra_data: Optional[Dict[str, Any]] = None, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Tạo chuỗi JWT Access Token chứa ID người dùng và thời gian hết hạn.
    
    :param subject: Định danh chính của User (thường là user.id hoặc user.email)
    :param extra_data: Dữ liệu bổ sung nếu muốn đưa vào token (ví dụ: role="admin")
    :param expires_delta: Thời gian hết hạn tùy chọn
    """
    to_encode: Dict[str, Any] = {}
    
    if extra_data:
        to_encode.update(extra_data)
        
    # Đặt trường "sub" (Subject) tiêu chuẩn của JWT
    to_encode["sub"] = str(subject)
    
    # Tính thời gian hết hạn (Expiration Time)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    # Mã hóa thành chuỗi JWT
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Giải mã và kiểm tra tính hợp lệ của Token.
    Trả về payload (dict) nếu hợp lệ, trả về None nếu token hết hạn hoặc giả mạo.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.PyJWTError:
        return None