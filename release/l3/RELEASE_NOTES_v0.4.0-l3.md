# AFIMS-R v0.4.0 L3 Release Notes

## What Was Certified

AFIMS-R v0.4.0 was certified by the Release Governance workflow as a technical project L3 release.

## Exact Commit

```text
463b1c1e8dfdccdfe323b90ef62ab6661718b31c
```

## Exact Container Digest

```text
ghcr.io/zablotnydawid-tdk/afims-r:463b1c1e8dfdccdfe323b90ef62ab6661718b31c@sha256:f82746b2f67df70dd1ef4038d0c699da4b78c19d0915c9f63c01bd5b22659c17
```

## Security Gate

- Trivy CRITICAL: 0
- Trivy HIGH: 0
- Vulnerability gate: PASS
- SBOM: present
- Provenance: present
- RG-026: PASS

## Evidence Chain

The successful governance run is `29473975758`, attempt `1`, on branch `main` for the exact certified commit. The evidence artifacts are `generated-evidence`, `immutable-evidence-proof`, and `certified-release-decision`.

## Cryptographic Signature

`release-decision.json` was signed with a Sigstore/Cosign bundle. The expected certificate identity is:

```text
https://github.com/zablotnydawid-tdk/-AFIMS-R/.github/workflows/release-governance.yml@refs/heads/main
```

The expected OIDC issuer is:

```text
https://token.actions.githubusercontent.com
```

## Immutable Archive

The final archive contains 7 verified objects in MinIO Object Lock COMPLIANCE mode, with version IDs, read-back, hash matching, and future retain-until timestamps recorded in `final-archive-evidence.json`.

## Historical Fail-Closed Progression

The prior failed runs remain part of the audit trail and are preserved as fail-closed evidence:

- `29457855374`: executable mode failure.
- `29458622529`: invalid GHCR reference.
- `29460521533`: Trivy vulnerability gate failure.
- `29464587625`: PEP 668 global pip failure.
- `29467056881`: final MinIO retention verifier false negative.

## Granted Maturity

L3 is granted by the actual `opa-result.json` and `release-decision.json` artifacts.

## Not Granted

L4 is not granted by this release closure.

## Trust Boundaries

This is a technical project AFIMS-R certification produced by the repository governance workflow, not an external accredited certificate. The self-hosted runner and MinIO evidence store are controlled by the repository owner/operator.

## Verification Instructions

Use `VERIFY_L3_RELEASE.md` and `release/l3/AFIMS_R_L3_RELEASE_MANIFEST.json` to verify the commit, workflow run, container digest, OPA decision, Cosign bundle, and immutable archive evidence.
