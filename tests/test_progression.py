# Copyright (c) 2026 Milkeyyy

import json
from pathlib import Path

from mogutune_core.progression import Action, HostProgression, VoteProgression

GOLDEN = Path(__file__).parent / "golden"


def test_vote_thresholds_golden() -> None:
	data = json.loads((GOLDEN / "vote_thresholds.json").read_text(encoding="utf-8"))
	prog = VoteProgression(threshold_ratio=data["threshold_ratio"])
	for step in data["steps"]:
		action = Action[step["action"]]
		if "vote" in step:
			prog.vote(Action[step["vote"]["action"]], step["vote"]["user"])
		elif "unvote" in step:
			prog.unvote_on_leave(step["unvote"]["user"])
		else:
			prog.reset()
		assert prog.votes(action) == step["expected_votes"]
		assert prog.should_advance(action, data["active_players"]) is step["should_advance"]


def test_host_progression() -> None:
	prog = HostProgression()
	assert prog.can_advance(Action.NEXT, actor_id=1, owner_id=1) is True
	assert prog.can_advance(Action.NEXT, actor_id=2, owner_id=1) is False
