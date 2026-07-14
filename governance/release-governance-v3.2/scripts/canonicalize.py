#!/usr/bin/env python3
import json, sys
if len(sys.argv) != 3:
    raise SystemExit("usage: canonicalize.py INPUT.json OUTPUT.json")
with open(sys.argv[1], encoding="utf-8") as f:
    data=json.load(f)
with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, ensure_ascii=False, sort_keys=True, separators=(",",":"))
    f.write("\n")
