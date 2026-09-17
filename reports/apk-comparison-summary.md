# APK Static Comparison Report

Generated at: 2026-09-10T23:28:28.903301+00:00

## Targets

- VulnerableKioskApp: `vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk` / `com.example.vulnerablekiosk`
- HardenedKioskApp: `hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk` / `com.example.hardenedkiosk`

## Reports

- `reports/vulnerable-apk-report.json`
- `reports/hardened-apk-report.json`
- `reports/apk-comparison-report.json`

## Main Differences

- Vulnerable findings: 13
- Hardened findings: 0
- Vulnerable permissions: `android.permission.INTERNET, android.permission.CAMERA, android.permission.ACCESS_FINE_LOCATION, android.permission.RECORD_AUDIO, android.permission.READ_PHONE_STATE, android.permission.READ_EXTERNAL_STORAGE, android.permission.WRITE_EXTERNAL_STORAGE, android.permission.RECEIVE_BOOT_COMPLETED`
- Hardened permissions: `none`
- Vulnerable cleartext: `True`
- Hardened cleartext: `False`
- Vulnerable backup: `True`
- Hardened backup: `False`

## Layer Summary

- Rede e Comunicação: VulnerableKioskApp embeds HTTP endpoints and allows cleartext. HardenedKioskApp embeds only HTTPS demonstration endpoints and blocks cleartext traffic.
- Aplicação: VulnerableKioskApp contains hardcoded test credentials/tokens and dangerous capability requests. HardenedKioskApp has no detected dangerous permissions and no detected HTTP or prohibited test credential strings.
- Segurança Física / Modo Kiosk: No ADB/device-policy collection was performed because this run was APK-only. Device posture requires a connected emulator/device.

## Tooling Note

`adb_probe/probe.py` was found, but it was not executed because this run is APK-only. The existing probe also collects device-level state only; it does not currently accept APK path, package name, or output path arguments.
