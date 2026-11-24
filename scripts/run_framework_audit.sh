#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
serial="${TCC_DEVICE:-emulator-5556}"

if [[ -x "${project_root}/.venv/bin/python" ]]; then
  python_command="${project_root}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  python_command="$(command -v python3)"
else
  echo "Error: activate or create the project virtual environment first." >&2
  exit 2
fi

if ! "${python_command}" -c 'import androguard, framework_audit, yaml' >/dev/null 2>&1; then
  echo "Error: project dependencies are missing. Run:" >&2
  echo "  source scripts/activate_venv.sh" >&2
  exit 2
fi

adb_path="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}/platform-tools/adb"
if [[ ! -x "${adb_path}" ]]; then
  adb_path="$(command -v adb || true)"
fi
if [[ -z "${adb_path}" || ! -x "${adb_path}" ]]; then
  echo "Error: adb was not found." >&2
  exit 2
fi

if ! "${adb_path}" devices | awk 'NR > 1 {print $1}' | grep -Fxq "${serial}"; then
  echo "Error: authorized device not found: ${serial}" >&2
  exit 3
fi

vulnerable_apk="${project_root}/vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk"
hardened_apk="${project_root}/hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk"
if [[ ! -f "${vulnerable_apk}" || ! -f "${hardened_apk}" ]]; then
  echo "Error: reference APKs are missing. Run build_reference_apks.sh first." >&2
  exit 3
fi

cd "${project_root}"
"${python_command}" -m framework_audit.cli \
  --serial "${serial}" \
  --adb "${adb_path}" \
  --vulnerable "${vulnerable_apk}" \
  --hardened "${hardened_apk}" \
  --output-dir reports/framework-audit

echo "Framework audit completed: reports/framework-audit/framework-audit-summary.md"
