from urllib.parse import quote_plus
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_SERVER: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "test_db"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180

    # Cấu hình lưu trữ đám mây Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Cấu hình Quên/Đặt lại mật khẩu & Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int = 15
    RESET_PASSWORD_COOLDOWN_MINUTES: int = 2

    # Cấu hình SMTP Email (aiosmtplib)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@espirit.com"
    SMTP_FROM_NAME: str = "E-Spirit Support"
    SMTP_TLS: bool = True


    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+aiomysql://{self.MYSQL_USER}:{password}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()