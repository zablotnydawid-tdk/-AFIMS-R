#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT_JSON="${INPUT_JSON:-$ROOT_DIR/examples/evidence-input.example.json}"
SCHEMA_JSON="${SCHEMA_JSON:-$ROOT_DIR/schemas/release-decision.schema.json}"

pass(){ printf 'PASS  %s\n' "$1"; }
fail(){ printf 'FAIL  %s\n' "$1" >&2; exit 1; }
need(){ command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"; }

need sha256sum; need python3; need jq; need opa

(
  cd "$ROOT_DIR"
  sha256sum -c SHA256SUMS.txt
) >/dev/null || fail "repository manifest mismatch"
pass "SHA256SUMS verified"

python3 - "$SCHEMA_JSON" "$INPUT_JSON" <<'PY'
import json, sys
from jsonschema import Draft202012Validator, FormatChecker
s=json.load(open(sys.argv[1])); d=json.load(open(sys.argv[2]))
Draft202012Validator(s, format_checker=FormatChecker()).validate(d)
PY
pass "schema validation"

bash "$ROOT_DIR/scripts/validate-evidence-graph.sh" "$INPUT_JSON" >/dev/null
pass "DAG validation"

opa test "$ROOT_DIR/opa" -v
pass "OPA tests"

jq -e '.release_gates[] | select(.id=="RG-026" and .status=="PASS")' "$INPUT_JSON" >/dev/null \
  || fail "RG-026 missing"
jq -e '.release_gates[] | select(.id=="RG-027" and .status=="PASS")' "$INPUT_JSON" >/dev/null \
  || fail "RG-027 missing"
jq -e '.archive_evidence |
  .versioning_enabled==true and .object_lock_enabled==true and
  .retention_mode=="COMPLIANCE" and .readback_verified==true' "$INPUT_JSON" >/dev/null \
  || fail "immutable archive proof invalid"
pass "RG-026 and RG-027 executable evidence present"

printf '\nPRE_PUSH_STATUS: PASS\n'
