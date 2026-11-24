#!/usr/bin/env bash

set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: ./scripts/create_tcc_avd.sh

Creates the official Android AVD used by the TCC demonstration.

Required:
  ANDROID_HOME or ANDROID_SDK_ROOT

Optional environment variables:
  TCC_AVD_NAME       Default: Kiosk_TCC_API_35
  TCC_API_LEVEL      Default: 35
  TCC_DEVICE_PROFILE Default: pixel_6
  TCC_IMAGE_TAG      Default: google_apis
EOF
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "Error: unsupported argument: $1" >&2
  echo "Run with --help for usage." >&2
  exit 2
fi

android_sdk_root="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
avd_name="${TCC_AVD_NAME:-Kiosk_TCC_API_35}"
api_level="${TCC_API_LEVEL:-35}"
device_profile="${TCC_DEVICE_PROFILE:-pixel_6}"
image_tag="${TCC_IMAGE_TAG:-google_apis}"
host_arch="$(uname -m)"

if [[ -z "${android_sdk_root}" ]]; then
  echo "Error: set ANDROID_HOME or ANDROID_SDK_ROOT." >&2
  exit 2
fi

case "${host_arch}" in
  x86_64|amd64)
    image_arch="x86_64"
    ;;
  aarch64|arm64)
    image_arch="arm64-v8a"
    ;;
  *)
    echo "Error: unsupported host architecture: ${host_arch}" >&2
    exit 2
    ;;
esac

sdkmanager_path="${android_sdk_root}/cmdline-tools/latest/bin/sdkmanager"
avdmanager_path="${android_sdk_root}/cmdline-tools/latest/bin/avdmanager"
emulator_path="${android_sdk_root}/emulator/emulator"
system_image="system-images;android-${api_level};${image_tag};${image_arch}"

for tool_path in "${sdkmanager_path}" "${avdmanager_path}"; do
  if [[ ! -x "${tool_path}" ]]; then
    echo "Error: Android command-line tool not found: ${tool_path}" >&2
    exit 2
  fi
done

echo "Installing emulator and system image ${system_image}"
"${sdkmanager_path}" --sdk_root="${android_sdk_root}" \
  "emulator" \
  "platform-tools" \
  "platforms;android-${api_level}" \
  "${system_image}"

if [[ ! -x "${emulator_path}" ]]; then
  echo "Error: emulator was not installed at ${emulator_path}" >&2
  exit 3
fi

echo "Checking KVM acceleration"
acceleration_output="$(${emulator_path} -accel-check 2>&1)" || {
  printf '%s\n' "${acceleration_output}" >&2
  echo "Error: Android Emulator could not use hardware acceleration." >&2
  exit 3
}
printf '%s\n' "${acceleration_output}"

if [[ "$(uname -s)" == "Linux" ]]; then
  if [[ ! -r /dev/kvm || ! -w /dev/kvm ]]; then
    echo "Error: the current user needs read/write access to /dev/kvm." >&2
    exit 3
  fi
fi

if "${avdmanager_path}" list avd | grep -Fq "Name: ${avd_name}"; then
  echo "AVD already exists and was preserved: ${avd_name}"
else
  echo "Creating AVD ${avd_name}"
  printf 'no\n' | "${avdmanager_path}" create avd \
    --name "${avd_name}" \
    --package "${system_image}" \
    --device "${device_profile}"
fi

if ! "${avdmanager_path}" list avd | grep -Fq "Name: ${avd_name}"; then
  echo "Error: avdmanager did not create a usable AVD named ${avd_name}." >&2
  exit 4
fi

if ! "${emulator_path}" -list-avds | grep -Fxq "${avd_name}"; then
  echo "Error: Android Emulator does not recognize AVD ${avd_name}." >&2
  exit 4
fi

echo "AVD ready: ${avd_name}"
echo "Start it with:"
echo "  ${emulator_path} @${avd_name} -accel on -gpu auto"
