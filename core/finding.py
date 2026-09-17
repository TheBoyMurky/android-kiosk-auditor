"""Canonical finding model shared by every future analyzer and probe."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class Finding:
    rule_id: str
    title: str
    severity: Severity
    source: str
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    remediation: str | None = None
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("rule_id", "title", "source", "description"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["severity"] = self.severity.value
        data["references"] = list(self.references)
        return data
