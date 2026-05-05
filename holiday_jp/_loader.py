"""バンドルされた祝日 CSV を読み込むモジュール（パッケージ内部用）。"""

from datetime import date
from importlib import resources

from holiday_jp.holiday import Holiday

_CSV_FILENAME = "syukujitsu.csv"


def load_holidays() -> dict[int, list[Holiday]]:
    """バンドル済み CSV を読み込み、年をキーにした辞書を返す。

    各年のリストは CSV 上の出現順（＝日付昇順）を保つ。
    ヘッダー行や日付として解釈できない行はスキップする。
    """

    csv_text = resources.files("holiday_jp").joinpath(_CSV_FILENAME).read_text(encoding="utf-8")
    holidays: dict[int, list[Holiday]] = {}
    for line in csv_text.splitlines():
        date_str, sep, name = line.partition(",")
        if not sep:
            continue
        ymd = date_str.split("/")
        if len(ymd) != 3 or not all(p.isdigit() for p in ymd):
            continue
        year, month, day = (int(p) for p in ymd)
        holidays.setdefault(year, []).append(
            Holiday(
                year=year,
                month=month,
                date=day,
                name=name,
                local_date=date(year, month, day),
            )
        )
    return holidays
