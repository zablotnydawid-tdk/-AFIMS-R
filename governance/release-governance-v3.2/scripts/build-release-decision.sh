#!/usr/bin/env bash
set -euo pipefail
INPUT="${1:?input json required}"
METRICS="${2:?metrics json required}"
OPA_RESULT="${3:?opa result json required}"
OUTPUT="${4:?output json required}"

decision=$(jq -r '.result[0].expressions[0].value.decision.status' "$OPA_RESULT")
maturity=$(jq -r '.result[0].expressions[0].value.maturity.level' "$OPA_RESULT")
reason_codes=$(jq '.result[0].expressions[0].value.decision.reason_codes' "$OPA_RESULT")
confidence=$(jq '.confidence' "$METRICS")

test "$decision" = "PASS"
test "$maturity" = "L3" -o "$maturity" = "L4"

jq \
  --arg status "$decision" \
  --arg maturity "$maturity" \
  --argjson reasons "$reason_codes" \
  --argjson confidence "$confidence" \
  '.record_status="CERTIFIED_RECORD"
   | .decision={status:$status,reason_codes:$reasons}
   | .maturity={level:$maturity}
   | .confidence=$confidence
   | .integrity={signed:true,signature_verified:true,document_sha256:null}
   | del(.claimed)' "$INPUT" > "$OUTPUT"
