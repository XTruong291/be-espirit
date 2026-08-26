from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

router = APIRouter()
#API Register
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới"
)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # 1. Kiểm tra username đã tồn tại
    query_user = await db.execute(select(User).where(User.username == payload.username))
    if query_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập đã tồn tại."
        )

    # 2. Kiểm tra email đã tồn tại
    query_email = await db.execute(select(User).where(User.email == payload.email))
    if query_email.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng."
        )

    # 3. Tạo User mới
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password)
    )

    # 4. Lưu vào DB
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
#API Login
@router.post("/login", response_model=TokenResponse, summary="Đăng nhập hệ thống")
async def login(credentials: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    # 1. Tìm user theo username
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalars().first()

    # 2. Xác thực thông tin
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác."
        )

    # 3. Tạo access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }