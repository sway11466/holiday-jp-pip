"""共通のテストフィクスチャ。"""

import pytest

import holiday_jp


@pytest.fixture(autouse=True)
def _reset_global_state() -> None:
    """各テスト前後でグローバル状態を初期化する。

    ``use_holiday_jp(scope='global')`` はモジュール内のシングルトンに
    設定や extends を蓄積するため、テスト間の汚染を防ぐためにリセットする。
    """

    holiday_jp._global_instance = None
    yield
    holiday_jp._global_instance = None
