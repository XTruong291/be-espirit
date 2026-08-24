#file để test token sửa sau nhé 
def get_password_hash(password: str) -> str:
    return f"hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return f"hashed_{plain_password}" == hashed_password

def create_access_token(data: dict) -> str:
    return "fake_jwt_token_for_testing"