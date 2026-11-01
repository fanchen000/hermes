#!/usr/bin/env python3
"""Print unlocalized short labels for manual review. No network I/O."""
import json
from pathlib import Path
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
root = Path(__file__).resolve().parents[2]
rows = json.loads((root / ".l10n_artifacts/missing.json").read_text(encoding="utf-8"))
max_length = int(sys.argv[1]) if len(sys.argv) > 1 else 36
category = sys.argv[2] if len(sys.argv) > 2 else ""
entries = []
for row in rows:
    key = row["key"]
    if not (2 <= len(key) <= max_length and re.search("[A-Za-z]{3,}", key)):
        continue
    if any(c in key for c in "\n\r{}"):
        continue
    if category and not any(category.lower() in path.lower() for path in row["sources"]):
        continue
    entries.append(key)
for key in sorted(entries, key=lambda k: (len(k), k.casefold())):
    print(key.replace("\t", " "))
print(f"=== {len(entries)} labels", file=sys.stderr)
