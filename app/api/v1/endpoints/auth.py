from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from app.api.deps import get_current_user  # Import hàm xác thực từ Bước 3

router = APIRouter()


# 1. API PUBLIC: Đăng ký tài khoản mới (Không cần đăng nhập)
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới"
)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # 1. Kiểm tra username hoặc email đã tồn tại hay chưa
    query = await db.execute(
        select(User).where(
            or_(User.username == payload.username, User.email == payload.email)
        )
    )
    existing_user = query.scalars().first()
    
    if existing_user:
        if existing_user.username == payload.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đăng nhập đã tồn tại."
            )
        if existing_user.email == payload.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng."
            )

    # 2. Tạo User mới
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password)
    )

    # 3. Lưu vào DB
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


# 2. API PUBLIC: Đăng nhập hệ thống (Không cần đăng nhập)
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
        subject=str(user.id),
        extra_data={"username": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# 3. API PRIVATE (BƯỚC 4): Lấy thông tin tài khoản hiện tại (Cần đăng nhập)
@router.get("/me", response_model=UserResponse, summary="Lấy thông tin tài khoản đang đăng nhập")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    API này đã được KHÓA bằng Depends(get_current_user).
    Chỉ khi truyền đúng Bearer Token hợp lệ ở Header mới xem được dữ liệu.
    """
    return current_user