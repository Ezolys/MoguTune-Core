# mogutune-core

MoguTune のイントロクイズボットから抽出した、I/O を持たない純粋なゲームロジック。

Discord Bot (`MoguTune`) と Discord Activity (`MoguTune-Activity`) で同一コードを共有するために使用する。

## 制約

- `discord` / `mafic` / `httpx` 等の I/O ライブラリを import 禁止 (例外: `pymongo` は `mogutune_core/db.py` のみ)
- 乱数は必ず注入された `random.Random` を使う
- 日時は `datetime.datetime` (tz-aware) を注入し、`now()` の直接呼び出しをしない
