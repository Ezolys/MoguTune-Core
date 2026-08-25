# Copyright (c) 2026 Milkeyyy

import random
from enum import Enum
from typing import TYPE_CHECKING

from mogutune_core.models import Player, Track
from mogutune_core.roster import Roster

if TYPE_CHECKING:
	from datetime import datetime


class RaiseHandError(Enum):
	"""早押しの拒否理由"""

	NOT_PLAYING = "not_playing"
	"""再生中のトラックがない"""
	ALREADY_ANSWERING = "already_answering"
	"""別のプレイヤーが解答中"""
	CANNOT_ANSWER = "cannot_answer"
	"""解答できない状態"""
	NOT_JOINED = "not_joined"
	"""クイズに参加していない"""
	MISS = "miss"
	"""お手つき中"""


class AnswerState:
	"""解答に関する状態の容器"""

	def __init__(self) -> None:
		self.can_answer: bool = False
		"""解答ができる状態かどうか"""
		self.answering_player_id: int | None = None
		"""現在解答中のプレイヤーのID"""
		self.question_started_at: datetime | None = None
		"""問題開始時刻"""
		self.current_track_uri: str | None = None
		"""現在再生中のトラックのURI (None なら再生中でない)"""


def check_raise_hand(state: AnswerState, roster: Roster, user_id: int) -> Player | RaiseHandError:
	"""早押しの受理判定を行う

	判定順序は既存 session.py の raise_hand を踏襲:
	1) 再生中のトラックがない → NOT_PLAYING
	2) 解答中のプレイヤーがいる → ALREADY_ANSWERING
	3) 解答できない状態 → CANNOT_ANSWER
	4) 参加していない → NOT_JOINED
	5) お手つき中かつ2人以上 → MISS
	"""
	if state.current_track_uri is None:
		return RaiseHandError.NOT_PLAYING
	if state.answering_player_id is not None:
		return RaiseHandError.ALREADY_ANSWERING
	if not state.can_answer:
		return RaiseHandError.CANNOT_ANSWER

	player = roster.get(user_id)
	if player is None:
		return RaiseHandError.NOT_JOINED

	# お手つき中のプレイヤーをはじく (プレイヤー数一人の場合ははじかない)
	if player.miss and len(roster.players) > 1:
		return RaiseHandError.MISS

	return player


def generate_choices(correct: Track, pool: list[Track], rng: random.Random) -> list[Track]:
	"""正解以外から4つサンプルし、正解を足してシャッフルした5択を返す"""
	other_tracks = [t for t in pool if t.uri != correct.uri]
	dummy_tracks = rng.sample(other_tracks, 4)
	answer_options = [*dummy_tracks, correct]
	rng.shuffle(answer_options)
	return answer_options


def is_correct(answer_uri: str | None, current_uri: str | None) -> bool:
	"""解答が正解かどうかを判定する"""
	return current_uri == answer_uri


def refresh_misses(roster: Roster) -> None:
	"""全プレイヤーの不正解フラグをリセットする"""
	for player in roster.players:
		player.incorrect_reset()
