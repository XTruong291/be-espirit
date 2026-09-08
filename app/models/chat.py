# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship

from app.models.user import Base


class ChatSession(Base):
    """Model quản lý các Phiên trò chuyện (Chat Sessions)."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="Phiên trò chuyện mới")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class ChatMessage(Base):
    """Model quản lý các Tin nhắn (Chat Messages) trong phiên."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # 'user' hoặc 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")
