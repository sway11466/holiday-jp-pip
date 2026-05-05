"""HolidayJP.get() のテスト。"""

from datetime import date, datetime, timedelta, timezone

import pytest

from holiday_jp import Holiday, UnsupportedDateError, use_holiday_jp

JST = timezone(timedelta(hours=9))


def test_basic_call_returns_all() -> None:
    holidayjp = use_holiday_jp()
    assert len(holidayjp.get()) == len(holidayjp.all())


def test_filter_by_date_object() -> None:
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get(date(2021, 5, 3))
    assert len(holidays) == 1
    assert holidays[0].name == "憲法記念日"


def test_filter_by_date_with_no_match() -> None:
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get(date(2021, 5, 10))
    assert holidays == []


def test_filter_by_year_kwarg() -> None:
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get(year=2021)
    assert len(holidays) == 17


def test_filter_by_year_and_month_kwargs() -> None:
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get(year=2021, month=5)
    assert len(holidays) == 3


def test_filter_by_year_month_date_kwargs() -> None:
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get(year=2021, month=5, date=3)
    assert len(holidays) == 1


def test_filter_by_name_kwarg() -> None:
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get(name="体育の日")
    assert len(holidays) == 53


def test_filter_by_year_and_name_kwargs() -> None:
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get(year=2021, name="スポーツの日")
    assert len(holidays) == 1
    assert holidays[0].month == 7
    assert holidays[0].date == 23


def test_filter_with_dict_cond() -> None:
    """dict 形式の cond も受け付ける。"""
    holidayjp = use_holiday_jp()
    holidays = holidayjp.get({"year": 2021, "month": 5, "date": 3})
    assert len(holidays) == 1


def test_invalid_calendar_date_returns_empty() -> None:
    """ありえない日付は空配列（is_valid_date は呼ばない）。"""
    holidayjp = use_holiday_jp()
    assert holidayjp.get({"year": 2001, "month": 1, "date": 32}) == []


def test_unsupported_year_raises_by_default() -> None:
    holidayjp = use_holiday_jp()
    with pytest.raises(UnsupportedDateError):
        holidayjp.get({"year": 1954, "month": 1, "date": 1})


def test_unsupported_year_returns_empty_with_ignore() -> None:
    holidayjp = use_holiday_jp(unsupported_date_behavior="ignore")
    assert holidayjp.get({"year": 1954, "month": 1, "date": 1}) == []
    assert holidayjp.get({"year": 2099, "month": 1, "date": 1}) == []


def test_extends_is_searchable() -> None:
    custom = Holiday(year=2023, month=3, date=10, name="test", local_date=date(2023, 3, 10))
    holidayjp = use_holiday_jp(extends=[custom], scope="local")
    holidays = holidayjp.get({"year": 2023, "month": 3, "date": 10})
    assert holidays == [custom]


def test_datetime_jst_input() -> None:
    """JST 0:00 の datetime を渡すと JST 日付として扱われる。"""
    holidayjp = use_holiday_jp()
    dt = datetime(2021, 5, 3, 0, 0, tzinfo=JST)
    holidays = holidayjp.get(dt)
    assert len(holidays) == 1
    assert holidays[0].name == "憲法記念日"


def test_datetime_utc_input_converts_to_jst() -> None:
    """UTC 15:00 = JST 0:00 翌日。timezone_effect=True (default) では JST 日付に変換される。"""
    holidayjp = use_holiday_jp()
    dt = datetime(2021, 5, 2, 15, 0, tzinfo=timezone.utc)  # 2021-05-03 00:00 JST
    holidays = holidayjp.get(dt)
    assert len(holidays) == 1
    assert holidays[0].name == "憲法記念日"


def test_datetime_with_timezone_effect_false_uses_raw_ymd() -> None:
    """timezone_effect=False では tzinfo を無視して year/month/day をそのまま使う。"""
    holidayjp = use_holiday_jp(timezone_effect=False, scope="local")
    dt = datetime(2021, 5, 2, 15, 0, tzinfo=timezone.utc)  # 本来は JST 5/3 だが…
    holidays = holidayjp.get(dt)
    # raw ymd は 5/2 なので一致しない（5/2 は祝日でない）
    assert holidays == []
