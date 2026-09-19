from pydantic import BaseModel, EmailStr, Field, model_validator


class ForgotPasswordRequest(BaseModel):
    """Payload yêu cầu link khôi phục mật khẩu."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Payload xác thực token và cập nhật mật khẩu mới."""
    token: str = Field(..., min_length=1, description="Token đặt lại mật khẩu từ email")
    new_password: str = Field(..., min_length=6, max_length=100, description="Mật khẩu mới (tối thiểu 6 ký tự)")
    confirm_password: str = Field(..., min_length=6, max_length=100, description="Xác nhận mật khẩu mới")

    @model_validator(mode="after")
    def verify_passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("Mật khẩu xác nhận không trùng khớp.")
        return self


class MessageResponse(BaseModel):
    """Định dạng phản hồi thông điệp chuẩn."""
    message: str
