"""HolidayJP.setting() の挙動テスト。"""

from holiday_jp import use_holiday_jp


def test_default_setting() -> None:
    holidayjp = use_holiday_jp()
    s = holidayjp.setting()
    assert s.timezone_effect is True
    assert s.unsupported_date_behavior == "error"
    assert s.weekend == [5, 6]
    assert s.extends == []


def test_timezone_effect_set_to_false() -> None:
    holidayjp = use_holiday_jp(timezone_effect=False)
    assert holidayjp.setting().timezone_effect is False


def test_returned_setting_is_a_copy() -> None:
    """setting() の返り値を変更しても本体には反映されない。"""
    holidayjp = use_holiday_jp(timezone_effect=False)
    s = holidayjp.setting()
    s.timezone_effect = True
    assert holidayjp.setting().timezone_effect is False


def test_weekend_override() -> None:
    holidayjp = use_holiday_jp(weekend=[6])
    assert holidayjp.setting().weekend == [6]


def test_unsupported_date_behavior_override() -> None:
    holidayjp = use_holiday_jp(unsupported_date_behavior="ignore")
    assert holidayjp.setting().unsupported_date_behavior == "ignore"
