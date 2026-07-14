# AFIMS-R v0.4.0 — Release Evidence & Governance

Status: **LOCAL EVIDENCE PASS / READY FOR EXTERNAL CI GOVERNANCE**

AFIMS-R v0.4.0 extends the executable v0.3.0 fixture layer with bounded Final
Confidence evaluation, fail-closed release verification, CI workflows, and a
two-phase Release Governance v3.2 adapter. It preserves the original v0.2.0
engine lineage and all 85 AFIMS-T executable fixtures.

## Verified local result

```text
SOURCE_V0.2.0_SHA256_MATCH: PASS
AFIMS_T_FIXTURES_COMPLETE: 85/85
AFIMS_T_CASES_EXECUTED: 85/85
AFIMS_T_SUITE_EXPECTATIONS_MET: 85/85
INDIVIDUAL_EVIDENCE_ARTIFACTS: 85/85
EVIDENCE_HASH_VALIDITY: 85/85
GROUP_REPORTS: 10/10
UNIT_AND_CONFORMANCE_TESTS: 115/115
INDEPENDENT_SUITE_CERTIFIER: PASS
FINAL_CONFIDENCE_1_TO_13: PASS
FINAL_CONFIDENCE_14: NO (bounded fixture scope)
LOCAL_EVIDENCE_DECISION: PASS
RELEASE_STATUS: READY_FOR_CI
GOVERNANCE_MATURITY: NONE
L3_GRANTED: false
L4_GRANTED: false
```

`READY_FOR_CI` is not a release certification. L3/L4 require execution of the
external workflow with RG-026, immutable MinIO Object Lock storage in
COMPLIANCE mode, read-back proof/RG-027, final OPA evaluation, keyless Cosign
signature, and independent protected environments.

## Execute locally

```bash
python -m pip install -e .
./scripts/test.sh
python -m scripts.build_release_manifest
sha256sum -c SHA256SUMS.txt
```

The test script regenerates fixtures, runs all tests, executes the 85 cases,
verifies each evidence hash, evaluates Final Confidence, and builds release
readiness. Missing external governance tools are reported but do not convert a
local evidence result into L3/L4.

## Principal artifacts

```text
fixtures/afims_t_cases.json
evidence/afims_t/T1_01.json ... T10_10.json
evidence/EVIDENCE_MANIFEST.json
reports/groups/T1_REPORT.json ... T10_REPORT.json
reports/AFIMS_T_COMPLIANCE_REPORT.json
reports/FINAL_CONFIDENCE_REPORT.json
reports/RELEASE_READINESS.json
reports/EXTERNAL_TOOL_AVAILABILITY.json
.github/workflows/afims-check.yml
.github/workflows/release-governance.yml
governance/release-governance-v3.2/
docs/RELEASE_GOVERNANCE.md
docs/RISK_REGISTER.md
```

## Trust boundary

The local PASS proves conformance of the exact bundled deterministic reference
fixtures and integrity of their generated evidence. It does not prove universal
hallucination detection, arbitrary-domain correctness, production behavior, L3,
L4, or external accreditation. Final Confidence question 14 is answered only
by a bounded deterministic completeness audit; the report explicitly marks it
as non-exhaustive outside that scope.
