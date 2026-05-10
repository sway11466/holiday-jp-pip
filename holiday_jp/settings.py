"""Settings: ライブラリの動作設定。"""

from dataclasses import dataclass, field
from typing import Literal

from holiday_jp.holiday import Holiday

UnsupportedDateBehavior = Literal["error", "ignore"]


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
    # 週末として扱う曜日。0(月)〜6(日) の値を入れる。デフォルトは土曜・日曜。
    weekend: list[int] = field(default_factory=lambda: [5, 6])
    # 追加で祝日として扱うレコード。
    extends: list[Holiday] = field(default_factory=list)
    # 祝日 CSV のパス。None の場合はバンドル CSV を使用する。
    csv_path: str | None = None
