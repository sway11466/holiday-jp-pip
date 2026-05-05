# CICD ドキュメント

`holiday-jp-pip` の開発・テスト・ビルド・PyPI 公開手順。

Python 環境管理は **uv** を使用する。`uv` のインストールは [README](../README.md) または公式ドキュメント参照。

## 初回セットアップ

```bash
uv sync
```

`.venv/` が自動作成され、開発依存（`pytest`, `pytest-cov`）がインストールされる。

## テスト

### ローカル

```bash
uv run pytest
uv run pytest --cov=holiday_jp        # カバレッジ計測
uv run pytest -v tests/test_get.py    # 個別ファイル実行
```

Windows のコンソールで日本語を含むテスト出力を見る場合は `PYTHONIOENCODING=utf-8` を付ける。

### 自動テスト

GitHub Actions の [`test`](../.github/workflows/test.yml) ワークフローが `main` ブランチへの push と PR で起動する。
ubuntu / windows / macos × Python 3.10 / 3.11 / 3.12 / 3.13 のマトリクスで pytest を実行する。

## ビルド

```bash
uv build
```

`dist/holiday_jp_pip-{version}.tar.gz`（sdist）と `dist/holiday_jp_pip-{version}-py3-none-any.whl`（wheel）が生成される。

wheel の中身に `holiday_jp/syukujitsu.csv` と `holiday_jp/py.typed` が含まれていることを確認する：

```bash
uv run python -c "import zipfile; print('\n'.join(zipfile.ZipFile('dist/holiday_jp_pip-0.1.0-py3-none-any.whl').namelist()))"
```

## PyPI 公開

### 準備

1. PyPI と TestPyPI のそれぞれでアカウントを作成
   - https://pypi.org/account/register/
   - https://test.pypi.org/account/register/
2. プロジェクトスコープの API トークンを発行
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/
3. トークンは `UV_PUBLISH_TOKEN` 環境変数で渡すか、`~/.pypirc` に保存する
   - GitHub Actions では Repository Secrets に `PYPI_TOKEN` / `TEST_PYPI_TOKEN` として登録（自動公開ワークフロー実装時）

### TestPyPI で動作確認

本番公開の前に必ず TestPyPI で確認する。

```bash
uv build
uv publish --publish-url https://test.pypi.org/legacy/ --token $TEST_PYPI_TOKEN

# 別の venv で動作検証
uv pip install --index-url https://test.pypi.org/simple/ holiday-jp-pip
```

### PyPI 本番公開

1. `main` ブランチがリリース可能な状態（テスト pass、ドキュメント整備済み）であることを確認
2. `pyproject.toml` の `version` をバンプ（[SemVer](https://semver.org/) 準拠）
3. `holiday_jp/__init__.py` の `__version__` も同じ値に更新
4. コミットしてタグを切る
   ```bash
   git commit -am "chore: bump version to 0.1.0"
   git tag v0.1.0
   git push origin main --tags
   ```
5. ビルド & 公開
   ```bash
   uv build
   uv publish --token $PYPI_TOKEN
   ```

### 自動公開

公開には **Trusted Publishing（OIDC）** を使用し、長期 API トークンを保持しない。
PyPI / TestPyPI それぞれで Publisher 登録が必要（一度だけ、後述）。

#### TestPyPI ドライラン: [`.github/workflows/test-publish.yml`](../.github/workflows/test-publish.yml)

手動実行（`workflow_dispatch`）で TestPyPI に公開する。本番リリース前の動作確認用。

GitHub の Actions タブから `test-publish` を選び "Run workflow" をクリック。

```
pytest → uv build → uv publish --publish-url https://test.pypi.org/legacy/
```

#### 本番公開: [`.github/workflows/publish.yml`](../.github/workflows/publish.yml)

`v*` タグのプッシュをトリガーに以下を順に実行：

1. `pytest`（公開前の最終確認）
2. `uv build`（sdist + wheel）
3. `uv publish --trusted-publishing always`（PyPI へ公開）
4. GitHub Release を自動作成（自動生成リリースノート、dist/ 添付）

#### Trusted Publishing 初期設定（一度だけ）

**TestPyPI 側**:
1. https://test.pypi.org/manage/project/holiday-jp-pip/settings/publishing/
2. Owner: `sway11466` / Repository: `holiday-jp-pip` / Workflow: `test-publish.yml` / Environment: `testpypi`

**PyPI 側**:
1. https://pypi.org/manage/project/holiday-jp-pip/settings/publishing/
2. Owner: `sway11466` / Repository: `holiday-jp-pip` / Workflow: `publish.yml` / Environment: `pypi`

**GitHub 側**:
- Settings ＞ Environments で `testpypi` と `pypi` を作成
- 任意で `pypi` の方には Required reviewers を設定して承認ゲートにする

#### リリース手順

```bash
# 1. pyproject.toml と holiday_jp/__init__.py の __version__ をバンプ
# 2. コミット & push
# 3. （任意）GitHub Actions UI から test-publish を実行 → TestPyPI で動作確認
# 4. タグを切ってプッシュ
git tag v0.2.0
git push origin v0.2.0
```

→ ワークフローが PyPI 公開と GitHub Release 作成を自動で行う。

## 祝日 CSV の更新

バンドル CSV `holiday_jp/syukujitsu.csv` は内閣府公式 CSV を UTF-8 化して同梱したもの。
内閣府が CSV を更新したら手動で取り込む。

```bash
# 取得（cp932 → utf-8 変換）
uv run python -c "
import urllib.request
with urllib.request.urlopen('https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv') as r:
    raw = r.read()
with open('holiday_jp/syukujitsu.csv', 'w', encoding='utf-8', newline='') as f:
    f.write(raw.decode('cp932'))
"

# テストの max 件数チェックなどを更新
uv run pytest tests/test_loader.py tests/test_max.py
```

GitHub Actions による定期取得・更新は将来の検討事項（[backlog](backlog.md) 参照）。
