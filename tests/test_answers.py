# Copyright (c) 2026 Milkeyyy

import json
import random
from pathlib import Path

from mogutune_core import answers
from mogutune_core.models import Player, Track
from mogutune_core.roster import Roster

GOLDEN = Path(__file__).parent / "golden"
_CHOICE_COUNT = 5


def _make_state(**overrides: object) -> answers.AnswerState:
	state = answers.AnswerState()
	state.current_track_uri = overrides.get("current_track_uri", "https://example.com/current")
	state.can_answer = overrides.get("can_answer", True)
	state.answering_player_id = overrides.get("answering_player_id")
	return state


def _roster_with(ids: list[int], misses: list[bool] | None = None) -> Roster:
	roster = Roster()
	for i, user_id in enumerate(ids):
		roster.add_player(user_id)
		if misses and misses[i]:
			roster.get(user_id).miss = True
	return roster


def test_raise_hand_conflict_golden() -> None:
	data = json.loads((GOLDEN / "raise_hand_conflict.json").read_text(encoding="utf-8"))
	roster = _roster_with(data["players"])
	state = _make_state(**data["state"])
	for step in data["sequence"]:
		result = answers.check_raise_hand(state, roster, step["actor"])
		if step["expected"] == "PLAYER":
			assert isinstance(result, Player)
			assert result.id == step["player_id"]
			state.answering_player_id = result.id
		else:
			assert result == answers.RaiseHandError[step["expected"]]


def test_miss_chain_golden() -> None:
	data = json.loads((GOLDEN / "miss_chain.json").read_text(encoding="utf-8"))
	roster = _roster_with([p["id"] for p in data["players"]], [p["miss"] for p in data["players"]])
	state = _make_state()
	for check in data["checks"]:
		result = answers.check_raise_hand(state, roster, check["actor"])
		if check["expected"] == "MISS":
			assert result == answers.RaiseHandError.MISS
		else:
			assert isinstance(result, Player)
			assert result.id == check["player_id"]

	# 単独プレイヤーの場合は miss でも解答できる
	single = data["single_player"]
	roster2 = _roster_with([p["id"] for p in single["players"]], [p["miss"] for p in single["players"]])
	result = answers.check_raise_hand(_make_state(), roster2, single["actor"])
	assert isinstance(result, Player)
	assert result.id == single["player_id"]


def test_answer_timeout_golden() -> None:
	# 5秒未解答 → 不正解 (incorrect()) が呼ばれた後の状態を検証
	data = json.loads((GOLDEN / "answer_timeout.json").read_text(encoding="utf-8"))
	roster = Roster()
	roster.add_player(data["answering_player_id"])
	player = roster.get(data["answering_player_id"])
	player.incorrect()
	assert player.id == data["expected"]["id"]
	assert player.point == data["expected"]["point"]
	assert player.miss is data["expected"]["miss"]


def test_generate_choices() -> None:
	correct = Track(uri="c", title="C", author="a", source="youtube")
	pool = [Track(uri=f"u{i}", title=f"t{i}", author="a", source="youtube") for i in range(8)]
	choices = answers.generate_choices(correct, pool, random.Random(1))
	assert len(choices) == _CHOICE_COUNT
	assert correct in choices
	assert len({c.uri for c in choices}) == _CHOICE_COUNT


def test_is_correct() -> None:
	assert answers.is_correct("a", "a") is True
	assert answers.is_correct("a", "b") is False
	assert answers.is_correct(None, "a") is False
	assert answers.is_correct(None, None) is True


def test_refresh_misses() -> None:
	roster = _roster_with([1, 2], [True, True])
	answers.refresh_misses(roster)
	assert all(not p.miss for p in roster.players)
