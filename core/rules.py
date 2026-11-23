"""YAML rule loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .finding import Severity
from .evaluation import EvaluationMode


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
    tcc_parameters: tuple[str, ...] = ()
    checklist_ids: tuple[str, ...] = ()
    evaluation_mode: EvaluationMode = EvaluationMode.INDICATOR


def _required_text(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuleLoadError(f"rules[{index}].{key} must be a non-empty string")
    return value.strip()


def _optional_text_list(item: dict[str, Any], key: str, index: int) -> tuple[str, ...]:
    values = item.get(key, [])
    if not isinstance(values, list) or not all(
        isinstance(value, str) and value.strip() for value in values
    ):
        raise RuleLoadError(f"rules[{index}].{key} must be a list of strings")
    return tuple(value.strip() for value in values)


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

        references = _optional_text_list(item, "references", index)
        tcc_parameters = _optional_text_list(item, "tcc_parameters", index)
        checklist_ids = _optional_text_list(item, "checklist_ids", index)
        evaluation_mode_text = item.get("evaluation_mode", "indicator")
        try:
            evaluation_mode = EvaluationMode(evaluation_mode_text)
        except (TypeError, ValueError) as exc:
            allowed = ", ".join(mode.value for mode in EvaluationMode)
            raise RuleLoadError(
                f"rules[{index}].evaluation_mode must be one of: {allowed}"
            ) from exc

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
                references=references,
                tcc_parameters=tcc_parameters,
                checklist_ids=checklist_ids,
                evaluation_mode=evaluation_mode,
            )
        )

    return rules
