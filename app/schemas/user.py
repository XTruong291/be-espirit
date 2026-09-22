from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Import hàm kiểm tra email thật/giả 
from app.utils.email_validator import validate_real_email


# Schema chung cho phản hồi thông báo đơn giản
class MessageResponse(BaseModel):
    message: str


# Schema dữ liệu gửi lên khi Đăng ký
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Tên đăng nhập từ 3-50 ký tự")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Mật khẩu tối thiểu 6 ký tự")

    @field_validator("email")
    @classmethod
    def check_email_real(cls, v: str) -> str:
        return validate_real_email(v)


# Schema dữ liệu gửi lên khi Đăng nhập
class UserLoginRequest(BaseModel):
    username: str
    password: str


# Schema dữ liệu trả về cho Client (Cần cấu hình from_attributes)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str = "user"
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Schema trả về Token khi Login thành công
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Schema cho User thường cập nhật thông tin cá nhân
class UserUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    avatar_url: Optional[str] = None

    @field_validator("email")
    @classmethod
    def check_email_real(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_real_email(v)
        return v


# Schema cho Admin cập nhật thông tin bất kỳ User nào
class UserAdminUpdateRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = None
    avatar_url: Optional[str] = None

    @field_validator("email")
    @classmethod
    def check_email_real(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_real_email(v)
        return v


#  BỔ SUNG CHO TÍNH NĂNG XÁC THỰC EMAIL OTP 

# Schema gửi yêu cầu tạo mã OTP
class SendOTPRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def check_email_real(cls, v: str) -> str:
        return validate_real_email(v)


# Schema gửi yêu cầu xác minh mã OTP 
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str = Field(
        ..., 
        min_length=6, 
        max_length=6, 
        pattern=r"^[0-9]+$", 
        description="Mã OTP bắt buộc đúng 6 chữ số"
    )

    @field_validator("email")
    @classmethod
    def check_email_real(cls, v: str) -> str:
        return validate_real_email(v)