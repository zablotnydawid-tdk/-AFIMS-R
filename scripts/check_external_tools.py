from __future__ import annotations

import json
import shutil
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
TOOLS = ("jq", "opa", "docker", "cosign", "mc")


def main() -> int:
    availability = {name: shutil.which(name) is not None for name in TOOLS}
    report = {
        "schema_version": "AFIMS-R.ExternalToolAvailability.v1",
        "scope": "local_execution_environment",
        "tools": availability,
        "external_governance_executed": False,
        "note": "Missing tools do not weaken local AFIMS-T evidence, but block local execution of L3/L4 governance.",
    }
    output = BASE / "reports" / "EXTERNAL_TOOL_AVAILABILITY.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("EXTERNAL_TOOLS_AVAILABLE: " + ", ".join(name for name, present in availability.items() if present))
    print("EXTERNAL_GOVERNANCE_EXECUTED: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
