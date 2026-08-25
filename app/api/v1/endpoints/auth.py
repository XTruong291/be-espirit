from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.user import User  # Model dựng tạm
from app.schemas.user import UserRegisterRequest, UserResponse, UserLoginRequest, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()
#API register
@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới"
)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    # 1. Kiểm tra username đã tồn tại trong DB chưa
    query_user = await db.execute(select(User).where(User.username == payload.username))
    if query_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Tên đăng nhập đã tồn tại."
        )

    # 2. Kiểm tra email đã tồn tại chưa
    query_email = await db.execute(select(User).where(User.email == payload.email))
    if query_email.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email đã được sử dụng."
        )

    # 3. Tạo instance User mới 
    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password)
    )

    # 4. Lưu thông tin vào Database
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
 #API login
@router.post("/login", response_model=TokenResponse)
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
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    # Trả về kết quả đúng với TokenResponse schema
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }