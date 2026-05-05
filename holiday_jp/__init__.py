"""holiday-jp-pip: 内閣府公式データに基づく日本の祝日判定ライブラリ。"""

from copy import deepcopy
from typing import Iterable

from holiday_jp._loader import load_holidays
from holiday_jp.holiday import Holiday
from holiday_jp.settings import Settings, SettingScope, UnsupportedDateBehavior

__version__ = "0.1.0"
__all__ = [
    "Holiday",
    "HolidayJP",
    "Settings",
    "use_holiday_jp",
    "__version__",
]


class HolidayJP:
    """祝日判定インスタンス。通常は :func:`use_holiday_jp` 経由で取得する。"""

    def __init__(self, holidays: dict[int, list[Holiday]], settings: Settings) -> None:
        self._holidays = holidays
        self._settings = settings

    def all(self) -> list[Holiday]:
        """全祝日を年・出現順（CSV 上の昇順）に並べたリストを返す。"""
        return [h for year in sorted(self._holidays) for h in self._holidays[year]]

    def min(self) -> Holiday:
        """最も過去の祝日レコードを返す。"""
        return self._holidays[min(self._holidays)][0]

    def max(self) -> Holiday:
        """最も未来の祝日レコードを返す。"""
        last = self._holidays[max(self._holidays)]
        return last[-1]

    def setting(self) -> Settings:
        """現在の設定のコピーを返す。返り値を変更してもライブラリの動作は変わらない。"""
        return deepcopy(self._settings)


_BASE_HOLIDAYS: dict[int, list[Holiday]] = load_holidays()
_global_instance: HolidayJP | None = None


def _clone_base_holidays() -> dict[int, list[Holiday]]:
    """ベースデータの浅いクローンを返す。Holiday は frozen のためオブジェクトは共有してよい。"""
    return {year: list(holidays) for year, holidays in _BASE_HOLIDAYS.items()}


def use_holiday_jp(
    *,
    timezone_effect: bool | None = None,
    unsupported_date_behavior: UnsupportedDateBehavior | None = None,
    weekend: Iterable[int] | None = None,
    extends: Iterable[Holiday] | None = None,
    scope: SettingScope = "global",
) -> HolidayJP:
    """祝日判定インスタンスを返す。

    ``scope='global'``（デフォルト）はモジュール内で共有されるシングルトンを返し、
    指定された設定でグローバル状態を更新する。後続の呼び出しは設定が引き継がれる。
    ``scope='local'`` は独立したインスタンスを生成し、他に影響しない。

    None を渡したパラメータは反映されず、対応する設定は変更されない。
    """

    global _global_instance
    if scope == "local":
        instance = HolidayJP(_clone_base_holidays(), Settings())
    else:
        if _global_instance is None:
            _global_instance = HolidayJP(_clone_base_holidays(), Settings())
        instance = _global_instance

    settings = instance._settings
    if timezone_effect is not None:
        settings.timezone_effect = timezone_effect
    if unsupported_date_behavior is not None:
        settings.unsupported_date_behavior = unsupported_date_behavior
    if weekend is not None:
        settings.weekend = list(weekend)
    if extends is not None:
        extra_list = list(extends)
        settings.extends = extra_list
        for h in extra_list:
            instance._holidays.setdefault(h.year, []).append(h)

    return instance
