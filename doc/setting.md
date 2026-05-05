# ライブラリの設定

`HolidayJP(...)` に渡すキーワード引数で動作を変更できる。

```python
from holiday_jp import HolidayJP, Holiday
from datetime import date

holidayjp = HolidayJP(
    timezone_effect=True,
    unsupported_date_behavior="error",
    weekend=[5, 6],
    extends=[],
)
```

すべて省略可能。設定値はインスタンスごとに独立しており、複数の `HolidayJP` を生成しても互いに影響しない。
現在の設定値は `holidayjp.setting()` で取得できる（返り値は **コピー** で、変更しても本体に反映されない）。

---

## timezone_effect

- 何の設定？
    - 入力 `datetime` を JST に変換してから日付を取り出すか否か
- 型: `bool`
- デフォルト値: `True`
- 説明
    - `True` の場合、`datetime` を引数に取るメソッドは `astimezone(JST)` で JST に変換してから `year/month/day` を抽出する
    - `False` の場合、`datetime` の `year/month/day` をそのまま使う（タイムゾーン情報を無視）
    - 利用側で既に JST 変換済みの `datetime` を渡す場合は `False` にすると無駄な変換を避けられる
    - `datetime.date`（時刻なし）と `dict` 入力には影響しない

## unsupported_date_behavior

- 何の設定？
    - サポート範囲外の年が指定された場合の挙動
- 型: `Literal["error", "ignore"]`
- デフォルト値: `"error"`
- 説明
    - サポート範囲は内閣府ホームページの[「国民の祝日」について](https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html)に記載される範囲（おおむね 1955 年〜現在年＋1 年）
    - `"error"` を指定すると、サポート外の年が指定されたとき `UnsupportedDateError` を送出
    - `"ignore"` を指定すると、サポート外の年が指定されてもエラーにならない
        - `get` は空配列を返す
        - `is_holiday` は `False` を返す（サポート外の日付には祝日が存在しない前提）
        - `is_weekend` は通常通りカレンダー上の曜日で判定する
        - `is_weekday` は週末でなければ `True` を返す（祝日が存在しない前提）

## weekend

- 何の設定？
    - 週末として扱う曜日
- 型: `list[int]`
- デフォルト値: `[5, 6]`（土曜・日曜）
- 説明
    - 各値は `datetime.date.weekday()` に従い 0=月曜, 6=日曜
    - JS 版（`Date.getDay()` で 0=日曜, 6=土曜）と番号体系が異なる点に注意
- 使用例

    ```python
    # 月〜金を「週末」とするカレンダー
    HolidayJP(weekend=[0, 1, 2, 3, 4])
    ```

## extends

- 何の設定？
    - 祝日として扱う日付を追加する
- 型: `list[Holiday]`
- デフォルト値: `[]`
- 説明
    - 既存のバンドル CSV に加えて、独自の `Holiday` レコードを判定対象に含める
    - 同じ年・月・日の `Holiday` を複数登録した場合は、`get()` が複数件を返す
- 使用例

    ```python
    from datetime import date
    from holiday_jp import HolidayJP, Holiday

    custom = [Holiday(year=2099, month=12, date=31, name="社内記念日",
                       local_date=date(2099, 12, 31))]
    holidayjp = HolidayJP(extends=custom)
    holidayjp.is_holiday(date(2099, 12, 31))  # True
    ```
