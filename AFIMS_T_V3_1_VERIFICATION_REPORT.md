# AFIMS-T v3.1 Package Verification Report

## Summary

```yaml
package: /mnt/c/Users/zablo/Desktop/witness/AFIMIS/release-governance-v31.zip
declared_package_sha256: 8a829e5bfa95fdc8a05a53c45afdcf9d6dbd2e0c382fa53479b698a2c99e38e3
actual_package_sha256: 64006d483141224d4a7b67689d1d06d8288c66f5ed75401756f1fae8f725be74
package_sha256_match: false
files_detected: 16
zip_entries_detected: 19
path_traversal: PASS
baseline_modified: false
external_execution: false
external_gate: BLOCKED
l3_granted: false
l4_granted: false
final_verdict: V3_1_PACKAGE_VALIDATION_FAIL
```

The package is visible and its ZIP table can be listed safely, but the package SHA-256 does not match the declared value. Validation therefore stopped fail-closed before extraction or execution.

## Local Validation

| Check | Result |
| --- | --- |
| Archive SHA-256 | FAIL |
| Safe ZIP listing | PASS |
| Path traversal scan | PASS |
| Extraction | NOT_EXECUTED_HASH_MISMATCH |
| File SHA-256 manifest | NOT_EXECUTED_HASH_MISMATCH |
| JSON validation | NOT_EXECUTED_HASH_MISMATCH |
| YAML validation | NOT_EXECUTED_HASH_MISMATCH |
| `python -m py_compile` | NOT_EXECUTED_HASH_MISMATCH |
| `bash -n` | NOT_EXECUTED_HASH_MISMATCH |
| `shellcheck` | NOT_EXECUTED_HASH_MISMATCH |
| `opa test` | NOT_EXECUTED_HASH_MISMATCH |

Observed tool availability:

```yaml
unzip: NOT_AVAILABLE
python_yaml: AVAILABLE
shellcheck: NOT_AVAILABLE
opa: NOT_AVAILABLE
```

## Detected ZIP Entries

```text
release/
tests/
release/examples/
release/release-decision.schema.json
release/release-policy.rego
release/confidence.rego
release/evidence-graph.schema.json
release/evidence-manifest.schema.json
release/release-gates.schema.json
release/release-governance.md
release/examples/verified.yaml
release/examples/tampered-confidence.yaml
release/examples/fail-critical.yaml
release/examples/unverified.yaml
tests/release_decision_test.rego
tests/tamper_test.rego
tests/confidence_test.rego
tests/integrity_test.rego
tests/maturity_test.rego
```

## Claim Verification

All v3.1 claims remain unproven because the archive was not extracted or executed after the SHA mismatch:

| Claim | Candidate implementation | Candidate test | Local result | External limitation |
| --- | --- | --- | --- | --- |
| OPA test: 14 PASS | `release/*.rego` | `tests/*.rego` | NOT_EXECUTED_HASH_MISMATCH | OPA unavailable and package hash mismatch |
| RFC8785 canonicalization: PASS | UNVERIFIED | UNVERIFIED | NOT_EXECUTED_HASH_MISMATCH | No trusted extraction |
| deterministic confidence: PASS | `release/confidence.rego` | `tests/confidence_test.rego` | NOT_EXECUTED_HASH_MISMATCH | OPA unavailable and package hash mismatch |
| Cosign identity verification: IMPLEMENTED | `release/release-governance.md` | UNVERIFIED | NOT_EXECUTED_HASH_MISMATCH | No external Cosign run |
| MinIO versioning requirement: ENFORCED | `release/release-governance.md` | UNVERIFIED | NOT_EXECUTED_HASH_MISMATCH | No MinIO execution |
| COMPLIANCE retention: ENFORCED | `release/release-governance.md` | UNVERIFIED | NOT_EXECUTED_HASH_MISMATCH | No Object Lock proof |
| read-back SHA-256: ENFORCED | `release/release-governance.md` | UNVERIFIED | NOT_EXECUTED_HASH_MISMATCH | No archive read-back |
| Critical FAIL -> confidence 0: ENFORCED | `release/confidence.rego` | `tests/confidence_test.rego` | NOT_EXECUTED_HASH_MISMATCH | OPA unavailable and package hash mismatch |
| S4 error -> pipeline blocked: ENFORCED | `release/release-policy.rego` | `tests/release_decision_test.rego` | NOT_EXECUTED_HASH_MISMATCH | OPA unavailable and package hash mismatch |

## Conclusion

The v3.1 package cannot be accepted as a trusted supporting baseline in this run. It must be re-supplied with a matching SHA-256 or the expected SHA-256 must be corrected and re-verified from a trusted source.
