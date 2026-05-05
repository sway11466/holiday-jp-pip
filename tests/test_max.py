"""HolidayJP.max() のテスト。"""

from holiday_jp import use_holiday_jp


def test_basic_call() -> None:
    holidayjp = use_holiday_jp()
    holidayjp.max()


def test_max_is_2027_labor_thanksgiving() -> None:
    """バンドル CSV の最終レコードは 2027/11/23 勤労感謝の日。"""
    holidayjp = use_holiday_jp()
    holiday = holidayjp.max()
    assert holiday.year == 2027
    assert holiday.month == 11
    assert holiday.date == 23
    assert holiday.name == "勤労感謝の日"
