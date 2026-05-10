# Backlog

公開準備および周辺作業の TODO リスト。完了したら削除する。

## next
- [ ] 急遽0.2にあげたので、仕様を確認したり残作業を行う
  - 腹持ちのCSVではなく外部CSVを渡すモードがあるという認識dが、その動きか？　外部CSVがないと動かない作りになっていたら想定外。
  - この差分は元npm版にはないので、READMEやドキュメントの更新も必要。
  - また、元npm版はextendsで独自祝日の追加ができたはず、今回の修正もextendsに寄せた方が良い気がしてる（要検討）


## ドキュメント

- [ ] `doc/tutorial.md` を整備（基本〜応用ユースケース）
- [ ] `CHANGELOG.md` を導入（GitHub Releases の自動生成ノートに加えて、人間が辿りやすい形で履歴を残す）

## 自動化

- [ ] GitHub Actions: 内閣府 CSV を取得・UTF-8 変換してバンドルを更新（doc/architecture.md「祝日 CSV を UTF-8 変換する」ADR の将来構想）
- [ ] `test-publish.yml` をタグ起動に変更し本番リリースと手順を揃える（例: `v*-rc*` / `test-v*` のような専用タグ push をトリガに TestPyPI へ公開。現状は `workflow_dispatch` で手動実行のため本番（`v*` タグ push）と手順が乖離している）

## 品質

- [ ] `ruff` を開発依存に追加（lint + format）し、`pyproject.toml` で設定
- [ ] CI（`.github/workflows/test.yml`）に `ruff check` ステップを追加
- [ ] `mypy` か `pyright` で `py.typed` 同梱の効果を検証

## 周辺

- [ ] 来年の祝日 CSV 更新（内閣府が 2028 年データを公開したタイミング、自動化が間に合わない場合は手動）
- [ ] Python 3.14 サポート追加（リリース時に CI matrix に追加）
- [ ] OSS 化を意識するなら `CONTRIBUTING.md` / `SECURITY.md` の追加（趣味プロジェクト範囲なら省略可）
