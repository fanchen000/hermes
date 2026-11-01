#!/usr/bin/env python3
"""Audit a zh-Hans catalog against Xcode compiler-extracted .stringsdata.

Offline, stdlib-only; never reads credentials or calls network endpoints.
Use: python Tools/zh_hans/audit_catalog.py .l10n_artifacts/strings
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CATALOG = ROOT / "App/Resources/Localizable.xcstrings"
OUTPUT = ROOT / ".l10n_artifacts"

# Placeholders may be printf-style, positional, or Swift's compiled substitution.
PRINTF = re.compile(r"%(?:(?:[1-9]\d*)\$)?[-+# 0']*\d*(?:\.\d+)?(?:hh|ll|[hlLzjt])?[@dDuUxXfFeEgGcCsSpPaA%]")
SWIFT = re.compile(r"\\\([^)]*\)")
JS_TEMPLATE = re.compile(r"\$\{[^}]*\}")

def tokens(value: str) -> list[str]:
    # Compare base type, not positional index: translators may reorder indices.
    return sorted(t.split("$")[-1] for t in PRINTF.findall(value) if t != "%%")

def main() -> int:
    source_dir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUTPUT / "strings"
    files = sorted(source_dir.glob("*.stringsdata"))
    keys = collections.defaultdict(lambda: collections.defaultdict(set))
    bad_files = []
    for file in files:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            source = data.get("source", "")
            for table, entries in (data.get("tables") or {}).items():
                for entry in entries:
                    key = entry.get("key")
                    if isinstance(key, str) and key:
                        keys[table][key].add(source)
        except (ValueError, OSError, TypeError, AttributeError) as exc:
            bad_files.append({"file": file.name, "error": str(exc)})
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    existing = catalog.get("strings", {})
    translated = {}
    missing = []
    invalid = []
    verbatim = {}
    for key, sources in sorted(keys["Localizable"].items()):
        node = existing.get(key, {})
        value = (node.get("localizations") or {}).get("zh-Hans", {}).get("stringUnit", {}).get("value")
        state = (node.get("localizations") or {}).get("zh-Hans", {}).get("stringUnit", {}).get("state")
        approved_whitespace = (
            value == key
            and "intentionally unchanged (" in node.get("comment", "")
        )
        if (
            not isinstance(value, str)
            or (not value.strip() and not approved_whitespace)
            or state != "translated"
        ):
            missing.append({"key": key, "sources": sorted(sources)})
        else:
            translated[key] = value
            if value == key:
                comment = node.get("comment", "")
                if "intentionally unchanged (" in comment:
                    verbatim[key] = comment
                elif re.search(r"[A-Za-z]{3}", key):
                    invalid.append({"key": key, "reason": "unreviewed_verbatim_key"})
            if tokens(key) != tokens(value):
                invalid.append({"key": key, "translation": value, "reason": "printf_placeholder_mismatch"})
            if SWIFT.findall(key) != SWIFT.findall(value):
                invalid.append({"key": key, "translation": value, "reason": "swift_interpolation_mismatch"})
            if JS_TEMPLATE.findall(key) != JS_TEMPLATE.findall(value):
                invalid.append({"key": key, "translation": value, "reason": "javascript_interpolation_mismatch"})
            if key != value and not re.search("[\u3400-\u9fff]", value) and re.search("[A-Za-z]{3}", key):
                invalid.append({"key": key, "translation": value, "reason": "possibly_untranslated"})
    OUTPUT.mkdir(exist_ok=True)
    report = {
        "extract_files": len(files),
        "bad_extract_files": bad_files,
        "table_unique_keys": {name: len(entries) for name, entries in keys.items()},
        "localizable_extracted": len(keys["Localizable"]),
        "localizable_translated": len(translated),
        "localizable_missing": len(missing),
        "reviewed_verbatim_count": len(verbatim),
        "natural_language_or_prior_translations": len(translated) - len(verbatim),
        "full_catalog_coverage": (not missing and not invalid and not bad_files),
        "catalog_entries_total": len(existing),
        "catalog_entries_not_in_compiler_extract": len(set(existing) - set(keys["Localizable"])),
        "invalid_translations": invalid,
    }
    (OUTPUT / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT / "missing.json").write_text(json.dumps(missing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if bad_files or invalid or ("--require-full" in sys.argv and missing) else 0

if __name__ == "__main__":
    raise SystemExit(main())
