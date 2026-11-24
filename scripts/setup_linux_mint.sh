#!/usr/bin/env bash

set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: ./scripts/setup_linux_mint.sh

Installs and validates the dependencies required by android-kiosk-auditor on
Linux Mint or another Ubuntu-based distribution.

Optional environment variables:
  ANDROID_HOME          SDK destination (default: $HOME/Android/Sdk)
  TCC_AVD_NAME          AVD name (default: Kiosk_TCC_API_35)
  TCC_SKIP_APT=1        Skip system package installation
  TCC_SKIP_AVD=1        Skip AVD creation
  TCC_SKIP_VALIDATION=1 Skip project tests and Android builds
EOF
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "Error: unsupported argument: $1" >&2
  echo "Run with --help for usage." >&2
  exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
android_sdk_root="${ANDROID_HOME:-${HOME}/Android/Sdk}"
login_user="$(id -un)"
command_tools_version="15859902"
command_tools_archive="commandlinetools-linux-${command_tools_version}_latest.zip"
command_tools_url="https://dl.google.com/android/repository/${command_tools_archive}"
command_tools_sha256="4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583"
profile_path="${HOME}/.profile"
profile_marker="# android-kiosk-auditor Android SDK"

if [[ "$(uname -m)" != "x86_64" ]]; then
  echo "Error: this setup currently supports x86_64 Linux hosts only." >&2
  exit 2
fi

if [[ ! -r /etc/os-release ]]; then
  echo "Error: /etc/os-release was not found; Linux Mint/Ubuntu is required." >&2
  exit 2
fi

# shellcheck disable=SC1091
source /etc/os-release
distribution_id="${ID:-unknown}"
distribution_like="${ID_LIKE:-}"
if [[ "${distribution_id}" != "linuxmint" \
      && "${distribution_id}" != "ubuntu" \
      && " ${distribution_like} " != *" ubuntu "* \
      && " ${distribution_like} " != *" debian "* ]]; then
  echo "Error: unsupported distribution: ${distribution_id}." >&2
  exit 2
fi

if [[ "${TCC_SKIP_APT:-0}" != "1" ]]; then
  echo "Installing Linux packages"
  sudo apt-get update
  sudo apt-get install -y \
    bridge-utils \
    ca-certificates \
    cpu-checker \
    curl \
    git \
    libvirt-clients \
    libvirt-daemon-system \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    python3-venv \
    qemu-kvm \
    unzip \
    zip

  sudo usermod -aG kvm,libvirt "${login_user}"
fi

mkdir -p "${android_sdk_root}/cmdline-tools"
sdkmanager_path="${android_sdk_root}/cmdline-tools/latest/bin/sdkmanager"

if [[ ! -x "${sdkmanager_path}" ]]; then
  echo "The Android SDK license must be reviewed and accepted by you."
  read -r -p "Have you reviewed and accepted the Android SDK terms? [y/N] " accepted
  case "${accepted}" in
    y|Y|yes|YES) ;;
    *)
      echo "Installation stopped before downloading the Android tools."
      echo "Terms: https://developer.android.com/studio/terms"
      exit 3
      ;;
  esac

  temporary_dir="$(mktemp -d /tmp/android-kiosk-setup.XXXXXX)"
  trap 'rm -rf -- "${temporary_dir}"' EXIT
  archive_path="${temporary_dir}/${command_tools_archive}"

  echo "Downloading Android Command-line Tools ${command_tools_version}"
  curl --fail --location --proto '=https' --tlsv1.2 \
    "${command_tools_url}" --output "${archive_path}"
  printf '%s  %s\n' "${command_tools_sha256}" "${archive_path}" | sha256sum --check

  unzip -q "${archive_path}" -d "${temporary_dir}/extracted"
  mkdir -p "${android_sdk_root}/cmdline-tools/latest"
  cp -a "${temporary_dir}/extracted/cmdline-tools/." \
    "${android_sdk_root}/cmdline-tools/latest/"
fi

export ANDROID_HOME="${android_sdk_root}"
export PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools:${ANDROID_HOME}/emulator:${PATH}"

if ! grep -Fq "${profile_marker}" "${profile_path}" 2>/dev/null; then
  echo "Writing Android SDK environment to ${profile_path}"
  {
    printf '\n%s\n' "${profile_marker}"
    printf 'export ANDROID_HOME="%s"\n' "${android_sdk_root}"
    printf 'export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"\n'
  } >>"${profile_path}"
fi

echo "Review and accept the Android package licenses when prompted"
"${sdkmanager_path}" --sdk_root="${android_sdk_root}" --licenses

echo "Installing Android SDK packages"
"${sdkmanager_path}" --sdk_root="${android_sdk_root}" \
  "build-tools;35.0.0" \
  "emulator" \
  "platform-tools" \
  "platforms;android-35" \
  "system-images;android-35;google_apis;x86_64"

echo "Preparing the Python environment"
# shellcheck disable=SC1091
source "${project_root}/scripts/activate_venv.sh"
python -m pip install -r "${project_root}/mock-server/requirements.txt"

if [[ "${TCC_SKIP_VALIDATION:-0}" != "1" ]]; then
  echo "Validating tests, APK builds, and reports"
  "${project_root}/scripts/validate_project.sh"
fi

avd_deferred=0
if [[ "${TCC_SKIP_AVD:-0}" != "1" ]]; then
  if [[ -r /dev/kvm && -w /dev/kvm ]]; then
    "${project_root}/scripts/create_tcc_avd.sh"
  else
    avd_deferred=1
  fi
fi

echo
echo "Linux Mint setup completed."
echo "Android SDK: ${android_sdk_root}"
echo "Python environment: ${project_root}/.venv"
if (( avd_deferred == 1 )); then
  echo "KVM group membership requires a new login session."
  echo "After logging out and in again, run:"
  echo "  cd ${project_root}"
  echo "  ./scripts/create_tcc_avd.sh"
fi
echo "Next step: ./scripts/prepare_tcc_avd_demo.sh --rebuild"
