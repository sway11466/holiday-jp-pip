# Backlog

公開準備および周辺作業の TODO リスト。完了したら削除する。

## 公開準備

- [ ] `pyproject.toml` の最終調整（classifiers, URL, keywords の見直し）
- [ ] `doc/cicd.md` を整備（テスト、ビルド、TestPyPI / PyPI 公開手順）
- [ ] `doc/tutorial.md` を整備（基本〜応用ユースケース）
- [ ] TestPyPI で動作確認
- [ ] PyPI 本番公開

## 自動化

- [x] GitHub Actions: pytest 自動実行（push / PR トリガー） → `.github/workflows/test.yml`
- [ ] GitHub Actions: PyPI publish ワークフロー（tag トリガー）
- [ ] GitHub Actions: 内閣府 CSV を取得・UTF-8 変換してバンドルを更新（doc/architecture.md「祝日 CSV を UTF-8 変換する」ADR の将来構想）

## 連携

- [ ] SleepSwitcher の `core/schedule.py` の `is_holiday()` スタブを `holiday_jp.HolidayJP().is_holiday()` に差し替え（SleepSwitcher 側の作業）
