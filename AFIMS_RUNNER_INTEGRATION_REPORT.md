# Afims Runner Integration Report

```yaml
runner_dir: /mnt/c/TDK/AFIMS-INFRA/runner
runner_registered: NOT_EXECUTED
registration_token: BLOCKED_UNVERIFIED
labels:
  - self-hosted
  - linux
  - x64
  - afims-release
pull_request_workflows_allowed: FAIL
recommended_user: afims-runner
current_wsl_user: root
current_wsl_user_acceptable_for_service: FAIL
manual_registration_required: PRESENT
manual_steps:
  - Create or select a constrained Linux user/context for AFIMS runner.
  - Download GitHub Actions runner from repository Settings > Actions > Runners.
  - Configure it for zablotnydawid-tdk/-AFIMS-R with labels self-hosted, linux, x64, afims-release.
  - Do not store the registration token in documentation or repository files.
  - Run only workflow_dispatch release governance jobs from approved refs.
github_configuration_map:
  release-archive:
    secrets:
      - MINIO_ENDPOINT
      - MINIO_ACCESS_KEY
      - MINIO_SECRET_KEY
    variables:
      - MINIO_BUCKET
  release-certification_or_repository_variables:
    - COSIGN_CERTIFICATE_IDENTITY_REGEXP
    - COSIGN_CERTIFICATE_OIDC_ISSUER
  values_source: /mnt/c/TDK/AFIMS-INFRA/secrets/minio.env
  values_disclosed: false
external_gate: BLOCKED
l3_granted: false
l4_granted: false
```

No secret values are included in this report. External Gate remains BLOCKED and L3/L4 are not granted.
