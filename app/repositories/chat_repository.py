from typing import Optional, List
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.future import select
# pyrefly: ignore [missing-import]
from sqlalchemy import func, desc

from app.models.chat import ChatSession, ChatMessage


class ChatRepository:
    """
    Tầng Data Access tương tác trực tiếp với DB cho ChatSession và ChatMessage.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, user_id: int, title: str = "Phiên trò chuyện mới") -> ChatSession:
        """Tạo một phiên trò chuyện mới."""
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Tìm ChatSession theo ID."""
        result = await self.db.execute(select(ChatSession).where(ChatSession.id == session_id))
        return result.scalars().first()

    async def get_user_sessions(self, user_id: int, skip: int = 0, limit: int = 100) -> List[ChatSession]:
        """Lấy danh sách các phiên trò chuyện của người dùng, sắp xếp updated_at DESC."""
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_user_sessions(self, user_id: int) -> int:
        """Đếm tổng số phiên trò chuyện của user."""
        stmt = select(func.count(ChatSession.id)).where(ChatSession.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def update_session_title(self, session: ChatSession, title: str) -> ChatSession:
        """Cập nhật tiêu đề phiên chat."""
        session.title = title
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def update_session_updated_at(self, session: ChatSession) -> None:
        """Cập nhật mốc thời gian updated_at cho session."""
        session.updated_at = func.now()
        self.db.add(session)
        await self.db.commit()

    async def delete_session(self, session: ChatSession) -> None:
        """Xóa phiên trò chuyện (tin nhắn tự động xóa theo cascade)."""
        await self.db.delete(session)
        await self.db.commit()

    async def create_message(self, session_id: int, sender: str, content: str) -> ChatMessage:
        """Lưu một tin nhắn mới vào DB."""
        message = ChatMessage(session_id=session_id, sender=sender, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_session_messages(self, session_id: int) -> List[ChatMessage]:
        """Lấy toàn bộ lịch sử tin nhắn trong một phiên (sắp xếp created_at ASC)."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_session_messages(self, session_id: int) -> int:
        """Đếm số tin nhắn hiện tại trong phiên."""
        stmt = select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
