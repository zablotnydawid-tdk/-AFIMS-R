#!/usr/bin/env bash
set -euo pipefail
ALIAS="${1:?mc alias required}"
OBJECT="${2:?object path required}"
EXPECTED_SHA="${3:?sha256 required}"

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

mc cp "${ALIAS}/${OBJECT}" "$tmp" >/dev/null
actual=$(sha256sum "$tmp" | awk '{print $1}')
[[ "$actual" == "$EXPECTED_SHA" ]] || { echo "archive hash mismatch"; exit 1; }

info=$(mc retention info --json "${ALIAS}/${OBJECT}")
mode=$(jq -r '.status // .mode // empty' <<<"$info" | tr '[:lower:]' '[:upper:]')
[[ "$mode" == *"COMPLIANCE"* ]] || { echo "COMPLIANCE retention not confirmed"; exit 1; }

echo "ARCHIVE_HASH_AND_RETENTION_VERIFIED"
