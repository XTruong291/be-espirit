import smtplib

# Điền trực tiếp thông tin của bạn vào đây để test
SENDER_EMAIL = "congwan2006@gmail.com"
SENDER_PASSWORD = "anskraabnvsdiyjg"  # 16 ký tự viết liền

print("Đang kết nối tới Google SMTP...")
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    print(" KẾT NỐI THÀNH CÔNG! Mật khẩu ứng dụng hoàn toàn chính xác.")
    server.quit()
except Exception as e:
    print(" KẾT NỐI THẤT BẠI:")
    print(e)