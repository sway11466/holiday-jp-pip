# JS 版（holiday-jp-npm）との差分

`holiday-jp-pip` は JS 版 [`@sway11466/holiday-jp-npm`](https://github.com/sway11466/holiday-jp-npm) の Python 移植版です。
バンドルする祝日 CSV と全公開メソッドの**振る舞い**は等価ですが、API の形と一部の設計判断に差があります。

## 同一な点

- バンドル CSV: 内閣府公式 CSV を UTF-8 化したもの。**両版で SHA256 一致**（1955〜2027 年、計 1067 件）
- 公開メソッドの機能: `all` / `min` / `max` / `setting` / `get` / `is_holiday` / `is_weekend` / `is_weekday` / `is_valid_date` / `is_support_date`
- 設定オプションの意味: `timezone_effect` / `unsupported_date_behavior` / `weekend` / `extends`
- `Holiday.local_date` のセマンティクス: JS 0:00 の瞬間を保持し、利用者の TZ で再解釈可能（v0.2.0 で揃えた）

## 実装としての差分

### 1. グローバルシングルトンを廃止

| | JS | Python |
|---|---|---|
| エントリ | `useHolidayJP({scope: 'global' \| 'local'})` | `HolidayJP()` |
| 共有状態 | `scope='global'` で同一プロセス内に共有設定を保持 | なし。各 `HolidayJP()` は独立 |

JS 版は React Hooks 流の `useHolidayJP()` でグローバル共有設定を mutate するパターンでした。
Python では「インスタンスは引数で渡す」が一般的なため、共有を廃止して各インスタンスを独立させました。
グローバル共有が必要な場合は利用側で `_default = HolidayJP(...)` のように明示するのが推奨。

詳細: [architecture.md「シングルトンパターンを採用しない」](architecture.md#シングルトンパターンを採用しない（クラス直接インスタンス化）)

### 2. `createCond` / `createDate` を公開しない

JS 版が提供する `createCond(Date)` / `createDate(cond)` は Python 版では公開しません。
Python の標準機能で 1 行で書けるためです：

| JS | Python |
|---|---|
| `holidayjp.createCond(d)` | `d.astimezone(JST).year, .month, .day` |
| `holidayjp.createDate({y, m, d})` | `datetime(y, m, d, tzinfo=JST)` |

`JST` 定数は v0.2.0 から公開（`from holiday_jp import JST`）。
詳細: [architecture.md「createCond / createDate を公開しない」](architecture.md#createcond--createdate-を公開しない)

## Python 側で純増している便利機能

JS 版にはないが Python 版で追加されたもの：

- **キーワード引数対応**: `HolidayJP(timezone_effect=False, weekend=[6])` / `holidayjp.get(year=2021, month=5)`
- **`py.typed` 同梱**: 型ヒント完備（`Typing :: Typed` classifier）
- **`Holiday` が `frozen=True`**: 不変データクラス
- **`JST` 定数の公開**: `extends` 用 Holiday 構築時などに使える
- **型付き例外**: `InvalidDateError` / `UnsupportedDateError`（`ValueError` 派生）

## 機械的な命名差（言語慣習）

機能差ではなく言語の流儀に従った変換のみ：

| JS | Python |
|---|---|
| `useHolidayJP()` | `HolidayJP()` |
| `isHoliday()` `isWeekend()` etc. | `is_holiday()` `is_weekend()` etc. |
| `timezoneEffect` | `timezone_effect` |
| `unsupportedDateBehavior` | `unsupported_date_behavior` |
| `localDate` | `local_date` |
| `Date.getDay()` 0=日…6=土 | `date.weekday()` 0=月…6=日（`weekend` 設定の番号もこれに従う） |
| `true` / `false` / `Error` | `True` / `False` / `Exception` |

## バージョン履歴

- **v0.1.0**: 初版。`Holiday.local_date` は `datetime.date`（JST 固定）として実装。
- **v0.2.0**: `Holiday.local_date` を `datetime`（`tzinfo=JST`）に変更し、JS 版の `localDate` と等価に。
  ハワイ / UTC など非 JST 環境で `holiday.local_date.astimezone(local_tz).date()` により利用者ローカルの日付が得られるようになった。
