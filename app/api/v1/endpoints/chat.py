from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_current_user, get_chat_service
from app.models.user import User
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse,
)
from app.services.chat_service import ChatService

router = APIRouter()


@router.get("/sessions", response_model=ChatSessionListResponse, summary="Lấy danh sách các phiên trò chuyện")
async def get_sessions(
    skip: int = Query(0, ge=0, description="Số lượng bỏ qua"),
    limit: int = Query(100, ge=1, le=500, description="Số lượng lấy tối đa"),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Lấy danh sách tất cả các phiên trò chuyện của người dùng đang đăng nhập (sắp xếp theo updated_at mới nhất).
    """
    sessions, total = await chat_service.get_user_sessions(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return ChatSessionListResponse(items=sessions, total=total)


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED, summary="Tạo mới một phiên trò chuyện")
async def create_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Tạo mới một phiên trò chuyện (Chat Session).
    """
    title = payload.title or "Phiên trò chuyện mới"
    session = await chat_service.create_session(user_id=current_user.id, title=title)
    return session


@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse, summary="Lấy lịch sử tin nhắn trong phiên trò chuyện")
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Lấy toàn bộ lịch sử tin nhắn trong phiên chat.
    Trả về lỗi 404 Not Found nếu phiên không tồn tại hoặc thuộc về người dùng khác.
    """
    session, messages = await chat_service.get_session_messages(
        session_id=session_id,
        user_id=current_user.id
    )
    return ChatHistoryResponse(
        session_id=session.id,
        session_title=session.title,
        messages=messages
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED, summary="Gửi tin nhắn và nhận câu trả lời từ AI Assistant")
async def send_message(
    session_id: int,
    payload: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Gửi tin nhắn trong phiên trò chuyện và nhận câu trả lời giả lập từ E-Spirit Mock AI Service.
    - Lưu tin nhắn của user vào DB trước.
    - Tự động cập nhật tên phiên chat nếu là tin nhắn đầu tiên.
    - Trả về câu trả lời của trợ lý AI.
    """
    _, assistant_msg = await chat_service.send_message(
        session_id=session_id,
        user_id=current_user.id,
        content=payload.content
    )
    return assistant_msg


@router.delete("/sessions/{session_id}", summary="Xóa phiên trò chuyện")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Xóa phiên trò chuyện kèm toàn bộ tin nhắn liên quan.
    Trả về 404 Not Found nếu không có quyền sở hữu.
    """
    await chat_service.delete_session(session_id=session_id, user_id=current_user.id)
    return {"success": True, "message": f"Đã xóa thành công phiên trò chuyện ID {session_id}."}
