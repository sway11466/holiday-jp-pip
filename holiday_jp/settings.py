"""Settings: ライブラリの動作設定。"""

from dataclasses import dataclass, field
from typing import Literal

from holiday_jp.holiday import Holiday

UnsupportedDateBehavior = Literal["error", "ignore"]
SettingScope = Literal["global", "local"]
Weekday = Literal[0, 1, 2, 3, 4, 5, 6]


@dataclass
class Settings:
    """ライブラリの動作設定。

    weekend の数値は :py:meth:`datetime.date.weekday` に従い 0=月曜, 6=日曜。
    JS 版（``Date.getDay()`` の 0=日曜）と番号体系が異なる点に注意。
    """

    # JST に変換してから年月日を取得するか。
    timezone_effect: bool = True
    # サポート範囲外の年が指定されたときの挙動。
    unsupported_date_behavior: UnsupportedDateBehavior = "error"
    # 週末として扱う曜日。デフォルトは土曜(5)・日曜(6)。
    weekend: list[Weekday] = field(default_factory=lambda: [5, 6])
    # 追加で祝日として扱うレコード。
    extends: list[Holiday] = field(default_factory=list)
