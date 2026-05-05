"""HolidayJP.is_valid_date() のテスト。"""

from datetime import date, datetime

from holiday_jp import use_holiday_jp


def test_valid_by_date() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_valid_date(date(2021, 5, 3)) is True


def test_valid_by_datetime() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_valid_date(datetime(2021, 5, 3, 12, 0, 0)) is True


def test_valid_by_dict() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_valid_date({"year": 2021, "month": 5, "date": 3}) is True


def test_invalid_by_dict_with_bad_day() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_valid_date({"year": 2021, "month": 1, "date": 32}) is False


def test_invalid_by_dict_missing_field() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_valid_date({"year": 2021, "month": 1}) is False
