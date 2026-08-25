# Copyright (c) 2026 Milkeyyy

from dataclasses import dataclass


@dataclass
class Player:
	"""クイズのプレイヤー (参加者)"""

	id: int
	"""プレイヤーのID"""
	point: int = 0
	"""ポイント (正答数)"""
	miss: bool = False
	"""不正解フラグ"""

	def correct(self) -> None:
		"""ポイントを1増やす"""
		self.point += 1

	def incorrect(self) -> None:
		"""不正解フラグを立てる"""
		self.miss = True

	def incorrect_reset(self) -> None:
		"""不正解フラグを消す"""
		self.miss = False

	def reset(self) -> None:
		"""ポイントと不正解フラグをリセット"""
		self.point = 0
		self.miss = False


@dataclass(frozen=True)
class Track:
	"""クイズで扱うトラック (I/O 非依存の値オブジェクト)"""

	uri: str | None
	title: str
	author: str
	source: str
	identifier: str | None = None
	artwork_url: str | None = None
	isrc: str | None = None
	length_ms: int | None = None


def is_same_track(left: Track | None, right: Track | None) -> bool:
	"""同一トラックかどうかを判定する (uri → identifier → (title, author, source) の優先順位)"""
	if left is None or right is None:
		return False
	if left.uri is not None and right.uri is not None:
		return left.uri == right.uri

	if left.identifier is not None and right.identifier is not None:
		return left.identifier == right.identifier

	return left.title == right.title and left.author == right.author and left.source == right.source
