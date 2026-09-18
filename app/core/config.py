from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

# Tự động xác định thư mục gốc của dự án (thư mục be-espirit)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_SERVER: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "test_db"

    # Đặt giá trị mặc định phòng trường hợp chưa đọc được .env
    SECRET_KEY: str = "your_super_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180

    # Cấu hình lưu trữ đám mây Cloudinary
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # Cấu hình gửi mail OTP Gmail
    SENDER_EMAIL: str = ""
    SENDER_PASSWORD: str = ""

    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+aiomysql://{self.MYSQL_USER}:{password}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    class Config:
        # Đường dẫn tuyệt đối tới .env giúp Pydantic luôn tìm thấy bất kể đứng ở thư mục nào
        env_file = BASE_DIR / ".env"
        extra = "ignore"


settings = Settings()