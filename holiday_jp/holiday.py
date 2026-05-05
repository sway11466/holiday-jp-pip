"""Holiday: 祝日 1 件を表す不変データクラス。"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Holiday:
    """祝日 1 件を表す不変データクラス。

    属性:
        year:       祝日の年（JST 基準）
        month:      祝日の月（1〜12）
        date:       祝日の日（1〜31）
        name:       祝日名（日本語）
        local_date: JST 0:00 という「瞬間」を表す TZ 付き ``datetime``。
                    実行環境の TZ で再解釈するには ``local_date.astimezone()`` を呼ぶ。
                    例: ハワイ環境で ``local_date.astimezone().date()`` は前日（5/2）を返す。
    """

    year: int
    month: int
    date: int
    name: str
    local_date: datetime
