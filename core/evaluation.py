"""Evaluation states used by the framework reports."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum


class EvaluationStatus(str, Enum):
    CONFORME = "conforme"
    NAO_CONFORME = "nao_conforme"
    NAO_AVALIADO = "nao_avaliado"
    NAO_APLICAVEL = "nao_aplicavel"


class EvaluationMode(str, Enum):
    CONCLUSIVE = "conclusive"
    INDICATOR = "indicator"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class ControlEvaluation:
    rule_id: str
    status: EvaluationStatus
    mode: EvaluationMode
    indicator_observed: bool
    rationale: str
    tcc_parameters: tuple[str, ...] = ()
    checklist_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        data["mode"] = self.mode.value
        data["tcc_parameters"] = list(self.tcc_parameters)
        data["checklist_ids"] = list(self.checklist_ids)
        return data
