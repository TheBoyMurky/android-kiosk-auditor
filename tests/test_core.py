import json
import re

import pytest

from core import (
    EvaluationMode,
    Finding,
    JsonReportGenerator,
    RuleLoadError,
    Severity,
    load_rules,
)


def test_load_rules(tmp_path):
    rule_file = tmp_path / "rules.yaml"
    rule_file.write_text(
        """rules:
  - id: KIOSK-001
    title: Escape is possible
    severity: high
    description: The user can leave kiosk mode.
    tcc_parameters: [P10]
    checklist_ids: [KSK-01, KSK-02]
""",
        encoding="utf-8",
    )

    rules = load_rules(rule_file)
    assert rules[0].severity is Severity.HIGH
    assert rules[0].tcc_parameters == ("P10",)
    assert rules[0].checklist_ids == ("KSK-01", "KSK-02")
    assert rules[0].evaluation_mode is EvaluationMode.INDICATOR


def test_duplicate_rule_ids_are_rejected(tmp_path):
    rule_file = tmp_path / "rules.yaml"
    rule_file.write_text(
        """rules:
  - {id: K-1, title: One, severity: low, description: First}
  - {id: K-1, title: Two, severity: high, description: Second}
""",
        encoding="utf-8",
    )

    with pytest.raises(RuleLoadError, match="duplicate rule id"):
        load_rules(rule_file)


def test_rule_traceability_fields_must_be_string_lists(tmp_path):
    rule_file = tmp_path / "rules.yaml"
    rule_file.write_text(
        """rules:
  - id: K-1
    title: Invalid traceability
    severity: low
    description: Invalid mapping.
    tcc_parameters: P01
""",
        encoding="utf-8",
    )

    with pytest.raises(RuleLoadError, match="tcc_parameters"):
        load_rules(rule_file)


def test_rule_evaluation_mode_must_be_known(tmp_path):
    rule_file = tmp_path / "rules.yaml"
    rule_file.write_text(
        """rules:
  - id: K-1
    title: Invalid mode
    severity: low
    description: Invalid evaluation mode.
    evaluation_mode: automatic-maybe
""",
        encoding="utf-8",
    )

    with pytest.raises(RuleLoadError, match="evaluation_mode"):
        load_rules(rule_file)


def test_canonical_automated_rules_have_valid_traceability():
    rules = load_rules("rules/kiosk_rules.yaml")

    for rule in rules:
        assert rule.tcc_parameters
        assert rule.checklist_ids
        assert all(re.fullmatch(r"P(?:0[1-9]|1[0-6])", value) for value in rule.tcc_parameters)
        assert all(re.fullmatch(r"[A-Z]{3}-\d{2}", value) for value in rule.checklist_ids)


def test_json_report(tmp_path):
    finding = Finding(
        rule_id="KIOSK-001",
        title="Escape is possible",
        severity=Severity.CRITICAL,
        source="adb_probe",
        description="The user can leave kiosk mode.",
        evidence={"activity": "com.android.settings.Settings"},
        tcc_parameters=("P10",),
        checklist_ids=("KSK-01",),
    )
    output = JsonReportGenerator().write(
        tmp_path / "report.json",
        [finding],
        {"serial": "emulator-5554"},
    )

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["finding_count"] == 1
    assert report["findings"][0]["severity"] == "critical"
    assert report["findings"][0]["tcc_parameters"] == ["P10"]
    assert report["findings"][0]["checklist_ids"] == ["KSK-01"]
