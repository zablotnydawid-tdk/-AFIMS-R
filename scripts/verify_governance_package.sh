#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "usage: $0 <package.zip> <expected-sha256> [report-dir]" >&2
  exit 2
fi

package_zip="$1"
expected_sha256="$2"
report_dir="${3:-governance-package-verification}"

python3 - "$package_zip" "$expected_sha256" "$report_dir" <<'PY'
import hashlib
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


package_zip = Path(sys.argv[1])
expected_sha256 = sys.argv[2].strip().lower()
report_dir = Path(sys.argv[3])
report_dir.mkdir(parents=True, exist_ok=True)


def status_record(status, detail="", files=None):
    return {"status": status, "detail": detail, "files": files or []}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def unsafe_zip_name(name):
    normalized = name.replace("\\", "/")
    return (
        normalized.startswith("/")
        or normalized.startswith("//")
        or any(part == ".." for part in normalized.split("/"))
    )


def write_reports(report):
    json_path = report_dir / "governance-package-verification.json"
    md_path = report_dir / "governance-package-verification.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Governance Package Verification",
        "",
        f"- package: `{report['package']}`",
        f"- expected_sha256: `{report['expected_sha256']}`",
        f"- actual_sha256: `{report['actual_sha256']}`",
        f"- package_sha256_match: `{str(report['package_sha256_match']).lower()}`",
        f"- final_status: `{report['final_status']}`",
        f"- files_detected: `{report['files_detected']}`",
        "",
        "## Validation",
    ]
    for key, value in report["validation"].items():
        lines.append(f"- {key}: `{value['status']}` {value.get('detail', '')}".rstrip())
    lines.extend(["", "## Files"])
    for item in report.get("file_hashes", []):
        lines.append(f"- `{item['sha256']}`  `{item['path']}`")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


report = {
    "package": str(package_zip),
    "expected_sha256": expected_sha256,
    "actual_sha256": None,
    "package_sha256_match": False,
    "files_detected": 0,
    "zip_entries": [],
    "path_traversal_entries": [],
    "file_hashes": [],
    "validation": {
        "zip_list": status_record("NOT_EXECUTED"),
        "path_traversal": status_record("NOT_EXECUTED"),
        "extract": status_record("NOT_EXECUTED"),
        "json": status_record("NOT_EXECUTED"),
        "yaml": status_record("NOT_EXECUTED"),
        "python_py_compile": status_record("NOT_EXECUTED"),
        "bash_n": status_record("NOT_EXECUTED"),
        "shellcheck": status_record("NOT_EXECUTED"),
        "opa_test": status_record("NOT_EXECUTED"),
    },
    "final_status": "FAIL",
}

if not package_zip.is_file():
    report["validation"]["zip_list"] = status_record("FAIL", "package not found")
    write_reports(report)
    sys.exit(1)

report["actual_sha256"] = sha256_file(package_zip)
report["package_sha256_match"] = report["actual_sha256"].lower() == expected_sha256

try:
    with zipfile.ZipFile(package_zip) as zf:
        entries = zf.namelist()
        report["zip_entries"] = entries
        report["files_detected"] = len([n for n in entries if not n.endswith("/")])
        report["validation"]["zip_list"] = status_record("PASS", f"{len(entries)} entries")
        bad_entries = [n for n in entries if unsafe_zip_name(n)]
        report["path_traversal_entries"] = bad_entries
        report["validation"]["path_traversal"] = (
            status_record("FAIL", "unsafe archive paths", bad_entries)
            if bad_entries
            else status_record("PASS")
        )
except Exception as exc:
    report["validation"]["zip_list"] = status_record("FAIL", str(exc))
    write_reports(report)
    sys.exit(1)

if not report["package_sha256_match"]:
    report["validation"]["extract"] = status_record("NOT_EXECUTED_HASH_MISMATCH")
    report["final_status"] = "FAIL"
    write_reports(report)
    sys.exit(1)

if report["path_traversal_entries"]:
    report["validation"]["extract"] = status_record("NOT_EXECUTED_PATH_TRAVERSAL")
    report["final_status"] = "FAIL"
    write_reports(report)
    sys.exit(1)

