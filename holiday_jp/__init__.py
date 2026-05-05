"""holiday-jp-pip: 内閣府公式データに基づく日本の祝日判定ライブラリ。"""

from copy import deepcopy
from datetime import date as _date, datetime, timedelta, timezone
from typing import Iterable

from holiday_jp._loader import load_holidays
from holiday_jp.holiday import Holiday
from holiday_jp.settings import Settings, SettingScope, UnsupportedDateBehavior

__version__ = "0.1.0"
__all__ = [
    "Holiday",
    "HolidayJP",
    "InvalidDateError",
    "Settings",
    "UnsupportedDateError",
    "use_holiday_jp",
    "__version__",
]

# JST は 1951 年以降 DST 不採用のため固定オフセットで扱う（doc/architecture.md 参照）。
_JST = timezone(timedelta(hours=9), name="JST")


class InvalidDateError(ValueError):
    """存在しない日付（例: 2021/1/32）が指定されたときに発生する例外。"""


class UnsupportedDateError(ValueError):
    """サポート範囲外の年が指定されたときに発生する例外。"""


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

    def is_valid_date(self, cond: _date | datetime | dict) -> bool:
        """指定値が year/month/date の揃った実在する日付か否かを返す。"""
        c = self._to_condition(cond)
        return self._is_valid_condition(c)

    def is_support_date(self, cond: _date | datetime | dict) -> bool:
        """指定値の年がサポート範囲内（min().year <= year <= max().year）か返す。

        year を持たない条件は True を返す（範囲外と判定しない）。
        """
        c = self._to_condition(cond)
        year = c.get("year")
        if year is None:
            return True
        return self.min().year <= year <= self.max().year

    def get(
        self,
        cond: _date | datetime | dict | None = None,
        /,
        *,
        year: int | None = None,
        month: int | None = None,
        date: int | None = None,
        name: str | None = None,
    ) -> list[Holiday]:
        """条件に合致する祝日のリストを返す。

        引数なしで呼ぶと全祝日を返す。
        位置引数 ``cond`` には ``date``/``datetime``/dict を渡せる。
        キーワード引数 ``year``/``month``/``date``/``name`` でも条件を指定できる。
        サポート外の年が指定された場合の挙動は ``unsupported_date_behavior`` 設定に従う。
        """
        if cond is None and year is None and month is None and date is None and name is None:
            return self.all()

        if cond is not None:
            c = self._to_condition(cond)
        else:
            c = {}
            if year is not None:
                c["year"] = year
            if month is not None:
                c["month"] = month
            if date is not None:
                c["date"] = date
            if name is not None:
                c["name"] = name

        if not self.is_support_date(c):
            if self._settings.unsupported_date_behavior == "ignore":
                return []
            raise UnsupportedDateError(f"not supported date: {c}")

        pool = self._holidays.get(c["year"], []) if "year" in c else self.all()
        return [
            h
            for h in pool
            if (c.get("month") in (None, h.month))
            and (c.get("date") in (None, h.date))
            and (c.get("name") in (None, h.name))
        ]

    def is_holiday(self, cond: _date | datetime | dict) -> bool:
        """指定日が祝日か否かを返す。

        存在しない日付（例: 2021/1/32）が渡された場合は :class:`InvalidDateError` を送出する。
        サポート外の年が渡された場合の挙動は ``unsupported_date_behavior`` 設定に従う。
        """
        c = self._to_condition(cond)
        if not self._is_valid_condition(c):
            raise InvalidDateError(f"invalid date: {c}")
        if not self.is_support_date(c):
            if self._settings.unsupported_date_behavior == "ignore":
                return False
            raise UnsupportedDateError(f"not supported date: {c}")
        return any(
            h.year == c["year"] and h.month == c["month"] and h.date == c["date"]
            for h in self._holidays.get(c["year"], [])
        )

    def is_weekend(self, cond: _date | datetime | dict) -> bool:
        """指定日が週末（``settings.weekend`` の曜日）か返す。

        曜日番号は :py:meth:`datetime.date.weekday` に従い 0=月曜, 6=日曜。
        ``unsupported_date_behavior='ignore'`` の場合はサポート外でも例外を出さず、
        カレンダー上の曜日に基づいて判定する。
        """
        c = self._to_condition(cond)
        if not self._is_valid_condition(c):
            raise InvalidDateError(f"invalid date: {c}")
        if not self.is_support_date(c) and self._settings.unsupported_date_behavior != "ignore":
            raise UnsupportedDateError(f"not supported date: {c}")
        weekday = _date(c["year"], c["month"], c["date"]).weekday()
        return weekday in self._settings.weekend

    def is_weekday(self, cond: _date | datetime | dict) -> bool:
        """指定日が平日（週末でも祝日でもない日）か返す。"""
        return not self.is_weekend(cond) and not self.is_holiday(cond)

    def _to_condition(self, cond: _date | datetime | dict) -> dict:
        """入力を ``{year?, month?, date?, name?}`` の dict に正規化する。"""
        if isinstance(cond, datetime):
            if self._settings.timezone_effect:
                cond = cond.astimezone(_JST)
            return {"year": cond.year, "month": cond.month, "date": cond.day}
        if isinstance(cond, _date):
            return {"year": cond.year, "month": cond.month, "date": cond.day}
        if isinstance(cond, dict):
            return cond
        raise TypeError(f"unsupported cond type: {type(cond).__name__}")

    @staticmethod
    def _is_valid_condition(c: dict) -> bool:
        if "year" not in c or "month" not in c or "date" not in c:
            return False
        try:
            _date(c["year"], c["month"], c["date"])
        except (ValueError, TypeError):
            return False
        return True


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
