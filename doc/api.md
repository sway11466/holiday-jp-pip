# API ドキュメント

`holiday-jp-pip` の公開 API 仕様。

## HolidayJP

```python
from holiday_jp import HolidayJP

holidayjp = HolidayJP(
    timezone_effect=True,
    unsupported_date_behavior="error",
    weekend=[5, 6],
    extends=[],
)
```

祝日判定インスタンスを生成する。各引数は省略可能。設定の詳細は [setting.md](setting.md) を参照。
インスタンスは独立しており、複数生成しても互いに影響しない（[architecture.md](architecture.md) の「シングルトンパターンを採用しない」ADR 参照）。

---

## 入力型: cond について

多くのメソッドは判定対象として `cond` を受け取る。指定可能な型は以下：

| 型 | 例 | 備考 |
|---|---|---|
| `datetime.date` | `date(2021, 5, 3)` | JST 日付として扱う |
| `datetime.datetime` | `datetime(2021, 5, 3, 12, 0, tzinfo=ZoneInfo("Asia/Tokyo"))` | `timezone_effect=True` のとき JST に変換してから日付を取り出す |
| `dict` | `{"year": 2021, "month": 5, "date": 3}` | キーは `year`, `month`, `date`, `name`（メソッドにより必須キーが異なる） |

`cond` で表現される日付はすべて JST の暦上の日付として解釈される。

---

## all

- パラメーター: なし
- 戻り値: `list[Holiday]` — ライブラリで扱う全祝日
- 説明: 年・出現順（CSV 上の昇順）に並べたリストを返す

```python
holidayjp.all()  # [Holiday(year=1955, month=1, date=1, name='元日', ...), ...]
```

## min

- パラメーター: なし
- 戻り値: `Holiday` — 最も古い祝日
- 説明: バンドルされた CSV の最古の祝日レコードを返す

## max

- パラメーター: なし
- 戻り値: `Holiday` — 最も新しい祝日
- 説明: バンドルされた CSV の最新の祝日レコードを返す

## setting

- パラメーター: なし
- 戻り値: `Settings` — 動作設定の **コピー**
- 説明: 返り値を変更してもインスタンスの動作は変わらない

## get

- パラメーター
    - `cond: date | datetime | dict | None`（位置引数のみ）
    - `year: int | None`（キーワード）
    - `month: int | None`（キーワード）
    - `date: int | None`（キーワード）
    - `name: str | None`（キーワード）
- 戻り値: `list[Holiday]`
- 説明
    - すべて省略すると `all()` と同じ全件を返す
    - `cond` を渡した場合はそれを条件として、`year/month/date/name` のキーワード引数を渡した場合はそれらの組み合わせで絞り込む
    - サポート外の年が指定された場合の挙動は `unsupported_date_behavior` 設定に従う
    - 存在しない日付（例: 2021/1/32）の場合は単に空配列を返す（例外を発生させない）

```python
holidayjp.get(date(2021, 5, 3))                 # [Holiday(... name='憲法記念日' ...)]
holidayjp.get(year=2021, month=5)                # 2021 年 5 月の祝日 3 件
holidayjp.get(name="スポーツの日")                # スポーツの日（年指定なしで全期間）
holidayjp.get({"year": 2021, "month": 5})        # dict も可
```

## is_valid_date

- パラメーター: `cond: date | datetime | dict`
- 戻り値: `bool`
- 説明
    - `cond` が `year`/`month`/`date` を全て持ち、かつ実在する暦日の場合に `True`
    - 一つでも欠けていたり、ありえない日付（2021/1/32 等）の場合は `False`

## is_support_date

- パラメーター: `cond: date | datetime | dict`
- 戻り値: `bool`
- 説明
    - `cond` の年がサポート範囲内（`min().year <= year <= max().year`）の場合に `True`
    - 年を持たない条件は `True` を返す（範囲外と判定しない）
    - 存在しない暦日でも、年さえ範囲内なら `True`

## is_holiday

- パラメーター: `cond: date | datetime | dict`
- 戻り値: `bool`
- 説明
    - 指定した日付が祝日の場合に `True`
    - 存在しない日付（2021/1/32 等）の場合は `InvalidDateError` を送出
    - サポート外の年が指定された場合の挙動は `unsupported_date_behavior` 設定に従う

## is_weekend

- パラメーター: `cond: date | datetime | dict`
- 戻り値: `bool`
- 説明
    - 指定した日付が週末の場合に `True`
    - 「週末」とみなす曜日は `weekend` 設定で指定（デフォルトは土曜・日曜）
    - 曜日番号は `datetime.date.weekday()` に従い 0=月曜, 6=日曜
    - 祝日であっても週末であれば `True` を返す
    - 存在しない日付の場合は `InvalidDateError` を送出
    - サポート外の年が指定された場合の挙動は `unsupported_date_behavior` 設定に従う（`ignore` の場合はカレンダー上の曜日で判定する）

## is_weekday

- パラメーター: `cond: date | datetime | dict`
- 戻り値: `bool`
- 説明
    - 指定した日付が平日（週末でも祝日でもない日）の場合に `True`
    - 存在しない日付の場合は `InvalidDateError` を送出
    - サポート外の年が指定された場合の挙動は `unsupported_date_behavior` 設定に従う（`ignore` の場合は祝日が存在しない前提で動作する）

---

## データクラス

### Holiday

不変のデータクラス（`@dataclass(frozen=True)`）。

| フィールド | 型 | 説明 |
|---|---|---|
| `year` | `int` | 祝日の年（JST 基準） |
| `month` | `int` | 月（1〜12） |
| `date` | `int` | 日（1〜31） |
| `name` | `str` | 祝日名（日本語） |
| `local_date` | `datetime.date` | JST 日付を表す `date`。常に `year/month/date` と一致する |

### Settings

動作設定。詳細は [setting.md](setting.md) を参照。

---

## 例外

| クラス | 親 | 発生条件 |
|---|---|---|
| `InvalidDateError` | `ValueError` | `is_holiday`, `is_weekend`, `is_weekday` に存在しない日付（年/月/日が欠けている、または 2021/1/32 のようにありえない値）が渡されたとき |
| `UnsupportedDateError` | `ValueError` | サポート範囲外の年が指定され、かつ `unsupported_date_behavior='error'`（デフォルト）のとき |
