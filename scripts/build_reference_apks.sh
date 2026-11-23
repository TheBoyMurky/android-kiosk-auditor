#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
android_sdk_root="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"

if [[ -z "${android_sdk_root}" ]]; then
  echo "Error: set ANDROID_HOME or ANDROID_SDK_ROOT to an Android SDK." >&2
  exit 2
fi

if [[ ! -f "${android_sdk_root}/platforms/android-35/android.jar" ]]; then
  echo "Error: Android SDK Platform 35 is not installed in ${android_sdk_root}." >&2
  exit 2
fi

if ! command -v java >/dev/null 2>&1; then
  echo "Error: Java is not available on PATH." >&2
  exit 2
fi

java_major="$(java -version 2>&1 | sed -n '1s/.*version "\([0-9][0-9]*\).*/\1/p')"
if [[ -z "${java_major}" || "${java_major}" -lt 17 ]]; then
  echo "Error: JDK 17 or newer is required." >&2
  exit 2
fi

echo "Building VulnerableKioskApp with JDK ${java_major} and SDK ${android_sdk_root}"
(
  cd "${project_root}/vulnerable-kiosk-app"
  ./gradlew assembleDebug --no-daemon
)

echo "Building HardenedKioskApp with JDK ${java_major} and SDK ${android_sdk_root}"
(
  cd "${project_root}/hardened-kiosk-app"
  ./gradlew assembleDebug --no-daemon
)

vulnerable_apk="${project_root}/vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk"
hardened_apk="${project_root}/hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk"

for apk_path in "${vulnerable_apk}" "${hardened_apk}"; do
  if [[ ! -f "${apk_path}" ]]; then
    echo "Error: expected APK was not generated: ${apk_path}" >&2
    exit 3
  fi
done

echo "Reference APKs generated successfully:"
echo "  ${vulnerable_apk}"
echo "  ${hardened_apk}"
