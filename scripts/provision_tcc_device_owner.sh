#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
serial="${TCC_DEVICE:-emulator-5556}"
package_name="com.example.hardenedkiosk"
admin_component="${package_name}/.KioskDeviceAdminReceiver"
android_sdk_root="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
adb_path="${android_sdk_root}/platform-tools/adb"

if [[ ! -x "${adb_path}" ]]; then
  adb_path="$(command -v adb || true)"
fi
if [[ -z "${adb_path}" || ! -x "${adb_path}" ]]; then
  echo "Error: adb was not found." >&2
  exit 2
fi

if ! "${adb_path}" devices | awk 'NR > 1 {print $1}' | grep -Fxq "${serial}"; then
  echo "Error: authorized emulator not found: ${serial}" >&2
  exit 3
fi

apk_path="${project_root}/hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk"
if [[ ! -f "${apk_path}" ]]; then
  echo "Error: hardened APK not found. Run build_reference_apks.sh first." >&2
  exit 3
fi

echo "Installing HardenedKioskApp"
"${adb_path}" -s "${serial}" install -r "${apk_path}"

current_owner="$("${adb_path}" -s "${serial}" shell dpm list-owners 2>/dev/null || true)"
if grep -Fq "${admin_component}" <<<"${current_owner}"; then
  echo "Device Owner already configured: ${admin_component}"
else
  echo "Provisioning Device Owner: ${admin_component}"
  if ! "${adb_path}" -s "${serial}" shell dpm set-device-owner "${admin_component}"; then
    echo "Error: Android refused Device Owner provisioning." >&2
    echo "Use a clean AVD without accounts, reinstall the APK, and run this script again." >&2
    exit 4
  fi
fi

"${adb_path}" -s "${serial}" shell am force-stop "${package_name}"
"${adb_path}" -s "${serial}" shell am start \
  -n "${package_name}/.MainActivity"

echo "Device Owner ready. Tap 'Ativar Kiosk Demonstrativo' in the app."
