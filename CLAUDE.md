# CLAUDE.md

このファイルは Claude Code がこのリポジトリで作業する際の指示書です。
公開向けの仕様は `doc/` 配下、ユーザー向けの導入は `README.md` を参照してください。

## プロジェクト概要

日本の祝日判定 Python ライブラリ。既存 JS 版 `@sway11466/holiday-jp-npm` の Python 移植版で、PyPI に `holiday-jp-pip` として公開する。
内閣府公式の祝日 CSV をパッケージにバンドルし、ネットワーク取得なしのスタンドアローン動作を維持する。

## 関連ドキュメント

- 引継ぎ・初期方針: [holiday-jp-pip-start.md](holiday-jp-pip-start.md)
- 公開 API 仕様: [doc/api.md](doc/api.md)
- 設定リファレンス: [doc/setting.md](doc/setting.md)
- 設計判断（ADR）: [doc/architecture.md](doc/architecture.md)
- テスト・公開手順: [doc/cicd.md](doc/cicd.md)
- 移植元 JS 実装: `../holiday-jp-npm/`

## ディレクトリ構成

```
holiday_jp/             # パッケージ本体
  __init__.py           # ファクトリ関数 use_holiday_jp() / HolidayJP クラス
  holiday.py            # Holiday データクラス
  settings.py           # Settings 設定クラス
  syukujitsu.csv        # バンドル CSV（UTF-8 化済み）
tests/                  # pytest テスト（JS 版テストケースを移植）
doc/                    # 公開用ドキュメント
pyproject.toml          # PyPI 公開設定
```

## 開発コマンド

Python 環境管理は **uv** を使う。`.venv/` は `uv sync` で自動作成される。

```bash
# 初回セットアップ（venv 作成 + 依存インストール）
uv sync

# テスト
uv run pytest
uv run pytest --cov=holiday_jp

# 任意の Python スクリプトを実行
uv run python <script.py>

# 依存追加
uv add <package>                # 本体依存（このプロジェクトでは原則使わない＝依存ゼロ原則）
uv add --dev <package>          # 開発依存（pytest 等）

# ビルド
uv build

# TestPyPI / PyPI 公開
uv publish --publish-url https://test.pypi.org/legacy/
uv publish
```

Windows コンソールで日本語を出力する際は `PYTHONIOENCODING=utf-8` を付けると文字化けしない。

## コーディング規約

- **Python 3.10+** 前提（`zoneinfo` 標準、`match` 構文使用可）
- **依存ゼロ**: リリースパッケージに外部依存を入れない（標準ライブラリのみ）。開発依存は `pytest` 等のみ
- **型ヒント必須**: 公開 API は全て型注釈する
- **命名**: snake_case（JS 版の camelCase をそのまま訳す。例: `timezoneEffect` → `timezone_effect`）
- **データクラス**: `@dataclass(frozen=True)` で不変にする方針
- **コメント**: WHY のみ書く。WHAT は書かない

## JS 版から移植する際の事故りやすい点

| 項目 | JS 版 | Python 版 | 注意 |
|------|-------|-----------|------|
| 曜日番号 | `Date.getDay()` 0=日, 6=土 | `datetime.date.weekday()` 0=月, 6=日 | `weekend` 設定の数値が**ずれる**。デフォルトは JS=`[0,6]` → Py=`[5,6]` |
| 月 | 0-indexed (`new Date(2021, 5-1, 3)`) | 1-indexed (`date(2021, 5, 3)`) | `Holiday.month` は 1-indexed で揃える（JS 版データクラスも 1-indexed） |
| 日付型 | `Date`（時刻含む） | `datetime.date` | 時刻情報を持たないため `timezone_effect` の挙動を Python 用に再設計 |
| 真偽値 | `true` / `false` | `True` / `False` | エラー文言を訳す際の些細な差異 |
| `local_date` | 実行環境 TZ の `Date` | 常に JST の `date` | Python は TZ 非対応 `date` のため JST 日付に統一（[ADR](doc/architecture.md#local_date-は-jst-日付に統一する) 参照） |
| JST 表現 | — | `timezone(timedelta(hours=9))` | `zoneinfo` は Windows で `tzdata` 依存になるため不採用 |

## 重要な設計判断（要約）

- **CSV 腹持ち + UTF-8 バンドル**: 内閣府 CSV は Shift_JIS だが UTF-8 化したものをバンドルする。詳細は [doc/architecture.md](doc/architecture.md)
- **依存ゼロ**: 趣味プロジェクト + 軽量化のため。詳細同上
- **scope='global'**: モジュールレベルのシングルトンで共有設定を保持。`'local'` で独立インスタンス

## やってはいけないこと

- バンドル CSV を Shift_JIS のまま入れない（依存ゼロ原則を破ることになる）
- リリースパッケージに `requirements.txt` 経由で外部依存を入れない
- `holiday_jp/syukujitsu.csv` を手動編集しない（更新時は再ダウンロード→UTF-8 変換の手順を踏む）
- JS 版にない API を独断で追加しない（必要なら ADR に記録してから）

## テスト方針

- JS 版 `holiday-jp-npm/test/` のテストケースを 1 対 1 で Python に移植する
- ファイル名対応: `test_*.ts` → `test_*.py`
- 移植時は曜日番号・月の indexing 差異に特に注意（上の対応表参照）
