"""HolidayJP(csv_path=...) の挙動テスト。"""

from datetime import date, datetime
from pathlib import Path

import pytest

from holiday_jp import Holiday, HolidayJP, JST, UnsupportedDateError


def _write_csv(tmp_path: Path, body: str) -> Path:
    csv = tmp_path / "custom.csv"
    csv.write_text(body, encoding="utf-8")
    return csv


def test_csv_path_uses_external_file(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path, "2030/1/1,カスタム元日\n2030/12/31,カスタム大晦日\n")
    holidayjp = HolidayJP(csv_path=csv)
    assert holidayjp.is_holiday(date(2030, 1, 1)) is True
    assert holidayjp.is_holiday(date(2030, 12, 31)) is True


def test_csv_path_does_not_merge_bundle(tmp_path: Path) -> None:
    """外部 CSV 指定時はバンドル CSV を使わない。"""
    csv = _write_csv(tmp_path, "2030/1/1,カスタム元日\n")
    holidayjp = HolidayJP(csv_path=csv)
    # バンドル CSV にある 2021/5/3 はサポート外になる
    with pytest.raises(UnsupportedDateError):
        holidayjp.is_holiday(date(2021, 5, 3))


def test_csv_path_accepts_str(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path, "2030/1/1,カスタム元日\n")
    holidayjp = HolidayJP(csv_path=str(csv))
    assert holidayjp.is_holiday(date(2030, 1, 1)) is True


def test_csv_path_with_extends(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path, "2030/1/1,カスタム元日\n")
    extra = Holiday(year=2030, month=2, date=2, name="追加",
                    local_date=datetime(2030, 2, 2, tzinfo=JST))
    holidayjp = HolidayJP(csv_path=csv, extends=[extra])
    assert holidayjp.is_holiday(date(2030, 1, 1)) is True
    assert holidayjp.is_holiday(date(2030, 2, 2)) is True


def test_csv_path_setting_reflects_path(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path, "2030/1/1,カスタム元日\n")
    holidayjp = HolidayJP(csv_path=csv)
    assert holidayjp.setting().csv_path == str(csv)


def test_default_setting_csv_path_is_none() -> None:
    assert HolidayJP().setting().csv_path is None


def test_csv_path_min_max_reflects_external(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path, "2030/1/1,a\n2031/6/15,b\n2032/12/31,c\n")
    holidayjp = HolidayJP(csv_path=csv)
    assert holidayjp.min().year == 2030
    assert holidayjp.max().year == 2032


def test_csv_path_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        HolidayJP(csv_path=tmp_path / "no_such_file.csv")


def test_csv_path_does_not_affect_default_instance(tmp_path: Path) -> None:
    """csv_path 指定インスタンスがデフォルトインスタンスのデータを汚染しない。"""
    csv = _write_csv(tmp_path, "2030/1/1,カスタム元日\n")
    HolidayJP(csv_path=csv)
    default = HolidayJP()
    assert default.is_holiday(date(2021, 5, 3)) is True
    assert default.min().year == 1955
