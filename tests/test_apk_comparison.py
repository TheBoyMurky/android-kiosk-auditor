import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from apk_analyzer import ApkAnalyzer
from apk_analyzer.comparison import (
    ComparisonTarget,
    analyze_target,
    build_comparison,
    write_json,
    write_summary,
)


VULNERABLE_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.vulnerable" android:versionCode="1" android:versionName="lab">
    <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="28" />
    <uses-permission android:name="android.permission.CAMERA" />
    <application android:debuggable="true" android:allowBackup="true"
        android:usesCleartextTraffic="true">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <receiver android:name=".DebugReceiver" android:exported="true" />
    </application>
</manifest>
"""

HARDENED_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.hardened" android:versionCode="1" android:versionName="secure">
    <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="35" />
    <application android:debuggable="false" android:allowBackup="false"
        android:usesCleartextTraffic="false"
        android:networkSecurityConfig="@xml/network_security_config">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""


def _write_apk(path: Path, manifest: str, dex_payload: bytes) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr("AndroidManifest.xml", manifest)
        archive.writestr("classes.dex", dex_payload)


def test_reproducible_comparison_contains_hashes_and_scope(tmp_path):
    vulnerable_apk = tmp_path / "vulnerable.apk"
    hardened_apk = tmp_path / "hardened.apk"
    _write_apk(
        vulnerable_apk,
        VULNERABLE_MANIFEST,
        b"header http://10.0.2.2/mock password api_key footer",
    )
    _write_apk(
        hardened_apk,
        HARDENED_MANIFEST,
        b"header https://example.com/secure footer",
    )

    analyzer = ApkAnalyzer("rules/kiosk_rules.yaml")
    vulnerable = analyze_target(
        analyzer,
        ComparisonTarget("VulnerableKioskApp", vulnerable_apk),
        base_dir=tmp_path,
    )
    hardened = analyze_target(
        analyzer,
        ComparisonTarget("HardenedKioskApp", hardened_apk),
        base_dir=tmp_path,
    )
    comparison = build_comparison(vulnerable, hardened)

    expected_hash = hashlib.sha256(vulnerable_apk.read_bytes()).hexdigest()
    assert vulnerable["target"]["sha256"] == expected_hash
    assert vulnerable["target"]["apk_path"] == "vulnerable.apk"
    assert vulnerable["dex_indicators"]["urls"] == ["http://10.0.2.2/mock"]
    assert vulnerable["dex_indicators"]["credential_markers"] == [
        "api_key",
        "password",
    ]
    assert hardened["summary"]["finding_count"] == 0
    vulnerable_evaluations = {
        item["rule_id"]: item for item in vulnerable["evaluations"]
    }
    hardened_evaluations = {
        item["rule_id"]: item for item in hardened["evaluations"]
    }
    assert vulnerable_evaluations["APK-001"]["status"] == "nao_conforme"
    assert vulnerable_evaluations["APK-002"]["status"] == "nao_avaliado"
    assert vulnerable_evaluations["APK-002"]["indicator_observed"] is True
    assert hardened_evaluations["APK-001"]["status"] == "conforme"
    assert hardened_evaluations["KIOSK-002"]["status"] == "nao_avaliado"
    assert hardened["summary"]["evaluation_status_counts"] == {
        "conforme": 1,
        "nao_conforme": 0,
        "nao_avaliado": 3,
        "nao_aplicavel": 0,
    }
    assert comparison["comparison"]["cleartext_configuration"] == {
        "vulnerable": True,
        "hardened": False,
    }
    assert "não avaliados" in comparison["scope_note"]


def test_report_writers_create_valid_documents(tmp_path):
    comparison = {
        "generated_at": "2026-01-01T00:00:00+00:00",
        "targets": {
            "vulnerable": {"apk_path": "v.apk", "sha256": "a" * 64},
            "hardened": {"apk_path": "h.apk", "sha256": "b" * 64},
        },
        "comparison": {
            "finding_count": {"vulnerable": 2, "hardened": 0},
            "evaluation_status_counts": {
                "vulnerable": {"nao_conforme": 1, "nao_avaliado": 3},
                "hardened": {"conforme": 1, "nao_avaliado": 3},
            },
        },
        "scope_note": "Static scope only.",
    }
    json_path = tmp_path / "comparison.json"
    summary_path = tmp_path / "summary.md"

    write_json(json_path, comparison)
    write_summary(summary_path, comparison)

    assert json.loads(json_path.read_text())["scope_note"] == "Static scope only."
    summary = summary_path.read_text()
    assert "sha256" in summary
    assert "Ausência de achados não significa" in summary
