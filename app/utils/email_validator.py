from email_validator import validate_email, EmailNotValidError
from app.core.exceptions import BaseAppException

# Danh sách một số domain email rác/tạm thời phổ biến
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", 
    "guerrillamail.com", "trashmail.com", "yopmail.com",
    "sharklasers.com", "getnada.com", "dispostable.com"
}

def validate_real_email(email: str) -> str:
    """
    Kiểm tra cú pháp, sự tồn tại của MX Record (DNS) và chặn email rác.
    """
    try:
        # check_deliverability=True sẽ thực hiện tra cứu DNS MX Record
        email_info = validate_email(email, check_deliverability=True)
        normalized_email = email_info.normalized
        domain = email_info.domain.lower()

    except EmailNotValidError as e:
        # Email sai cú pháp hoặc Domain không có máy chủ nhận Mail
        raise BaseAppException(
            message=f"Email không hợp lệ hoặc tên miền không tồn tại: {str(e)}",
            status_code=400
        )

    # Chặn các domain Temp Mail
    if domain in DISPOSABLE_DOMAINS:
        raise BaseAppException(
            message="Hệ thống không chấp nhận email tạm thời/email rác.",
            status_code=400
        )

    return normalized_email