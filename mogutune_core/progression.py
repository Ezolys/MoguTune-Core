# Copyright (c) 2026 Milkeyyy

from enum import Enum


class Mode(Enum):
	"""進行モード"""

	HOST = "host"
	"""主催者のみが進行操作できる"""
	VOTE = "vote"
	"""過半数の投票で進行できる (枠組みのみ。UI は各フロントで後日実装)"""


class Action(Enum):
	"""進行操作"""

	NEXT = "next"
	"""次の問題へ"""
	SKIP = "skip"
	"""問題をスキップ"""
	END = "end"
	"""クイズを終了"""


class HostProgression:
	"""主催者による進行"""

	@staticmethod
	def can_advance(action: Action, actor_id: int, owner_id: int) -> bool:
		"""主催者のみ進行操作を許可する"""
		del action
		return actor_id == owner_id


class VoteProgression:
	"""投票による進行"""

	def __init__(self, threshold_ratio: float = 0.5) -> None:
		self.threshold_ratio = threshold_ratio
		"""可決に必要な投票数の割合 (過半数 = 厳密には > で判定)"""
		self._votes: dict[int, Action] = {}
		"""ユーザーID → 投票内容"""

	def vote(self, action: Action, user_id: int) -> None:
		"""投票する (重複投票は無視)"""
		if user_id not in self._votes:
			self._votes[user_id] = action

	def unvote_on_leave(self, user_id: int) -> None:
		"""退出時に投票を取り消す"""
		self._votes.pop(user_id, None)

	def votes(self, action: Action) -> int:
		"""指定したアクションへの投票数を返す"""
		return sum(1 for a in self._votes.values() if a is action)

	def should_advance(self, action: Action, active_players: int) -> bool:
		"""指定したアクションが可決するかどうかを返す (votes > active * ratio)"""
		return self.votes(action) > active_players * self.threshold_ratio

	def reset(self) -> None:
		"""問題遷移・解答開始時に投票をリセットする"""
		self._votes.clear()
