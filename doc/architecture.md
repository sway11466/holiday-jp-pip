# アーキテクチャー

ADR（Architecture Decision Record）に近い形でアーキテクチャーを残しておく。
JS 版 `holiday-jp-npm` の ADR を踏襲しつつ、Python 移植で追加検討した項目を加える。

## 祝日 CSV を腹持ちする
   - Decision（決定事項）
      - 祝日 CSV をリリースパッケージに含む
   - Context（経緯・背景情報）
      - スタンドアローンで動くことを重視
   - Consideration（比較・検討内容）
      - 起動時に CSV を取得しにいく
         - サポート期間が自動更新されるメリットはある
         - インターネット環境が必須になることは、取得元 URL を指定可能にすることで回避可能
         - 公開ファイルは Shift_JIS なので文字コード変換が必要となる事もあきらめた要因の 1 つ

## 祝日 CSV を UTF-8 変換する
   - Decision（決定事項）
      - Shift_JIS で公開されている祝日 CSV を UTF-8 変換してバンドルする
   - Context（経緯・背景情報）
      - リリースパッケージは外部ライブラリに依存したくない
      - Python は標準ライブラリで Shift_JIS（`encoding='cp932'`）を扱えるため、技術的にはそのまま読むことも可能
      - しかし JS 版と扱いを揃え、リポジトリ内の CSV を素直に読める状態に保つため UTF-8 化する
      - 将来的には CSV 取得と UTF-8 変換を GitHub Actions 等で自動化する
   - Consideration（比較・検討内容）
      - Shift_JIS のまま持ち、`open(..., encoding='cp932')` で読む
         - 最新ファイルをそのまま使えるメリットあり
         - JS 版とリポジトリ内ファイルの状態がずれるデメリット
      - SJIS 変換ライブラリではなく自前で必要最低限のバイナリ変換で補う
         - 使用される単語が限定的なのでありかもしれないが不毛

## 依存ライブラリ無し
   - Decision（決定事項）
      - リリースパッケージに依存ライブラリは使用しない
   - Context（経緯・背景情報）
      - 趣味の要素が強い
      - ライブラリを軽くしたい
      - Python 3.10+ なら `zoneinfo` が標準ライブラリにあるためタイムゾーン処理も追加依存なしで可能
   - Consideration（比較・検討内容）
      - 趣味なので特になし

## Python 3.10 以上を対象とする
   - Decision（決定事項）
      - サポート対象を Python 3.10 以上とする
   - Context（経緯・背景情報）
      - `zoneinfo` は 3.9 から標準だが、3.10 で安定して使える
      - `match` 構文や Union 型の `X | Y` 記法など、可読性に効く新機能が 3.10 から使える
      - 3.10 のサポート期限は 2026 年 10 月で十分長い
   - Consideration（比較・検討内容）
      - 3.9 以上にする
         - `zoneinfo` は使えるが、新しい型構文が使えず冗長
      - 3.11 以上にする
         - 古い環境を切るメリットが少ない

## シングルトンパターンを採用しない（クラス直接インスタンス化）
   - Decision（決定事項）
      - 公開 API は `HolidayJP(...)` クラスの直接インスタンス化のみとする
      - `use_holiday_jp()` のようなファクトリ関数や `scope='global'/'local'` のスコープ切替は提供しない
      - 各 `HolidayJP` インスタンスは独立しており、互いに影響しない
   - Context（経緯・背景情報）
      - JS 版（`useHolidayJP()` + `scope` オプション）は React Hooks 流のシングルトン共有パターンを採用していたが、これは React/モジュール再利用文化由来であり Python では一般的でない
      - Python の慣習は `requests.Session()`、`pathlib.Path()` のようにクラスを直接インスタンス化する形
      - `logging.getLogger(name)` 風のキャッシュ済み共有インスタンスもあるが、本ライブラリの「共有グローバル状態を mutate する」挙動とは性質が異なる
      - JS 版でも「グローバル extends がリセットされない問題」がテスト中に明示されており、グローバル共有はそもそも設計上の負債だった
   - Consideration（比較・検討内容）
      - `use_holiday_jp()` 関数を残す
         - JS 版と命名が揃い移植性は良いが、`use_*` は React Hooks 規約と衝突し Python では誤読を招く
      - `get_holiday_jp()` でシングルトンを提供する
         - `logging.getLogger` 流に倣えるが、共有設定を mutate する API は副作用が大きく Python 文化に馴染まない
      - シングルトンを使いたい利用者は自前で `_default = HolidayJP()` を定義すれば良い（明示的な方が望ましい）

## API 命名は React Hooks の `use_*` 接頭辞を使わない
   - Decision（決定事項）
      - 公開 API に `use_*` 接頭辞を持つ関数を含めない
   - Context（経緯・背景情報）
      - JS 版の `useHolidayJP()` は React Hooks の命名規約に倣ったもの
      - React の lint は「`use` で始まる関数は Hook」と解釈してフックの呼び出し位置を強制する
      - Python に Hooks の概念はなく、`use_*` 命名はノイズかつ誤読を招く
   - Consideration（比較・検討内容）
      - JS 版と命名を完全に揃える
         - 移植元との対応は明確になるが、Python ユーザーへの違和感が大きい

