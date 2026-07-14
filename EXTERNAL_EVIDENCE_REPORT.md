# AFIMS-R v0.4.0 External Evidence Report

Status: BLOCKED
Date: 2026-07-15

## Summary

External governance has not been executed. Local AFIMS-R evidence is reproduced and the release candidate is READY_FOR_CI, but the external gate requires an operator-provided GitHub repository, protected GitHub environments, configured secrets/variables, and a MinIO bucket with Object Lock COMPLIANCE retention.

No L3 or L4 claim is made by this report.

## Current Evidence

```yaml
input_zip_sha256: b4eb43bd9225a188197b57d2d70b4152f2bf7196a30ddb189c045d71d188a284
embedded_governance_zip_sha256: c9349dc606505dce02eed1cf116d4d91101aadb5d8cffeacdcc8d96fcbb8fb1f
repository: null
commit_sha: null
afims_check:
  run_id: null
  run_url: null
  conclusion: NOT_EXECUTED
release_governance:
  run_id: null
  run_url: null
  conclusion: NOT_EXECUTED
rg_026: NOT_EXECUTED
rg_027: NOT_EXECUTED
minio_compliance_readback: NOT_EXECUTED
opa_decision: NOT_EXECUTED
cosign_verification: NOT_EXECUTED
protected_environment_approvals: NOT_VERIFIED
external_gate_decision: BLOCKED
governance_maturity: NONE
l3_granted: false
l4_granted: false
```

## Local Reproduction

- `python3 -m unittest discover -s tests -v`: PASS, 115 tests.
- `bash scripts/test.sh`: PASS.
- `python3 -m scripts.build_release_manifest`: PASS, 173 release files hashed.
- `sha256sum -c SHA256SUMS.txt`: PASS.
- Workflow YAML parse: PASS.
- Moving workflow references scan: PASS, no `@v*`, `@master`, `@main`, OPA `latest`, or unversioned MinIO `mc` workflow downloads remain.

## Supply Chain Hardening Applied

- GitHub Actions pinned to commit SHAs.
- OPA pinned to `v1.18.2` with SHA256 verification.
- MinIO Client pinned to `RELEASE.2025-08-13T08-35-41Z` with SHA256 verification.
- Workflow-installed Python packages pinned: `jsonschema==4.25.1`, `pyyaml==6.0.2`.
- Root and nested `SHA256SUMS.txt` manifests updated and verified.

## Unresolved

- Operator must provide `GITHUB_REPOSITORY` in `owner/repository` format.
- Operator must confirm `release-archive` and `release-certification` environments with independent required reviewers and no self-approval.
- Operator must confirm secrets: `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`.
- Operator must confirm variables: `MINIO_BUCKET`, `COSIGN_CERTIFICATE_IDENTITY_REGEXP`, `COSIGN_CERTIFICATE_OIDC_ISSUER`.
- Operator must confirm MinIO Object Lock, versioning enabled, and default retention mode `COMPLIANCE`.

## Required Next Steps

1. Add the repository remote and push this exact candidate commit.
2. Run `AFIMS Check` on the immutable commit and independently verify the `afims-r-local-evidence` artifact.
3. Verify protected environments and MinIO Object Lock COMPLIANCE configuration.
4. Run `Release Governance v3.2` with required approvals.
5. Independently revalidate artifacts, OPA result, Cosign bundle, trust chain, and final WORM read-back.
6. Replace this BLOCKED report with the final external evidence report.
