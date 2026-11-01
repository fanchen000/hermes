#!/usr/bin/env python3
"""Sync localized app-extension strings from the reviewed primary catalog.

Read actual Swift compiler .stringsdata rather than inventing extension keys.
--check verifies committed catalogs without mutating them (used in CI).
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "App/Resources/Localizable.xcstrings"
TARGETS = {
    "Push/Widgets/Localizable.xcstrings": ("/Push/Widgets/", "/Push/Shared/"),
    "Push/NotificationContent/Localizable.xcstrings": ("/Push/NotificationContent/",),
}


def main() -> int:
    source_dir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".l10n_artifacts/strings"
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    all_keys = {name: set() for name in TARGETS}
    files = sorted(source_dir.glob("*.stringsdata"))
    if not files:
        raise ValueError("No compiler extraction files available")
    for file in files:
        obj = json.loads(file.read_text(encoding="utf-8"))
        origin = obj.get("source", "")
        for target, prefixes in TARGETS.items():
            if any(prefix in origin for prefix in prefixes):
                all_keys[target].update(
                    item["key"] for item in obj.get("tables", {}).get("Localizable", [])
                )
    for target, keys in all_keys.items():
        if not keys:
            raise ValueError(f"No extracted keys for extension {target}")
        missed = keys - source["strings"].keys()
        if missed:
            raise ValueError(f"Untranslated extension keys: {sorted(missed)}")
        result = {k: v for k, v in source.items() if k != "strings"}
        result["strings"] = {key: source["strings"][key] for key in sorted(keys)}
        path = ROOT / target
        if "--check" in sys.argv:
            previous = json.loads(path.read_text(encoding="utf-8"))
            if previous != result:
                raise ValueError(f"Extension translations are stale: {target}")
        else:
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{target}: {len(keys)} source-matched localized strings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
