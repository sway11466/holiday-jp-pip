"""HolidayJP.is_holiday() のテスト。"""

from datetime import date, datetime, timedelta, timezone

import pytest

from holiday_jp import Holiday, HolidayJP, InvalidDateError, JST, UnsupportedDateError

def test_holiday_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_holiday(date(2021, 5, 3)) is True  # 憲法記念日

def test_holiday_by_dict() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_holiday({"year": 2021, "month": 5, "date": 3}) is True

def test_not_holiday_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_holiday(date(2021, 5, 20)) is False

def test_not_holiday_by_dict() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_holiday({"year": 2021, "month": 5, "date": 20}) is False

def test_invalid_date_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(InvalidDateError):
        holidayjp.is_holiday({"year": 2021, "month": 5, "date": 32})

def test_missing_field_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(InvalidDateError):
        holidayjp.is_holiday({"year": 2021, "month": 5})

def test_older_year_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_holiday({"year": 1954, "month": 1, "date": 1})

def test_newer_year_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_holiday({"year": 2099, "month": 1, "date": 1})

def test_unsupported_year_returns_false_with_ignore() -> None:
    holidayjp = HolidayJP(unsupported_date_behavior="ignore")
    assert holidayjp.is_holiday({"year": 1954, "month": 1, "date": 1}) is False
    assert holidayjp.is_holiday({"year": 2099, "month": 1, "date": 1}) is False

def test_datetime_jst_is_a_holiday() -> None:
    holidayjp = HolidayJP()
    dt = datetime(2021, 2, 11, 15, 0, tzinfo=JST)  # JST 15:00 → JST 2/11 (建国記念の日)
    assert holidayjp.is_holiday(dt) is True

def test_datetime_utc_converts_to_jst_next_day() -> None:
    """UTC 15:00 = JST 翌 0:00。建国記念日 2/11 15:00 UTC → JST 2/12（祝日でない）。"""
    holidayjp = HolidayJP()
    dt = datetime(2021, 2, 11, 15, 0, tzinfo=timezone.utc)
    assert holidayjp.is_holiday(dt) is False

def test_timezone_effect_false_uses_raw_ymd_on_utc_input() -> None:
    """timezone_effect=False + UTC tzinfo: tzinfo を無視して year/month/day をそのまま使う。"""
    holidayjp = HolidayJP(timezone_effect=False)
    dt = datetime(2021, 2, 11, 15, 0, tzinfo=timezone.utc)
    # raw ymd は 2/11 で建国記念日として True
    assert holidayjp.is_holiday(dt) is True

def test_timezone_effect_false_uses_raw_ymd_on_jst_input() -> None:
    """timezone_effect=False + JST tzinfo: 結果は変わらず year/month/day をそのまま使う。"""
    holidayjp = HolidayJP(timezone_effect=False)
    dt = datetime(2021, 2, 11, 15, 0, tzinfo=JST)
    assert holidayjp.is_holiday(dt) is True

def test_extends_is_recognized() -> None:
    custom = Holiday(year=2023, month=3, date=10, name="test", local_date=datetime(2023, 3, 10, tzinfo=JST))
    holidayjp = HolidayJP(extends=[custom])
    assert holidayjp.is_holiday({"year": 2023, "month": 3, "date": 10}) is True
