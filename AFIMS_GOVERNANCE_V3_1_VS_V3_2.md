# AFIMS Governance v3.1 vs v3.2

## Scope

```yaml
v3_1: AFIMS-T Release Governance v3.1 package
v3_1_trust_status: FAILED_SHA256_MATCH
v3_2: governance/release-governance-v3.2
v3_2_baseline_commit: 31dc77b09612524597295d84e32613a186cbfe30
baseline_modified: false
external_execution: false
external_gate: BLOCKED
l3_granted: false
l4_granted: false
```

The v3.1 package was not imported and v3.2 was not downgraded. Because the v3.1 archive hash does not match the declared SHA-256, v3.1 controls are treated as untrusted until a matching package is supplied.

## Comparison Matrix

| Area | Control | Classification | Notes |
| --- | --- | --- | --- |
| architecture | generator | REQUIRES_EXECUTION | v3.1 not trusted; v3.2 generator exists in workflow but external run blocked |
| architecture | validator | REQUIRES_EXECUTION | v3.1 not trusted; v3.2 local validator path exists |
| architecture | certifier | REQUIRES_EXECUTION | v3.2 certifier job exists but was not externally executed |
| architecture | role_separation | REQUIRES_EXECUTION | v3.2 uses separate jobs; actual protected approval flow not verified |
| architecture | fail_closed | REQUIRES_EXECUTION | v3.2 has fail-closed shell checks; external proof not run |
| governance | schema_version | INCOMPATIBLE | v3.1 and v3.2 are different governance baselines |
| governance | evidence_graph | REQUIRES_EXECUTION | v3.1 not executed; v3.2 graph validation not externally run |
| governance | confidence_calculation | REQUIRES_EXECUTION | v3.1 claim unproven; v3.2 OPA execution blocked |
| governance | critical_fail_handling | REQUIRES_EXECUTION | v3.1 claim unproven |
| governance | maturity_assignment | REQUIRES_EXECUTION | No L3/L4 without external run |
| governance | rg_026 | REQUIRES_EXECUTION | v3.2 script exists; not externally executed |
| governance | rg_027 | REQUIRES_EXECUTION | Requires MinIO COMPLIANCE upload and read-back |
| cosign | mode | REQUIRES_EXECUTION | v3.2 uses keyless Cosign; required current contract may differ |
| cosign | oidc_identity | REQUIRES_EXECUTION | v3.2 references OIDC vars; values not verified |
| cosign | oidc_issuer | REQUIRES_EXECUTION | v3.2 references OIDC vars; values not verified |
| cosign | bundle_saved | REQUIRES_EXECUTION | Bundle path exists in workflow; no run artifact |
| cosign | signature_verified | REQUIRES_EXECUTION | No Cosign run |
| cosign | verification_evidence_saved | REQUIRES_EXECUTION | No certified artifact |
| minio | endpoint_contract | REQUIRES_EXECUTION | Secrets and vars not verified |
| minio | bucket_contract | REQUIRES_EXECUTION | Vars not verified |
| minio | versioning_check | REQUIRES_EXECUTION | v3.2 checks versioning; no external MinIO proof |
| minio | object_lock_check | REQUIRES_EXECUTION | Requires real bucket |
| minio | compliance_retention_check | REQUIRES_EXECUTION | Requires real bucket policy |
| minio | upload | REQUIRES_EXECUTION | Not executed |
| minio | read_back | REQUIRES_EXECUTION | Not executed |
| minio | hash_comparison | REQUIRES_EXECUTION | Not executed |
| minio | version_id_capture | REQUIRES_EXECUTION | Not proven in either trusted run |
| github_actions | triggers | INCOMPATIBLE | v3.2 `afims-check` expects PR or main push; release governance expects dispatch/tag |
| github_actions | environments | INCOMPATIBLE | v3.2 uses `release-archive` and `release-certification`; requested bootstrap currently unresolved |
| github_actions | action_sha_pinning | V3_2_IMPROVEMENT | Actions in v3.2 are pinned to full commit SHA |
| github_actions | runner_metadata_capture | MISSING_IN_BOTH | No trusted proof of runner metadata capture |
| github_actions | artifact_upload | V3_2_IMPROVEMENT | v3.2 uploads generated, immutable, and certified artifacts |
| github_actions | permissions | V3_2_IMPROVEMENT | v3.2 narrows permissions to contents/packages/id-token as needed |

## Port Decision

```yaml
v3_1_unique_controls: []
v3_2_improvements:
  - GitHub Actions pinned to full commit SHA values.
  - OPA and MinIO client downloads pinned to explicit versions and SHA-256 checks.
  - Separate generate-and-validate, archive-and-prove, and certify-sign-finalize jobs.
  - Exact checkout of GITHUB_SHA.
  - Evidence artifact upload across stages.
controls_to_port: []
port_decision: NO_PORT_FROM_UNTRUSTED_PACKAGE
```

No v3.1 mechanism is ported in this branch because the package did not pass SHA-256 verification. This preserves a single canonical governance workflow: Release Governance v3.2.

## Repository Bootstrap Status

```yaml
main_branch:
  status: CREATED_AT_APPROVED_SHA
  sha: 31dc77b09612524597295d84e32613a186cbfe30
workflow_registration:
  status: STILL_REQUIRES_GITHUB_ACTIONS_REGISTRATION_CHECK
environments:
  release-archive: MISSING_OR_UNVERIFIED
  release-certification: MISSING_OR_UNVERIFIED
minio:
  credentials: BLOCKED_UNVERIFIED
  object_lock: NOT_EXECUTED
  compliance_retention: NOT_EXECUTED
external_gate:
  status: BLOCKED
```

## Final Verdict

```text
V3_1_PACKAGE_VALIDATION_FAIL
```
