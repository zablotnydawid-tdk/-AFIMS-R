from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
import os
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
EXCLUDED_NAMES = {"SHA256SUMS.txt", "RELEASE_MANIFEST.json"}
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".git"}


def include(path: Path) -> bool:
    relative = path.relative_to(BASE)
    if path.name in EXCLUDED_NAMES:
        return False
    if path.suffix == ".pyc":
        return False
    return not any(part in EXCLUDED_PARTS for part in relative.parts)


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def files() -> list[Path]:
    return sorted(path for path in BASE.rglob("*") if path.is_file() and include(path))


def main() -> int:
    entries = [
        {
            "path": path.relative_to(BASE).as_posix(),
            "size": path.stat().st_size,
            "sha256": digest(path),
        }
        for path in files()
    ]
    manifest = {
        "schema_version": "AFIMS-R.ReleaseManifest.v1",
        "system": "AFIMS-R",
        "version": "0.4.0",
        "created_at": os.environ.get("SOURCE_DATE_EPOCH_ISO", "1970-01-01T00:00:00+00:00"),
        "source_package_sha256": "1d1382c2905ecf9f1afe1b2600041042107877bc9d9089f10a0e44cd5a82fdd8",
        "file_count": len(entries),
        "files": entries,
    }
    (BASE / "RELEASE_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    checksum_files = files() + [BASE / "RELEASE_MANIFEST.json"]
    lines = [f"{digest(path)}  {path.relative_to(BASE).as_posix()}" for path in sorted(checksum_files)]
    (BASE / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"RELEASE_FILES_HASHED: {len(checksum_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
