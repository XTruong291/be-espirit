from typing import List, Tuple
from app.models.chat import ChatSession, ChatMessage
from app.repositories.chat_repository import ChatRepository
from app.services.ai_service import AIService
from app.core.exceptions import NotFoundException


class ChatService:
    """
    Tầng Nghiệp vụ (Business Service) xử lý logic phiên trò chuyện và nhắn tin với AI Assistant.
    """
    def __init__(self, chat_repo: ChatRepository, ai_service: AIService):
        self.chat_repo = chat_repo
        self.ai_service = ai_service

    async def create_session(self, user_id: int, title: str = "Phiên trò chuyện mới") -> ChatSession:
        """Tạo một phiên trò chuyện mới cho người dùng."""
        return await self.chat_repo.create_session(user_id=user_id, title=title)

    async def get_user_sessions(self, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[ChatSession], int]:
        """Lấy danh sách các phiên chat của user kèm tổng số lượng."""
        sessions = await self.chat_repo.get_user_sessions(user_id=user_id, skip=skip, limit=limit)
        total = await self.chat_repo.count_user_sessions(user_id=user_id)
        return sessions, total

    async def _get_verified_session(self, session_id: int, user_id: int) -> ChatSession:
        """
        Helper kiểm tra sự tồn tại và quyền sở hữu session.
        Nếu không tồn tại hoặc thuộc về user khác -> Trả về 404 Not Found để ngăn ngừa dò quét ID.
        """
        session = await self.chat_repo.get_session_by_id(session_id)
        if not session or session.user_id != user_id:
            raise NotFoundException("Không tìm thấy phiên trò chuyện.")
        return session

    async def get_session_messages(self, session_id: int, user_id: int) -> Tuple[ChatSession, List[ChatMessage]]:
        """Lấy toàn bộ lịch sử tin nhắn của phiên trò chuyện."""
        session = await self._get_verified_session(session_id=session_id, user_id=user_id)
        messages = await self.chat_repo.get_session_messages(session_id=session_id)
        return session, messages

    async def send_message(self, session_id: int, user_id: int, content: str) -> Tuple[ChatMessage, ChatMessage]:
        """
        Xử lý gửi tin nhắn:
        1. Xác thực quyền sở hữu session (404 Not Found nếu không hợp lệ).
        2. Tự động cập nhật title nếu đây là tin nhắn đầu tiên và title đang ở dạng mặc định.
        3. Lưu & commit tin nhắn của USER trước để đảm bảo không mất dữ liệu nếu AI lỗi.
        4. Gọi AIService lấy phản hồi giả lập.
        5. Lưu & commit tin nhắn của ASSISTANT và cập nhật updated_at của session.
        """
        session = await self._get_verified_session(session_id=session_id, user_id=user_id)

        # Cập nhật title bằng 30 ký tự đầu của tin nhắn user nếu là tin nhắn đầu tiên
        msg_count = await self.chat_repo.count_session_messages(session_id=session_id)
        if msg_count == 0 and session.title == "Phiên trò chuyện mới":
            new_title = content.strip()[:30]
            if new_title:
                await self.chat_repo.update_session_title(session, new_title)

        # 1. Lưu tin nhắn của User trước
        user_msg = await self.chat_repo.create_message(
            session_id=session_id,
            sender="user",
            content=content
        )

        # 2. Gọi Mock AI Service sinh câu trả lời
        ai_reply = await self.ai_service.generate_reply(
            session_id=session_id,
            user_message=content
        )

        # 3. Lưu tin nhắn của Assistant và cập nhật mốc thời gian session
        assistant_msg = await self.chat_repo.create_message(
            session_id=session_id,
            sender="assistant",
            content=ai_reply
        )
        await self.chat_repo.update_session_updated_at(session)

        return user_msg, assistant_msg

    async def delete_session(self, session_id: int, user_id: int) -> None:
        """Xóa phiên trò chuyện kèm toàn bộ lịch sử tin nhắn."""
        session = await self._get_verified_session(session_id=session_id, user_id=user_id)
        await self.chat_repo.delete_session(session)
