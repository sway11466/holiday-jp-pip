"""HolidayJP.min() のテスト。"""

from holiday_jp import use_holiday_jp


def test_basic_call() -> None:
    holidayjp = use_holiday_jp()
    holidayjp.min()


def test_min_is_1955_new_year() -> None:
    holidayjp = use_holiday_jp()
    holiday = holidayjp.min()
    assert holiday.year == 1955
    assert holiday.month == 1
    assert holiday.date == 1
    assert holiday.name == "元日"
