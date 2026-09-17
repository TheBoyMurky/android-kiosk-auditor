import subprocess
from unittest.mock import Mock

import pytest

from adb_probe import AdbCommandError, AdbProbe


RESPONSES = {
    ("shell", "getprop", "ro.build.version.release"): "14\n",
    ("shell", "getprop", "ro.build.version.sdk"): "34\n",
    ("shell", "getprop", "ro.debuggable"): "0\n",
    ("shell", "getprop", "ro.secure"): "1\n",
    ("shell", "getprop", "ro.adb.secure"): "1\n",
    ("shell", "settings", "get", "global", "adb_enabled"): "1\n",
    ("shell", "pm", "list", "packages"): "package:z.app\npackage:a.app\n",
    ("shell", "dumpsys", "device_policy"): "Device Policy Manager state:\n  mUserSetupComplete=true\n",
}


def successful_runner(command, **kwargs):
    assert command[:3] == ["adb", "-s", "emulator-5554"]
    assert kwargs["shell"] is False
    assert kwargs["capture_output"] is True
    key = tuple(command[3:])
    return subprocess.CompletedProcess(command, 0, RESPONSES[key], "")


def test_collects_device_snapshot_with_safe_argument_lists():
    snapshot = AdbProbe(serial="emulator-5554", runner=successful_runner).collect()

    assert snapshot.android_version == "14"
    assert snapshot.android_sdk == "34"
    assert snapshot.ro_debuggable == "0"
    assert snapshot.ro_secure == "1"
    assert snapshot.ro_adb_secure == "1"
    assert snapshot.adb_enabled is True
    assert snapshot.installed_packages == ("a.app", "z.app")
    assert "Device Policy Manager state" in snapshot.device_policy
    assert snapshot.to_dict()["installed_packages"] == ["a.app", "z.app"]


def test_adb_failure_has_stderr_context():
    runner = Mock(
        return_value=subprocess.CompletedProcess(["adb"], 1, "", "device offline\n")
    )

    with pytest.raises(AdbCommandError, match="device offline"):
        AdbProbe(runner=runner).collect()


def test_empty_serial_and_invalid_timeout_are_rejected():
    with pytest.raises(ValueError, match="serial"):
        AdbProbe(serial=" ")
    with pytest.raises(ValueError, match="timeout"):
        AdbProbe(timeout=0)
