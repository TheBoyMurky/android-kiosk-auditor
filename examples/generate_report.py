from core import Finding, JsonReportGenerator, Severity, load_rules


rules = load_rules("rules/kiosk_rules.yaml")
rule = rules[0]
finding = Finding(
    rule_id=rule.id,
    title=rule.title,
    severity=rule.severity,
    source="example",
    description=rule.description,
    evidence={"package_name": "com.example.kiosk"},
    remediation=rule.remediation,
    references=rule.references,
)

JsonReportGenerator().write(
    "kiosk-audit-report.json",
    [finding],
    {"apk": "example.apk", "sha256": "not-calculated"},
)
