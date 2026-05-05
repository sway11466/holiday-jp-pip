"""HolidayJP.is_weekday() のテスト。"""

from datetime import date, datetime, timedelta, timezone

import pytest

from holiday_jp import Holiday, HolidayJP, InvalidDateError, JST, UnsupportedDateError

def test_friday_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekday(date(2021, 5, 7)) is True  # 金曜・平日

def test_friday_by_dict() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekday({"year": 2021, "month": 5, "date": 7}) is True

def test_saturday_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekday(date(2021, 5, 8)) is False  # 土曜

def test_sunday_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekday(date(2021, 5, 9)) is False  # 日曜

def test_sunday_by_dict() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekday({"year": 2021, "month": 5, "date": 9}) is False

def test_holiday_on_monday_is_not_weekday() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_weekday(date(2021, 5, 3)) is False  # 月曜・憲法記念日

def test_holiday_on_saturday_is_not_weekday() -> None:
    """週末かつ祝日も「平日でない」を満たす。"""
    holidayjp = HolidayJP()
    assert holidayjp.is_weekday(date(2021, 5, 1)) is False  # 土曜

def test_invalid_date_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(InvalidDateError):
        holidayjp.is_weekday({"year": 2021, "month": 5, "date": 32})

def test_missing_field_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(InvalidDateError):
        holidayjp.is_weekday({"year": 2021, "month": 5})

def test_older_year_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_weekday({"year": 1954, "month": 1, "date": 1})

def test_newer_year_raises() -> None:
    holidayjp = HolidayJP()
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_weekday({"year": 2099, "month": 1, "date": 1})

def test_datetime_jst_is_weekday() -> None:
    holidayjp = HolidayJP()
    dt = datetime(2021, 5, 7, 15, 0, tzinfo=JST)  # JST 5/7 金曜
    assert holidayjp.is_weekday(dt) is True

def test_datetime_utc_converts_to_weekend() -> None:
    """金曜 UTC 15:00 → 土曜 JST 00:00（週末扱い）。"""
    holidayjp = HolidayJP()
    dt = datetime(2021, 5, 7, 15, 0, tzinfo=timezone.utc)  # JST 5/8 土曜
    assert holidayjp.is_weekday(dt) is False

def test_timezone_effect_false_uses_raw_ymd() -> None:
    """timezone_effect=False では tzinfo を無視して year/month/day をそのまま使う。"""
    holidayjp = HolidayJP(timezone_effect=False)
    dt = datetime(2021, 5, 7, 15, 0, tzinfo=timezone.utc)  # raw ymd 5/7 金曜
    assert holidayjp.is_weekday(dt) is True

def test_unsupported_with_ignore_older() -> None:
    """ignore: 週末でなければ平日扱い（祝日は無いという前提）。"""
    holidayjp = HolidayJP(unsupported_date_behavior="ignore")
    # 1954/1/1 金曜 → 平日
    assert holidayjp.is_weekday({"year": 1954, "month": 1, "date": 1}) is True
    # 1954/1/2 土曜 → 平日でない
    assert holidayjp.is_weekday({"year": 1954, "month": 1, "date": 2}) is False

def test_unsupported_with_ignore_future_weekday() -> None:
    """ignore: 将来年の平日 → True（祝日は無いという前提）。"""
    holidayjp = HolidayJP(unsupported_date_behavior="ignore")
    # 2099/1/1 木曜
    assert holidayjp.is_weekday({"year": 2099, "month": 1, "date": 1}) is True

def test_unsupported_with_ignore_future_weekend() -> None:
    """ignore: 将来年の週末 → False。"""
    holidayjp = HolidayJP(unsupported_date_behavior="ignore")
    # 2099/1/3 土曜
    assert holidayjp.is_weekday({"year": 2099, "month": 1, "date": 3}) is False

def test_extends_makes_weekday_into_not_weekday() -> None:
    """extends で平日が祝日になる → is_weekday は False。"""
    custom = Holiday(year=2023, month=3, date=10, name="test", local_date=datetime(2023, 3, 10, tzinfo=JST))
    holidayjp = HolidayJP(extends=[custom])
    # 2023/3/10 は元は金曜・平日
    assert holidayjp.is_weekday({"year": 2023, "month": 3, "date": 10}) is False
