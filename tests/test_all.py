"""HolidayJP.all() のテスト。"""

from holiday_jp import HolidayJP


def test_basic_call() -> None:
    holidayjp = HolidayJP()
    holidayjp.all()


def test_returns_non_empty_list() -> None:
    holidayjp = HolidayJP()
    holidays = holidayjp.all()
    assert len(holidays) > 0


def test_returned_in_year_ascending_order() -> None:
    holidayjp = HolidayJP()
    holidays = holidayjp.all()
    years = [h.year for h in holidays]
    assert years == sorted(years)


def test_count_matches_csv_size() -> None:
    """バンドル CSV が 1067 件（1955〜2027）であることを前提とした件数チェック。"""
    holidayjp = HolidayJP()
    assert len(holidayjp.all()) == 1067
