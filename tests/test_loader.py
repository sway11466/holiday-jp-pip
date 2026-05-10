"""祝日 CSV ローダーのテスト。"""

from datetime import datetime
from pathlib import Path

import pytest

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


def test_csv_path_loads_external_file(tmp_path: Path) -> None:
    """csv_path 指定時は外部ファイルから祝日を読み込む。"""
    csv = tmp_path / "custom.csv"
    csv.write_text(
        "国民の祝日・休日月日,国民の祝日・休日名称\n"
        "2030/1/1,カスタム元日\n"
        "2030/12/31,カスタム大晦日\n",
        encoding="utf-8",
    )
    data = load_holidays(csv)
    assert sorted(data.keys()) == [2030]
    assert [h.name for h in data[2030]] == ["カスタム元日", "カスタム大晦日"]
    assert data[2030][0].local_date == datetime(2030, 1, 1, 0, 0, tzinfo=JST)


def test_csv_path_accepts_str(tmp_path: Path) -> None:
    csv = tmp_path / "custom.csv"
    csv.write_text("2031/5/5,test\n", encoding="utf-8")
    data = load_holidays(str(csv))
    assert data[2031][0].name == "test"


def test_csv_path_independent_from_bundle(tmp_path: Path) -> None:
    """外部 CSV を指定したときバンドル CSV はマージされない。"""
    csv = tmp_path / "custom.csv"
    csv.write_text("2030/1/1,カスタム元日\n", encoding="utf-8")
    data = load_holidays(csv)
    assert 1955 not in data
    assert 2027 not in data


def test_csv_path_empty_file(tmp_path: Path) -> None:
    csv = tmp_path / "empty.csv"
    csv.write_text("", encoding="utf-8")
    assert load_holidays(csv) == {}


def test_csv_path_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_holidays(tmp_path / "does_not_exist.csv")


def test_csv_path_skips_invalid_lines(tmp_path: Path) -> None:
    """ヘッダ行や日付として解釈できない行はスキップされる。"""
    csv = tmp_path / "mixed.csv"
    csv.write_text(
        "国民の祝日・休日月日,国民の祝日・休日名称\n"
        "garbage line without slash\n"
        "abc/def/ghi,壊れた行\n"
        "2030/2/11,建国記念の日\n",
        encoding="utf-8",
    )
    data = load_holidays(csv)
    assert list(data.keys()) == [2030]
    assert len(data[2030]) == 1
    assert data[2030][0].name == "建国記念の日"
