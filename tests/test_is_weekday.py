"""HolidayJP.is_weekday() のテスト。"""

from datetime import date

import pytest

from holiday_jp import InvalidDateError, UnsupportedDateError, use_holiday_jp


def test_normal_weekday() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_weekday(date(2021, 5, 7)) is True  # 金曜・平日


def test_saturday_is_not_weekday() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_weekday(date(2021, 5, 8)) is False  # 土曜


def test_holiday_on_monday_is_not_weekday() -> None:
    holidayjp = use_holiday_jp()
    assert holidayjp.is_weekday(date(2021, 5, 3)) is False  # 月曜・憲法記念日


def test_holiday_on_saturday_is_not_weekday() -> None:
    """週末かつ祝日も「平日でない」を満たす。"""
    holidayjp = use_holiday_jp()
    assert holidayjp.is_weekday(date(2021, 5, 1)) is False  # 土曜


def test_invalid_date_raises() -> None:
    holidayjp = use_holiday_jp()
    with pytest.raises(InvalidDateError):
        holidayjp.is_weekday({"year": 2021, "month": 5, "date": 32})


def test_older_year_raises_by_default() -> None:
    holidayjp = use_holiday_jp()
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_weekday({"year": 1954, "month": 1, "date": 1})


def test_unsupported_with_ignore() -> None:
    """ignore: 週末でなければ平日扱い（祝日は無いという前提）。"""
    holidayjp = use_holiday_jp(unsupported_date_behavior="ignore")
    # 1954/1/1 金曜 → 平日
    assert holidayjp.is_weekday({"year": 1954, "month": 1, "date": 1}) is True
    # 1954/1/2 土曜 → 平日でない
    assert holidayjp.is_weekday({"year": 1954, "month": 1, "date": 2}) is False
