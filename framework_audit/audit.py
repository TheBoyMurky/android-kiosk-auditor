"""Generate a P01-P16 audit record from APK and authorized ADB evidence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adb_probe import AdbProbe
from apk_analyzer import ApkAnalyzer
from apk_analyzer.comparison import (
    ComparisonTarget,
    analyze_target,
    build_comparison,
    write_json,
    write_summary,
)


PARAMETERS = {
    "P01": ("Depuração", "Aplicação"),
    "P02": ("Backup", "Aplicação"),
    "P03": ("Permissões", "Aplicação"),
    "P04": ("Componentes", "Aplicação"),
    "P05": ("Credenciais", "Aplicação"),
    "P06": ("Dados e logs", "Aplicação"),
    "P07": ("Sessões", "Aplicação"),
    "P08": ("Plataforma", "Sistema operacional"),
    "P09": ("ADB", "Sistema operacional"),
    "P10": ("Confinamento", "Modo kiosk"),
    "P11": ("Políticas", "Modo kiosk"),
    "P12": ("Interfaces", "Segurança física"),
    "P13": ("Texto claro", "Comunicação em rede"),
    "P14": ("Autenticidade", "Comunicação em rede"),
    "P15": ("Atualizações", "Manutenção"),
    "P16": ("Intervenção", "Manutenção"),
}

FOLLOW_UP = {
    "P02": "Revisar regras de extração e testar backup conforme a versão Android.",
    "P03": "Justificar funcionalmente cada permissão solicitada.",
    "P04": "Testar invocação e controles de acesso dos componentes necessários.",
    "P05": "Confirmar em código se os marcadores correspondem a segredos reutilizáveis.",
    "P06": "Inspecionar arquivos, preferências, bancos, cache e Logcat em execução.",
    "P07": "Testar troca, abandono e encerramento de atendimentos sucessivos.",
    "P08": "Confirmar suporte, atualização e origem da imagem com o fornecedor.",
    "P09": "Distinguir ADB de laboratório da política exigida para produção.",
    "P10": "Testar Home, Recentes, notificações, configurações, reinício e falhas.",
    "P11": "Confirmar Device Owner/MDM, allowlist e políticas administrativas ativas.",
    "P12": "Inspecionar gabinete, USB, boot/recovery e periféricos no terminal físico.",
    "P13": "Observar o tráfego e confirmar quais dados passam pelos destinos detectados.",
    "P14": "Testar certificados inválidos, expirados e hostname incompatível.",
    "P15": "Testar origem, assinatura, falha, recuperação e compatibilidade da atualização.",
    "P16": "Revisar autorização, registros e restauração das restrições após manutenção.",
}


@dataclass(slots=True)
class FrameworkAuditRunner:
    rules_path: Path
    serial: str
    vulnerable_apk: Path
    hardened_apk: Path
    output_dir: Path
    base_dir: Path
    adb_path: str | Path = "adb"
    adb_runner: Any = None

    def run(self) -> dict[str, Any]:
        started_at = datetime.now(timezone.utc)
        analyzer = ApkAnalyzer(self.rules_path)
        vulnerable = analyze_target(
            analyzer,
            ComparisonTarget("VulnerableKioskApp", self.vulnerable_apk),
            base_dir=self.base_dir,
        )
        hardened = analyze_target(
            analyzer,
            ComparisonTarget("HardenedKioskApp", self.hardened_apk),
            base_dir=self.base_dir,
        )
        comparison = build_comparison(vulnerable, hardened)
        probe_options = {"serial": self.serial, "adb_path": self.adb_path}
        if self.adb_runner is not None:
            probe_options["runner"] = self.adb_runner
        snapshot = AdbProbe(**probe_options).collect()
        device = snapshot.to_dict()

        parameter_records = self._parameter_records(vulnerable, hardened, device)
        finished_at = datetime.now(timezone.utc)
        report = {
            "schema_version": "android-kiosk-framework-audit-1.0",
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "duration_seconds": round((finished_at - started_at).total_seconds(), 3),
            "scope": {
                "serial": self.serial,
                "authorization_note": (
                    "ADB collection must be executed only on an authorized device or emulator."
                ),
                "automated_scope": (
                    "Static APK rules, DEX indicators, and read-only Android device collection."
                ),
                "limitation": (
                    "Manual, dynamic, physical, TLS, maintenance, and production-context "
                    "controls remain not evaluated unless separate evidence is attached."
                ),
            },
            "artifacts": {
                "vulnerable": vulnerable["target"],
                "hardened": hardened["target"],
            },
            "device": device,
            "parameter_records": parameter_records,
            "summary": self._summary(parameter_records),
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(self.output_dir / "vulnerable-apk-report.json", vulnerable)
        write_json(self.output_dir / "hardened-apk-report.json", hardened)
        write_json(self.output_dir / "apk-comparison-report.json", comparison)
        write_summary(self.output_dir / "apk-comparison-summary.md", comparison)
        write_json(self.output_dir / "adb-device-snapshot.json", device)
        write_json(self.output_dir / "framework-audit-report.json", report)
        self._write_markdown(report)
        return report

    @staticmethod
    def _evaluations_by_parameter(report: dict) -> dict[str, dict]:
        result = {}
        for evaluation in report["evaluations"]:
            for parameter in evaluation["tcc_parameters"]:
                result[parameter] = evaluation
        return result

    def _parameter_records(self, vulnerable: dict, hardened: dict, device: dict) -> list[dict]:
        vulnerable_evaluations = self._evaluations_by_parameter(vulnerable)
        hardened_evaluations = self._evaluations_by_parameter(hardened)
        records = []
        for parameter, (title, layer) in PARAMETERS.items():
            record = {
                "parameter": parameter,
                "title": title,
                "layer": layer,
                "status": "nao_avaliado",
                "coverage": "manual",
                "evidence": {},
                "application_evaluations": {},
                "scenario_results": {
                    "vulnerable": None,
                    "hardened": None,
                    "device": None,
                },
                "required_follow_up": FOLLOW_UP.get(parameter),
            }
            if parameter in vulnerable_evaluations or parameter in hardened_evaluations:
                record["coverage"] = (
                    "automatic" if parameter in {"P01", "P03", "P04"} else "partial"
                )
                record["application_evaluations"] = {
                    "vulnerable": vulnerable_evaluations.get(parameter),
                    "hardened": hardened_evaluations.get(parameter),
                }
                for scenario, evaluation in record["application_evaluations"].items():
                    if evaluation is not None:
                        record["scenario_results"][scenario] = {
                            "status": evaluation["status"],
                            "indicator_observed": evaluation.get("indicator_observed"),
                            "evidence_collected": True,
                        }
                statuses = {
                    item["status"]
                    for item in record["application_evaluations"].values()
                    if item is not None
                }
                if parameter in {"P01", "P03", "P04", "P05"} and len(statuses) == 1:
                    record["status"] = statuses.pop()
                elif parameter in {"P01", "P03", "P04", "P05"}:
                    record["status"] = "nao_avaliado"
                    record["required_follow_up"] = (
                        "Os dois cenários possuem estados diferentes; interpretar por artefato."
                    )
                if parameter == "P05":
                    record["evidence"] = {
                        "vulnerable_credential_literals": vulnerable["dex_indicators"]["credential_literals"],
                        "hardened_credential_literals": hardened["dex_indicators"]["credential_literals"],
                        "scope_limitation": (
                            "A conclusão cobre somente os padrões de literais estáticos definidos."
                        ),
                    }
            elif parameter == "P05":
                record["coverage"] = "partial"
                record["evidence"] = {
                    "vulnerable_credential_markers": vulnerable["dex_indicators"]["credential_markers"],
                    "hardened_credential_markers": hardened["dex_indicators"]["credential_markers"],
                }
                record["scenario_results"]["vulnerable"] = {
                    "status": "nao_avaliado",
                    "indicator_observed": bool(record["evidence"]["vulnerable_credential_markers"]),
                    "evidence_collected": True,
                }
                record["scenario_results"]["hardened"] = {
                    "status": "nao_avaliado",
                    "indicator_observed": bool(record["evidence"]["hardened_credential_markers"]),
                    "evidence_collected": True,
                }
            elif parameter in {"P08", "P09", "P10", "P11"}:
                record["coverage"] = "partial"
                record["evidence"] = self._device_evidence(parameter, device)
                record["scenario_results"]["device"] = {
                    "status": "nao_avaliado",
                    "indicator_observed": None,
                    "evidence_collected": True,
                }
            elif parameter == "P13":
                record["coverage"] = "partial"
                record["evidence"] = {
                    "vulnerable_cleartext": vulnerable["manifest_summary"]["uses_cleartext_traffic"],
                    "hardened_cleartext": hardened["manifest_summary"]["uses_cleartext_traffic"],
                    "vulnerable_urls": vulnerable["dex_indicators"]["urls"],
                    "hardened_urls": hardened["dex_indicators"]["urls"],
                }
                record["scenario_results"]["vulnerable"] = {
                    "status": "nao_avaliado",
                    "indicator_observed": bool(
                        record["evidence"]["vulnerable_cleartext"]
                        or record["evidence"]["vulnerable_urls"]
                    ),
                    "evidence_collected": True,
                }
                record["scenario_results"]["hardened"] = {
                    "status": "nao_avaliado",
                    "indicator_observed": bool(
                        record["evidence"]["hardened_cleartext"]
                        or record["evidence"]["hardened_urls"]
                    ),
                    "evidence_collected": True,
                }
            records.append(record)
        return records

    @staticmethod
    def _device_evidence(parameter: str, device: dict) -> dict:
        if parameter == "P08":
            return {
                "android_version": device["android_version"],
                "android_sdk": device["android_sdk"],
                "security_patch": device["security_patch"],
                "build_fingerprint": device["build_fingerprint"],
                "installed_package_count": len(device["installed_packages"]),
            }
        if parameter == "P09":
            return {
                "adb_enabled": device["adb_enabled"],
                "ro_debuggable": device["ro_debuggable"],
                "ro_secure": device["ro_secure"],
                "ro_adb_secure": device["ro_adb_secure"],
            }
        if parameter == "P10":
            lock_task_lines = [
                line.strip()
                for line in device["activity_state"].splitlines()
                if "locktask" in line.lower()
            ]
            return {"lock_task_lines": lock_task_lines}
        return {"device_policy": device["device_policy"]}

    @staticmethod
    def _summary(records: list[dict]) -> dict:
        statuses = {status: 0 for status in (
            "conforme", "nao_conforme", "nao_avaliado", "nao_aplicavel"
        )}
        coverage = {level: 0 for level in ("automatic", "partial", "manual")}
        scenario_statuses = {
            scenario: dict(statuses) for scenario in ("vulnerable", "hardened", "device")
        }
        evidence_collected = 0
        for record in records:
            statuses[record["status"]] += 1
            coverage[record["coverage"]] += 1
            if any(
                result and result["evidence_collected"]
                for result in record["scenario_results"].values()
            ):
                evidence_collected += 1
            for scenario, result in record["scenario_results"].items():
                if result is not None:
                    scenario_statuses[scenario][result["status"]] += 1
        return {
            "status_counts": statuses,
            "scenario_status_counts": scenario_statuses,
            "coverage_counts": coverage,
            "parameters_with_evidence": evidence_collected,
            "parameters_requiring_manual_evidence": len(records) - evidence_collected,
        }

    @staticmethod
    def _scenario_label(result: dict | None) -> str:
        if result is None:
            return "-"
        status = result["status"]
        indicator = result["indicator_observed"]
        if indicator is True:
            return f"{status} (indicador encontrado)"
        if indicator is False:
            return f"{status} (sem indicador)"
        if result["evidence_collected"]:
            return f"{status} (evidência coletada)"
        return status

    @staticmethod
    def _markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
        """Build a Markdown table whose source columns are visually aligned."""
        widths = [
            max(len(headers[index]), *(len(row[index]) for row in rows))
            for index in range(len(headers))
        ]

        def format_row(values: list[str]) -> str:
            cells = [value.ljust(widths[index]) for index, value in enumerate(values)]
            return "| " + " | ".join(cells) + " |"

        separator = "| " + " | ".join("-" * width for width in widths) + " |"
        return [format_row(headers), separator, *(format_row(row) for row in rows)]

    def _write_markdown(self, report: dict) -> None:
        lines = [
            "# Registro de auditoria do framework P01-P16",
            "",
            f"- Dispositivo: `{self.serial}`",
            f"- Início: `{report['started_at']}`",
            f"- Duração: `{report['duration_seconds']} s`",
            "",
            "## Resultado por parâmetro",
            "",
            (
                f"A execução coletou evidências para "
                f"**{report['summary']['parameters_with_evidence']} de 16 parâmetros**. "
                "`nao_avaliado` significa que a evidência ainda exige interpretação ou teste manual; "
                "não significa que o script deixou de executar."
            ),
            "",
        ]
        headers = [
            "ID", "Tema", "Cobertura", "APK vulnerável", "APK endurecido",
            "Dispositivo", "Conclusão global", "Próxima evidência",
        ]
        rows = []
        for record in report["parameter_records"]:
            follow_up = (record["required_follow_up"] or "-").replace("|", "/")
            results = record["scenario_results"]
            rows.append([
                record["parameter"],
                record["title"],
                record["coverage"],
                self._scenario_label(results["vulnerable"]),
                self._scenario_label(results["hardened"]),
                self._scenario_label(results["device"]),
                record["status"],
                follow_up,
            ])
        lines.extend(self._markdown_table(headers, rows))
        lines.extend([
            "",
            "## Limitação",
            "",
            report["scope"]["limitation"],
            "",
            "A ausência de achados automáticos não comprova segurança integral.",
        ])
        (self.output_dir / "framework-audit-summary.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
