"""バンドル CSV ローダーのテスト。"""

from datetime import datetime

from holiday_jp import JST, Holiday
from holiday_jp._loader import load_holidays


def test_returns_dict_indexed_by_year() -> None:
    data = load_holidays()
    assert isinstance(data, dict)
    assert all(isinstance(k, int) for k in data)
    assert all(isinstance(v, list) for v in data.values())
    assert all(isinstance(h, Holiday) for v in data.values() for h in v)


def test_year_range_covers_1955_to_2027() -> None:
    data = load_holidays()
    years = sorted(data.keys())
    assert years[0] == 1955
    assert years[-1] == 2027


def test_first_record_is_new_year_1955() -> None:
    data = load_holidays()
    first = data[1955][0]
    assert first.year == 1955
    assert first.month == 1
    assert first.date == 1
    assert first.name == "元日"


def test_last_record_is_2027_labor_thanksgiving() -> None:
    data = load_holidays()
    last = data[2027][-1]
    assert last.year == 2027
    assert last.month == 11
    assert last.date == 23
    assert last.name == "勤労感謝の日"


def test_total_count_in_expected_range() -> None:
    """JS 版 README の「約 1067 件」前後であること。"""
    data = load_holidays()
    total = sum(len(v) for v in data.values())
    assert 1000 <= total <= 1200


def test_each_year_list_is_sorted_by_date() -> None:
    """各年のリストは CSV 出現順（日付昇順）。"""
    data = load_holidays()
    for year, holidays in data.items():
        keys = [(h.month, h.date) for h in holidays]
        assert keys == sorted(keys), f"year {year} is not sorted: {keys}"


def test_local_date_is_jst_aware_datetime() -> None:
    """local_date は JST tzinfo 付き datetime で year/month/day と一致する。"""
    data = load_holidays()
    first = data[1955][0]  # 1955/1/1 元日
    assert isinstance(first.local_date, datetime)
    assert first.local_date == datetime(1955, 1, 1, 0, 0, tzinfo=JST)
    assert first.local_date.tzinfo is not None
