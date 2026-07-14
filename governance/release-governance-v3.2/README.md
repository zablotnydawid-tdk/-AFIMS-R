# AFIMS Release Governance v3.2

Two-phase, fail-closed release certification pipeline.

## Correct trust order

```text
Generator
  → deterministic evidence
  → RG-026 Trust Chain Consistency
  → MinIO evidence upload
  → read-back + Object Lock COMPLIANCE verification
  → RG-027 Immutable Evidence
  → final OPA Certifier
  → L3 or L4
  → canonical release-decision.json
  → Cosign sign-blob + verify-blob
  → final WORM archive
```

L3 cannot be granted before both RG-026 and RG-027 are PASS.

L4 additionally requires fresh, release-bound, production operational evidence with a future `valid_until`.

## Jobs

1. `generate-and-validate`
2. `archive-and-prove`
3. `certify-sign-finalize`

## Security properties

- Generator cannot provide `confidence`, `decision_status`, or `maturity_level`.
- Critical FAIL forces confidence to 0.
- RG-026 compares image and provenance digests and creates the evidence manifest.
- RG-027 is created only after upload, read-back hash verification, versioning verification, Object Lock verification, and COMPLIANCE retention verification.
- Final OPA certification runs only after RG-027.
- Cosign signing occurs only after OPA PASS.
- The example remains non-production evidence.

## Required secrets

- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`

## Required variables

- `MINIO_BUCKET`
- `COSIGN_CERTIFICATE_IDENTITY_REGEXP`
- `COSIGN_CERTIFICATE_OIDC_ISSUER`

## Repository requirements

- executable `scripts/test.sh`
- Dockerfile
- GitHub Container Registry access
- MinIO bucket created with Object Lock
- versioning enabled
- default retention mode COMPLIANCE
- CI credentials unable to shorten retention

## Local gate

```bash
bash scripts/pre-push.sh
```

Requires `jq`, `opa`, Python 3, and the Python package `jsonschema`.

## Digest semantics

`release-decision.sha256` is the authoritative detached SHA-256 of the canonical signed JSON. The internal `integrity.document_sha256` remains `null` to avoid a recursive self-hash claim.
