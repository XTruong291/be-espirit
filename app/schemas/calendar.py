from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class HourInfo(BaseModel):
    """Thông tin chi tiết một canh giờ âm lịch."""
    name: str = Field(..., description="Tên canh giờ (ví dụ: Giờ Tý)", example="Giờ Tý")
    time_range: str = Field(..., description="Khung giờ dương lịch (23:00 - 01:00)", example="23:00 - 01:00")
    is_auspicious: bool = Field(..., description="True nếu là giờ Hoàng Đạo, False nếu là Hắc Đạo")
    star_name: str = Field(..., description="Tên sao trực nhật", example="Thanh Long")

    model_config = ConfigDict(from_attributes=True)


class LunarDateResponse(BaseModel):
    """Thông tin ngày Âm - Dương lịch đầy đủ."""
    solar_date: str = Field(..., description="Ngày dương lịch YYYY-MM-DD", example="2026-09-08")
    day: int = Field(..., example=8)
    month: int = Field(..., example=9)
    year: int = Field(..., example=2026)
    day_of_week: str = Field(..., example="Thứ Ba")
    lunar_day: int = Field(..., description="Ngày âm lịch", example=28)
    lunar_month: int = Field(..., description="Tháng âm lịch", example=7)
    lunar_year: int = Field(..., description="Năm âm lịch", example=2026)
    is_leap_month: bool = Field(False, description="Cờ đánh dấu tháng nhuận")
    can_chi_year: str = Field(..., description="Can chi của năm", example="Bính Ngọ")
    can_chi_month: str = Field(..., description="Can chi của tháng", example="Bính Thân")
    can_chi_day: str = Field(..., description="Can chi của ngày", example="Canh Thìn")
    is_first_day: bool = Field(False, description="Cờ đánh dấu Ngày Mồng Một")
    is_full_moon: bool = Field(False, description="Cờ đánh dấu Ngày Rằm")
    special_event: Optional[str] = Field(None, description="Tên sự kiện đặc biệt (Tết, Rằm tháng Giêng, ...)")
    spiritual_reminder: Optional[str] = Field(None, description="Thông điệp/lời nhắc tâm linh gợi ý")
    auspicious_hours: List[HourInfo] = Field(default_factory=list, description="Danh sách 12 canh giờ hoàng/hắc đạo")

    model_config = ConfigDict(from_attributes=True)


class MonthCalendarResponse(BaseModel):
    """Dữ liệu toàn bộ một tháng dương lịch cho giao diện Calendar Grid."""
    year: int = Field(..., example=2026)
    month: int = Field(..., example=9)
    total_days: int = Field(..., example=30)
    days: List[LunarDateResponse]

    model_config = ConfigDict(from_attributes=True)


class AuspiciousHoursResponse(BaseModel):
    """Danh sách các giờ Hoàng Đạo và Hắc Đạo trong ngày."""
    solar_date: str = Field(..., example="2026-09-08")
    can_chi_day: str = Field(..., example="Canh Thìn")
    hours: List[HourInfo]

    model_config = ConfigDict(from_attributes=True)


class LunarToSolarResponse(BaseModel):
    """Kết quả chuyển đổi từ Âm lịch sang Dương lịch."""
    lunar_date: str = Field(..., example="2026-01-15")
    is_leap_month: bool = Field(False)
    solar_date: str = Field(..., example="2026-03-03")
    solar_day: int = Field(..., example=3)
    solar_month: int = Field(..., example=3)
    solar_year: int = Field(..., example=2026)

    model_config = ConfigDict(from_attributes=True)
