#!/usr/bin/env bash

# This file must be sourced so activation persists in the current shell.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "Error: this script must be sourced:" >&2
  echo "  source scripts/activate_venv.sh" >&2
  exit 2
fi

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv_path="${project_root}/.venv"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not available on PATH." >&2
  return 2
fi

if [[ ! -x "${venv_path}/bin/python" ]]; then
  echo "Creating Python virtual environment in ${venv_path}"
  python3 -m venv "${venv_path}" || return 2
fi

# shellcheck disable=SC1091
source "${venv_path}/bin/activate"

if ! python -c 'import androguard, framework_audit, pytest, yaml' >/dev/null 2>&1; then
  echo "Installing project development dependencies"
  (
    cd "${project_root}" || exit 2
    python -m pip install -e '.[dev]'
  ) || return 2
fi

echo "Virtual environment active: ${VIRTUAL_ENV}"
python --version