## 命名は snake_case に統一する
   - Decision（決定事項）
      - JS 版 API の camelCase は全て snake_case に変換する（`isHoliday` → `is_holiday`、`timezoneEffect` → `timezone_effect`）
   - Context（経緯・背景情報）
      - PEP 8 に従う
      - Python ユーザーに違和感のない API にする
   - Consideration（比較・検討内容）
      - JS 版と同じ camelCase を使う
         - 移植元との対応が分かりやすい反面、Python の慣習から外れる

## 曜日番号は Python の weekday() に揃える
   - Decision（決定事項）
      - `weekend` 設定の曜日番号は `datetime.date.weekday()`（0=月曜, 6=日曜）に従う
      - デフォルトは `[5, 6]`（土・日）
   - Context（経緯・背景情報）
      - JS 版は `Date.getDay()`（0=日曜, 6=土曜）でデフォルト `[0, 6]`
      - Python ユーザーが標準ライブラリと同じ感覚で使えるようにする
   - Consideration（比較・検討内容）
      - JS 版と同じ「0=日曜」を採用する
         - 移植時に番号を変換しなくてよいメリット
         - Python 標準と食い違うため利用者が混乱するデメリットの方が大きい

## local_date は JST 0:00 を表す TZ 付き datetime とする
   - Decision（決定事項）
      - `Holiday.local_date` は `datetime`（`tzinfo=JST` 付き、時刻は 0:00 固定）として保持する
      - 利用者は `local_date.astimezone(local_tz).date()` で実行環境タイムゾーンの日付を取得できる
   - Context（経緯・背景情報）
      - JS 版の `localDate` は `Date`（絶対時刻 + 実行環境 TZ で再解釈可能）として設計されていた
      - クラウドサーバー（UTC / US リージョン）から日本向けアプリを動かすケースで、利用者の TZ で日付を表示したい需要がある
      - Python は `datetime`（TZ-aware 可能）と `date`（TZ 非対応）を分けて持つ。瞬間を表現するには `datetime` が正しい
      - Python 文化として「TZ が関わるなら必ず TZ-aware にする」（ナイーブ datetime は事故の元）が広く支持されており、本決定はこの文化にも合致する
   - Consideration（比較・検討内容）
      - `local_date: date`（TZ 非対応の JST 固定日付）にする
         - シンプルで Windows の astimezone OS API 制約を踏まなくて済む
         - JS 版の TZ 再解釈機能を失う点が決定的な欠点（v0.1.x で採用していたが v0.2.0 で本案に変更）
      - `local_date: datetime`（ナイーブ）にする
         - Python 文化的に推奨されない（ナイーブ datetime の意味が曖昧）
      - 既存 fields（year/month/date）と重複するため `local_date` 自体を撤廃する
         - JS 版互換性を失う、また `astimezone` する起点として有用なため残す価値がある

## JST は固定オフセット +09:00 として扱う
   - Decision（決定事項）
      - JST を表現する際は `datetime.timezone(timedelta(hours=9))` を使い、`zoneinfo.ZoneInfo('Asia/Tokyo')` は使わない
   - Context（経緯・背景情報）
      - 日本は 1951 年以降 DST を採用していない（本ライブラリのデータ範囲 1955 年以降は常に +09:00）
      - Windows の Python 標準 `zoneinfo` は IANA tzdata を内蔵せず、`tzdata` パッケージか OS のタイムゾーンデータが必要
      - 依存ゼロ原則を貫くため、tzdata に依存しない固定オフセットを採用する
   - Consideration（比較・検討内容）
      - `ZoneInfo('Asia/Tokyo')` を使う
         - 意味的にはより正確だが、Windows での tzdata 依存が発生する

## createCond / createDate を公開しない
   - Decision（決定事項）
      - JS 版が公開している `createCond(Date)` / `createDate(HolidayJPCondition)` 相当のヘルパーメソッドは Python 版では公開しない
      - 内部の `_to_condition` は private のまま維持
   - Context（経緯・背景情報）
      - JS 版 `createCond`: `Date` から `{year, month, date}` を取り出すヘルパー
      - JS 版 `createDate`: `{year, month, date}` から JST 0:00 の `Date` を生成するヘルパー
      - Python では両方とも標準機能で 1 行で書ける：
         - `createCond(d)` 相当: `d.astimezone(JST)` してフィールド参照
         - `createDate({y,m,d})` 相当: `datetime(y, m, d, tzinfo=JST)`
      - `JST` 定数は v0.2.0 で公開済みなので利用者は即座に書ける
   - Consideration（比較・検討内容）
      - 公開する
         - JS 版とのメソッドパリティが取れる
         - 薄いラッパーを維持するコストと、利用者から見たときの「素の datetime で書けるのにメソッドがある」紛らわしさが上回る
      - `holiday_jp.to_jst_datetime(y, m, d)` のようなトップレベル関数として提供する
         - 結局 1 行ラッパーで価値が薄い

## Holiday データクラスは frozen にする
   - Decision（決定事項）
      - `Holiday` は `@dataclass(frozen=True)` で不変にする
   - Context（経緯・背景情報）
      - 祝日レコードは値オブジェクト的な性質を持ち、変更されると困る
      - 内部で複数インスタンスがベースデータを共有する設計のため、利用側が誤って書き換えるリスクを排除したい
   - Consideration（比較・検討内容）
      - 通常の dataclass にする
         - 利用者が書き換える誘惑が残る
