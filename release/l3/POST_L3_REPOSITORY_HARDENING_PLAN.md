# Post-L3 Repository Hardening Plan

This is a read-only hardening plan prepared after the L3 closure. No repository settings were changed by this document.

## Current Observations

- Repository: zablotnydawid-tdk/-AFIMS-R
- Visibility: public
- Current default branch: `afims-r-v0.4.0-external-evidence`
- `main` SHA at audit time: `463b1c1e8dfdccdfe323b90ef62ab6661718b31c`
- Branch protection for `main`: not configured according to GitHub API response `Branch not protected`.
- Branch protection for current default branch: not configured according to GitHub API response `Branch not protected`.
- Merge commit: enabled
- Squash merge: enabled
- Rebase merge: enabled
- Auto merge: disabled
- Delete branch on merge: disabled
- Open PRs at audit time: PR #1, draft, `afims-r-v0.4.0-gate-integration` to `main`.
- Open issues at audit time: none.

## Stale Merged Branch Review

Remote branches remaining after merged remediation work should be reviewed before deletion. Do not delete branches until the L3 closure PR is merged and the audit owner confirms retention requirements. Branches observed:

- `afims-r-fix-certifier-python-isolation`
- `afims-r-fix-final-retention-proof`
- `afims-r-fix-ghcr-image-reference`
- `afims-r-fix-test-executable-bit`
- `afims-r-local-trust-island-clean`
- `afims-r-remediate-trivy-findings`
- `afims-r-v0.4.0-external-evidence`
- `afims-r-v0.4.0-gate-integration`
- `main`

## Recommended Controls

1. Decide whether `main` should become the default branch after the L3 closure is reviewed. Do not switch automatically.
2. Enable branch protection for the default release branch and `main`.
3. Require pull requests before merging to the protected branch.
4. Require AFIMS Check and any release validation checks before merge.
5. Block force pushes and branch deletion on protected branches.
6. Require signed commits or signed tags for release operations if the operator key policy is ready.
7. Restrict who can push to protected branches.
8. Require linear history only if it does not conflict with audit requirements to preserve merge commits.
9. Keep historical failed workflow runs immutable and referenced in release notes.
10. Keep Release Governance dispatch manual and evidence-first until L4 requirements are separately satisfied.

## Proposed Release Operation Plan

- Proposed tag: `v0.4.0-l3`
- Tag target: `463b1c1e8dfdccdfe323b90ef62ab6661718b31c`
- Tag status at preparation time: not present locally or remotely.
- Recommended tag type: annotated and signed when release signing policy is configured.
- Proposed GitHub Release: draft first, not published by this closure.
- Proposed attachments: certified-release-decision ZIP, manifest JSON/YAML/MD, `VERIFY_L3_RELEASE.md`, `RELEASE_NOTES_v0.4.0-l3.md`, and `release/l3/SHA256SUMS.txt`.
