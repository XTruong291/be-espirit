import math
from datetime import datetime, date, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Tuple, Dict, Any, List, Optional

# Múi giờ Việt Nam UTC+7 (Hỗ trợ ZoneInfo và fallback khi chạy trên Windows chưa cài tzdata)
try:
    VN_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
except ZoneInfoNotFoundError:
    VN_TIMEZONE = timezone(timedelta(hours=7))

TZ_OFFSET = 7.0

# Các hằng số cố định (Khai báo ngoài loop để tối ưu RAM & CPU)
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
DAY_OF_WEEK_VN = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

# 12 Canh giờ âm lịch theo phong thủy (Giờ Tý: 23:00 - 01:00)
HOURS_DEFINITION = [
    {"name": "Tý", "time_range": "23:00 - 01:00", "index": 0},
    {"name": "Sửu", "time_range": "01:00 - 03:00", "index": 1},
    {"name": "Dần", "time_range": "03:00 - 05:00", "index": 2},
    {"name": "Mão", "time_range": "05:00 - 07:00", "index": 3},
    {"name": "Thìn", "time_range": "07:00 - 09:00", "index": 4},
    {"name": "Tỵ", "time_range": "09:00 - 11:00", "index": 5},
    {"name": "Ngọ", "time_range": "11:00 - 13:00", "index": 6},
    {"name": "Mùi", "time_range": "13:00 - 15:00", "index": 7},
    {"name": "Thân", "time_range": "15:00 - 17:00", "index": 8},
    {"name": "Dậu", "time_range": "17:00 - 19:00", "index": 9},
    {"name": "Tuất", "time_range": "19:00 - 21:00", "index": 10},
    {"name": "Hợi", "time_range": "21:00 - 23:00", "index": 11},
]

# Bảng 6 Giờ Hoàng Đạo theo Chi ngày
AUSPICIOUS_HOURS_MAP = {
    0: {0, 1, 3, 6, 8, 9},       # Tý
    1: {2, 3, 5, 8, 10, 11},      # Sửu
    2: {0, 1, 4, 5, 7, 10},       # Dần
    3: {2, 3, 6, 7, 9, 11},       # Mão
    4: {2, 4, 5, 8, 9, 11},       # Thìn
    5: {1, 4, 6, 7, 10, 11},      # Tỵ
    6: {0, 1, 3, 6, 8, 9},       # Ngọ
    7: {2, 3, 5, 8, 10, 11},      # Mùi
    8: {0, 1, 4, 5, 7, 10},       # Thân
    9: {2, 3, 6, 7, 9, 11},       # Dậu
    10: {2, 4, 5, 8, 9, 11},      # Tuất
    11: {1, 4, 6, 7, 10, 11},     # Hợi
}

STAR_NAMES = {
    0: ["Thanh Long", "Minh Đường", "Thiên Hình", "Kim Quỹ", "Bảo Quang", "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Nguyên Vũ", "Tư Mệnh", "Câu Trận", "Chu Tước"],
    1: ["Chu Tước", "Câu Trận", "Thanh Long", "Minh Đường", "Thiên Hình", "Kim Quỹ", "Bảo Quang", "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Nguyên Vũ", "Tư Mệnh"],
    2: ["Thanh Long", "Minh Đường", "Thiên Hình", "Chu Tước", "Kim Quỹ", "Bảo Quang", "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Nguyên Vũ", "Tư Mệnh", "Câu Trận"],
    3: ["Nguyên Vũ", "Tư Mệnh", "Thanh Long", "Minh Đường", "Thiên Hình", "Chu Tước", "Kim Quỹ", "Bảo Quang", "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Câu Trận"],
    4: ["Bạch Hổ", "Ngọc Đường", "Thanh Long", "Thiên Hình", "Minh Đường", "Kim Quỹ", "Bảo Quang", "Câu Trận", "Tư Mệnh", "Thiên Lao", "Nguyên Vũ", "Chu Tước"],
    5: ["Nguyên Vũ", "Tư Mệnh", "Câu Trận", "Bạch Hổ", "Thanh Long", "Minh Đường", "Kim Quỹ", "Bảo Quang", "Thiên Hình", "Ngọc Đường", "Thiên Lao", "Chu Tước"],
}


def jdn(d: int, m: int, y: int) -> int:
    """Tính số ngày Julian (Julian Day Number)."""
    a = (14 - m) // 12
    y1 = y + 4800 - a
    m1 = m + 12 * a - 3
    return d + (153 * m1 + 2) // 5 + 365 * y1 + y1 // 4 - y1 // 100 + y1 // 400 - 32045


