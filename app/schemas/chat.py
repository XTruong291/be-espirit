from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    """Schema Request tạo mới phiên trò chuyện."""
    title: Optional[str] = Field(default="Phiên trò chuyện mới", max_length=255)


class ChatSessionResponse(BaseModel):
    """Schema Response thông tin một phiên trò chuyện."""
    id: int
    user_id: int
    title: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ChatSessionListResponse(BaseModel):
    """Schema Response danh sách các phiên trò chuyện."""
    items: List[ChatSessionResponse]
    total: int


class ChatMessageCreate(BaseModel):
    """Schema Request gửi tin nhắn từ phía User."""
    content: str = Field(..., min_length=1, description="Nội dung tin nhắn người dùng gửi")


class ChatMessageResponse(BaseModel):
    """Schema Response chi tiết một tin nhắn trong phiên."""
    id: int
    session_id: int
    sender: str
    content: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryResponse(BaseModel):
    """Schema Response lịch sử trò chuyện gồm danh sách tin nhắn."""
    session_id: int
    session_title: str
    messages: List[ChatMessageResponse]
