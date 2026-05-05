"""HolidayJP.is_weekend() のテスト。"""

from datetime import date, datetime, timedelta, timezone

import pytest

from holiday_jp import HolidayJP, InvalidDateError, JST, UnsupportedDateError

def test_saturday_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekend(date(2021, 5, 8)) is True  # 土曜

def test_saturday_by_dict() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekend({"year": 2021, "month": 5, "date": 8}) is True

def test_monday_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekend(date(2021, 5, 10)) is False  # 月曜

def test_monday_by_dict() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekend({"year": 2021, "month": 5, "date": 10}) is False

def test_invalid_date_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(InvalidDateError):
        holidayjp.is_weekend({"year": 2021, "month": 5, "date": 32})

def test_missing_field_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(InvalidDateError):
        holidayjp.is_weekend({"year": 2021, "month": 5})

def test_older_year_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_weekend({"year": 1954, "month": 1, "date": 1})

def test_newer_year_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_weekend({"year": 2099, "month": 1, "date": 1})

def test_unsupported_year_older_with_ignore_uses_calendar() -> None:
    """ignore モード: サポート外（過去）でもカレンダー上の曜日で判定する。"""
    holidayjp = HolidayJP(unsupported_date_behavior="ignore")
    # 1954/1/1 は金曜 → 週末でない
    assert holidayjp.is_weekend({"year": 1954, "month": 1, "date": 1}) is False
    # 1954/1/2 は土曜 → 週末
    assert holidayjp.is_weekend({"year": 1954, "month": 1, "date": 2}) is True

def test_unsupported_year_future_with_ignore_uses_calendar() -> None:
    """ignore モード: サポート外（未来）でもカレンダー上の曜日で判定する。"""
    holidayjp = HolidayJP(unsupported_date_behavior="ignore")
    # 2099/1/1 は木曜 → 週末でない
    assert holidayjp.is_weekend({"year": 2099, "month": 1, "date": 1}) is False
    # 2099/1/3 は土曜 → 週末
    assert holidayjp.is_weekend({"year": 2099, "month": 1, "date": 3}) is True

def test_datetime_jst_saturday() -> None:
    holidayjp = HolidayJP()
    dt = datetime(2021, 5, 8, 15, 0, tzinfo=JST)
    assert holidayjp.is_weekend(dt) is True

def test_datetime_utc_converts_to_jst_next_day() -> None:
    """UTC 15:00 → JST 翌 00:00。土曜 5/8 15:00 UTC → JST 5/9 00:00（日曜だが日曜は週末）。"""
    holidayjp = HolidayJP()
    dt = datetime(2021, 5, 8, 15, 0, tzinfo=timezone.utc)
    assert holidayjp.is_weekend(dt) is True  # 5/9 日曜
    # 月曜にずれるケース
    dt2 = datetime(2021, 5, 9, 15, 0, tzinfo=timezone.utc)  # JST 5/10 月曜
    assert holidayjp.is_weekend(dt2) is False

def test_timezone_effect_false_uses_raw_ymd() -> None:
    holidayjp = HolidayJP(timezone_effect=False)
    dt = datetime(2021, 5, 9, 15, 0, tzinfo=timezone.utc)  # raw は 5/9 日曜
    assert holidayjp.is_weekend(dt) is True

def test_custom_weekend_thursday_only() -> None:
    """weekend=[3]（木曜のみ）。土曜は週末でない、木曜は週末。"""
    holidayjp = HolidayJP(weekend=[3])
    assert holidayjp.is_weekend(date(2021, 5, 8)) is False  # 土曜
    assert holidayjp.is_weekend(date(2021, 5, 6)) is True  # 木曜
