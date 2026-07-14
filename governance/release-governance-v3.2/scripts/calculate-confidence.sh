#!/usr/bin/env bash
set -euo pipefail
INPUT="${1:?input json required}"
OUTPUT="${2:?output json required}"

jq -e . "$INPUT" >/dev/null

critical_fail=$(jq '[.release_gates[] | select(.severity=="CRITICAL" and .status=="FAIL")] | length' "$INPUT")
mandatory_total=$(jq '[.release_gates[] | select(.mandatory==true)] | length' "$INPUT")
mandatory_verified=$(jq '[.release_gates[] | select(.mandatory==true and .status=="PASS")] | length' "$INPUT")

if [[ "$critical_fail" -gt 0 ]]; then
  confidence="0"
else
  confidence=$(jq -n --argjson n "$mandatory_verified" --argjson d "$mandatory_total" \
    'if $d == 0 then 0 else (($n / $d) * 10000 | floor) / 100 end')
fi

jq -n \
  --argjson numerator "$mandatory_verified" \
  --argjson denominator "$mandatory_total" \
  --argjson critical_failures "$critical_fail" \
  --argjson value "$confidence" \
  '{confidence:{value:$value,numerator:$numerator,denominator:$denominator},critical_failures:$critical_failures}' > "$OUTPUT"
