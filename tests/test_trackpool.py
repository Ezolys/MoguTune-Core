# Copyright (c) 2026 Milkeyyy

import json
import random
from pathlib import Path

from mogutune_core import trackpool
from mogutune_core.models import Track

GOLDEN = Path(__file__).parent / "golden"
_Q_COUNT = 5


def test_dedupe_golden() -> None:
	data = json.loads((GOLDEN / "trackpool_dedupe.json").read_text(encoding="utf-8"))
	tracks = [Track(uri=uri, title=f"t-{i}", author="a", source="youtube") for i, uri in enumerate(data["input_uris"])]
	deduped = trackpool.dedupe(tracks)
	assert [t.uri for t in deduped] == data["expected_uris"]


def test_validate_golden() -> None:
	data = json.loads((GOLDEN / "trackpool_validate.json").read_text(encoding="utf-8"))
	for case in data["cases"]:
		expected = trackpool.PoolError[case["expected"]] if case["expected"] is not None else None
		assert trackpool.validate(case["unique_count"], case["q_count"]) == expected


def test_sample_questions_is_deterministic_with_same_seed() -> None:
	tracks = [Track(uri=f"u{i}", title=f"t{i}", author="a", source="youtube") for i in range(10)]
	first = trackpool.sample_questions(tracks, _Q_COUNT, random.Random(42))
	second = trackpool.sample_questions(tracks, _Q_COUNT, random.Random(42))
	assert [t.uri for t in first] == [t.uri for t in second]
	assert len(first) == _Q_COUNT