with tempfile.TemporaryDirectory(prefix="afims-governance-package-") as tmp:
    root = Path(tmp) / "package"
    root.mkdir()
    with zipfile.ZipFile(package_zip) as zf:
        zf.extractall(root)
    report["validation"]["extract"] = status_record("PASS", str(root))

    all_files = sorted(p for p in root.rglob("*") if p.is_file())
    report["file_hashes"] = [
        {"path": str(p.relative_to(root)), "sha256": sha256_file(p)} for p in all_files
    ]

    def run_command(name, command):
        proc = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.returncode, proc.stdout.strip()

    json_files = [p for p in all_files if p.suffix.lower() == ".json"]
    json_failures = []
    for p in json_files:
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            json_failures.append(f"{p.relative_to(root)}: {exc}")
    report["validation"]["json"] = (
        status_record("FAIL", "; ".join(json_failures), json_failures)
        if json_failures
        else status_record("PASS", f"{len(json_files)} files")
    )

    yaml_files = [p for p in all_files if p.suffix.lower() in (".yaml", ".yml")]
    try:
        import yaml
        yaml_failures = []
        for p in yaml_files:
            try:
                yaml.safe_load(p.read_text(encoding="utf-8"))
            except Exception as exc:
                yaml_failures.append(f"{p.relative_to(root)}: {exc}")
        report["validation"]["yaml"] = (
            status_record("FAIL", "; ".join(yaml_failures), yaml_failures)
            if yaml_failures
            else status_record("PASS", f"{len(yaml_files)} files")
        )
    except Exception:
        report["validation"]["yaml"] = status_record("NOT_EXECUTED_TOOL_UNAVAILABLE", "python yaml module unavailable")

    py_files = [p for p in all_files if p.suffix.lower() == ".py"]
    py_failures = []
    for p in py_files:
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as exc:
            py_failures.append(f"{p.relative_to(root)}: {exc}")
    report["validation"]["python_py_compile"] = (
        status_record("FAIL", "; ".join(py_failures), py_failures)
        if py_failures
        else status_record("PASS", f"{len(py_files)} files")
    )

    sh_files = [p for p in all_files if p.suffix.lower() == ".sh"]
    bash_failures = []
    for p in sh_files:
        code, output = run_command("bash", ["bash", "-n", str(p)])
        if code != 0:
            bash_failures.append(f"{p.relative_to(root)}: {output}")
    report["validation"]["bash_n"] = (
        status_record("FAIL", "; ".join(bash_failures), bash_failures)
        if bash_failures
        else status_record("PASS", f"{len(sh_files)} files")
    )

    if shutil.which("shellcheck"):
        shellcheck_failures = []
        for p in sh_files:
            code, output = run_command("shellcheck", ["shellcheck", str(p)])
            if code != 0:
                shellcheck_failures.append(f"{p.relative_to(root)}: {output}")
        report["validation"]["shellcheck"] = (
            status_record("FAIL", "; ".join(shellcheck_failures), shellcheck_failures)
            if shellcheck_failures
            else status_record("PASS", f"{len(sh_files)} files")
        )
    else:
        report["validation"]["shellcheck"] = status_record("NOT_EXECUTED_TOOL_UNAVAILABLE", "shellcheck not found")

    rego_dirs = sorted({str(p.parent.relative_to(root)) for p in all_files if p.suffix.lower() == ".rego"})
    if shutil.which("opa"):
        if rego_dirs:
            code, output = run_command("opa", ["opa", "test", *rego_dirs])
            report["validation"]["opa_test"] = (
                status_record("PASS", output) if code == 0 else status_record("FAIL", output)
            )
        else:
            report["validation"]["opa_test"] = status_record("NOT_EXECUTED_NO_REGO")
    else:
        report["validation"]["opa_test"] = status_record("NOT_EXECUTED_TOOL_UNAVAILABLE", "opa not found")

statuses = [v["status"] for v in report["validation"].values()]
if any(s == "FAIL" for s in statuses):
    report["final_status"] = "FAIL"
elif any(s.startswith("NOT_EXECUTED") for s in statuses):
    report["final_status"] = "NOT_EXECUTED"
else:
    report["final_status"] = "PASS"

write_reports(report)
sys.exit(0 if report["final_status"] == "PASS" else 1)
PY
