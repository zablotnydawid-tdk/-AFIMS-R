#!/usr/bin/env bash
set -euo pipefail
ALIAS="${1:?mc alias}"
BUCKET="${2:?bucket}"
PREFIX="${3:?prefix}"
EVIDENCE_DIR="${4:?evidence directory}"
OUTPUT="${5:?output json}"

mc version info "$ALIAS/$BUCKET" | grep -qi enabled
mc retention info --default "$ALIAS/$BUCKET" | grep -qi compliance

objects='[]'
while IFS= read -r -d '' file; do
  rel="${file#"$EVIDENCE_DIR"/}"
  remote="$BUCKET/$PREFIX/evidence/$rel"
  sha=$(sha256sum "$file" | awk '{print $1}')

  mc cp --attr "sha256=$sha" "$file" "$ALIAS/$remote" >/dev/null

  tmp=$(mktemp)
  mc cp "$ALIAS/$remote" "$tmp" >/dev/null
  readback=$(sha256sum "$tmp" | awk '{print $1}')
  rm -f "$tmp"
  test "$readback" = "$sha"

  retention_json=$(mc retention info --json "$ALIAS/$remote")
  echo "$retention_json" | grep -qi compliance

  objects=$(jq \
    --arg path "evidence/$rel" \
    --arg sha256 "$sha" \
    '. + [{path:$path,sha256:$sha256,retention_verified:true}]' <<<"$objects")
done < <(find "$EVIDENCE_DIR" -type f -print0 | sort -z)

manifest_sha=$(sha256sum "$EVIDENCE_DIR/SHA256SUMS.txt" | awk '{print $1}')

jq -n \
  --arg prefix "$PREFIX" \
  --arg manifest_sha256 "$manifest_sha" \
  --argjson objects "$objects" \
  '{
    prefix:$prefix,
    manifest_sha256:$manifest_sha256,
    objects:$objects,
    versioning_enabled:true,
    object_lock_enabled:true,
    retention_mode:"COMPLIANCE",
    readback_verified:true
  }' > "$OUTPUT"
