# Copyright (c) 2026 Milkeyyy

from dataclasses import dataclass

from mogutune_core.models import Player


@dataclass(frozen=True)
class RankEntry:
	"""ランキングの1行"""

	rank: int
	"""順位 (同点同順: 1,1,3形式)"""
	player_id: int
	"""プレイヤーのID"""
	point: int
	"""ポイント"""


def build_ranking(players: list[Player]) -> list[RankEntry]:
	"""ポイント降順のランキングを生成する (表示整形は呼び出し側)"""
	sorted_players = sorted(players, key=lambda p: p.point, reverse=True)

	entries: list[RankEntry] = []
	display_rank = 1
	for i, p in enumerate(sorted_players):
		# 前の人より点数が低ければ順位を更新 (同点の場合は順位を維持)
		if i > 0 and p.point < sorted_players[i - 1].point:
			display_rank = i + 1
		entries.append(RankEntry(rank=display_rank, player_id=p.id, point=p.point))
	return entries
