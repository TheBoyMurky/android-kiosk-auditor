"""Reproducible static comparison reports for the reference APKs."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from core import ControlEvaluation, EvaluationMode, EvaluationStatus

from .analyzer import (
    ANDROID,
    IMPLEMENTED_RULE_IDS,
    PROTECTIVE_COMPONENT_PERMISSIONS,
    ApkAnalysisError,
    ApkAnalyzer,
)


URL_PATTERN = re.compile(rb"https?://[^\x00-\x20\x7f\"'<>]{3,}", re.IGNORECASE)
CREDENTIAL_MARKERS = (
    b"api_key",
    b"apikey",
    b"password",
    b"secret",
    b"sessiontoken",
    b"token",
)
CREDENTIAL_LITERAL_PATTERNS = (
    re.compile(rb"\badmin[0-9]{3,}\b", re.IGNORECASE),
    re.compile(rb"\b(?:test[_-])?api[_-]?key[_-]?[a-z0-9_-]{6,}\b", re.IGNORECASE),
    re.compile(rb"\b(?:fake[_-])?(?:secret|token)[a-z0-9_-]{4,}\b", re.IGNORECASE),
)
DEX_CREDENTIAL_RULE_ID = "APK-004"


@dataclass(frozen=True, slots=True)
class ComparisonTarget:
    name: str
    apk_path: Path


def _android_bool(element, name: str) -> bool | None:
    value = element.get(f"{ANDROID}{name}")
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def _display_path(path: Path, base_dir: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dex_indicators(path: Path) -> dict[str, list[str]]:
    urls: set[str] = set()
    markers: set[str] = set()
    credential_literals: set[str] = set()
    try:
        with ZipFile(path) as archive:
            dex_names = sorted(
                name for name in archive.namelist()
                if name.startswith("classes") and name.endswith(".dex")
            )
            for name in dex_names:
                payload = archive.read(name)
                urls.update(
                    match.decode("utf-8", errors="replace")
                    for match in URL_PATTERN.findall(payload)
                )
                lowered = payload.lower()
                markers.update(
                    marker.decode("ascii")
                    for marker in CREDENTIAL_MARKERS
                    if marker in lowered
                )
                for pattern in CREDENTIAL_LITERAL_PATTERNS:
                    credential_literals.update(
                        match.group(0).decode("utf-8", errors="replace")
                        for match in pattern.finditer(payload)
                    )
    except (BadZipFile, OSError, KeyError) as exc:
        raise ApkAnalysisError(f"could not inspect DEX strings in {path}: {exc}") from exc
    return {
        "urls": sorted(urls),
        "credential_markers": sorted(markers),
        "credential_literals": sorted(credential_literals),
    }


def analyze_target(
    analyzer: ApkAnalyzer,
    target: ComparisonTarget,
    *,
    base_dir: Path,
) -> dict:
    path = target.apk_path
    manifest = analyzer.extract_manifest(path)
    findings = analyzer.analyze_manifest(
        manifest, source=f"apk_analyzer:{path.name}"
    )
    findings_by_rule = {
        rule_id: [finding for finding in findings if finding.rule_id == rule_id]
        for rule_id in IMPLEMENTED_RULE_IDS
    }
    indicators = _dex_indicators(path)
    evaluations = []
    for rule_id in (*IMPLEMENTED_RULE_IDS, DEX_CREDENTIAL_RULE_ID):
        rule = analyzer.get_rule(rule_id)
        observed = (
            bool(indicators["credential_literals"])
            if rule_id == DEX_CREDENTIAL_RULE_ID
            else bool(findings_by_rule[rule_id])
        )
        if rule.evaluation_mode is EvaluationMode.CONCLUSIVE:
            status = (
                EvaluationStatus.NAO_CONFORME
                if observed
                else EvaluationStatus.CONFORME
            )
            if rule_id == DEX_CREDENTIAL_RULE_ID:
                rationale = (
                    "Um literal compatível com os padrões de credencial delimitados foi encontrado no DEX."
                    if observed
                    else "Nenhum literal compatível com os padrões de credencial delimitados foi encontrado no DEX."
                )
            else:
                rationale = (
                    "A regra implementada encontrou evidência direta de descumprimento do critério."
                    if observed
                    else "A regra implementada encontrou evidência direta de atendimento do critério."
                )
        else:
            status = EvaluationStatus.NAO_AVALIADO
            rationale = (
                "Um indicador foi observado, mas a conclusão exige evidência contextual."
                if observed
                else "Nenhum indicador foi observado, mas esta regra isolada não estabelece conformidade."
            )
        evaluations.append(
            ControlEvaluation(
                rule_id=rule.id,
                status=status,
                mode=rule.evaluation_mode,
                indicator_observed=observed,
                rationale=rationale,
                tcc_parameters=rule.tcc_parameters,
                checklist_ids=rule.checklist_ids,
            )
        )
    application = manifest.find("application")
    if application is None:
        raise ApkAnalysisError("AndroidManifest.xml has no <application> element")

    permissions = sorted(
        {
            element.get(f"{ANDROID}name")
            for tag in ("uses-permission", "uses-permission-sdk-23")
            for element in manifest.findall(tag)
            if element.get(f"{ANDROID}name")
        }
    )
    components = []
    for tag in ("activity", "activity-alias", "service", "receiver", "provider"):
        for component in application.findall(tag):
            components.append(
                {
                    "type": tag,
                    "name": component.get(f"{ANDROID}name", "<unnamed>"),
                    "exported": _android_bool(component, "exported"),
                    "has_intent_filter": component.find("intent-filter") is not None,
                    "permission": component.get(f"{ANDROID}permission"),
                }
            )

    uses_sdk = manifest.find("uses-sdk")
    return {
        "schema_version": "static-apk-report-2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_mode": "reproducible_static_apk_no_adb_device",
        "target": {
            "name": target.name,
            "apk_path": _display_path(path, base_dir),
            "sha256": _sha256(path),
            "size_bytes": path.stat().st_size,
            "package_name": manifest.get("package"),
            "version_code": manifest.get(f"{ANDROID}versionCode"),
            "version_name": manifest.get(f"{ANDROID}versionName"),
            "min_sdk": uses_sdk.get(f"{ANDROID}minSdkVersion") if uses_sdk is not None else None,
            "target_sdk": uses_sdk.get(f"{ANDROID}targetSdkVersion") if uses_sdk is not None else None,
        },
        "tooling": {
            "engine": "android-kiosk-auditor",
            "rules_path": _display_path(Path("rules/kiosk_rules.yaml"), base_dir),
            "external_android_tools_required": False,
        },
        "manifest_summary": {
            "debuggable": _android_bool(application, "debuggable"),
            "allow_backup": _android_bool(application, "allowBackup"),
            "uses_cleartext_traffic": _android_bool(application, "usesCleartextTraffic"),
            "network_security_config": application.get(f"{ANDROID}networkSecurityConfig"),
            "permissions": permissions,
            "components": components,
        },
        "dex_indicators": indicators,
        "summary": {
            "finding_count": len(findings),
            "finding_scope_note": (
                "A contagem inclui somente regras implementadas pelo ApkAnalyzer atual; "
                "ausência de achados não comprova segurança completa."
            ),
            "evaluation_status_counts": {
                status.value: sum(
                    evaluation.status is status for evaluation in evaluations
                )
                for status in EvaluationStatus
            },
        },
        "evaluation_policy": {
            "statuses": [status.value for status in EvaluationStatus],
            "not_applicable_policy": (
                "nao_aplicavel exige justificativa humana documentada e nunca é "
                "atribuído automaticamente."
            ),
            "severity_note": (
                "A severidade é uma classificação inicial de triagem do catálogo, "
                "não uma pontuação universal de risco cientificamente validada."
            ),
            "credential_scope_note": (
                "APK-004 conclui apenas sobre os padrões de literais estáticos definidos; "
                "não detecta segredos ofuscados, montados dinamicamente ou recebidos remotamente."
            ),
        },
        "evaluations": [evaluation.to_dict() for evaluation in evaluations],
        "findings": [finding.to_dict() for finding in findings],
    }


def build_comparison(vulnerable: dict, hardened: dict) -> dict:
    def exported_internal(report: dict) -> list[dict]:
        result = []
        for component in report["manifest_summary"]["components"]:
            name = component["name"]
            is_launcher = name.endswith(".MainActivity") or name == ".MainActivity"
            is_protected = component.get("permission") in PROTECTIVE_COMPONENT_PERMISSIONS
            if component["exported"] is True and not is_launcher and not is_protected:
                result.append(component)
        return result

    return {
        "schema_version": "static-apk-comparison-2.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_mode": "reproducible_static_apk_no_adb_device",
        "targets": {
            "vulnerable": vulnerable["target"],
            "hardened": hardened["target"],
        },
        "report_paths": {
            "vulnerable": "reports/vulnerable-apk-report.json",
            "hardened": "reports/hardened-apk-report.json",
        },
        "comparison": {
            "finding_count": {
                "vulnerable": vulnerable["summary"]["finding_count"],
                "hardened": hardened["summary"]["finding_count"],
            },
            "evaluation_status_counts": {
                "vulnerable": vulnerable["summary"]["evaluation_status_counts"],
                "hardened": hardened["summary"]["evaluation_status_counts"],
            },
            "permissions": {
                "vulnerable": vulnerable["manifest_summary"]["permissions"],
                "hardened": hardened["manifest_summary"]["permissions"],
            },
            "cleartext_configuration": {
                "vulnerable": vulnerable["manifest_summary"]["uses_cleartext_traffic"],
                "hardened": hardened["manifest_summary"]["uses_cleartext_traffic"],
            },
            "backup_configuration": {
                "vulnerable": vulnerable["manifest_summary"]["allow_backup"],
                "hardened": hardened["manifest_summary"]["allow_backup"],
            },
            "exported_internal_components": {
                "vulnerable": exported_internal(vulnerable),
                "hardened": exported_internal(hardened),
            },
            "dex_urls": {
                "vulnerable": vulnerable["dex_indicators"]["urls"],
                "hardened": hardened["dex_indicators"]["urls"],
            },
            "credential_markers": {
                "vulnerable": vulnerable["dex_indicators"]["credential_markers"],
                "hardened": hardened["dex_indicators"]["credential_markers"],
            },
        },
        "scope_note": (
            "Esta comparação cobre somente verificações estáticas implementadas e "
            "indicadores de strings DEX. Controles de dispositivo, kiosk, TLS, físicos, "
            "dinâmicos e operacionais permanecem não avaliados nesta execução."
        ),
    }


def write_json(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_summary(path: Path, comparison: dict) -> None:
    vulnerable = comparison["targets"]["vulnerable"]
    hardened = comparison["targets"]["hardened"]
    counts = comparison["comparison"]["finding_count"]
    statuses = comparison["comparison"]["evaluation_status_counts"]
    text = f"""# Relatório de comparação estática dos APKs

