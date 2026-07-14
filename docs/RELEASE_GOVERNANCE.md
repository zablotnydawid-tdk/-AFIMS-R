# AFIMS-R v0.4.0 release governance

AFIMS-R uses two deliberately separate decision layers.

## Local evidence decision

`scripts/test.sh` regenerates all 85 fixtures, executes every case, verifies the
85 evidence hashes, evaluates Final Confidence questions 1–14, and produces
`reports/RELEASE_READINESS.json`.

`READY_FOR_CI` means only that the deterministic local evidence gates passed. It
does not grant L3, L4, external certification, production validation, or a
signed release decision.

## External two-phase decision

`.github/workflows/release-governance.yml` integrates the vendored, hash-verified
Release Governance v3.2 controls. Its order is fixed:

1. execute tests and produce evidence;
2. build and push the exact commit image;
3. generate SBOM, provenance, and vulnerability evidence;
4. execute RG-026 trust-chain consistency;
5. upload to a MinIO bucket with Object Lock in COMPLIANCE mode;
6. read back the archived evidence and prove RG-027;
7. evaluate the final OPA decision;
8. build the canonical record and sign it with keyless Cosign;
9. archive and read back the signed final record.

Only that external workflow may produce L3 or L4. L4 additionally requires
fresh, verified operational evidence bound to the exact release digest. Manual
confidence, maturity, or release-decision claims are intentionally absent from
the pipeline input.

Required repository configuration includes `MINIO_BUCKET`, MinIO credentials,
and the accepted Cosign certificate identity and OIDC issuer. Protected GitHub
environments named `release-archive` and `release-certification` should enforce
independent approvals and role separation.

## Evidence boundary

The executable fixtures prove conformance of the declared reference scenarios.
They do not prove universal hallucination detection, arbitrary-domain accuracy,
production behavior, or external certification.
