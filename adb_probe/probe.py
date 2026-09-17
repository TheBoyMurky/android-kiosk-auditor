"""Collect security-relevant Android device state through ADB."""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


class AdbCommandError(RuntimeError):
    """Raised when ADB cannot execute or returns an unsuccessful status."""


@dataclass(frozen=True, slots=True)
class AdbSnapshot:
    serial: str | None
    android_version: str
    android_sdk: str
    ro_debuggable: str
    ro_secure: str
    ro_adb_secure: str
    adb_enabled: bool | None
    installed_packages: tuple[str, ...]
    device_policy: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["installed_packages"] = list(self.installed_packages)
        return data


RunCommand = Callable[..., subprocess.CompletedProcess[str]]


class AdbProbe:
    """Execute a fixed set of read-only ADB commands without a shell."""

    def __init__(
        self,
        serial: str | None = None,
        *,
        adb_path: str | Path = "adb",
        timeout: float = 30.0,
        runner: RunCommand = subprocess.run,
    ) -> None:
        if serial is not None and not serial.strip():
            raise ValueError("serial must not be empty")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        self.serial = serial
        self.adb_path = str(adb_path)
        self.timeout = timeout
        self._runner = runner

    def collect(self) -> AdbSnapshot:
        """Collect device properties, packages, and device-owner policy state."""
        return AdbSnapshot(
            serial=self.serial,
            android_version=self._getprop("ro.build.version.release"),
            android_sdk=self._getprop("ro.build.version.sdk"),
            ro_debuggable=self._getprop("ro.debuggable"),
            ro_secure=self._getprop("ro.secure"),
            ro_adb_secure=self._getprop("ro.adb.secure"),
            adb_enabled=self._parse_setting(
                self._shell("settings", "get", "global", "adb_enabled")
            ),
            installed_packages=self._parse_packages(
                self._shell("pm", "list", "packages")
            ),
            device_policy=self._shell("dumpsys", "device_policy"),
        )

    def _getprop(self, name: str) -> str:
        return self._shell("getprop", name)

    def _shell(self, *arguments: str) -> str:
        return self._execute(("shell", *arguments))

    def _execute(self, arguments: Sequence[str]) -> str:
        command = [self.adb_path]
        if self.serial is not None:
            command.extend(("-s", self.serial))
        command.extend(arguments)

        try:
            result = self._runner(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
                shell=False,
            )
        except FileNotFoundError as exc:
            raise AdbCommandError(f"ADB executable not found: {self.adb_path}") from exc
        except subprocess.TimeoutExpired as exc:
            raise AdbCommandError(
                f"ADB command timed out after {self.timeout:g}s: {self._display(command)}"
            ) from exc
        except OSError as exc:
            raise AdbCommandError(
                f"could not execute ADB command {self._display(command)}: {exc}"
            ) from exc

        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown ADB error"
            raise AdbCommandError(
                f"ADB command failed ({result.returncode}): "
                f"{self._display(command)}: {detail}"
            )
        return result.stdout.strip()

    @staticmethod
    def _parse_setting(value: str) -> bool | None:
        normalized = value.strip().lower()
        if normalized == "1":
            return True
        if normalized == "0":
            return False
        return None

    @staticmethod
    def _parse_packages(output: str) -> tuple[str, ...]:
        packages = {
            line.removeprefix("package:").strip()
            for line in output.splitlines()
            if line.strip().startswith("package:")
        }
        packages.discard("")
        return tuple(sorted(packages))

    @staticmethod
    def _display(command: Sequence[str]) -> str:
        # Used only for diagnostics; it is never passed to a shell.
        return " ".join(command)
