from xml.etree import ElementTree
from zipfile import ZipFile

from apk_analyzer import ApkAnalyzer


MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.kiosk">
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:debuggable="true" android:allowBackup="true">
        <activity android:name=".MainActivity" android:exported="true" />
        <service android:name="PrivateService" android:exported="false" />
        <receiver android:name="BootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
"""


def test_manifest_checks_map_to_rules():
    analyzer = ApkAnalyzer("rules/kiosk_rules.yaml")
    findings = analyzer.analyze_manifest(ElementTree.fromstring(MANIFEST))

    assert [finding.rule_id for finding in findings] == [
        "APK-001",
        "APK-002",
        "APK-003",
        "KIOSK-002",
        "KIOSK-002",
    ]
    assert findings[2].evidence["permission"] == "android.permission.CAMERA"
    assert findings[3].evidence["component_name"] == "com.example.kiosk.MainActivity"
    assert findings[4].evidence["has_intent_filter"] is True


def test_plain_xml_manifest_is_extracted_from_apk(tmp_path):
    apk = tmp_path / "sample.apk"
    with ZipFile(apk, "w") as archive:
        archive.writestr("AndroidManifest.xml", MANIFEST)

    findings = ApkAnalyzer("rules/kiosk_rules.yaml").analyze(apk)

    assert len(findings) == 5
    assert all(finding.source == "apk_analyzer:sample.apk" for finding in findings)


def test_allow_backup_defaults_to_enabled():
    manifest = ElementTree.fromstring(
        """<manifest xmlns:android="http://schemas.android.com/apk/res/android">
        <application android:debuggable="false" android:allowBackup="false" />
        </manifest>"""
    )
    findings = ApkAnalyzer("rules/kiosk_rules.yaml").analyze_manifest(manifest)
    assert findings == []
