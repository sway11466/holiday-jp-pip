"""Holiday データクラスの基本動作テスト。"""

from dataclasses import FrozenInstanceError
from datetime import date, datetime

import pytest

from holiday_jp import Holiday, JST


def test_holiday_holds_given_values() -> None:
    h = Holiday(year=2024, month=5, date=3, name="憲法記念日", local_date=datetime(2024, 5, 3, tzinfo=JST))
    assert h.year == 2024
    assert h.month == 5
    assert h.date == 3
    assert h.name == "憲法記念日"
    assert h.local_date == datetime(2024, 5, 3, tzinfo=JST)


def test_holiday_is_frozen() -> None:
    h = Holiday(year=2024, month=5, date=3, name="憲法記念日", local_date=datetime(2024, 5, 3, tzinfo=JST))
    with pytest.raises(FrozenInstanceError):
        h.year = 2025  # type: ignore[misc]


def test_holiday_equality_by_value() -> None:
    a = Holiday(year=2024, month=5, date=3, name="憲法記念日", local_date=datetime(2024, 5, 3, tzinfo=JST))
    b = Holiday(year=2024, month=5, date=3, name="憲法記念日", local_date=datetime(2024, 5, 3, tzinfo=JST))
    assert a == b
