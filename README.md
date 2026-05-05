# holiday-jp-pip

内閣府ホームページの[「国民の祝日」について](https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html)に基づいて平日や祝日を判定する Python ライブラリです。
独自の祝日を追加することも可能です。

JS 版 [`@sway11466/holiday-jp-npm`](https://github.com/sway11466/holiday-jp-npm) の Python 移植版です。

- 判定ルール

    | 日付の種類 | 判定方法 |
    |------------|----------|
    | 平日 | 週末でも祝日でもない日 |
    | 週末 | 土曜日および日曜日（対象となる曜日は設定で変更可能） |
    | 祝日 | 内閣府ホームページの[「国民の祝日」について](https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html)に記載の祝日 |

- 判定の例（2024年5月）

    | 日付の種類 | 5/1(水) | 5/2(木) | 5/3(金) | 5/4(土) | 5/5(日) | 5/6(月) | 5/7(火) |
    |------------|---------|---------|---------|---------|---------|---------|---------|
    | 平日 | 〇 | 〇 | × | × | × | × | 〇 |
    | 週末 | × | × | × | 〇 | 〇 | × | × |
    | 祝日 | × | × | 〇 | 〇 | 〇 | 〇 | × |

## インストール

```
pip install holiday-jp-pip
```

## 使い方

- 初期化

    ```python
    from holiday_jp import HolidayJP
    holidayjp = HolidayJP()
    ```

- 指定日が祝日であるか判定する

    ```python
    from datetime import date
    ret = holidayjp.is_holiday(date(2021, 5, 3))  # 2021/5/3 憲法記念日
    print(ret)  # True
    ```

- 指定日が平日であるか判定する

    ```python
    ret = holidayjp.is_weekday(date(2021, 5, 7))  # 2021/5/7 平日
    print(ret)  # True
    ```

- 指定した条件に当てはまる祝日を取得する（例 1）

    ```python
    holidays = holidayjp.get(year=2021, month=5)
    print(len(holidays))           # 3
    print(holidays[0].name)        # 憲法記念日
    print(holidays[0].local_date)  # 2021-05-03 の date オブジェクト
    ```

- 指定した条件に当てはまる祝日を取得する（例 2）

    ```python
    holidays = holidayjp.get(year=2021, name="スポーツの日")
    print(len(holidays))           # 1
    print(holidays[0].local_date)  # 2021-07-23 の date オブジェクト
    ```

- 独自の祝日を追加する

    ```python
    from datetime import date
    from holiday_jp import HolidayJP, Holiday

    additional = [Holiday(year=2023, month=3, date=10, name="test", local_date=date(2023, 3, 10))]
    holidayjp = HolidayJP(extends=additional)
    ret = holidayjp.is_holiday(date(2023, 3, 10))
    print(ret)  # True
    ```

## 説明

- 1955 年〜2027 年に対応しています
    - 内閣府ホームページで公開しているデータに依存しているためです
    - 対応外の日付を指定するとエラーを起こします（設定で変更可能）
- このライブラリは実行環境のタイムゾーンを考慮して日本時間での祝日判定を行います
- [設定](./doc/setting.md)で以下の挙動を変更可能です
    - 対応外の日付を指定した場合のエラー発生有無
    - タイムゾーン考慮の有無
    - 週末として扱う曜日
    - 独自の祝日の追加
- より詳細な情報は [doc フォルダ](./doc/index.md) 内のドキュメントを参照してください
