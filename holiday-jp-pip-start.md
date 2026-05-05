# holiday-jp-pip 新規プロジェクト引継ぎ

## プロジェクト概要

日本の祝日判定 Python ライブラリ。
既存の JS ライブラリ `@sway11466/holiday-jp-npm` の Python 移植版として PyPI に公開する。

- **PyPI パッケージ名**: `holiday-jp-pip`
- **GitHub リポジトリ名**: `holiday-jp-pip`
- **参考 JS 版**: https://github.com/sway11466/holiday-jp-npm

---

## JS 版ライブラリの仕様（移植元）

### データソース

内閣府公式 CSV をバンドル。ネットワーク取得なし。

- URL: https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv
- 形式: `YYYY/M/D,祝日名称`
- カバー範囲: 1955年〜2027年（約1067件）
- カスタム祝日を追加注入する `extends` オプションあり

### 公開 API

| メソッド | 説明 |
|----------|------|
| `all()` | 全祝日リストを返す |
| `min()` / `max()` | 最古／最新の祝日レコードを返す |
| `get(cond?)` | 日付や条件で祝日を絞り込む |
| `is_holiday(date)` | 祝日か否かを返す |
| `is_weekend(date)` | 週末か否かを返す（デフォルト: 土日） |
| `is_weekday(date)` | 週末でも祝日でもない日か否かを返す |
| `is_valid_date(cond)` | 実在する日付か否かを返す |
| `is_support_date(cond)` | データ範囲内の年か否かを返す |

### 設定オプション

| オプション | デフォルト | 説明 |
|------------|------------|------|
| `timezone_effect` | `True` | JST に変換してから年月日を取得する |
| `unsupported_date_behavior` | `'error'` | 範囲外年の挙動（`'error'` or `'ignore'`） |
| `weekend` | `[5, 6]` | 週末とみなす曜日番号（Python の weekday()） |
| `extends` | `[]` | 追加カスタム祝日レコード |
| `scope` | `'global'` | `'global'` はシングルトン、`'local'` は独立インスタンス |

### データ型

```python
@dataclass
class Holiday:
    year: int
    month: int
    date: int
    name: str
    local_date: datetime.date
```

---

## Python 版の設計方針

### ディレクトリ構成

```
holiday-jp-pip/
├── holiday_jp/
│   ├── __init__.py        # パッケージエントリ・ファクトリ関数
│   ├── holiday.py         # Holiday データクラス
│   ├── settings.py        # 設定クラス
│   └── syukujitsu.csv     # バンドルデータ
├── tests/
│   ├── test_all.py
│   ├── test_get.py
│   ├── test_is_holiday.py
│   ├── test_is_weekend.py
│   ├── test_is_weekday.py
│   └── ...
├── pyproject.toml         # PyPI 公開設定
└── README.md
```

### 技術選定

- Python 3.10+
- タイムゾーン: `zoneinfo.ZoneInfo('Asia/Tokyo')`（標準ライブラリ、追加依存なし）
- データクラス: `@dataclass`
- テスト: `pytest`
- PyPI 公開: `pyproject.toml` + `twine` または `flit`

### JS 版との対応

| JS | Python |
|----|--------|
| `useHolidayJP()` | `use_holiday_jp()` ファクトリ関数 or `HolidayJP` クラス |
| `Date` | `datetime.date` |
| `getDay()` (0=日) | `weekday()` (0=月) ← 番号が違うので注意 |
| `timezoneEffect` | `timezone_effect` |

---

## SleepSwitcher との連携

このライブラリ完成後、SleepSwitcher の `core/schedule.py` に組み込む。

```python
# core/schedule.py（現状はスタブ）
def is_holiday(schedule: dict, d: date) -> bool:
    return False  # フェーズ 3 で実装
```

↓ 完成後はこうする

```python
from holiday_jp import use_holiday_jp

_holiday_jp = use_holiday_jp()

def is_holiday(schedule: dict, d: date) -> bool:
    return _holiday_jp.is_holiday(d)
```

---

## TODO

- [ ] `holiday-jp-pip` フォルダ作成・git 初期化
- [ ] `syukujitsu.csv` をダウンロードしてバンドル
- [ ] `Holiday` データクラス実装
- [ ] CSV 読み込み・年別インデックス構築
- [ ] `is_holiday()` 実装
- [ ] `is_weekend()` / `is_weekday()` 実装
- [ ] `get()` / `all()` / `min()` / `max()` 実装
- [ ] `scope` のシングルトン／ローカル切り替え実装
- [ ] `extends` オプション実装
- [ ] `timezone_effect` オプション実装
- [ ] pytest テスト作成（JS 版のテストケースを移植）
- [ ] `pyproject.toml` 整備
- [ ] PyPI テスト公開（TestPyPI）
- [ ] PyPI 本番公開
- [ ] SleepSwitcher の `is_holiday()` スタブを本実装に差し替え
