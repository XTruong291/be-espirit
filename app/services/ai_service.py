import asyncio


class AIService:
    """
    Mock AI Service giả lập câu trả lời của Trợ lý Tâm linh / Thờ cúng (E-Spirit).
    Thiết kế tách biệt độc lập để sau này chỉ cần thay ruột bằng LLM/RAG engine thực sự.
    """

    async def generate_reply(self, session_id: int, user_message: str) -> str:
        """
        Sinh câu trả lời giả lập mang ngữ cảnh tâm linh dựa trên nội dung tin nhắn.
        """
        # Giả lập thời gian phản hồi bất đồng bộ (500ms)
        await asyncio.sleep(0.5)

        lowered = user_message.lower()

        if any(w in lowered for w in ["văn khấn", "khấn"]):
            return (
                "Nam mô A Di Đà Phật! Về lễ nghi và bài văn khấn, bạn nên chuẩn bị trang phục chỉnh tề, "
                "thắp 3 nén hương thơm, giữ tâm thanh tịnh và đọc thành tâm từ trong tâm khảm. "
                "Bạn cần bài văn khấn cụ thể cho dịp nào (Rằm, Mùng 1, Gia tiên, hay Táo quân)?"
            )
        elif any(w in lowered for w in ["thắp hương", "hương", "nhang"]):
            return (
                "Khi thắp hương, thói quen tốt nhất là thắp số nén lẻ (1, 3 hoặc 5 nén). "
                "1 nén đại diện cho Tâm hương, 3 nén đại diện cho Tam bảo (Phật - Pháp - Tăng) hoặc Tam tài (Thiên - Địa - Nhân). "
                "Hãy giữ ngọn lửa thắp hương bằng cả hai tay với lòng thành kính."
            )
        elif any(w in lowered for w in ["phong thủy", "hướng", "bàn thờ"]):
            return (
                "Về vị trí đặt bàn thờ: Bàn thờ nên được đặt ở vị trí 'tọa cát hướng cát', nơi tĩnh lặng và trang trọng nhất trong nhà. "
                "Nên tránh đặt bàn thờ đối diện cửa nhà vệ sinh, dưới xà ngang hoặc nơi có luồng gió thổi trực tiếp."
            )
        elif any(w in lowered for w in ["lễ vật", "mâm cúng", "sắm lễ"]):
            return (
                "Mâm cúng dâng lên Gia tiên và Chư Phật cốt ở lòng thành. Lễ vật cơ bản gồm: Hương, Hoa tươi, "
                "Đăng (đèn/nến), Trà, Quả sạch, Trầu cau cùng mâm cơm thanh khiết được chuẩn bị chu đáo."
            )
        else:
            return (
                f"Dạ, về thắc mắc '{user_message}', Trợ lý E-Spirit xin đồng hành cùng gia chủ. "
                "Trong văn hóa thờ cúng tâm linh, lòng thành kính và sự thanh tịnh là điều cốt lõi nhất. "
                "Bạn có muốn E-Spirit hỗ trợ thêm thông tin chi tiết nào khác không?"
            )
