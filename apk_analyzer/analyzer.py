"""Basic AndroidManifest.xml checks for APK files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from core import Finding, Rule, load_rules

ANDROID_NAMESPACE = "http://schemas.android.com/apk/res/android"
ANDROID = f"{{{ANDROID_NAMESPACE}}}"

RULE_DEBUGGABLE = "APK-001"
RULE_ALLOW_BACKUP = "APK-002"
RULE_DANGEROUS_PERMISSION = "APK-003"
RULE_EXPORTED_COMPONENT = "KIOSK-002"

COMPONENT_TAGS = ("activity", "activity-alias", "service", "receiver", "provider")

# Android platform permissions whose protection level includes "dangerous".
# Grouped here deliberately so the decision remains deterministic and auditable.
DANGEROUS_PERMISSIONS = frozenset(
    {
        "android.permission.ACCEPT_HANDOVER",
        "android.permission.ACCESS_BACKGROUND_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_MEDIA_LOCATION",
        "android.permission.ACTIVITY_RECOGNITION",
        "android.permission.ADD_VOICEMAIL",
        "android.permission.ANSWER_PHONE_CALLS",
        "android.permission.BLUETOOTH_ADVERTISE",
        "android.permission.BLUETOOTH_CONNECT",
        "android.permission.BLUETOOTH_SCAN",
        "android.permission.BODY_SENSORS",
        "android.permission.BODY_SENSORS_BACKGROUND",
        "android.permission.CALL_PHONE",
        "android.permission.CAMERA",
        "android.permission.GET_ACCOUNTS",
        "android.permission.NEARBY_WIFI_DEVICES",
        "android.permission.POST_NOTIFICATIONS",
        "android.permission.PROCESS_OUTGOING_CALLS",
        "android.permission.READ_CALENDAR",
        "android.permission.READ_CALL_LOG",
        "android.permission.READ_CONTACTS",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.READ_MEDIA_AUDIO",
        "android.permission.READ_MEDIA_IMAGES",
        "android.permission.READ_MEDIA_VIDEO",
        "android.permission.READ_MEDIA_VISUAL_USER_SELECTED",
        "android.permission.READ_PHONE_NUMBERS",
        "android.permission.READ_PHONE_STATE",
        "android.permission.READ_SMS",
        "android.permission.RECEIVE_MMS",
        "android.permission.RECEIVE_SMS",
        "android.permission.RECEIVE_WAP_PUSH",
        "android.permission.RECORD_AUDIO",
        "android.permission.SEND_SMS",
        "android.permission.USE_SIP",
        "android.permission.UWB_RANGING",
        "android.permission.WRITE_CALENDAR",
        "android.permission.WRITE_CALL_LOG",
        "android.permission.WRITE_CONTACTS",
        "android.permission.WRITE_EXTERNAL_STORAGE",
    }
)


class ApkAnalysisError(RuntimeError):
    """Raised when an APK or its manifest cannot be decoded."""


class ApkAnalyzer:
    def __init__(self, rules_path: str | Path) -> None:
        rules = load_rules(rules_path)
        self._rules = {rule.id: rule for rule in rules}
        required = {
            RULE_DEBUGGABLE,
            RULE_ALLOW_BACKUP,
            RULE_DANGEROUS_PERMISSION,
            RULE_EXPORTED_COMPONENT,
        }
        missing = required.difference(self._rules)
        if missing:
            raise ValueError(f"missing analyzer rules: {', '.join(sorted(missing))}")

    def analyze(self, apk_path: str | Path) -> list[Finding]:
        path = Path(apk_path)
        manifest = self.extract_manifest(path)
        return self.analyze_manifest(manifest, source=f"apk_analyzer:{path.name}")

    def extract_manifest(self, apk_path: str | Path) -> ElementTree.Element:
        """Extract and decode AndroidManifest.xml from an APK."""
        path = Path(apk_path)
        if not path.is_file():
            raise ApkAnalysisError(f"APK does not exist: {path}")

        try:
            with ZipFile(path) as apk_zip:
                raw_manifest = apk_zip.read("AndroidManifest.xml")
            # Plain XML is useful for fixtures and uncommon unpacked/repacked APKs.
            if raw_manifest.lstrip().startswith(b"<"):
                return ElementTree.fromstring(raw_manifest)
        except (BadZipFile, KeyError, ElementTree.ParseError) as exc:
            raise ApkAnalysisError(f"invalid APK manifest in {path}: {exc}") from exc

        try:
            try:
                from androguard.core.apk import APK
            except ImportError:  # Compatibility with Androguard 3.x.
                from androguard.core.bytecodes.apk import APK

            manifest = APK(str(path)).get_android_manifest_xml()
        except Exception as exc:
            raise ApkAnalysisError(f"could not decode binary manifest in {path}: {exc}") from exc

        if manifest is None:
            raise ApkAnalysisError(f"APK has no decodable AndroidManifest.xml: {path}")
        return manifest

    def analyze_manifest(
        self, manifest: ElementTree.Element, source: str = "apk_analyzer"
    ) -> list[Finding]:
        findings: list[Finding] = []
        application = manifest.find("application")
        if application is None:
            raise ApkAnalysisError("AndroidManifest.xml has no <application> element")

        if self._android_bool(application, "debuggable") is True:
            findings.append(
                self._finding(
                    RULE_DEBUGGABLE,
                    source,
                    {"attribute": "android:debuggable", "value": True},
                )
            )

        allow_backup = self._android_bool(application, "allowBackup")
        if allow_backup is not False:
            findings.append(
                self._finding(
                    RULE_ALLOW_BACKUP,
                    source,
                    {
                        "attribute": "android:allowBackup",
                        "value": allow_backup,
                        "effective_value": True,
                        "declared": allow_backup is not None,
                    },
                )
            )

        for permission in self._dangerous_permissions(manifest):
            findings.append(
                self._finding(
                    RULE_DANGEROUS_PERMISSION,
                    source,
                    {"permission": permission},
                )
            )

        package_name = manifest.get("package", "")
        for component in self._exported_components(application):
            raw_name = component.get(f"{ANDROID}name", "<unnamed>")
            findings.append(
                self._finding(
                    RULE_EXPORTED_COMPONENT,
                    source,
                    {
                        "component_type": component.tag,
                        "component_name": self._qualified_name(package_name, raw_name),
                        "exported": component.get(f"{ANDROID}exported"),
                        "has_intent_filter": component.find("intent-filter") is not None,
                        "permission": component.get(f"{ANDROID}permission"),
                    },
                )
            )

        return findings

    def _finding(self, rule_id: str, source: str, evidence: dict) -> Finding:
        rule: Rule = self._rules[rule_id]
        return Finding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            source=source,
            description=rule.description,
            evidence=evidence,
            remediation=rule.remediation,
            references=rule.references,
        )

    @staticmethod
    def _android_bool(element: ElementTree.Element, name: str) -> bool | None:
        value = element.get(f"{ANDROID}{name}")
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
        return None

    @staticmethod
    def _dangerous_permissions(manifest: ElementTree.Element) -> list[str]:
        declared = {
            element.get(f"{ANDROID}name")
            for tag in ("uses-permission", "uses-permission-sdk-23")
            for element in manifest.findall(tag)
        }
        return sorted(permission for permission in declared if permission in DANGEROUS_PERMISSIONS)

    @staticmethod
    def _exported_components(
        application: ElementTree.Element,
    ) -> Iterable[ElementTree.Element]:
        for tag in COMPONENT_TAGS:
            for component in application.findall(tag):
                exported = component.get(f"{ANDROID}exported")
                explicitly_exported = exported is not None and exported.lower() == "true"
                implicitly_exported = exported is None and component.find("intent-filter") is not None
                if explicitly_exported or implicitly_exported:
                    yield component

    @staticmethod
    def _qualified_name(package_name: str, component_name: str) -> str:
        if component_name.startswith("."):
            return f"{package_name}{component_name}"
        if "." not in component_name and package_name:
            return f"{package_name}.{component_name}"
        return component_name
