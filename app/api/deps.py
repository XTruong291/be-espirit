from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# Chuyển từ OAuth2PasswordBearer sang HTTPBearer để dán trực tiếp Token trên Swagger UI
security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Trích xuất chuỗi JWT Token từ Header Bearer
    token = credentials.credentials
    
    # 2. Giải mã token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    # 3. Truy vấn Database tìm user
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
        
    return user