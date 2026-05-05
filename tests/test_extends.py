"""extends オプションの挙動テスト。"""

from datetime import date

from holiday_jp import Holiday, HolidayJP


def test_extends_appears_in_all() -> None:
    custom = Holiday(year=2099, month=12, date=31, name="未来", local_date=date(2099, 12, 31))
    holidayjp = HolidayJP(extends=[custom])
    assert custom in holidayjp.all()


def test_extends_into_existing_year() -> None:
    custom = Holiday(year=2024, month=2, date=29, name="閏年特別", local_date=date(2024, 2, 29))
    holidayjp = HolidayJP(extends=[custom])
    holidays_2024 = [h for h in holidayjp.all() if h.year == 2024]
    assert custom in holidays_2024
    # 既存の 2024 年祝日が消えていない
    assert len(holidays_2024) > 1


def test_extends_into_new_year() -> None:
    custom = Holiday(year=2099, month=1, date=1, name="未来元日", local_date=date(2099, 1, 1))
    holidayjp = HolidayJP(extends=[custom])
    assert holidayjp.max() == custom


def test_setting_reflects_extends_passed() -> None:
    custom = Holiday(year=2099, month=1, date=1, name="未来元日", local_date=date(2099, 1, 1))
    holidayjp = HolidayJP(extends=[custom])
    assert holidayjp.setting().extends == [custom]
