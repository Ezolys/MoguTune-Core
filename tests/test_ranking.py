# Copyright (c) 2026 Milkeyyy

import json
from pathlib import Path

from mogutune_core import ranking
from mogutune_core.models import Player

GOLDEN = Path(__file__).parent / "golden"


def test_ranking_ties_golden() -> None:
	data = json.loads((GOLDEN / "ranking_ties.json").read_text(encoding="utf-8"))
	players = [Player(id=p["id"], point=p["point"]) for p in data["players"]]
	entries = ranking.build_ranking(players)
	assert [(e.rank, e.player_id, e.point) for e in entries] == [(e["rank"], e["player_id"], e["point"]) for e in data["expected"]]


def test_ranking_empty() -> None:
	assert ranking.build_ranking([]) == []


def test_ranking_single() -> None:
	entries = ranking.build_ranking([Player(id=1, point=3)])
	assert entries == [ranking.RankEntry(rank=1, player_id=1, point=3)]
