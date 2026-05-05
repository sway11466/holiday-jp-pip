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

## scope オプションでシングルトン／ローカルを切り替える
   - Decision（決定事項）
      - `scope='global'`（デフォルト）はモジュールレベルのシングルトンで設定を共有
      - `scope='local'` は独立インスタンスで他に影響しない
   - Context（経緯・背景情報）
      - JS 版の挙動をそのまま踏襲する
      - 既存利用者の使い方（scope 省略）と互換性を保つ
   - Consideration（比較・検討内容）
      - 常にインスタンスごと独立にする
         - シンプルだが JS 版と互換性が崩れる

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

## local_date は JST 日付に統一する
   - Decision（決定事項）
      - `Holiday.local_date` は常に JST 日付（`year/month/date` と一致する `datetime.date`）とする
   - Context（経緯・背景情報）
      - JS 版の `localDate` は実行環境タイムゾーンの `Date` オブジェクトを保持していた
      - Python の `datetime.date` はタイムゾーン非対応のため、TZ 依存の値を保持しても意味が曖昧になる
      - `datetime(...).astimezone()` で実行環境 TZ に変換する案は、Windows の OS API が 1970 年以前を扱えず `OSError` を発生させるため不採用
      - 実用上 `local_date` はライブラリ内部で使用されておらず、利用者向けの参照値である
   - Consideration（比較・検討内容）
      - `tzdata` パッケージを依存に追加して `zoneinfo` で正確な TZ 変換を行う
         - 依存ゼロ原則に反する
      - 実行環境の UTC オフセットを手動計算して TZ 変換する
         - DST 周辺で穴が出る可能性があり、コードが不必要に複雑になる

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

## Holiday データクラスは frozen にする
   - Decision（決定事項）
      - `Holiday` は `@dataclass(frozen=True)` で不変にする
   - Context（経緯・背景情報）
      - 祝日レコードは値オブジェクト的な性質を持ち、変更されると困る
      - シングルトンスコープで共有される際、利用側が誤って書き換えるリスクを排除したい
   - Consideration（比較・検討内容）
      - 通常の dataclass にする
         - 利用者が書き換える誘惑が残る
