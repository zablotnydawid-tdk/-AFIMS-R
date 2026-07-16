#!/usr/bin/env bash
set -euo pipefail
ALIAS="${1:?mc alias required}"
OBJECT="${2:?object path required}"
EXPECTED_SHA="${3:?sha256 required}"
EVIDENCE_PATH="${4:-}"

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

stat_json=$(mc stat --json --no-list "${ALIAS}/${OBJECT}")
jq -e '.status == "success"' <<<"$stat_json" >/dev/null
version_id=$(jq -er '.versionID | select(type == "string" and length > 0)' <<<"$stat_json")

mc cp --version-id "$version_id" "${ALIAS}/${OBJECT}" "$tmp" >/dev/null
actual=$(sha256sum "$tmp" | awk '{print $1}')
hash_match=false
if [[ "$actual" == "$EXPECTED_SHA" ]]; then
  hash_match=true
else
  echo "archive hash mismatch" >&2
fi

info=$(mc retention info --json --version-id "$version_id" "${ALIAS}/${OBJECT}")
status=$(jq -er '.status' <<<"$info")
[[ "$status" == "success" ]] || { echo "retention status is not success" >&2; exit 1; }

mode=$(jq -er '.mode' <<<"$info")
mode=$(printf '%s' "$mode" | tr '[:lower:]' '[:upper:]')
[[ "$mode" == "COMPLIANCE" ]] || { echo "COMPLIANCE retention not confirmed" >&2; exit 1; }

retain_until=$(jq -er '.until | select(type == "string" and length > 0)' <<<"$info")
python3 - "$retain_until" <<'PYVERIFY'
import sys
from datetime import datetime, timezone

value = sys.argv[1]
until = datetime.fromisoformat(value.replace("Z", "+00:00"))
assert until.tzinfo is not None
assert until > datetime.now(timezone.utc)
PYVERIFY

retention_verified=true
[[ "$hash_match" == "true" ]] || exit 1

if [[ -n "$EVIDENCE_PATH" ]]; then
  mkdir -p "$(dirname "$EVIDENCE_PATH")"
  jq -n     --arg path "$OBJECT"     --arg version_id "$version_id"     --arg expected_sha256 "$EXPECTED_SHA"     --arg readback_sha256 "$actual"     --arg retention_status "$status"     --arg retention_mode "$mode"     --arg retain_until "$retain_until"     --argjson stat_raw "$stat_json"     --argjson retention_raw "$info"     '{
      path:$path,
      version_id:$version_id,
      expected_sha256:$expected_sha256,
      readback_sha256:$readback_sha256,
      hash_match:($expected_sha256 == $readback_sha256),
      retention_status:$retention_status,
      retention_mode:$retention_mode,
      retain_until:$retain_until,
      retention_verified:true,
      exact_version_read_back:true,
      stat_raw:$stat_raw,
      retention_raw:$retention_raw
    }' > "$EVIDENCE_PATH"
fi

echo "ARCHIVE_HASH_AND_RETENTION_VERIFIED"
