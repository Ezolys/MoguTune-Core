# Copyright (c) 2026 Milkeyyy

from enum import Enum

from mogutune_core.models import Player


class RemoveReason(Enum):
	"""プレイヤー削除の結果"""

	REMOVED = "removed"
	"""通常の削除"""
	NO_PLAYERS_LEFT = "no_players_left"
	"""プレイヤーが0人になった"""
	OWNER_LEFT = "owner_left"
	"""主催者が退出した"""


class Roster:
	"""参加者の一覧・参加待ちキュー・主催者を管理する"""

	def __init__(self) -> None:
		self.players: list[Player] = []
		"""参加者一覧"""
		self.owner_id: int | None = None
		"""主催者のID"""
		self.queue: list[int] = []
		"""参加待ちのプレイヤーのID"""

	def add_player(self, user_id: int) -> None:
		"""プレイヤーを追加する (重複は無視)"""
		if self.is_joined(user_id):
			return
		self.players.append(Player(user_id))

	def remove_player(self, user_id: int) -> RemoveReason:
		"""プレイヤーを削除する

		終了処理 (end) は呼び出さない。NO_PLAYERS_LEFT / OWNER_LEFT の場合は
		呼び出し側 (ボット: session.end / Activity: room.end) が終了処理を行う。
		"""
		if not self.is_joined(user_id):
			return RemoveReason.REMOVED
		self.players = [player for player in self.players if player.id != user_id]
		if not self.players:
			return RemoveReason.NO_PLAYERS_LEFT
		if self.owner_id is not None and self.owner_id == user_id:
			return RemoveReason.OWNER_LEFT
		return RemoveReason.REMOVED

	def add_queue(self, user_id: int) -> None:
		"""参加待ちのプレイヤーを追加する (重複は無視)"""
		if user_id in self.queue:
			return
		self.queue.append(user_id)

	def remove_queue(self, user_id: int) -> None:
		"""参加待ちのプレイヤーを削除する"""
		if user_id in self.queue:
			self.queue.remove(user_id)

	def join_queued_players(self) -> None:
		"""参加待ちのプレイヤー全員を参加させる"""
		for user_id in self.queue:
			self.add_player(user_id)
		self.queue = []

	def is_joined(self, user_id: int) -> bool:
		"""プレイヤーが参加しているかどうかを返す"""
		return user_id in [player.id for player in self.players]

	def get(self, user_id: int) -> Player | None:
		"""プレイヤーを取得する (存在しない場合は None)"""
		for player in self.players:
			if player.id == user_id:
				return player
		return None
