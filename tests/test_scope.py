"""use_holiday_jp の scope（global / local）切替テスト。"""

from datetime import date

from holiday_jp import Holiday, use_holiday_jp


def test_local_instance_has_default_settings() -> None:
    hp = use_holiday_jp(scope="local")
    s = hp.setting()
    assert s.timezone_effect is True
    assert s.unsupported_date_behavior == "error"
    assert s.weekend == [5, 6]


def test_local_setting_does_not_affect_global() -> None:
    local = use_holiday_jp(weekend=[0, 1, 2, 3, 4], scope="local")
    glob = use_holiday_jp()
    assert local.setting().weekend == [0, 1, 2, 3, 4]
    assert glob.setting().weekend == [5, 6]


def test_global_setting_does_not_affect_existing_local() -> None:
    local = use_holiday_jp(scope="local")
    use_holiday_jp(weekend=[0])  # グローバルを変更
    assert local.setting().weekend == [5, 6]  # 変更前のまま


def test_two_local_instances_are_independent() -> None:
    local1 = use_holiday_jp(weekend=[0], scope="local")
    local2 = use_holiday_jp(weekend=[1], scope="local")
    assert local1.setting().weekend == [0]
    assert local2.setting().weekend == [1]


def test_omitting_scope_is_equivalent_to_global() -> None:
    use_holiday_jp(weekend=[3])
    implicit = use_holiday_jp()
    explicit = use_holiday_jp(scope="global")
    assert implicit.setting().weekend == [3]
    assert explicit.setting().weekend == [3]


def test_global_setting_persists_across_calls() -> None:
    use_holiday_jp(weekend=[5])
    other = use_holiday_jp()
    assert other.setting().weekend == [5]


def test_local_extends_does_not_affect_global() -> None:
    custom = Holiday(year=2025, month=3, date=10, name="カスタム", local_date=date(2025, 3, 10))
    local = use_holiday_jp(extends=[custom], scope="local")
    glob = use_holiday_jp()
    local_2025 = [h for h in local.all() if h.year == 2025 and h.month == 3 and h.date == 10]
    glob_2025 = [h for h in glob.all() if h.year == 2025 and h.month == 3 and h.date == 10]
    assert len(local_2025) == 1
    assert len(glob_2025) == 0
