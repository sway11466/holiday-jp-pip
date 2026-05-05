"""Holiday: 祝日 1 件を表す不変データクラス。"""

from dataclasses import dataclass
from datetime import date as _date


@dataclass(frozen=True)
class Holiday:
    """祝日 1 件を表す不変データクラス。

    属性:
        year:       祝日の年（JST 基準）
        month:      祝日の月（1〜12）
        date:       祝日の日（1〜31）
        name:       祝日名（日本語）
        local_date: JST 日付を ``datetime.date`` で表したもの。常に year/month/date と一致する。
                    JS 版は実行環境タイムゾーンの日付を保持していたが、Python の ``date``
                    はタイムゾーン非対応のため JST 日付に統一した（doc/architecture.md 参照）。
    """

    year: int
    month: int
    date: int
    name: str
    local_date: _date
