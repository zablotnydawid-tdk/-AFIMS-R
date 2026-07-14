from __future__ import annotations
import hashlib
import json
from typing import Any

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

def sha256_object(value: Any) -> str:
    return sha256_bytes(canonical_json(value))
