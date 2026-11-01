#!/usr/bin/env python3
"""Import exact-key translations from the MIT-licensed Hermex Chinese catalog.

Only identical source strings are eligible. Existing translations always win.
This does not perform fuzzy translation and does not claim complete coverage.
Usage: python Tools/zh_hans/import_translation_memory.py [--apply]
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audit_catalog import PRINTF

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEST = ROOT / "App/Resources/Localizable.xcstrings"
MEMORY = ROOT / ".l10n_artifacts/hermex_Localizable.xcstrings"
EXTRACTED = ROOT / ".l10n_artifacts/missing.json"
HAN = re.compile(r"[\u3400-\u9fff]")

def placeholders(s: str) -> list[str]:
    return sorted(t.split("$")[-1] for t in PRINTF.findall(s) if t != "%%")

def main() -> int:
    dest = json.loads(DEST.read_text(encoding="utf-8"))
    memory = json.loads(MEMORY.read_text(encoding="utf-8"))
    missing = {x["key"] for x in json.loads(EXTRACTED.read_text(encoding="utf-8"))}
    source_catalog = memory.get("strings", {})
    importable = {}
    reasons = collections.Counter()
    for key in sorted(missing):
        source = source_catalog.get(key)
        if not source:
            reasons["no_exact_key"] += 1
            continue
        locale = (source.get("localizations") or {}).get("zh-Hans", {})
        unit = locale.get("stringUnit", {})
        value = unit.get("value")
        if not isinstance(value, str) or not value.strip() or unit.get("state") != "translated":
            reasons["no_translated_zh_hans"] += 1
            continue
        if not HAN.search(value):
            reasons["no_chinese_characters"] += 1
            continue
        if placeholders(key) != placeholders(value):
            reasons["placeholder_mismatch"] += 1
            continue
        if "Hermex" in value and "Hermex" not in key:
            reasons["foreign_product_name"] += 1
            continue
        if key.count("\n") != value.count("\n"):
            reasons["newline_mismatch"] += 1
            continue
        importable[key] = {"extractionState":"manual", "localizations":{"zh-Hans":{"stringUnit":{"state":"translated", "value":value}}}}
    print(json.dumps({"missing_before": len(missing), "exact_importable": len(importable), "reasons": reasons}, ensure_ascii=False, indent=2))
    if "--apply" in sys.argv:
        dest["strings"].update(importable)
        dest["strings"] = dict(sorted(dest["strings"].items(), key=lambda item:item[0]))
        DEST.write_text(json.dumps(dest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Applied {len(importable)} exact-key translations. MIT attribution required.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
