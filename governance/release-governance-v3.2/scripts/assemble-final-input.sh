#!/usr/bin/env bash
set -euo pipefail
BASE="${1:?base input}"
RG026="${2:?rg026 result}"
ARCHIVE="${3:?archive evidence}"
OUTPUT="${4:?output}"

jq -s '
  .[0] as $base |
  .[1] as $rg026 |
  .[2] as $archive |
  $base
  | .archive_evidence=$archive
  | .release_gates += [
      {
        id:"RG-026",mandatory:true,severity:"CRITICAL",
        status:$rg026.status,evidence_ref:"evidence/rg-026.json"
      },
      {
        id:"RG-027",mandatory:true,severity:"CRITICAL",
        status:(if $archive.readback_verified == true
                  and $archive.versioning_enabled == true
                  and $archive.object_lock_enabled == true
                  and $archive.retention_mode == "COMPLIANCE"
                then "PASS" else "FAIL" end),
        evidence_ref:"archive-evidence.json"
      }
    ]
' "$BASE" "$RG026" "$ARCHIVE" > "$OUTPUT"
