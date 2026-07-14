from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .engine import run_validation
from .hashing import sha256_bytes


NUMBER_RE = re.compile(
    r"(?<![\w])[-+]?\d+(?:[.,]\d+)?(?:\s?(?:%|kWh|MWh|kWp|kW|MW|Wh|V|A|W|zł|PLN|min|h))?"
)


@dataclass(frozen=True)
class CheckResult:
    check_type: str
    passed: bool
    message: str
    observed: Any = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "check_type": self.check_type,
            "passed": self.passed,
            "message": self.message,
            "observed": self.observed,
        }


def _contains_all(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    missing = [value for value in check["values"] if value not in candidate]
    return CheckResult("contains_all", not missing, "required fragments present" if not missing else "required fragments missing", missing)


def _contains_none(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    found = [value for value in check["values"] if value in candidate]
    return CheckResult("contains_none", not found, "prohibited fragments absent" if not found else "prohibited fragments found", found)


def _regex_all(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    missing = [pattern for pattern in check["patterns"] if re.search(pattern, candidate, re.IGNORECASE | re.MULTILINE) is None]
    return CheckResult("regex_all", not missing, "required patterns matched" if not missing else "required patterns missing", missing)


def _regex_none(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    found = [pattern for pattern in check["patterns"] if re.search(pattern, candidate, re.IGNORECASE | re.MULTILINE)]
    return CheckResult("regex_none", not found, "prohibited patterns absent" if not found else "prohibited patterns matched", found)


def _preserve_numbers(candidate: str, check: dict[str, Any], case: dict[str, Any]) -> CheckResult:
    source = check.get("source", case["input"])
    expected = check.get("values") or NUMBER_RE.findall(source)
    missing = [value for value in expected if value not in candidate]
    extras: list[str] = []
    if check.get("forbid_extra", False):
        observed = NUMBER_RE.findall(candidate)
        extras = [value for value in observed if value not in expected]
    passed = not missing and not extras
    return CheckResult("preserve_numbers", passed, "numeric contract satisfied" if passed else "numeric contract violated", {"missing": missing, "extra": extras})


def _preserve_entities(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    missing = [value for value in check["values"] if value not in candidate]
    return CheckResult("preserve_entities", not missing, "entities preserved" if not missing else "entity missing or substituted", missing)


def _ordered_fragments(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    positions = [candidate.find(value) for value in check["values"]]
    passed = all(position >= 0 for position in positions) and positions == sorted(positions)
    return CheckResult("ordered_fragments", passed, "chronology preserved" if passed else "chronology changed", positions)


def _exact_count(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    observed = candidate.count(check["value"])
    passed = observed == check["count"]
    return CheckResult("exact_count", passed, "count matches" if passed else "count mismatch", observed)


def _json_fields(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    try:
        document = json.loads(candidate)
    except json.JSONDecodeError as exc:
        return CheckResult("json_fields", False, "invalid JSON", str(exc))
    missing = [field for field in check["required"] if field not in document]
    forbidden = [field for field in check.get("forbidden", []) if field in document]
    passed = not missing and not forbidden
    return CheckResult("json_fields", passed, "JSON contract satisfied" if passed else "JSON contract violated", {"missing": missing, "forbidden": forbidden})


def _identity_separation(_: str, check: dict[str, Any], case: dict[str, Any]) -> CheckResult:
    actors = case.get("actors", {})
    selected = [actors.get(name) for name in check.get("required", ["generator", "validator", "certifier"])]
    passed = all(selected) and len(selected) == len(set(selected))
    return CheckResult("identity_separation", passed, "roles separated" if passed else "role identity collision", actors)


def _hash_match(_: str, check: dict[str, Any], case: dict[str, Any]) -> CheckResult:
    payload = check.get("payload", case["input"]).encode("utf-8")
    observed = sha256_bytes(payload)
    expected = check["expected_sha256"]
    return CheckResult("hash_match", observed == expected, "hash matches" if observed == expected else "hash mismatch", observed)


def _python_ast(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    try:
        tree = ast.parse(candidate)
    except SyntaxError as exc:
        return CheckResult("python_ast", False, "syntax error", str(exc))
    observed_calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                observed_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                observed_calls.append(node.func.attr)
    found = sorted(set(check.get("forbidden_calls", [])).intersection(observed_calls))
    return CheckResult("python_ast", not found, "AST contract satisfied" if not found else "forbidden call found", found)


def _python_behavior(candidate: str, check: dict[str, Any], _: dict[str, Any]) -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="afims-code-") as directory:
        path = Path(directory) / "candidate.py"
        path.write_text(candidate + "\n\n" + check["harness"], encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, "-I", str(path)],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    expected = check.get("expected_stdout", "")
    passed = completed.returncode == 0 and completed.stdout.strip() == expected
    return CheckResult(
        "python_behavior",
        passed,
        "behavior matches" if passed else "behavior mismatch",
        {"returncode": completed.returncode, "stdout": completed.stdout.strip(), "stderr": completed.stderr.strip()},
    )


def _engine_verdict(candidate: str, check: dict[str, Any], case: dict[str, Any]) -> CheckResult:
    request = {
        "contract": {
            "contract_id": f"fixture-{case['test_id']}",
            "validation_mode": "PRESERVE",
            "required_format": check.get("required_format", "text"),
            "generator_id": case.get("actors", {}).get("generator", "fixture-generator"),
            "certifier_id": case.get("actors", {}).get("certifier", "fixture-certifier"),
        },
        "source": {"content": case["input"]},
        "answer": {"content": candidate},
        "generator": case.get("generator_payload", {"role": "GENERATOR", "service_id": "fixture-generator"}),
    }
    report = run_validation(request)
    observed = report["certification"]["verdict"]
    passed = observed == "PASS"
    return CheckResult(
        "engine_verdict",
        passed,
        "core engine accepted candidate" if passed else "core engine rejected candidate",
        {"observed": observed, "report_hash": report["report_hash"]},
    )


CHECKS: dict[str, Callable[[str, dict[str, Any], dict[str, Any]], CheckResult]] = {
    "contains_all": _contains_all,
    "contains_none": _contains_none,
    "regex_all": _regex_all,
    "regex_none": _regex_none,
    "preserve_numbers": _preserve_numbers,
    "preserve_entities": _preserve_entities,
    "ordered_fragments": _ordered_fragments,
    "exact_count": _exact_count,
    "json_fields": _json_fields,
    "identity_separation": _identity_separation,
    "hash_match": _hash_match,
    "python_ast": _python_ast,
    "python_behavior": _python_behavior,
    "engine_verdict": _engine_verdict,
}


def evaluate_fixture(case: dict[str, Any]) -> dict[str, Any]:
    results: list[CheckResult] = []
    for check in case["executable_evaluator"]["checks"]:
        evaluator = CHECKS.get(check["type"])
        if evaluator is None:
            results.append(CheckResult(check["type"], False, "unknown evaluator"))
            continue
        try:
            results.append(evaluator(case["candidate_output"], check, case))
        except Exception as exc:
            results.append(CheckResult(check["type"], False, f"evaluator error: {type(exc).__name__}: {exc}"))
    observed = "PASS" if results and all(item.passed for item in results) else "FAIL"
    return {
        "test_id": case["test_id"],
        "group": case["group"],
        "validator_id": "afims-fixture-validator-v0.4.0",
        "observed_validator_decision": observed,
        "expected_validator_decision": case["expected_validator_decision"],
        "suite_expectation_met": observed == case["expected_validator_decision"],
        "checks": [item.as_dict() for item in results],
        "unresolved": 0,
    }
