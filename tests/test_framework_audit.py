import json
import subprocess
from pathlib import Path
from zipfile import ZipFile

from framework_audit import FrameworkAuditRunner


VULNERABLE_MANIFEST = """<manifest xmlns:android="http://schemas.android.com/apk/res/android"
 package="com.example.vulnerable" android:versionCode="1" android:versionName="lab">
 <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="28" />
 <uses-permission android:name="android.permission.CAMERA" />
 <application android:debuggable="true" android:allowBackup="true"
  android:usesCleartextTraffic="true">
  <activity android:name=".MainActivity" android:exported="true">
   <intent-filter><action android:name="android.intent.action.MAIN" />
   <category android:name="android.intent.category.LAUNCHER" /></intent-filter>
  </activity>
  <receiver android:name=".DebugReceiver" android:exported="true" />
 </application>
</manifest>"""

HARDENED_MANIFEST = """<manifest xmlns:android="http://schemas.android.com/apk/res/android"
 package="com.example.hardened" android:versionCode="1" android:versionName="secure">
 <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="35" />
 <application android:debuggable="false" android:allowBackup="false"
  android:usesCleartextTraffic="false">
  <activity android:name=".MainActivity" android:exported="true">
   <intent-filter><action android:name="android.intent.action.MAIN" />
   <category android:name="android.intent.category.LAUNCHER" /></intent-filter>
  </activity>
 </application>
</manifest>"""

ADB_RESPONSES = {
    ("shell", "getprop", "ro.build.version.release"): "15\n",
    ("shell", "getprop", "ro.build.version.sdk"): "35\n",
    ("shell", "getprop", "ro.build.version.security_patch"): "2026-10-05\n",
    ("shell", "getprop", "ro.build.fingerprint"): "google/sdk/test\n",
    ("shell", "getprop", "ro.debuggable"): "0\n",
    ("shell", "getprop", "ro.secure"): "1\n",
    ("shell", "getprop", "ro.adb.secure"): "1\n",
    ("shell", "settings", "get", "global", "adb_enabled"): "1\n",
    ("shell", "pm", "list", "packages"): "package:com.example.vulnerable\npackage:com.example.hardened\n",
    ("shell", "dumpsys", "device_policy"): "Device Owner: none\n",
    ("shell", "dumpsys", "activity", "activities"): "mLockTaskModeState=NONE\n",
}


def _write_apk(path: Path, manifest: str, dex: bytes) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr("AndroidManifest.xml", manifest)
        archive.writestr("classes.dex", dex)


def _adb_runner(command, **kwargs):
    key = tuple(command[3:])
    return subprocess.CompletedProcess(command, 0, ADB_RESPONSES[key], "")


def test_framework_audit_records_all_parameters_and_evidence(tmp_path):
    vulnerable = tmp_path / "vulnerable.apk"
    hardened = tmp_path / "hardened.apk"
    output = tmp_path / "reports"
    _write_apk(vulnerable, VULNERABLE_MANIFEST, b"http://10.0.2.2 password admin123")
    _write_apk(hardened, HARDENED_MANIFEST, b"https://example.com")

    report = FrameworkAuditRunner(
        rules_path=Path("rules/kiosk_rules.yaml"),
        serial="emulator-5556",
        vulnerable_apk=vulnerable,
        hardened_apk=hardened,
        output_dir=output,
        base_dir=tmp_path,
        adb_runner=_adb_runner,
    ).run()

    records = {item["parameter"]: item for item in report["parameter_records"]}
    assert list(records) == [f"P{number:02d}" for number in range(1, 17)]
    assert records["P01"]["status"] == "nao_avaliado"
    assert records["P01"]["application_evaluations"]["vulnerable"]["status"] == "nao_conforme"
    assert records["P01"]["application_evaluations"]["hardened"]["status"] == "conforme"
    assert records["P01"]["scenario_results"]["vulnerable"]["status"] == "nao_conforme"
    assert records["P01"]["scenario_results"]["hardened"]["status"] == "conforme"
    assert records["P05"]["scenario_results"]["vulnerable"]["indicator_observed"] is True
    assert records["P03"]["coverage"] == "automatic"
    assert records["P03"]["scenario_results"]["vulnerable"]["status"] == "nao_conforme"
    assert records["P03"]["scenario_results"]["hardened"]["status"] == "conforme"
    assert records["P04"]["coverage"] == "automatic"
    assert records["P04"]["scenario_results"]["vulnerable"]["status"] == "nao_conforme"
    assert records["P04"]["scenario_results"]["hardened"]["status"] == "conforme"
    assert records["P05"]["coverage"] == "partial"
    assert records["P05"]["scenario_results"]["vulnerable"]["status"] == "nao_conforme"
    assert records["P05"]["scenario_results"]["hardened"]["status"] == "conforme"
    assert records["P08"]["scenario_results"]["device"]["evidence_collected"] is True
    assert records["P09"]["evidence"]["adb_enabled"] is True
    assert records["P10"]["evidence"]["lock_task_lines"] == [
        "mLockTaskModeState=NONE"
    ]
    assert records["P12"]["coverage"] == "manual"
    assert report["summary"]["status_counts"]["nao_avaliado"] == 16
    assert report["summary"]["scenario_status_counts"]["vulnerable"]["nao_conforme"] == 4
    assert report["summary"]["scenario_status_counts"]["hardened"]["conforme"] == 4
    assert report["summary"]["parameters_with_evidence"] == 10

    expected_files = {
        "vulnerable-apk-report.json",
        "hardened-apk-report.json",
        "apk-comparison-report.json",
        "apk-comparison-summary.md",
        "adb-device-snapshot.json",
        "framework-audit-report.json",
        "framework-audit-summary.md",
    }
    assert expected_files == {path.name for path in output.iterdir()}
    saved = json.loads((output / "framework-audit-report.json").read_text())
    assert saved["device"]["security_patch"] == "2026-10-05"
    markdown = (output / "framework-audit-summary.md").read_text()
    assert "P01-P16" in markdown
    assert "nao_conforme (indicador encontrado)" in markdown
    assert "10 de 16 parâmetros" in markdown
    table_lines = [line for line in markdown.splitlines() if line.startswith("|")]
    pipe_positions = [
        [index for index, character in enumerate(line) if character == "|"]
        for line in table_lines
    ]
    assert pipe_positions
    assert all(positions == pipe_positions[0] for positions in pipe_positions)
