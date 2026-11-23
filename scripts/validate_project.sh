#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_command="${PYTHON_COMMAND:-python}"

cd "${project_root}"

echo "1/4 Running Python tests"
"${python_command}" -m pytest -q

echo "2/4 Building reference APKs"
./scripts/build_reference_apks.sh

echo "3/4 Regenerating static evidence"
"${python_command}" -m apk_analyzer.cli \
  --vulnerable vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk \
  --hardened hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk

echo "4/4 Validating JSON reports"
for report_path in \
  reports/vulnerable-apk-report.json \
  reports/hardened-apk-report.json \
  reports/apk-comparison-report.json
do
  "${python_command}" -m json.tool "${report_path}" >/dev/null
done

echo "Validation completed successfully."
echo "Summary: reports/apk-comparison-summary.md"
