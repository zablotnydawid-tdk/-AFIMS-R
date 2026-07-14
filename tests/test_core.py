from __future__ import annotations
import json
import unittest
from pathlib import Path

from afims_r.engine import run_validation
from afims_r.extraction import extract
from afims_r.validators import numeric_validate, semantic_validate, governance_validate

BASE = Path(__file__).resolve().parents[1]

class CoreTests(unittest.TestCase):
    def request(self, source: str, answer: str, generator=None, same_role=False):
        return {
            "contract": {
                "contract_id": "vc_test",
                "validation_mode": "PRESERVE",
                "required_format": "text",
                "generator_id": "svc-a",
                "certifier_id": "svc-a" if same_role else "svc-c",
            },
            "source": {"content": source},
            "answer": {"content": answer},
            "generator": generator or {"role": "GENERATOR", "service_id": "svc-a"},
        }

    def test_01_baseline_pass(self):
        report = run_validation(self.request("Napięcie wynosi 253 V.", "Napięcie wynosi 253 V."))
        self.assertEqual(report["certification"]["verdict"], "PASS")

    def test_02_number_change_detected(self):
        result = numeric_validate(extract("253 V"), extract("235 V"))
        self.assertEqual(result.status.value, "FAIL")

    def test_03_numeric_addition_detected(self):
        result = numeric_validate(extract("253 V"), extract("253 V i 10 A"))
        self.assertEqual(result.status.value, "FAIL")

    def test_04_negation_reversal_detected(self):
        result = semantic_validate(extract("Nie wykazano ryzyka."), extract("Wykazano ryzyko."))
        self.assertEqual(result.status.value, "FAIL")

    def test_05_uncertainty_drift_detected(self):
        result = semantic_validate(extract("Może powodować błąd."), extract("Powoduje błąd."))
        self.assertEqual(result.status.value, "FAIL")

    def test_06_self_certification_block(self):
        result = governance_validate("g", "c", {"verdict": "PASS"})
        self.assertEqual(result.status.value, "FAIL")

    def test_07_role_separation_block(self):
        result = governance_validate("same", "same", {})
        self.assertEqual(result.status.value, "FAIL")

    def test_08_report_is_sealed(self):
        report = run_validation(self.request("Wartość 5 kW.", "Wartość 5 kW."))
        self.assertTrue(report["sealed"])
        self.assertTrue(report["report_hash"].startswith("sha256:"))

    def test_09_rule_registry_has_85_rules(self):
        data = json.loads((BASE / "registry" / "rules.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["rules"]), 85)

    def test_10_mapping_has_85_tests(self):
        data = json.loads((BASE / "registry" / "afims_t_mapping.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["tests"]), 85)

    def test_11_all_groups_present(self):
        data = json.loads((BASE / "registry" / "afims_t_mapping.json").read_text(encoding="utf-8"))
        self.assertEqual({t["group"] for t in data["tests"]}, {f"T{i}" for i in range(1, 11)})

    def test_12_fail_closed_on_validator_failure(self):
        report = run_validation(self.request("Napięcie 253 V.", "Napięcie 235 V."))
        self.assertEqual(report["certification"]["verdict"], "FAIL")

    def test_13_longest_energy_unit_is_not_truncated(self):
        model = extract("Moc 11,2 kWp, energia 10,24 kWh i 2 MWh.")
        self.assertEqual(model.numbers, ("11,2 kWp", "10,24 kWh", "2 MWh"))

if __name__ == "__main__":
    unittest.main()
