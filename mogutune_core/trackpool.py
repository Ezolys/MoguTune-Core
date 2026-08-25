# Copyright (c) 2026 Milkeyyy

import random
from enum import Enum

from mogutune_core.models import Track

MIN_TRACK_COUNT = 2
"""出題に必要な最低曲数"""
CHOICE_COUNT = 4
"""正解以外の選択肢数"""


class PoolError(Enum):
	"""出題プールの検証エラー種別 (メッセージへの写像は呼び出し側)"""

	TOO_FEW_TRACKS = "too_few_tracks"
	"""曲数が2曲未満"""
	NOT_ENOUGH_TRACKS = "not_enough_tracks"
	"""曲数が問題数 (および選択肢生成に必要な最小数) に足りない"""


def dedupe(tracks: list[Track]) -> list[Track]:
	"""URI が None の曲を除去し、URI 重複を除去する (出現順保持)"""
	unique_tracks: list[Track] = []
	seen_uris: set[str] = set()
	for track in tracks:
		if track.uri is None:
			continue
		if track.uri not in seen_uris:
			unique_tracks.append(track)
			seen_uris.add(track.uri)
	return unique_tracks


def validate(unique_count: int, q_count: int) -> PoolError | None:
	"""出題プールの検証を行う

	- unique_count < 2 → TOO_FEW_TRACKS
	- unique_count < max(q_count, 5) → NOT_ENOUGH_TRACKS
	- (選択肢は正解以外から4つサンプルするため、最低5曲必要)
	"""
	if unique_count < MIN_TRACK_COUNT:
		return PoolError.TOO_FEW_TRACKS
	if unique_count < max(q_count, CHOICE_COUNT + 1):
		return PoolError.NOT_ENOUGH_TRACKS
	return None


def sample_questions(tracks: list[Track], q_count: int, rng: random.Random) -> list[Track]:
	"""トラック一覧から問題数をランダムに取り出す"""
	return rng.sample(tracks, q_count)
