# External Gate Preflight

```yaml
repository: zablotnydawid-tdk/-AFIMS-R
workflow_id: 313374566
workflow_registered: PRESENT
workflow_dispatch_available: PRESENT
ready_to_dispatch: FAIL
external_gate: BLOCKED
l3_granted: false
l4_granted: false
final_verdict: EXTERNAL_GATE_PREFLIGHT_BLOCKED
```

## actions_permissions

| item | status |
| --- | --- |
| `actions_enabled` | `PASS` |
| `workflow_permissions` | `BLOCKED_UNVERIFIED` |
| `ability_to_publish_to_ghcr` | `BLOCKED_UNVERIFIED` |
| `id_token_permission_allowed` | `BLOCKED_UNVERIFIED` |

## environments

| item | status |
| --- | --- |
| `release-archive` | `MISSING` |
| `release-certification` | `MISSING` |

## secrets

| item | status |
| --- | --- |
| `MINIO_ENDPOINT` | `BLOCKED_UNVERIFIED` |
| `MINIO_ACCESS_KEY` | `BLOCKED_UNVERIFIED` |
| `MINIO_SECRET_KEY` | `BLOCKED_UNVERIFIED` |

## variables

| item | status |
| --- | --- |
| `MINIO_BUCKET` | `BLOCKED_UNVERIFIED` |
| `COSIGN_CERTIFICATE_IDENTITY_REGEXP` | `BLOCKED_UNVERIFIED` |
| `COSIGN_CERTIFICATE_OIDC_ISSUER` | `BLOCKED_UNVERIFIED` |

## minio

| item | status |
| --- | --- |
| `endpoint_reachable` | `NOT_EXECUTED` |
| `bucket_exists` | `NOT_EXECUTED` |
| `versioning_enabled` | `NOT_EXECUTED` |
| `object_lock_enabled` | `NOT_EXECUTED` |
| `default_retention_mode_compliance` | `NOT_EXECUTED` |
| `write_credentials_valid` | `NOT_EXECUTED` |
| `read_back_possible` | `NOT_EXECUTED` |

## ghcr

| item | status |
| --- | --- |
| `package_write_available` | `BLOCKED_UNVERIFIED` |
| `github_token_permissions_sufficient` | `BLOCKED_UNVERIFIED` |

## workflow_integrity

| item | status |
| --- | --- |
| `all_actions_pinned_to_full_sha` | `PASS` |
| `downloaded_opa_version_pinned` | `PASS` |
| `downloaded_minio_client_version_pinned` | `PASS` |
| `downloaded_binaries_verified_by_sha256` | `PASS` |
| `exact_github_sha_checkout` | `PASS` |
| `rg_026_implemented` | `PASS` |
| `rg_027_implemented` | `PASS` |
| `keyless_cosign_identity_and_issuer_verification_configured` | `PRESENT` |

## Dispatch Decision

Dispatch was not performed. Mandatory preflight is blocked by missing required environments and by configuration items that could not be verified without authenticated GitHub settings/secrets/variables access. No secret values were read or disclosed.

## Evidence Notes

- `release-archive` and `release-certification` are `MISSING` from the public environments API response.
- Actions permissions, secrets, and variables endpoints returned authentication-required responses, therefore those items are `BLOCKED_UNVERIFIED`.
- Workflow integrity checks passed locally: 12/12 action uses are full SHA pinned, OPA and MinIO client downloads are version pinned and SHA-256 verified, exact `${{ github.sha }}` checkout is configured, and RG-026/RG-027 paths are present.
