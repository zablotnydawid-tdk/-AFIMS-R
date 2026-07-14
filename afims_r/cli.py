from __future__ import annotations
import argparse
import json
from pathlib import Path
from .engine import run_validation

def main() -> None:
    parser = argparse.ArgumentParser(prog="afims-r")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("request")
    validate.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.command == "validate":
        payload = json.loads(Path(args.request).read_text(encoding="utf-8"))
        report = run_validation(payload)
        print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
