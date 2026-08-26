from pydantic import BaseModel, EmailStr

class UserRegisterRequest(BaseModel): #dữ liệu đăng ký người dùng 
    username: str
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):#Dữ liệu trả về sau khi đăng ký 
    id: int
    username: str
    email: EmailStr
    is_active: bool
    class Config:
        from_attributes = True
        
class UserLoginRequest(BaseModel):#Dữ liệu gửi lên khi đăng nhập
    username: str
    password: str
    
class TokenResponse(BaseModel):#Dữ liệu trả về sau khi đăng nhập thành công
    access_token: str
    token_type: str = "bearer"