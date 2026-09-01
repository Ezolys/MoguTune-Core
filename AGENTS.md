# AGENTS.md

MoguTune のイントロクイズロジックを抽出した I/O 非依存ライブラリ。Discord Bot (`MoguTune`) と Discord Activity (`MoguTune-Activity`) で共有する。

## コマンド

```sh
uv run pytest                     # 全テスト (sync のみ、DB 不要)
uv run pytest tests/test_ranking.py::test_ranking_ties_golden   # 単一テスト
uv run ruff check .               # lint (select=ALL ベース)
uv run ruff format --check .      # フォーマット検証 (タブインデント)
```

`uv` 管理 (`.venv` は gitignore 済み)、Python >= 3.13、CI なし。

## 設計上の制約 (README より)

- `discord` / `mafic` / `httpx` 等の I/O ライブラリの import 禁止。例外は `pymongo` で、`mogutune_core/db.py` のみ許可
- 乱数は必ず注入された `random.Random` を使う (直接 `random.*` を呼ばない)
- 日時は tz-aware の `datetime.datetime` を注入し、`now()` の直接呼び出しをしない

## スタイル

- タブインデント、line-length 140。コメント・docstring は日本語、全ファイル冒頭に `# Copyright (c) 2026 Milkeyyy` ヘッダー
- ruff は `F401` / `F841` が unfixable (自動削除しない。手動で対処)
- `tests/*.py` のみ `S101` (assert) / `S311` (決定論的乱数) を許可

## テストの注意点

- `tests/golden/*.json` は期待値を保持する golden テスト用フィクスチャ。ロジックを意図的に変えたらこの JSON も更新する必要がある
- ロケールは `mogutune_core/locales/{ja.json,en_GB.json}` で、`test_locales.py` がキー整合性を検証している

## その他

- `db.py` の `DBManager` は環境変数 `DB_URI` / `DB_NAME` を読み、`AsyncMongoClient` を使用 (コレクションは presets / guild_settings / playlists)。テストからは参照されない
- 公開 API は `mogutune_core/__init__.py` の `__all__` を維持する
