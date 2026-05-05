"""Settings データクラスの基本動作テスト。"""

from datetime import date, datetime

from holiday_jp import Holiday, JST, Settings


def test_default_values() -> None:
    s = Settings()
    assert s.timezone_effect is True
    assert s.unsupported_date_behavior == "error"
    assert s.weekend == [5, 6]
    assert s.extends == []


def test_override_values() -> None:
    extras = [Holiday(year=2024, month=1, date=2, name="custom", local_date=datetime(2024, 1, 2, tzinfo=JST))]
    s = Settings(
        timezone_effect=False,
        unsupported_date_behavior="ignore",
        weekend=[6],
        extends=extras,
    )
    assert s.timezone_effect is False
    assert s.unsupported_date_behavior == "ignore"
    assert s.weekend == [6]
    assert s.extends == extras


def test_default_factory_does_not_share_state() -> None:
    """default_factory による初期化で、別インスタンスのリストが共有されないこと。"""
    s1 = Settings()
    s2 = Settings()
    s1.weekend.append(0)
    s1.extends.append(
        Holiday(year=2024, month=1, date=2, name="custom", local_date=datetime(2024, 1, 2, tzinfo=JST))
    )
    assert s2.weekend == [5, 6]
    assert s2.extends == []
