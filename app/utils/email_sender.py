import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# pyrefly: ignore [missing-import]
import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_reset_password_email(email_to: str, raw_token: str) -> None:
    """
    Gửi email chứa liên kết khôi phục mật khẩu bất đồng bộ bằng aiosmtplib.
    URL bắt buộc trỏ về settings.FRONTEND_URL/reset-password?token=...
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = f"[{settings.SMTP_FROM_NAME}] Yêu cầu đặt lại mật khẩu"
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = email_to

    text_content = f"""Xin chào,
Bạn nhận được thư này vì đã yêu cầu đặt lại mật khẩu cho tài khoản của mình.
Vui lòng truy cập đường dẫn sau để tạo mật khẩu mới (Liên kết có hiệu lực trong {settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES} phút):
{reset_link}

Nếu bạn không yêu cầu hành động này, vui lòng bỏ qua thư này."""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 580px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px; }}
            .btn {{ display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: #ffffff !important; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 15px; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #64748b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Yêu cầu đặt lại mật khẩu</h2>
            <p>Xin chào,</p>
            <p>Hệ thống nhận được yêu cầu khôi phục mật khẩu từ tài khoản của bạn. Nhấn vào nút bên dưới để tiến hành đổi mật khẩu:</p>
            <p><a href="{reset_link}" class="btn" target="_blank">Đặt lại mật khẩu</a></p>
            <p>Hoặc sao chép liên kết này vào trình duyệt:<br><a href="{reset_link}">{reset_link}</a></p>
            <p><em>Lưu ý: Liên kết này chỉ có giá trị sử dụng một lần và sẽ hết hạn sau {settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES} phút.</em></p>
            <div class="footer">
                <p>Nếu bạn không thực hiện yêu cầu này, hãy yên tâm rằng tài khoản của bạn vẫn an toàn.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message.attach(MIMEText(text_content, "plain", "utf-8"))
    message.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER if settings.SMTP_USER else None,
            password=settings.SMTP_PASSWORD if settings.SMTP_PASSWORD else None,
            start_tls=settings.SMTP_TLS,
        )
        logger.info(f"Đã gửi email khôi phục mật khẩu thành công tới {email_to}")
    except Exception as e:
        logger.error(f"Lỗi khi gửi email khôi phục mật khẩu tới {email_to}: {str(e)}")
