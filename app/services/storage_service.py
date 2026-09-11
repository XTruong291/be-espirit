import asyncio
from typing import Optional
from fastapi import UploadFile
import cloudinary
import cloudinary.uploader

from app.core.config import settings
from app.core.exceptions import BadRequestException

# Giới hạn dung lượng tối đa: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


class StorageService:
    """
    Dịch vụ lưu trữ tệp (Storage Service) trừu tượng hóa tương tác với Cloudinary.
    Hỗ trợ validate định dạng, dung lượng và tự động resize/crop ảnh 300x300.
    """
    def __init__(self):
        if (
            settings.CLOUDINARY_CLOUD_NAME
            and settings.CLOUDINARY_API_KEY
            and settings.CLOUDINARY_API_SECRET
        ):
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True
            )
            self.is_configured = True
        else:
            self.is_configured = False

    async def upload_avatar(self, file: UploadFile, user_id: int) -> str:
        """
        Validate file và upload ảnh đại diện lên Cloudinary theo phương thức bất đồng bộ.
        """
        # 1. Kiểm tra định dạng MIME type
        content_type = file.content_type
        if not content_type or content_type.lower() not in ALLOWED_MIME_TYPES:
            raise BadRequestException("Định dạng file không hỗ trợ. Chỉ chấp nhận các định dạng ảnh JPG, PNG, WEBP.")

        # 2. Đọc file để kiểm tra dung lượng tối đa 5MB
        file_bytes = await file.read()
        file_size = len(file_bytes)
        if file_size > MAX_FILE_SIZE:
            raise BadRequestException(
                f"Dung lượng file ({file_size / (1024 * 1024):.2f}MB) vượt quá giới hạn cho phép (tối đa 5MB)."
            )
        if file_size == 0:
            raise BadRequestException("File tải lên rỗng. Vui lòng chọn một file hợp lệ.")

        # Reset con trỏ file
        await file.seek(0)

        # 3. Nếu chưa cấu hình Cloudinary credentials, trả về mock URL an toàn
        if not self.is_configured:
            safe_filename = file.filename or "avatar.jpg"
            return f"https://res.cloudinary.com/mock-cloud/image/upload/v1/e_spirit/avatars/user_{user_id}_{safe_filename}"

        # 4. Thực thi upload qua SDK trong thread pool để tránh block event loop
        def _sync_upload():
            import io
            return cloudinary.uploader.upload(
                io.BytesIO(file_bytes),
                folder="e_spirit/avatars",
                public_id=f"user_{user_id}_avatar",
                overwrite=True,
                transformation=[
                    {"width": 300, "height": 300, "crop": "fill", "gravity": "face"},
                    {"quality": "auto", "fetch_format": "auto"}
                ]
            )


        try:
            upload_result = await asyncio.to_thread(_sync_upload)
            secure_url = upload_result.get("secure_url")
            if not secure_url:
                raise BadRequestException("Không thể nhận đường dẫn ảnh an toàn từ Cloudinary.")
            return secure_url
        except Exception as e:
            if isinstance(e, BadRequestException):
                raise e
            raise BadRequestException(f"Lỗi khi tải ảnh lên Cloudinary: {str(e)}")
