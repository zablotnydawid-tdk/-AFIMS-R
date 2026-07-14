from __future__ import annotations
from datetime import datetime, timezone
from .certifier import certify
from .extraction import extract
from .hashing import sha256_object
from .metrics import calculate
from .models import to_dict
from .validators import validate_all

def run_validation(request: dict) -> dict:
    required = {"contract", "source", "answer", "generator"}
    missing = required - request.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    contract = dict(request["contract"])
    contract_hash = sha256_object(contract)
    source_text = request["source"]["content"]
    answer_text = request["answer"]["content"]
    source_hash = sha256_object({"content": source_text})
    answer_hash = sha256_object({"content": answer_text})
    results = validate_all(source_text, answer_text, contract, request["generator"])
    metrics = calculate(extract(source_text), results)
    certification = certify(contract["generator_id"], contract["certifier_id"], results, metrics)
    report = {
        "schema_version": "AFIMS-R.ValidationRun.v1",
        "afims_r_version": "0.4.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "contract_hash": contract_hash,
        "source_hash": source_hash,
        "response_hash": answer_hash,
        "validator_results": [to_dict(r) for r in results],
        "metrics": {k: to_dict(v) for k, v in metrics.items()},
        "certification": to_dict(certification),
    }
    report["report_hash"] = sha256_object(report)
    report["sealed"] = True
    return report
