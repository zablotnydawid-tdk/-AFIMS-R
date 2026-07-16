# AFIMS-R L3 Release Manifest

This manifest summarizes the evidence-backed L3 closure for AFIMS-R v0.4.0. The claim is limited to the technical AFIMS-R project certification produced by the repository governance workflow. It is not an external accredited certificate.

## Certified Subject

| Field | Value |
| --- | --- |
| Repository | zablotnydawid-tdk/-AFIMS-R |
| Certified commit | 463b1c1e8dfdccdfe323b90ef62ab6661718b31c |
| Workflow | AFIMS-R Release Governance v3.2 Registration Refresh |
| Workflow file | .github/workflows/release-governance.yml |
| Run ID | 29473975758 |
| Run attempt | 1 |
| Run URL | https://github.com/zablotnydawid-tdk/-AFIMS-R/actions/runs/29473975758 |
| Container image | ghcr.io/zablotnydawid-tdk/afims-r:463b1c1e8dfdccdfe323b90ef62ab6661718b31c |
| Container digest | sha256:f82746b2f67df70dd1ef4038d0c699da4b78c19d0915c9f63c01bd5b22659c17 |
| Release-decision JSON SHA-256 | 1a2e9cd4d135d238934fc353b46477df2efeb16124f62a43a7e188b63a8edbff |

## Gate Results

| Field | Value |
| --- | --- |
| Tests | PASS |
| AFIMS-T | PASS |
| Trivy CRITICAL | 0 |
| Trivy HIGH | 0 |
| OPA decision | PASS |
| Maturity level | L3 |
| Confidence | 100 |
| RG-026 | PASS |
| RG-027 | PASS |
| Cosign signature | CREATED |
| Cosign verification | PASS |

## Immutable Archive

| Field | Value |
| --- | --- |
| Bucket | afims-release-evidence |
| Initial archive prefix | zablotnydawid-tdk/-AFIMS-R/463b1c1e8dfdccdfe323b90ef62ab6661718b31c/29473975758-1 |
| Initial archive object count | 107 |
| Final archive prefix | zablotnydawid-tdk/-AFIMS-R/463b1c1e8dfdccdfe323b90ef62ab6661718b31c/29473975758-1/final |
| Final archive object count | 7 |
| Final read-back | True |
| Final hash match | True |
| Final COMPLIANCE lock | True |

### Final Archive Objects

| Object | Version ID Present | Hash Match | Retention Mode | Retain Until |
| --- | --- | --- | --- | --- |
| `release-decision.json` | True | True | COMPLIANCE | 2026-08-15T05:36:09.872Z |
| `release-decision.yaml` | True | True | COMPLIANCE | 2026-08-15T05:36:10.389Z |
| `release-decision.sha256` | True | True | COMPLIANCE | 2026-08-15T05:36:10.911Z |
| `release-decision.sigstore.json` | True | True | COMPLIANCE | 2026-08-15T05:36:11.39Z |
| `opa-result.json` | True | True | COMPLIANCE | 2026-08-15T05:36:11.883Z |
| `metrics.json` | True | True | COMPLIANCE | 2026-08-15T05:36:12.369Z |
| `archive-evidence.json` | True | True | COMPLIANCE | 2026-08-15T05:36:12.844Z |

## Actions Artifacts

| Artifact | Digest | Size |
| --- | --- | --- |
| `certified-release-decision` | `sha256:0c7c9d2eb8042e61d99ae19e7917a6ee147e5c33096e16e9ff75a3d443c72cb9` | 25432 |
| `finalization-attempt-evidence` | `sha256:71189bab745b015914fe1d74268902ec8885301bc7b75458fc5f96ff5f8f987c` | 30976 |
| `immutable-evidence-proof` | `sha256:3693ce0ec0355aff49300cb626eae6afc69efd2cd0914299f64da103a77fb022` | 5026 |
| `generated-evidence` | `sha256:1691c5f0e69d10a73534fbc1c62ffda53c68772f7543b3e3b525e3968fa42c67` | 284433 |
| `vulnerability-scan-evidence` | `sha256:067a9c3d611497108aa68b09ea57a88b060479d801383f60530c747cd42b6657` | 16815 |
| `zablotnydawid-tdk-afims-r_463b1c1e8dfdccdfe323b90ef62ab6661718b31c.spdx.json` | `sha256:4e4774dcc98f6eb9b36d5af2e91505b80859e2a9a1d167acf7213da099020e01` | 93493 |

## Historical Fail-Closed Progression

The following historical Release Governance runs remain immutable fail-closed evidence and are not erased or rerun by this closure.

| Run ID | Head SHA | Failure | Result |
| --- | --- | --- | --- |
| 29457855374 | `ebe75109800453ff80ab61174cbe1f14f603e590` | executable mode failure | FAIL_CLOSED |
| 29458622529 | `06ff4ac93f78bf185164f08d3450657de2fa9a88` | invalid GHCR reference | FAIL_CLOSED |
| 29460521533 | `fcad24029303959e91ed9ac464ba364575fabccf` | Trivy vulnerability gate failure | FAIL_CLOSED |
| 29464587625 | `4eda3d13724ec85ccd7bc10d7e2767d6f519b983` | PEP 668 global pip failure | FAIL_CLOSED |
| 29467056881 | `ed52e65ecc8805903700130f895ac45bd69133f1` | final MinIO retention verifier false negative | FAIL_CLOSED |

## Claims And Limitations

- L3 granted: true.
- L4 granted: false.
- Release published: false.
- This is a technical project AFIMS-R certification produced by the repository governance workflow, not an external accredited certificate.
- The self-hosted runner and MinIO evidence store are controlled by the repository owner/operator.
- L4 is not granted by this closure.
