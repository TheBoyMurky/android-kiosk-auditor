"""JSON report generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .finding import Finding


class JsonReportGenerator:
    schema_version = "1.0"

    def build(self, findings: Iterable[Finding], target: dict[str, str]) -> dict:
        ordered_findings = sorted(
            findings, key=lambda finding: (finding.rule_id, finding.source)
        )
        return {
            "schema_version": self.schema_version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target": dict(target),
            "summary": {"finding_count": len(ordered_findings)},
            "findings": [finding.to_dict() for finding in ordered_findings],
        }

    def write(
        self,
        output_path: str | Path,
        findings: Iterable[Finding],
        target: dict[str, str],
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        report = self.build(findings, target)
        path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path
