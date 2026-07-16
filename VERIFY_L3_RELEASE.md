# Verify AFIMS-R v0.4.0 L3 Release

This guide describes how a third party can verify the AFIMS-R L3 release evidence without requiring secrets, private MinIO credentials, or private endpoints.

## 1. Verify The Commit

```bash
git ls-remote https://github.com/zablotnydawid-tdk/-AFIMS-R.git refs/heads/main
git fetch origin main
git rev-parse origin/main
```

Expected commit:

```text
463b1c1e8dfdccdfe323b90ef62ab6661718b31c
```

## 2. Verify The Workflow Run

Open:

https://github.com/zablotnydawid-tdk/-AFIMS-R/actions/runs/29473975758

Expected values:

- event: workflow_dispatch
- head_branch: main
- head_sha: 463b1c1e8dfdccdfe323b90ef62ab6661718b31c
- run_attempt: 1
- conclusion: success

## 3. Verify The GHCR Image Digest

Expected image reference:

```text
ghcr.io/zablotnydawid-tdk/afims-r:463b1c1e8dfdccdfe323b90ef62ab6661718b31c
```

Expected digest from `release-decision.json`:

```text
sha256:f82746b2f67df70dd1ef4038d0c699da4b78c19d0915c9f63c01bd5b22659c17
```

## 4. Verify Release Decision Hash

Download the `certified-release-decision` artifact from the workflow run and verify:

```bash
sha256sum release-decision.json
cat release-decision.sha256
```

Expected SHA-256:

```text
1a2e9cd4d135d238934fc353b46477df2efeb16124f62a43a7e188b63a8edbff
```

## 5. Verify OPA Decision And Maturity

Inspect `opa-result.json` and `release-decision.json`. Expected values:

- OPA decision: PASS
- maturity_level: L3
- confidence: 100

Do not infer L3 from workflow success alone; use the artifact contents.

## 6. Verify Cosign Bundle

The signature bundle is `release-decision.sigstore.json`. Expected public identity values:

```text
certificate_identity=https://github.com/zablotnydawid-tdk/-AFIMS-R/.github/workflows/release-governance.yml@refs/heads/main
oidc_issuer=https://token.actions.githubusercontent.com
```

A verifier with `cosign` available can run `cosign verify-blob` against `release-decision.json` and the bundle using the identity regexp for this workflow path and `refs/heads/main`.

## 7. Verify Final Archive Evidence

Inspect `final-archive-evidence.json`. Expected values:

- run_id: 29473975758
- run_attempt: 1
- commit_sha: 463b1c1e8dfdccdfe323b90ef62ab6661718b31c
- all_objects_read_back: true
- all_hashes_match: true
- all_versions_recorded: true
- all_objects_compliance_locked: true
- final object count: 7

Each final object must have a version ID, matching expected/read-back SHA-256 values, retention mode COMPLIANCE, and a future retain-until timestamp relative to the run time.

## 8. Trust Boundaries

This release closure verifies a technical AFIMS-R project governance result. The self-hosted runner and MinIO evidence store are controlled by the repository owner/operator. This is not an external accredited certificate and it does not grant L4.
