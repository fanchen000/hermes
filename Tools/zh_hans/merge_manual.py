#!/usr/bin/env python3
"""Merge human-reviewed exact-match interface translations into the catalog."""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audit_catalog import tokens

CATALOG = ROOT / "App/Resources/Localizable.xcstrings"
MANUAL_FILES = sorted((ROOT / "Tools/zh_hans").glob("manual_*.json"))
MISSING = ROOT / ".l10n_artifacts/missing.json"

def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    manual = {}
    for file in MANUAL_FILES:
        translations = json.loads(file.read_text(encoding="utf-8"))
        for key, value in translations.items():
            if key in manual and manual[key] != value:
                raise ValueError(f"Conflicting manual translations: {key!r}")
            manual[key] = value
    missing = {item["key"] for item in json.loads(MISSING.read_text(encoding="utf-8"))}
    inserted = []
    skipped = []
    for key, value in manual.items():
        if key not in missing:
            skipped.append(key)
            continue
        if value == key:
            skipped.append(key)  # Product/protocol names remain unchanged.
            continue
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Untranslated or empty: {key!r}")
        if not re.search(r"[\u3400-\u9fff]", value):
            raise ValueError(f"No Chinese characters: {key!r} -> {value!r}")
        if tokens(key) != tokens(value):
            raise ValueError(f"Placeholder mismatch: {key!r} -> {value!r}")
        catalog["strings"][key] = {
            "extractionState": "manual",
            "localizations": {"zh-Hans": {"stringUnit": {"state": "translated", "value": value}}},
        }
        inserted.append(key)
    catalog["strings"] = dict(sorted(catalog["strings"].items()))
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"inserted": len(inserted), "already_present_or_not_extracted": len(skipped),
                      "catalog_total": len(catalog["strings"])}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
