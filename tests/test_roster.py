# Copyright (c) 2026 Milkeyyy

from mogutune_core.models import Player
from mogutune_core.roster import RemoveReason, Roster


def test_add_player_and_get() -> None:
	roster = Roster()
	roster.add_player(1)
	assert roster.is_joined(1)
	player = roster.get(1)
	assert isinstance(player, Player)
	assert player.id == 1
	assert roster.get(2) is None


def test_add_player_duplicate_ignored() -> None:
	roster = Roster()
	roster.add_player(1)
	roster.add_player(1)
	assert len(roster.players) == 1


def test_remove_reasons() -> None:
	# 最後の1人が抜ける → NO_PLAYERS_LEFT
	roster = Roster()
	roster.add_player(1)
	roster.owner_id = 1
	assert roster.remove_player(1) == RemoveReason.NO_PLAYERS_LEFT

	# 主催者が抜ける → OWNER_LEFT (他のプレイヤーは残る)
	roster2 = Roster()
	roster2.add_player(1)
	roster2.add_player(2)
	roster2.owner_id = 1
	assert roster2.remove_player(1) == RemoveReason.OWNER_LEFT
	assert roster2.remove_player(2) == RemoveReason.NO_PLAYERS_LEFT

	# 主催者以外が抜ける → REMOVED
	roster3 = Roster()
	roster3.add_player(1)
	roster3.add_player(2)
	roster3.owner_id = 1
	assert roster3.remove_player(2) == RemoveReason.REMOVED


def test_remove_not_joined() -> None:
	roster = Roster()
	assert roster.remove_player(1) == RemoveReason.REMOVED


def test_queue() -> None:
	roster = Roster()
	roster.add_queue(1)
	roster.add_queue(1)
	assert roster.queue == [1]
	roster.remove_queue(1)
	assert roster.queue == []
	roster.add_queue(2)
	roster.join_queued_players()
	assert roster.is_joined(2)
	assert roster.queue == []
