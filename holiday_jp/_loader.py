"""祝日 CSV を読み込むモジュール（パッケージ内部用）。"""

import os
from datetime import datetime, timedelta, timezone
from importlib import resources

from holiday_jp.holiday import Holiday

# JST は 1951 年以降 DST 不採用のため固定オフセットで扱う（doc/architecture.md 参照）。
_JST = timezone(timedelta(hours=9), name="JST")
_CSV_FILENAME = "syukujitsu.csv"


def load_holidays(csv_path: str | os.PathLike | None = None) -> dict[int, list[Holiday]]:
    """祝日 CSV を読み込み、年をキーにした辞書を返す。

    ``csv_path`` が ``None`` の場合はバンドル済み CSV を読み込む。
    パスが渡された場合はそのファイルを UTF-8 として読み込む（バンドル CSV は使わない）。
    各年のリストは CSV 上の出現順（＝日付昇順）を保つ。
    ヘッダー行や日付として解釈できない行はスキップする。
    """

    if csv_path is None:
        csv_text = resources.files("holiday_jp").joinpath(_CSV_FILENAME).read_text(encoding="utf-8")
    else:
        with open(csv_path, "r", encoding="utf-8") as f:
            csv_text = f.read()
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
                local_date=datetime(year, month, day, tzinfo=_JST),
            )
        )
    return holidays
