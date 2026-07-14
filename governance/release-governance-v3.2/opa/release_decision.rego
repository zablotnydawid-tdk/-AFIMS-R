package afims.release

import rego.v1

default result := {
  "decision": {"status": "FAIL", "reason_codes": ["DEFAULT_DENY"]},
  "maturity": {"level": "NONE"},
  "confidence": 0,
}

manual_claim_present if {
  object.get(input, "claimed", {}) != {}
}

gate_by_id(id) := gate if {
  some gate in input.release_gates
  gate.id == id
}

gate_pass(id) if {
  gate_by_id(id).status == "PASS"
}

critical_failure if {
  some gate in input.release_gates
  gate.severity == "CRITICAL"
  gate.status == "FAIL"
}

mandatory_incomplete if {
  some gate in input.release_gates
  gate.mandatory == true
  gate.status != "PASS"
}

rg026_pass if {
  gate_pass("RG-026")
}

rg027_pass if {
  gate_pass("RG-027")
  input.archive_evidence.versioning_enabled == true
  input.archive_evidence.object_lock_enabled == true
  input.archive_evidence.retention_mode == "COMPLIANCE"
  input.archive_evidence.readback_verified == true
  count(input.archive_evidence.objects) > 0
  every obj in input.archive_evidence.objects {
    obj.retention_verified == true
  }
}

all_l3_gates_pass if {
  not critical_failure
  not mandatory_incomplete
  rg026_pass
  rg027_pass
  count(input.release_gates) > 0
}

l4_required := [e | some e in object.get(input, "operational_evidence", []); e.mandatory_for_l4 == true]

l4_evidence_valid if {
  count(l4_required) > 0
  every e in l4_required {
    e.status == "VERIFIED"
    e.release_digest == input.subject.image.digest
    e.environment == "production"
    e.verification.verified == true
    time.parse_rfc3339_ns(e.issued_at) <= time.now_ns()
    time.parse_rfc3339_ns(e.valid_until) > time.now_ns()
  }
}

computed_confidence := 0 if {
  critical_failure
}

computed_confidence := round((verified / total) * 10000) / 100 if {
  not critical_failure
  mandatory := [g | some g in input.release_gates; g.mandatory == true]
  total := count(mandatory)
  total > 0
  verified := count([g | some g in mandatory; g.status == "PASS"])
}

result := {
  "decision": {"status": "FAIL", "reason_codes": ["MANUAL_DERIVED_FIELD"]},
  "maturity": {"level": "NONE"},
  "confidence": computed_confidence,
} if {
  manual_claim_present
}

result := {
  "decision": {"status": "FAIL", "reason_codes": ["CRITICAL_GATE_FAILED"]},
  "maturity": {"level": "NONE"},
  "confidence": 0,
} if {
  not manual_claim_present
  critical_failure
}

result := {
  "decision": {"status": "FAIL", "reason_codes": ["RG_026_TRUST_CHAIN_INCONSISTENT"]},
  "maturity": {"level": "NONE"},
  "confidence": computed_confidence,
} if {
  not manual_claim_present
  not critical_failure
  not rg026_pass
}

result := {
  "decision": {"status": "FAIL", "reason_codes": ["RG_027_IMMUTABLE_EVIDENCE_NOT_PROVEN"]},
  "maturity": {"level": "NONE"},
  "confidence": computed_confidence,
} if {
  not manual_claim_present
  not critical_failure
  rg026_pass
  not rg027_pass
}

result := {
  "decision": {"status": "FAIL", "reason_codes": ["MANDATORY_EVIDENCE_INCOMPLETE"]},
  "maturity": {"level": "NONE"},
  "confidence": computed_confidence,
} if {
  not manual_claim_present
  not critical_failure
  rg026_pass
  rg027_pass
  mandatory_incomplete
}

result := {
  "decision": {"status": "PASS", "reason_codes": [
    "ALL_REQUIRED_EVIDENCE_VERIFIED",
    "RG_026_TRUST_CHAIN_CONSISTENT",
    "RG_027_IMMUTABLE_EVIDENCE_VERIFIED",
    "L4_OPERATIONAL_EVIDENCE_VALID"
  ]},
  "maturity": {"level": "L4"},
  "confidence": computed_confidence,
} if {
  not manual_claim_present
  all_l3_gates_pass
  l4_evidence_valid
  computed_confidence == 100
}

result := {
  "decision": {"status": "PASS", "reason_codes": [
    "ALL_REQUIRED_EVIDENCE_VERIFIED",
    "RG_026_TRUST_CHAIN_CONSISTENT",
    "RG_027_IMMUTABLE_EVIDENCE_VERIFIED"
  ]},
  "maturity": {"level": "L3"},
  "confidence": computed_confidence,
} if {
  not manual_claim_present
  all_l3_gates_pass
  not l4_evidence_valid
  computed_confidence == 100
}
