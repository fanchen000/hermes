#!/usr/bin/env python3
"""Preserve explicitly reviewed language-neutral keys without fake translation.

Fails closed if a missing key has not been classified. Run after merge_manual.py
and before the final audit. No unreviewed English prose can be auto-accepted.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "App/Resources/Localizable.xcstrings"
MISSING = ROOT / ".l10n_artifacts/missing.json"
REVIEWED = ROOT / "Tools/zh_hans/verbatim_keys.json"


def main() -> int:
    groups = json.loads(REVIEWED.read_text(encoding="utf-8"))
    reasons = {}
    for reason, keys in groups.items():
        for key in keys:
            if key in reasons:
                raise ValueError(f"Duplicate preserved key: {key!r}")
            reasons[key] = reason
    missing = {item["key"] for item in json.loads(MISSING.read_text(encoding="utf-8"))}
    if missing != reasons.keys():
        raise ValueError(
            f"Unreviewed keys: {sorted(missing - reasons.keys())!r}; "
            f"stale classifications: {sorted(reasons.keys() - missing)!r}"
        )
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    for key, reason in reasons.items():
        catalog["strings"][key] = {
            "comment": f"zh-Hans: intentionally unchanged ({reason})",
            "extractionState": "manual",
            "localizations": {
                "zh-Hans": {"stringUnit": {"state": "translated", "value": key}}
            },
        }
    catalog["strings"] = dict(sorted(catalog["strings"].items()))
    CATALOG.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps({"preserved_exact": len(reasons), "by_reason": {
            name: len(keys) for name, keys in groups.items()
        }}, ensure_ascii=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
