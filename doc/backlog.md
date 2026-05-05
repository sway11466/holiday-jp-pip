# Backlog

公開準備および周辺作業の TODO リスト。完了したら削除する。

## 公開準備

- [ ] `doc/tutorial.md` を整備（基本〜応用ユースケース）

## 自動化

- [x] GitHub Actions: PyPI publish ワークフロー（tag トリガー、Trusted Publishing） → `.github/workflows/publish.yml`
- [ ] GitHub Actions: 内閣府 CSV を取得・UTF-8 変換してバンドルを更新（doc/architecture.md「祝日 CSV を UTF-8 変換する」ADR の将来構想）

## API 設計の保留事項

- [ ] `createCond` / `createDate` を公開するかの判断（JS 版にあり、Python では `_to_condition` として内部化中）
