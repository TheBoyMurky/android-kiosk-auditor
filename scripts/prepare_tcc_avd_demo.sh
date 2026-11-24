#!/usr/bin/env bash

set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: ./scripts/prepare_tcc_avd_demo.sh [--rebuild]

Starts the TCC AVD, installs both reference applications, and saves a snapshot.

Required:
  ANDROID_HOME or ANDROID_SDK_ROOT

Optional environment variables:
  TCC_AVD_NAME      Default: Kiosk_TCC_API_35
  TCC_EMULATOR_PORT Default: 5556
  TCC_SNAPSHOT_NAME Default: TCC-pronto
  PYTHON_COMMAND    Default: python
EOF
  exit 0
fi

if [[ $# -gt 1 || ( $# -eq 1 && "${1}" != "--rebuild" ) ]]; then
  echo "Error: expected no argument or --rebuild." >&2
  echo "Run with --help for usage." >&2
  exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
android_sdk_root="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
avd_name="${TCC_AVD_NAME:-Kiosk_TCC_API_35}"
emulator_port="${TCC_EMULATOR_PORT:-5556}"
snapshot_name="${TCC_SNAPSHOT_NAME:-TCC-pronto}"
rebuild="${1:-}"

if [[ -n "${PYTHON_COMMAND:-}" ]]; then
  python_command="${PYTHON_COMMAND}"
elif [[ -x "${project_root}/.venv/bin/python" ]]; then
  python_command="${project_root}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  python_command="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  python_command="$(command -v python)"
else
  echo "Error: Python was not found. Create .venv or set PYTHON_COMMAND." >&2
  exit 2
fi

if ! "${python_command}" -c 'import androguard, yaml' >/dev/null 2>&1; then
  echo "Error: ${python_command} does not have the project dependencies." >&2
  echo "Create .venv and run: .venv/bin/pip install -e '.[dev]'" >&2
  exit 2
fi

if [[ ! "${emulator_port}" =~ ^[0-9]+$ ]] \
  || (( emulator_port < 5554 || emulator_port > 5682 || emulator_port % 2 != 0 )); then
  echo "Error: TCC_EMULATOR_PORT must be an even number from 5554 to 5682." >&2
  exit 2
fi

if [[ -z "${android_sdk_root}" ]]; then
  echo "Error: set ANDROID_HOME or ANDROID_SDK_ROOT." >&2
  exit 2
fi

emulator_path="${android_sdk_root}/emulator/emulator"
adb_path="${android_sdk_root}/platform-tools/adb"
avdmanager_path="${android_sdk_root}/cmdline-tools/latest/bin/avdmanager"
serial="emulator-${emulator_port}"
vulnerable_apk="${project_root}/vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk"
hardened_apk="${project_root}/hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk"

for tool_path in "${emulator_path}" "${adb_path}" "${avdmanager_path}"; do
  if [[ ! -x "${tool_path}" ]]; then
    echo "Error: required Android tool not found: ${tool_path}" >&2
    exit 2
  fi
done

if ! "${avdmanager_path}" list avd | grep -Fq "Name: ${avd_name}"; then
  echo "Error: AVD ${avd_name} does not exist. Run create_tcc_avd.sh first." >&2
  exit 2
fi

if [[ "${rebuild}" == "--rebuild" || ! -f "${vulnerable_apk}" || ! -f "${hardened_apk}" ]]; then
  "${project_root}/scripts/build_reference_apks.sh"
fi

if ! "${adb_path}" devices | awk 'NR > 1 {print $1}' | grep -Fxq "${serial}"; then
  log_path="${project_root}/.tcc-emulator.log"
  echo "Starting ${avd_name} as ${serial}"
  "${emulator_path}" @"${avd_name}" \
    -port "${emulator_port}" \
    -accel on \
    -gpu auto \
    -no-boot-anim \
    >"${log_path}" 2>&1 &
  echo $! >"${project_root}/.tcc-emulator.pid"
fi

echo "Waiting for Android to finish booting"
"${adb_path}" -s "${serial}" wait-for-device
boot_completed=""
for _ in $(seq 1 120); do
  boot_completed="$(${adb_path} -s "${serial}" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
  if [[ "${boot_completed}" == "1" ]]; then
    break
  fi
  sleep 2
done

if [[ "${boot_completed}" != "1" ]]; then
  echo "Error: emulator did not finish booting within four minutes." >&2
  exit 3
fi

echo "Installing reference applications"
"${adb_path}" -s "${serial}" install -r "${vulnerable_apk}"
"${adb_path}" -s "${serial}" install -r "${hardened_apk}"

echo "Regenerating APK evidence"
(
  cd "${project_root}"
  "${python_command}" -m apk_analyzer.cli \
    --vulnerable "${vulnerable_apk}" \
    --hardened "${hardened_apk}"
)

"${adb_path}" -s "${serial}" shell am force-stop com.example.vulnerablekiosk
"${adb_path}" -s "${serial}" shell am force-stop com.example.hardenedkiosk
"${adb_path}" -s "${serial}" shell input keyevent HOME

echo "Saving snapshot ${snapshot_name}"
"${adb_path}" -s "${serial}" emu avd snapshot save "${snapshot_name}"

echo "Demonstration environment ready."
echo "AVD: ${avd_name}"
echo "Serial: ${serial}"
echo "Snapshot: ${snapshot_name}"
echo "Open VulnerableKioskApp:"
echo "  ${adb_path} -s ${serial} shell am start -n com.example.vulnerablekiosk/.MainActivity"
echo "Open HardenedKioskApp:"
echo "  ${adb_path} -s ${serial} shell am start -n com.example.hardenedkiosk/.MainActivity"
