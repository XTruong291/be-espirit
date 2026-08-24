from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.user import User  # Model dựng tạm
from app.schemas.user import UserRegisterRequest, UserResponse, UserLoginRequest, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()
@router.post("/login", response_model=TokenResponse) #API login
async def login(credentials: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    # Tìm user theo username
    res = await db.execute(select(User).where(User.username == credentials.username))
    user = res.scalars().first()

    # Kiểm tra user và verify password 
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác."
        )

    # Gọi hàm tạo token 
    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return {"access_token": token, "token_type": "bearer"}

