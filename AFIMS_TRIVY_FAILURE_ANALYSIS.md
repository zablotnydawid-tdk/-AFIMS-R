# AFIMS-R Trivy Failure Analysis

## Immutable failed run

- run_id: 29460521533
- head_sha: fcad24029303959e91ed9ac464ba364575fabccf
- image: ghcr.io/zablotnydawid-tdk/afims-r@sha256:9b47678088b9bc4f602b1c70f8f3c3bbd931757e500c28cd82d5154d0ddafaca
- verdict: RELEASE_GOVERNANCE_EXECUTION_FAIL
- immutable: true

## Original Trivy evidence reconstruction

The workflow log records Trivy action version v0.72.0, image scan mode, pkg types `os,library`, severity `CRITICAL,HIGH`, `ignore-unfixed=false`, and exit code 1. The original `evidence/vulnerability.json` was not uploaded because the artifact step was after the failing Trivy gate.

- original_trivy_report_persisted: false
- original_exact_cve_set_recoverable: false
- diagnostic_rescan_same_image_digest: true
- diagnostic_rescan_same_db_as_original: false

## Diagnostic rescan counts

- critical_count: 3
- high_count: 21
- os_count: 22
- library_count: 2
- fixable_count_from_trivy_fixed_version: 2
- unfixed_count_from_trivy_fixed_version: 22

| CVE | Severity | Package | Installed | Fixed | Classification | Class |
| --- | --- | --- | --- | --- | --- | --- |
| CVE-2026-53615 | HIGH | bsdutils | 1:2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-41992 | HIGH | gzip | 1.13-1 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-54369 | HIGH | libacl1 | 2.3.2-2+b1 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | libblkid1 | 2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | liblastlog2-2 | 2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | libmount1 | 2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2025-69720 | HIGH | libncursesw6 | 6.5+20250216-2 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | libsmartcols1 | 2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2025-69720 | HIGH | libtinfo6 | 6.5+20250216-2 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | libuuid1 | 2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | login | 1:4.16.0-2+really2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | mount | 2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2025-69720 | HIGH | ncurses-base | 6.5+20250216-2 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2025-69720 | HIGH | ncurses-bin | 6.5+20250216-2 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-13221 | CRITICAL | perl-base | 5.40.1-6 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-42496 | CRITICAL | perl-base | 5.40.1-6 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-8376 | CRITICAL | perl-base | 5.40.1-6 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-42497 | HIGH | perl-base | 5.40.1-6 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-48962 | HIGH | perl-base | 5.40.1-6 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-57432 | HIGH | perl-base | 5.40.1-6 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-9538 | HIGH | perl-base | 5.40.1-6 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-53615 | HIGH | util-linux | 2.41-5 | UNFIXED_IN_SOURCE_IMAGE | BASE_IMAGE_OS_PACKAGE | OS |
| CVE-2026-23949 | HIGH | jaraco.context | 5.3.0 | 6.1.0 | BUILD_TOOL_NOT_REQUIRED_AT_RUNTIME | library |
| CVE-2026-24049 | HIGH | wheel | 0.45.1 | 0.46.2 | BUILD_TOOL_NOT_REQUIRED_AT_RUNTIME | library |

## Source checks

Primary source spot checks were performed against Debian Security Tracker and upstream advisories. Debian tracker marks util-linux CVE-2026-53615 as vulnerable/unfixed for trixie, perl CVE-2026-13221 and CVE-2026-42496 as vulnerable/unfixed for trixie, gzip CVE-2026-41992 as vulnerable/unfixed for trixie, and ncurses CVE-2025-69720 as fixed only in newer unstable/forky/sid streams. Python findings are tied to build/install tooling; GitHub advisory GHSA-58pv-8j8x-9vj2 covers jaraco.context, and wheel fixed version was reported by Trivy as 0.46.2.

Reference URLs:

- https://security-tracker.debian.org/tracker/CVE-2026-53615
- https://security-tracker.debian.org/tracker/CVE-2026-13221
- https://security-tracker.debian.org/tracker/CVE-2026-42496
- https://security-tracker.debian.org/tracker/CVE-2026-8376
- https://security-tracker.debian.org/tracker/CVE-2026-41992
- https://security-tracker.debian.org/tracker/CVE-2025-69720
- https://github.com/jaraco/jaraco.context/security/advisories/GHSA-58pv-8j8x-9vj2

## Remediation design

- base_image_old: python:3.11-slim, unpinned, failed image detected Debian 13.6
- base_image_new: python:3.11.13-alpine3.22@sha256:6849ab1bde2e04f50c866a51c7f794b4388d1c7dcaee84470c4d67544dec8806
- base_image_architecture: linux/amd64
- dependency_lock: requirements.lock
- dependency_lock_sha256: b6687618a08b0dd4db100685689b44972367fae4f472931be8eb368d0fd465c4
- multi_stage_build: true
- runtime_build_tools_removed: pip, setuptools, wheel
- targeted_runtime_os_updates: libcrypto3, libssl3, musl, musl-utils, zlib

## Workflow hardening

- scan_before_push: true
- vulnerability_report_always_uploaded: true
- explicit_fail_closed_gate: true
- rebuild_between_scan_and_push: false
- old_failed_image_preserve_for_audit: true

## Local validation

- import: PASS
- api_smoke: PASS
- local_docker_build: PASS
- sbom: PASS
- trivy_critical_count: 0
- trivy_high_count: 0

## Verdict

TRIVY_VULNERABILITIES_FIXABLE
