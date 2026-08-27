# Copyright (c) 2026 Milkeyyy

"""Discord Activity 用の共有プロトコル (クライアント ↔ Activity サーバー ↔ ボット)

時刻はすべてエポックミリ秒 (float) で表す。サーバー (ボット) は表示文言を返さず、
必ずロケールキー (とパラメータ) のみを返す。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, TypeAdapter

from mogutune_core.progression import Action, Mode

# --- C→S (クライアント → ボット) ---


class StartMessage(BaseModel):
	"""ゲーム開始 (host のみ有効。vote は枠組みのみで現状エラー)"""

	type: Literal["start"]
	query: str
	q_count: int = Field(ge=1, le=50)
	mode: Mode = Mode.HOST


class RaiseHandMessage(BaseModel):
	"""早押し"""

	type: Literal["raise_hand"]


class AnswerMessage(BaseModel):
	"""5択の解答 (選択肢の uri)"""

	type: Literal["answer"]
	uri: str


class AdvanceMessage(BaseModel):
	"""主催者による進行操作"""

	type: Literal["advance"]
	action: Action


class VoteMessage(BaseModel):
	"""投票による進行 (枠組みのみ。mode != vote なら無視)"""

	type: Literal["vote"]
	action: Action


class PingMessage(BaseModel):
	"""時計オフセット推定用"""

	type: Literal["ping"]
	t: float


ClientMessage = StartMessage | RaiseHandMessage | AnswerMessage | AdvanceMessage | VoteMessage | PingMessage

client_message_adapter = TypeAdapter(ClientMessage)

# --- S→C (ボット → クライアント) ---


class PongMessage(BaseModel):
	type: Literal["pong"] = "pong"
	t: float
	server_time: float


class PlayerState(BaseModel):
	id: int
	username: str
	avatar: str
	point: int
	miss: bool
	answering: bool


class TrackInfo(BaseModel):
	"""答え情報 (正解公開後にのみ送信される)"""

	uri: str
	title: str
	author: str
	artwork_url: str | None = None


class ProgressionState(BaseModel):
	"""自分が押せる進行操作"""

	next: bool
	skip: bool
	end: bool


class StateMessage(BaseModel):
	type: Literal["state"] = "state"
	phase: Literal["lobby", "playing", "answered", "results"]
	mode: str
	owner_id: int | None
	players: list[PlayerState]
	q_number: int
	q_count: int
	current_answerer: int | None = None
	answer_deadline: float | None = None
	revealed_track: TrackInfo | None = None
	"""正解公開後のみ"""
	progression: ProgressionState


class QuestionStartMessage(BaseModel):
	type: Literal["question_start"] = "question_start"
	q_number: int
	start_at: float
	duration_ms: int | None
	"""length_ms 不明の場合は None (再生終了イベントで次へ)"""
	deadline: float | None = None


class AnsweringMessage(BaseModel):
	type: Literal["answering"] = "answering"
	user_id: int
	deadline: float
	choices: list[TrackInfo]


class AnswerResultMessage(BaseModel):
	type: Literal["answer_result"] = "answer_result"
	user_id: int
	correct: bool
	track: TrackInfo
	progression: ProgressionState


class ResumeMessage(BaseModel):
	"""不正解後の再生再開"""

	type: Literal["resume"] = "resume"
	resume_at: float


class RankingEntry(BaseModel):
	rank: int
	user_id: int
	point: int


class QuizEndMessage(BaseModel):
	type: Literal["quiz_end"] = "quiz_end"
	ranking: list[RankingEntry]


class ErrorMessage(BaseModel):
	type: Literal["error"] = "error"
	key: str
	params: list[object] = []


ServerMessage = (
	PongMessage
	| StateMessage
	| QuestionStartMessage
	| AnsweringMessage
	| AnswerResultMessage
	| ResumeMessage
	| QuizEndMessage
	| ErrorMessage
)

server_message_adapter = TypeAdapter(ServerMessage)

# --- ブリッジ (Activity サーバー ↔ ボット) ---


class BridgeUser(BaseModel):
	id: int
	username: str
	avatar: str
	locale: str


class JoinMessage(BaseModel):
	"""ユーザーの参加 (Activity サーバー → ボット)"""

	type: Literal["join"]
	instance_id: str
	guild_id: int
	channel_id: int
	user: BridgeUser


class LeaveMessage(BaseModel):
	"""ユーザーの退出 (Activity サーバー → ボット)"""

	type: Literal["leave"]
	instance_id: str
	user_id: int


class StateRequestMessage(BaseModel):
	"""再接続時の state 再送要求 (Activity サーバー → ボット)"""

	type: Literal["state_request"]
	instance_id: str


class ClientRelayMessage(BaseModel):
	"""クライアントメッセージの中継 (Activity サーバー → ボット)"""

	type: Literal["client"]
	instance_id: str
	user_id: int
	message: ClientMessage


class BridgePingMessage(BaseModel):
	"""クライアントの ping 中継 (Activity サーバー → ボット)"""

	type: Literal["ping"]
	instance_id: str
	t: float


class ServerRelayMessage(BaseModel):
	"""ボット → Activity サーバー: クライアントへ配信するサーバーメッセージ

	user_id 指定時はそのユーザーのみへ配信、None はインスタンス全体へブロードキャスト。
	"""

	type: Literal["message"]
	instance_id: str
	user_id: int | None = None
	message: ServerMessage


class BridgePongMessage(BaseModel):
	"""ボット → Activity サーバー: ping 応答 (server_time はボットの時刻)"""

	type: Literal["pong"]
	instance_id: str
	t: float
	server_time: float


BridgeToBotMessage = JoinMessage | LeaveMessage | StateRequestMessage | ClientRelayMessage | BridgePingMessage

bridge_to_bot_adapter = TypeAdapter(BridgeToBotMessage)

BridgeToServerMessage = ServerRelayMessage | BridgePongMessage

bridge_to_server_adapter = TypeAdapter(BridgeToServerMessage)
