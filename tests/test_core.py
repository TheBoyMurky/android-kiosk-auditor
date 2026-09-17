import json

import pytest

from core import Finding, JsonReportGenerator, RuleLoadError, Severity, load_rules


def test_load_rules(tmp_path):
    rule_file = tmp_path / "rules.yaml"
    rule_file.write_text(
        """rules:
  - id: KIOSK-001
    title: Escape is possible
    severity: high
    description: The user can leave kiosk mode.
""",
        encoding="utf-8",
    )

    rules = load_rules(rule_file)
    assert rules[0].severity is Severity.HIGH


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


def test_json_report(tmp_path):
    finding = Finding(
        rule_id="KIOSK-001",
        title="Escape is possible",
        severity=Severity.CRITICAL,
        source="adb_probe",
        description="The user can leave kiosk mode.",
        evidence={"activity": "com.android.settings.Settings"},
    )
    output = JsonReportGenerator().write(
        tmp_path / "report.json",
        [finding],
        {"serial": "emulator-5554"},
    )

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["finding_count"] == 1
    assert report["findings"][0]["severity"] == "critical"
