# 初回セットアップ手順

`holiday-jp-pip` を新規にゼロから立ち上げる際、または別アカウント・別環境にフォークする際に必要な
**一度だけ実施すれば良い** 手順を記録する。日々の開発・公開フローは [cicd.md](cicd.md) を参照。

---

## 1. GitHub リポジトリ

### 1-1. リポジトリ作成

- リポジトリ名: `holiday-jp-pip`（PyPI 名と揃える）
- Visibility: Public（PyPI 公開する以上、ソースも公開が自然）
- ライセンス: MIT（`LICENSE` ファイル）

### 1-2. ブランチ・基本設定

- デフォルトブランチ: `main`
- Settings ＞ Actions ＞ General で **Workflow permissions** を確認：
   - Read and write permissions（Release 作成のため `contents: write` が必要）

### 1-3. Environments

Settings ＞ Environments で以下 2 つを作成：

| 名前 | 用途 | 推奨設定 |
|---|---|---|
| `testpypi` | TestPyPI ドライラン用 | 特に保護なしで OK |
| `pypi` | 本番公開用 | 任意で **Required reviewers** に自分を設定して承認ゲート |

これらは workflow YAML の `environment.name` と一致させる必要がある。

---

## 2. PyPI / TestPyPI アカウント

### 2-1. アカウント作成

- 本番: https://pypi.org/account/register/
- テスト: https://test.pypi.org/account/register/

両方とも **二要素認証（2FA）を有効化必須**（PyPI ポリシー）。
Recovery codes は安全な場所に保管する。

### 2-2. 初回 0.1.0 を手動公開（ブートストラップ）

Trusted Publishing は **既存プロジェクトに対して** 設定するため、最初の 1 回はトークン経由で
プロジェクトを作る必要がある。手順：

1. PyPI / TestPyPI で **Pending Publisher** として事前登録する方法もある（プロジェクト未作成でも OK）
   - https://pypi.org/manage/account/publishing/ ＞ "Add a new pending publisher"
   - これを使うなら 2-3 にスキップ可
2. または API トークンを発行（Account settings ＞ API tokens）し、`uv publish --token <TOKEN>` で初回公開
   - トークンは "Project scope" ではなく "Entire account" で発行（プロジェクト未作成のため）
   - 公開後はそのトークンを破棄して、Trusted Publishing に切り替える

### 2-3. Trusted Publishing 設定

プロジェクト作成済み（または Pending Publisher として事前登録済み）であれば、以下で OIDC 経由の
トークンレス公開を有効化できる。

**TestPyPI**: https://test.pypi.org/manage/project/holiday-jp-pip/settings/publishing/

| 項目 | 値 |
|---|---|
| Owner | `sway11466` |
| Repository name | `holiday-jp-pip` |
| Workflow name | `test-publish.yml` |
| Environment name | `testpypi` |

**PyPI**: https://pypi.org/manage/project/holiday-jp-pip/settings/publishing/

| 項目 | 値 |
|---|---|
| Owner | `sway11466` |
| Repository name | `holiday-jp-pip` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

設定後は `uv publish --trusted-publishing always` で API トークン不要で公開できる。
ワークフロー側で `permissions: id-token: write` を付与済み（[publish.yml](../.github/workflows/publish.yml) 参照）。

---

## 3. ローカル開発環境

### 3-1. uv のインストール

Windows:

```powershell
winget install --id=astral-sh.uv -e
```

その他の環境は https://docs.astral.sh/uv/getting-started/installation/ 参照。

### 3-2. リポジトリ取得 & 依存解決

```bash
git clone https://github.com/sway11466/holiday-jp-pip.git
cd holiday-jp-pip
uv sync
```

`.venv/` が作成され、`pytest` などの開発依存が入る。

### 3-3. 動作確認

```bash
uv run pytest          # 全テスト
uv build               # sdist + wheel をローカル生成
```

---

## 4. リポジトリ内のコミット済み設定（参考）

| ファイル | 役割 |
|---|---|
| `pyproject.toml` | パッケージメタデータ、ビルド設定、`uv` 依存定義、`pytest` 設定 |
| `uv.lock` | 依存ロック（再現性のためコミット） |
| `.gitignore` | Python 標準 + `.claude/settings.local.json` を除外 |
| `.github/workflows/test.yml` | push / PR で pytest（3 OS × 4 Python） |
| `.github/workflows/test-publish.yml` | 手動 `workflow_dispatch` で TestPyPI 公開 |
| `.github/workflows/publish.yml` | `v*` タグ push で PyPI 公開 + GitHub Release 自動作成 |

---

## 5. トラブルシューティング

### Trusted Publishing が反応しない

- `permissions: id-token: write` がジョブに付いているか確認
- workflow ファイル名と Trusted Publisher 登録の `Workflow name` が一致しているか
- Environment 名が一致しているか
- 該当 Environment が GitHub 側で作成されているか

### `uv publish` が "version already exists" で失敗

PyPI / TestPyPI は同一バージョンの再アップロードを禁止している。`pyproject.toml` の `version` と
`holiday_jp/__init__.py` の `__version__` を bump する。

### Windows で日本語が文字化け

`PYTHONIOENCODING=utf-8` を環境変数に設定する。
