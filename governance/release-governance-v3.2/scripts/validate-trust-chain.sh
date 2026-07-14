#!/usr/bin/env bash
set -euo pipefail
INPUT="${1:?release input required}"
EVIDENCE_DIR="${2:?evidence directory required}"
OUTPUT="${3:?output required}"

expected_digest=$(jq -r '.subject.image.digest' "$INPUT")
test "$expected_digest" != "null"

provenance_digest=$(jq -r '.image.digest' "$EVIDENCE_DIR/provenance.json")
test "$provenance_digest" = "$expected_digest" || {
  echo "provenance/image digest mismatch" >&2
  exit 1
}

jq -e --arg d "$expected_digest" '.subject.image.digest == $d' "$INPUT" >/dev/null

manifest_tmp=$(mktemp)
trap 'rm -f "$manifest_tmp"' EXIT
(
  cd "$(dirname "$EVIDENCE_DIR")"
  find "$(basename "$EVIDENCE_DIR")" -type f -print0 |
    sort -z |
    xargs -0 sha256sum
) > "$manifest_tmp"

manifest_sha=$(sha256sum "$manifest_tmp" | awk '{print $1}')
cp "$manifest_tmp" "$EVIDENCE_DIR/SHA256SUMS.txt"

jq -n \
  --arg gate_id "RG-026" \
  --arg status "PASS" \
  --arg image_digest "$expected_digest" \
  --arg provenance_digest "$provenance_digest" \
  --arg manifest_sha256 "$manifest_sha" \
  '{gate_id:$gate_id,status:$status,image_digest:$image_digest,
    provenance_digest:$provenance_digest,evidence_manifest_sha256:$manifest_sha256}' > "$OUTPUT"
