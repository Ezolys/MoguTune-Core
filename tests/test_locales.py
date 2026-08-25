# Copyright (c) 2026 Milkeyyy

import json
from importlib import resources

LOCALES = resources.files("mogutune_core") / "locales"


def _flatten(d: dict, parent: str = "", sep: str = ".") -> dict:
	items: dict = {}
	for k, v in d.items():
		key = f"{parent}{sep}{k}" if parent else k
		if isinstance(v, dict):
			items.update(_flatten(v, key, sep))
		else:
			items[key] = v
	return items


def test_locale_keys_match() -> None:
	ja = json.loads((LOCALES / "ja.json").read_text(encoding="utf-8"))
	en = json.loads((LOCALES / "en_GB.json").read_text(encoding="utf-8"))
	assert _flatten(ja).keys() == _flatten(en).keys()
