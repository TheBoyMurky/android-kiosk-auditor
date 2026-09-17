"""YAML rule loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .finding import Severity


class RuleLoadError(ValueError):
    """Raised when a rule file cannot be parsed or validated."""


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    title: str
    severity: Severity
    description: str
    remediation: str | None = None
    references: tuple[str, ...] = ()


def _required_text(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuleLoadError(f"rules[{index}].{key} must be a non-empty string")
    return value.strip()


def load_rules(path: str | Path) -> list[Rule]:
    rule_path = Path(path)
    try:
        document = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuleLoadError(f"could not load {rule_path}: {exc}") from exc

    if not isinstance(document, dict) or not isinstance(document.get("rules"), list):
        raise RuleLoadError("the YAML root must contain a 'rules' list")

    rules: list[Rule] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(document["rules"]):
        if not isinstance(item, dict):
            raise RuleLoadError(f"rules[{index}] must be a mapping")

        rule_id = _required_text(item, "id", index)
        if rule_id in seen_ids:
            raise RuleLoadError(f"duplicate rule id: {rule_id}")
        seen_ids.add(rule_id)

        severity_text = _required_text(item, "severity", index).lower()
        try:
            severity = Severity(severity_text)
        except ValueError as exc:
            allowed = ", ".join(level.value for level in Severity)
            raise RuleLoadError(
                f"rules[{index}].severity must be one of: {allowed}"
            ) from exc

        references = item.get("references", [])
        if not isinstance(references, list) or not all(
            isinstance(reference, str) and reference.strip()
            for reference in references
        ):
            raise RuleLoadError(f"rules[{index}].references must be a list of strings")

        remediation = item.get("remediation")
        if remediation is not None and not isinstance(remediation, str):
            raise RuleLoadError(f"rules[{index}].remediation must be a string")

        rules.append(
            Rule(
                id=rule_id,
                title=_required_text(item, "title", index),
                severity=severity,
                description=_required_text(item, "description", index),
                remediation=remediation.strip() if remediation else None,
                references=tuple(reference.strip() for reference in references),
            )
        )

    return rules
