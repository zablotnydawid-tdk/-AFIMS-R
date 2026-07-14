package afims.release_test

import rego.v1
import data.afims.release

base_input := {
  "subject": {"image": {"digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}},
  "release_gates": [
    {"id":"tests","mandatory":true,"severity":"CRITICAL","status":"PASS"},
    {"id":"RG-026","mandatory":true,"severity":"CRITICAL","status":"PASS"},
    {"id":"RG-027","mandatory":true,"severity":"CRITICAL","status":"PASS"}
  ],
  "archive_evidence": {
    "prefix":"repo/sha/run",
    "manifest_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "objects":[{"path":"evidence/tests.log","sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","retention_verified":true}],
    "versioning_enabled":true,
    "object_lock_enabled":true,
    "retention_mode":"COMPLIANCE",
    "readback_verified":true
  },
  "operational_evidence": [],
  "claimed": {}
}

test_l3_pass_only_after_rg026_rg027 if {
  r := release.result with input as base_input
  r.decision.status == "PASS"
  r.maturity.level == "L3"
  r.confidence == 100
}

test_manual_confidence_fails if {
  x := object.union(base_input, {"claimed":{"confidence":100}})
  r := release.result with input as x
  r.decision.status == "FAIL"
  "MANUAL_DERIVED_FIELD" in r.decision.reason_codes
}

test_missing_rg026_fails if {
  x := object.union(base_input, {"release_gates":[
    {"id":"tests","mandatory":true,"severity":"CRITICAL","status":"PASS"},
    {"id":"RG-027","mandatory":true,"severity":"CRITICAL","status":"PASS"}
  ]})
  r := release.result with input as x
  r.decision.status == "FAIL"
  "RG_026_TRUST_CHAIN_INCONSISTENT" in r.decision.reason_codes
}

test_rg027_without_compliance_retention_fails if {
  bad_archive := object.union(base_input.archive_evidence, {"retention_mode":"GOVERNANCE"})
  x := object.union(base_input, {"archive_evidence":bad_archive})
  r := release.result with input as x
  r.decision.status == "FAIL"
  "RG_027_IMMUTABLE_EVIDENCE_NOT_PROVEN" in r.decision.reason_codes
}

test_critical_failure_zeroes_confidence if {
  x := object.union(base_input, {"release_gates":[
    {"id":"tests","mandatory":true,"severity":"CRITICAL","status":"FAIL"},
    {"id":"RG-026","mandatory":true,"severity":"CRITICAL","status":"PASS"},
    {"id":"RG-027","mandatory":true,"severity":"CRITICAL","status":"PASS"}
  ]})
  r := release.result with input as x
  r.decision.status == "FAIL"
  r.confidence == 0
}
