#!/usr/bin/env python3
"""Check an IPA's compiled Chinese strings, integrity and minimum OS."""
import json
import pathlib
import plistlib
import re
import sys
import zipfile

def main():
    path = pathlib.Path(sys.argv[1])
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f"Corrupt ZIP member: {bad}")
        names = z.namelist()
        apps = sorted({part.split("/")[1] for part in names
                       if part.startswith("Payload/") and part.count("/") > 1
                       and part.split("/")[1].endswith(".app")})
        if len(apps) != 1:
            raise ValueError(f"Expected one iOS .app, found {apps}")
        prefix = f"Payload/{apps[0]}/"
        info = plistlib.loads(z.read(prefix + "Info.plist"))
        localized = prefix + "zh-Hans.lproj/Localizable.strings"
        if localized not in names:
            raise ValueError("Compiled zh-Hans Localizable.strings missing")
        data = z.read(localized)
        try:
            entries = plistlib.loads(data)
        except Exception as exc:
            raise ValueError("Compiled Localizable.strings is not an Apple plist") from exc
        if not isinstance(entries, dict):
            raise ValueError("Compiled localization is not a dictionary")
        matched = None
        info_matched = None
        if "--verify-catalog" in sys.argv:
            source = pathlib.Path(__file__).resolve().parents[2] / "App/Resources/Localizable.xcstrings"
            catalog = json.loads(source.read_text(encoding="utf-8"))["strings"]
            expected = {
                k: v["localizations"]["zh-Hans"]["stringUnit"]["value"]
                for k, v in catalog.items()
                if "zh-Hans" in v.get("localizations", {})
            }
            mismatches = {
                key: {"expected": value, "actual": entries.get(key)}
                for key, value in expected.items()
                if entries.get(key) != value
            }
            if mismatches:
                preview = dict(list(mismatches.items())[:6])
                raise ValueError(f"{len(mismatches)} compiled/catalog mismatches: {preview}")
            matched = len(expected)
            info_strings = prefix + "zh-Hans.lproj/InfoPlist.strings"
            if info_strings not in names:
                raise ValueError("Compiled zh-Hans InfoPlist.strings missing")
            info_entries = plistlib.loads(z.read(info_strings))
            info_source = (pathlib.Path(__file__).resolve().parents[2] /
                           "App/Resources/zh-Hans.lproj/InfoPlist.strings")
            expected_info = dict(re.findall(
                r'^"([^"]+)"\s*=\s*"([^"]+)";\s*$',
                info_source.read_text(encoding="utf-8"), re.MULTILINE
            ))
            if len(expected_info) < 5:
                raise ValueError("Not enough translated iOS permission purpose strings")
            if any(info_entries.get(k) != v for k, v in expected_info.items()):
                raise ValueError("Compiled InfoPlist purpose strings differ from zh-Hans source")
            info_matched = len(expected_info)
        print(json.dumps({
            "ipa": path.name,
            "zip_integrity": "PASS",
            "bundle_id": info.get("CFBundleIdentifier"),
            "minimum_ios": info.get("MinimumOSVersion"),
            "bundle_display_name": info.get("CFBundleDisplayName"),
            "compiled_zh_hans_entries": len(entries),
            "compiled_catalog_entries_verified": matched,
            "compiled_info_plist_entries_verified": info_matched,
            "size_bytes": path.stat().st_size,
        }, ensure_ascii=False, indent=2))
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
