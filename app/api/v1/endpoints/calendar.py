from datetime import datetime
from fastapi import APIRouter, Query

from app.core.exceptions import BadRequestException
from app.schemas.calendar import (
    LunarDateResponse,
    MonthCalendarResponse,
    AuspiciousHoursResponse,
    LunarToSolarResponse,
)
from app.utils.lunar_calendar import (
    solar_to_lunar,
    lunar_to_solar,
    get_today_lunar_info,
    get_month_lunar_info,
)

router = APIRouter()


@router.get("/today", response_model=LunarDateResponse, summary="Lấy chi tiết Lịch Âm - Dương ngày hiện tại")
async def get_today():
    """
    Trả về chi tiết thông tin Âm lịch, Can Chi, Sự kiện tâm linh và 12 khung giờ Hoàng Đạo của ngày hiện tại.
    Bắt buộc tính theo múi giờ Việt Nam (`Asia/Ho_Chi_Minh` - UTC+7).
    """
    return get_today_lunar_info()


@router.get("/convert-solar", response_model=LunarDateResponse, summary="Chuyển đổi Dương lịch sang Âm lịch")
async def convert_solar(
    date_str: str = Query(..., alias="date", description="Ngày dương lịch theo định dạng YYYY-MM-DD", examples=["2026-09-08"])
):
    """
    Chuyển đổi một ngày Dương lịch bất kỳ sang Âm lịch Việt Nam.
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise BadRequestException("Định dạng ngày không hợp lệ. Vui lòng truyền định dạng YYYY-MM-DD (Ví dụ: 2026-09-08).")

    return solar_to_lunar(dt.day, dt.month, dt.year)


@router.get("/convert-lunar", response_model=LunarToSolarResponse, summary="Chuyển đổi Âm lịch sang Dương lịch")
async def convert_lunar(
    day: int = Query(..., ge=1, le=30, description="Ngày âm lịch (1 - 30)", examples=[15]),
    month: int = Query(..., ge=1, le=12, description="Tháng âm lịch (1 - 12)", examples=[1]),
    year: int = Query(..., ge=1800, le=2199, description="Năm âm lịch (1800 - 2199)", examples=[2026]),
    is_leap: bool = Query(False, alias="is_leap_month", description="Có phải tháng nhuận âm lịch hay không", examples=[False]),
):
    """
    Chuyển đổi ngày Âm lịch sang Dương lịch tương ứng.
    """
    return lunar_to_solar(lunar_day=day, lunar_month=month, lunar_year=year, is_leap_month=is_leap)


@router.get("/month", response_model=MonthCalendarResponse, summary="Lấy lịch Âm - Dương toàn bộ một tháng")
async def get_month(
    year: int = Query(..., ge=1800, le=2199, description="Năm cần tra cứu", examples=[2026]),
    month: int = Query(..., ge=1, le=12, description="Tháng cần tra cứu (1 - 12)", examples=[9]),
):
    """
    Lấy toàn bộ dữ liệu lịch của một tháng dương lịch (kèm thông tin ngày âm của từng ngày)
    để Frontend dễ dàng render giao diện Calendar Grid.
    """
    return get_month_lunar_info(year=year, month=month)


@router.get("/auspicious-hours", response_model=AuspiciousHoursResponse, summary="Tra cứu Giờ Hoàng Đạo trong ngày")
async def get_auspicious_hours_endpoint(
    date_str: str = Query(..., alias="date", description="Ngày dương lịch theo định dạng YYYY-MM-DD", examples=["2026-09-08"])
):
    """
    Tra cứu chi tiết 12 canh giờ (Hoàng Đạo & Hắc Đạo) kèm tên sao trực nhật của ngày chọn.
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise BadRequestException("Định dạng ngày không hợp lệ. Vui lòng truyền định dạng YYYY-MM-DD (Ví dụ: 2026-09-08).")

    info = solar_to_lunar(dt.day, dt.month, dt.year)
    return AuspiciousHoursResponse(
        solar_date=info["solar_date"],
        can_chi_day=info["can_chi_day"],
        hours=info["auspicious_hours"]
    )

