from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional

# Schema dữ liệu gửi lên khi Đăng ký
class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

# Schema dữ liệu gửi lên khi Đăng nhập
class UserLoginRequest(BaseModel):
    username: str
    password: str

# Schema dữ liệu trả về cho Client (Cần cấu hình from_attributes)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Dòng này giúp Pydantic ép kiểu dữ liệu ORM Model sang JSON không bị lỗi 500
    model_config = ConfigDict(from_attributes=True)

# Schema trả về Token khi Login thành công
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"