def get_new_moon_day(k: int, time_zone: float = TZ_OFFSET) -> int:
    """Tính ngày Sóc (New Moon) thứ k theo thuật toán Hồ Ngọc Đức (gốc 1900)."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = math.pi / 180.0
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)

    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.1516 + 390.67050646 * k - 0.0016541 * T2 - 0.00000164 * T3

    pt = -0.40720 * math.sin(Mpr * dr) \
         + 0.17241 * math.sin(M * dr) \
         + 0.01608 * math.sin(2 * Mpr * dr) \
         + 0.01039 * math.sin(2 * F * dr) \
         + 0.00739 * math.sin((Mpr - M) * dr) \
         - 0.00514 * math.sin((Mpr + M) * dr) \
         + 0.00208 * math.sin(2 * M * dr) \
         - 0.00111 * math.sin((Mpr - 2 * F) * dr) \
         - 0.00057 * math.sin((Mpr + 2 * F) * dr) \
         + 0.00056 * math.sin((2 * Mpr + M) * dr) \
         - 0.00042 * math.sin(2 * Mpr * dr) \
         + 0.00042 * math.sin((M + 2 * F) * dr) \
         + 0.00038 * math.sin((Mpr - 2 * F) * dr) \
         - 0.00024 * math.sin((2 * Mpr - M) * dr) \
         - 0.00017 * math.sin((259.18 - 1934.14 * T) * dr)
    Jd = Jd1 + pt
    return math.floor(Jd + 0.5 + time_zone / 24.0)


def get_sun_longitude(jdn_val: int, time_zone: float = TZ_OFFSET) -> int:
    """Tính kinh độ Mặt Trời (để phân định Tiết khí / Trung khí)."""
    T = (jdn_val - 0.5 - time_zone / 24.0 - 2415020.0) / 36525.0
    T2 = T * T
    dr = math.pi / 180.0
    M = 358.47583 + 35999.04975 * T - 0.000150 * T2
    L0 = 279.69668 + 36000.76892 * T + 0.0003025 * T2
    DL = (1.919460 - 0.004789 * T - 0.000014 * T2) * math.sin(M * dr) \
         + (0.020094 - 0.000100 * T) * math.sin(2 * M * dr) \
         + 0.000293 * math.sin(3 * M * dr)
    L = L0 + DL
    L = (L % 360 + 360) % 360
    return int(L // 30)


def get_lunar_month11(yy: int, time_zone: float = TZ_OFFSET) -> int:
    """Xác định tháng 11 âm lịch (tháng chứa Đông Chí) của năm yy."""
    off = jdn(31, 12, yy) - 2415021
    k = math.floor(off / 29.530588853)
    nm = get_new_moon_day(k, time_zone)
    sun_long = get_sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = get_new_moon_day(k - 1, time_zone)
    return nm


def get_leap_month_offset(a11: int, time_zone: float = TZ_OFFSET) -> int:
    """Xác định vị trí tháng nhuận."""
    k = math.floor((a11 - 2415021.0) / 29.530588853 + 0.5)
    last_sun_long = get_sun_longitude(get_new_moon_day(k, time_zone), time_zone)
    i = 1
    arc = last_sun_long
    while True:
        nm = get_new_moon_day(k + i, time_zone)
        sun_long = get_sun_longitude(nm, time_zone)
        if sun_long == arc:
            return i
        arc = sun_long
        i += 1
        if i > 14:
            break
    return 0


def get_auspicious_hours(chi_day_idx: int) -> List[Dict[str, Any]]:
    """Tính 12 khung giờ Hoàng Đạo / Hắc Đạo của ngày."""
    auspicious_indices = AUSPICIOUS_HOURS_MAP.get(chi_day_idx, set())
    star_names = STAR_NAMES.get(chi_day_idx % 6, STAR_NAMES[0])

    hours_list = []
    for h in HOURS_DEFINITION:
        idx = h["index"]
        is_yellow = idx in auspicious_indices
        hours_list.append({
            "name": f"Giờ {h['name']}",
            "time_range": h["time_range"],
            "is_auspicious": is_yellow,
            "star_name": star_names[idx] if idx < len(star_names) else ("Thanh Long" if is_yellow else "Hắc Đạo")
        })
    return hours_list


def get_spiritual_info(l_day: int, l_month: int, is_first: bool, is_full: bool) -> Tuple[Optional[str], Optional[str]]:
    """Xác định sự kiện tâm linh và lời nhắc nhở."""
    special_event = None
    spiritual_reminder = None

    if l_month == 1 and l_day == 1:
        special_event = "Tết Nguyên Đán"
        spiritual_reminder = "Đầu năm thắp hương gia tiên cầu một năm bình an, may mắn, vạn sự như ý."
    elif l_month == 1 and l_day == 15:
        special_event = "Tết Thượng Nguyên (Rằm Tháng Giêng)"
        spiritual_reminder = "Cúng Rằm tháng Giêng - Cầu an cả năm. Chuẩn bị mâm lễ thanh tịnh dâng gia tiên và chư Phật."
    elif l_month == 3 and l_day == 3:
        special_event = "Tết Hàn Thực"
        spiritual_reminder = "Chuẩn bị bánh trôi, bánh chay tưởng nhớ tổ tiên và nguồn cội."
    elif l_month == 4 and l_day == 15:
        special_event = "Lễ Phật Đản"
        spiritual_reminder = "Kỷ niệm Đức Phật Đản sinh. Làm nhiều việc thiện, phát tâm bồ đề, giữ tâm thanh tịnh."
    elif l_month == 5 and l_day == 5:
        special_event = "Tết Đoan Ngọ"
        spiritual_reminder = "Giết sâu bọ, ăn hoa quả mùa hè, nếp cẩm, bánh tro dâng cúng gia tiên."
    elif l_month == 7 and l_day == 15:
        special_event = "Tết Trung Nguyên (Vu Lan Báo Hiếu)"
        spiritual_reminder = "Mùa Vu Lan báo hiếu cha mẹ, gia tiên và cúng chúng sinh xá tội vong nhân."
    elif l_month == 8 and l_day == 15:
        special_event = "Tết Trung Thu"
        spiritual_reminder = "Tết đoàn viên gia đình. Chuẩn bị bánh trung thu, mâm ngũ quả dâng cúng gia tiên."
    elif l_month == 12 and l_day == 23:
        special_event = "Tết Táo Quân (23 tháng Chạp)"
        spiritual_reminder = "Sắm lễ cúng tiễn Táo Quân vỗ cánh về trời báo cáo ngọc hoàng."
    elif l_month == 12 and l_day in (29, 30):
        special_event = "Lễ Tất Niên"
        spiritual_reminder = "Chuẩn bị mâm cơm Tất Niên tri ân tổ tiên, khép lại năm cũ đón năm mới."
    elif is_first:
        special_event = "Ngày Mồng Một"
        spiritual_reminder = "Ngày Sóc - Thắp hương gia tiên, giữ tâm thanh tịnh, cầu bình an đầu tháng."
    elif is_full:
        special_event = "Ngày Rằm"
        spiritual_reminder = "Ngày Vọng - Thắp hương ngày Rằm, phát tâm hướng thiện, làm việc lành."

    return special_event, spiritual_reminder


def solar_to_lunar(day: int, month: int, year: int, time_zone: float = TZ_OFFSET) -> Dict[str, Any]:
    """Chuyển đổi Dương lịch sang Âm lịch Việt Nam (Chuẩn Hồ Ngọc Đức)."""
    day_number = jdn(day, month, year)
    k = math.floor((day_number - 2415021.076998695) / 29.530588853)
    month_start = get_new_moon_day(k + 1, time_zone)
    if month_start > day_number:
        month_start = get_new_moon_day(k, time_zone)
    else:
        k = k + 1

    a11 = get_lunar_month11(year, time_zone)
    b11 = a11
    if a11 >= month_start:
        lunar_year = year
        a11 = get_lunar_month11(year - 1, time_zone)
    else:
        lunar_year = year + 1
        b11 = get_lunar_month11(year + 1, time_zone)

    lunar_day = day_number - month_start + 1
    diff = math.floor((month_start - a11) / 29.0)
    lunar_leap = False
    lunar_month = diff + 11

    if b11 - a11 > 365:
        leap_month_diff = get_leap_month_offset(a11, time_zone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = True

    if lunar_month > 12:
        lunar_month = lunar_month - 12
    if lunar_month >= 11 and month_start < a11:
        lunar_year = lunar_year - 1

    # Can Chi
    can_year_idx = (lunar_year + 6) % 10
    chi_year_idx = (lunar_year + 8) % 12
    can_chi_year = f"{CAN[can_year_idx]} {CHI[chi_year_idx]}"

    can_month_idx = (can_year_idx * 2 + lunar_month + 1) % 10
    chi_month_idx = (lunar_month + 1) % 12
    can_chi_month = f"{CAN[can_month_idx]} {CHI[chi_month_idx]}"

    can_day_idx = (day_number + 9) % 10
    chi_day_idx = (day_number + 1) % 12
    can_chi_day = f"{CAN[can_day_idx]} {CHI[chi_day_idx]}"

    dt_obj = date(year, month, day)
    day_of_week = DAY_OF_WEEK_VN[dt_obj.weekday()]

    is_first_day = (lunar_day == 1)
    is_full_moon = (lunar_day == 15)

    special_event, spiritual_reminder = get_spiritual_info(lunar_day, lunar_month, is_first_day, is_full_moon)
    auspicious_hours = get_auspicious_hours(chi_day_idx)

    return {
        "solar_date": f"{year:04d}-{month:02d}-{day:02d}",
        "day": day,
        "month": month,
        "year": year,
        "day_of_week": day_of_week,
        "lunar_day": lunar_day,
        "lunar_month": lunar_month,
        "lunar_year": lunar_year,
        "is_leap_month": lunar_leap,
        "can_chi_year": can_chi_year,
        "can_chi_month": can_chi_month,
        "can_chi_day": can_chi_day,
        "is_first_day": is_first_day,
        "is_full_moon": is_full_moon,
        "special_event": special_event,
        "spiritual_reminder": spiritual_reminder,
        "auspicious_hours": auspicious_hours,
    }


def lunar_to_solar(lunar_day: int, lunar_month: int, lunar_year: int, is_leap_month: bool = False, time_zone: float = TZ_OFFSET) -> Dict[str, Any]:
    """Chuyển đổi Âm lịch sang Dương lịch Việt Nam."""
    if lunar_month < 11:
        a11 = get_lunar_month11(lunar_year - 1, time_zone)
    else:
        a11 = get_lunar_month11(lunar_year, time_zone)

    k = math.floor((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    off = lunar_month - 11
    if off < 0:
        off += 12

    b11 = get_lunar_month11(lunar_year if lunar_month < 11 else lunar_year + 1, time_zone)
    if b11 - a11 > 365:
        leap_off = get_leap_month_offset(a11, time_zone)
        if is_leap_month and off == leap_off:
            off += 1
        elif off > leap_off:
            off += 1

    month_start = get_new_moon_day(k + off, time_zone)
    target_jd = month_start + lunar_day - 1

    a = target_jd + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    s_day = e - (153 * m + 2) // 5 + 1
    s_month = m + 3 - 12 * (m // 10)
    s_year = 100 * b + d - 4800 + m // 10

    return {
        "lunar_date": f"{lunar_year:04d}-{lunar_month:02d}-{lunar_day:02d}",
        "is_leap_month": is_leap_month,
        "solar_date": f"{s_year:04d}-{s_month:02d}-{s_day:02d}",
        "solar_day": s_day,
        "solar_month": s_month,
        "solar_year": s_year,
    }


def get_today_lunar_info() -> Dict[str, Any]:
    """Lấy thông tin Âm lịch của ngày hôm nay theo Múi giờ Asia/Ho_Chi_Minh."""
    now_vn = datetime.now(VN_TIMEZONE)
    return solar_to_lunar(now_vn.day, now_vn.month, now_vn.year)


def get_month_lunar_info(year: int, month: int) -> Dict[str, Any]:
    """Lấy thông tin Âm lịch toàn bộ một tháng Dương lịch (Tối ưu hóa RAM/CPU)."""
    if month in (1, 3, 5, 7, 8, 10, 12):
        days_in_month = 31
    elif month in (4, 6, 9, 11):
        days_in_month = 30
    else:
        is_leap_year = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        days_in_month = 29 if is_leap_year else 28

    days_list = []
    for d in range(1, days_in_month + 1):
        info = solar_to_lunar(d, month, year)
        days_list.append(info)

    return {
        "year": year,
        "month": month,
        "total_days": days_in_month,
        "days": days_list
    }


def get_lunar_context_for_prompt() -> str:
    """Helper trả về chuỗi ngữ cảnh thời gian âm dương hiện tại cho AI Chatbot System Prompt."""
    now_vn = datetime.now(VN_TIMEZONE)
    info = solar_to_lunar(now_vn.day, now_vn.month, now_vn.year)

    lunar_str = f"ngày {info['lunar_day']}/{info['lunar_month']} năm {info['can_chi_year']} Âm lịch"
    if info['is_leap_month']:
        lunar_str += " (Tháng nhuận)"

    res = (
        f"Hôm nay là {info['day_of_week']}, ngày {now_vn.strftime('%d/%m/%Y')} Dương lịch "
        f"(tức {lunar_str}, ngày {info['can_chi_day']}, tháng {info['can_chi_month']})."
    )
    if info['special_event']:
        res += f" Hôm nay là {info['special_event']}."
    if info['spiritual_reminder']:
        res += f" Lời nhắc tâm linh: {info['spiritual_reminder']}"
    return res
