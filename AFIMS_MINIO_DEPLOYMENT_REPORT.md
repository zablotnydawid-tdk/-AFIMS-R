# Afims Minio Deployment Report

```yaml
infra_dir: /mnt/c/TDK/AFIMS-INFRA
compose_file: /mnt/c/TDK/AFIMS-INFRA/docker-compose.yml
secrets_file: /mnt/c/TDK/AFIMS-INFRA/secrets/minio.env
secrets_file_values_disclosed: false
minio_image: quay.io/minio/minio@sha256:a1a8bd4ac40ad7881a245bab97323e18f971e4d4cba2c2007ec1bedd21cbaba2
mc_image: quay.io/minio/mc@sha256:eb4ea9884b77704230e2423e9004d2fa738dc272876b9cc41a297d29443b8780
container: afims-minio
network: afims-trust-net
volume: afims-minio-data
bucket: afims-release-evidence
public_exposure: FAIL
loopback_ports:
  s3_api: 127.0.0.1:9010
  console: 127.0.0.1:9011
object_lock: PASS
versioning: PASS
default_retention_mode: COMPLIANCE
default_retention_days: 30
service_account: afims-certifier
upload: PASS
read_back: PASS
upload_hash: 26abfe95488b6baac954500ac6015df9a6178f2c23beebc058bca5bcd8758757
read_back_hash: 26abfe95488b6baac954500ac6015df9a6178f2c23beebc058bca5bcd8758757
hash_match: true
version_id: PRESENT
retain_until: PRESENT
external_gate: BLOCKED
l3_granted: false
l4_granted: false
```

No secret values are included in this report. External Gate remains BLOCKED and L3/L4 are not granted.
