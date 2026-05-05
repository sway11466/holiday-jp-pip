"""HolidayJP.is_support_date() のテスト。"""

from datetime import date

from holiday_jp import HolidayJP


def test_support_by_date() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_support_date(date(2021, 1, 10)) is True


def test_support_by_dict() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_support_date({"year": 2021, "month": 1, "date": 10}) is True


def test_invalid_calendar_day_is_still_supported_year() -> None:
    """カレンダー上ありえない日でも、年が範囲内なら True。"""
    holidayjp = HolidayJP()
    assert holidayjp.is_support_date({"year": 2021, "month": 1, "date": 32}) is True


def test_older_than_min_year_is_unsupported() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_support_date({"year": 1954, "month": 1, "date": 1}) is False


def test_newer_than_max_year_is_unsupported() -> None:
    holidayjp = HolidayJP()
    assert holidayjp.is_support_date({"year": 2099, "month": 1, "date": 1}) is False


def test_no_year_is_supported() -> None:
    """年を持たない条件は範囲外と判定しない。"""
    holidayjp = HolidayJP()
    assert holidayjp.is_support_date({"name": "元日"}) is True