Gerado em: {comparison['generated_at']}

## Artefatos

- VulnerableKioskApp: `{vulnerable['apk_path']}` (`sha256: {vulnerable['sha256']}`)
- HardenedKioskApp: `{hardened['apk_path']}` (`sha256: {hardened['sha256']}`)

## Relatórios

- `reports/vulnerable-apk-report.json`
- `reports/hardened-apk-report.json`
- `reports/apk-comparison-report.json`

## Resultados das regras implementadas

- Achados no VulnerableKioskApp: {counts['vulnerable']}
- Achados no HardenedKioskApp: {counts['hardened']}

As contagens incluem somente as regras implementadas pelo `ApkAnalyzer` atual.
Ausência de achados não significa que a aplicação ou o dispositivo estejam
integralmente seguros.

## Estados de avaliação

- VulnerableKioskApp: `{json.dumps(statuses['vulnerable'], ensure_ascii=False)}`
- HardenedKioskApp: `{json.dumps(statuses['hardened'], ensure_ascii=False)}`

Somente regras conclusivas podem atribuir `conforme` automaticamente. Regras
indicativas permanecem `nao_avaliado` até a revisão das evidências contextuais.
`nao_aplicavel` sempre exige justificativa humana documentada.

## Escopo

{comparison['scope_note']}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
