# Relatório de comparação estática dos APKs

Gerado em: 2026-11-24T02:05:00.600846+00:00

## Artefatos

- VulnerableKioskApp: `vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk` (`sha256: 9581314667a964eb575a4da1c156ef7d4975023ef49ed7a0215328ff390f6ad8`)
- HardenedKioskApp: `hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk` (`sha256: 517d50c0d63bfeefc5fb1cf2815f87687d58b7e2af6e36b07343d2c80c44a833`)

## Relatórios

- `reports/vulnerable-apk-report.json`
- `reports/hardened-apk-report.json`
- `reports/apk-comparison-report.json`

## Resultados das regras implementadas

- Achados no VulnerableKioskApp: 10
- Achados no HardenedKioskApp: 0

As contagens incluem somente as regras implementadas pelo `ApkAnalyzer` atual.
Ausência de achados não significa que a aplicação ou o dispositivo estejam
integralmente seguros.

## Estados de avaliação

- VulnerableKioskApp: `{"conforme": 0, "nao_conforme": 4, "nao_avaliado": 1, "nao_aplicavel": 0}`
- HardenedKioskApp: `{"conforme": 4, "nao_conforme": 0, "nao_avaliado": 1, "nao_aplicavel": 0}`

Somente regras conclusivas podem atribuir `conforme` automaticamente. Regras
indicativas permanecem `nao_avaliado` até a revisão das evidências contextuais.
`nao_aplicavel` sempre exige justificativa humana documentada.

## Escopo

Esta comparação cobre somente verificações estáticas implementadas e indicadores de strings DEX. Controles de dispositivo, kiosk, TLS, físicos, dinâmicos e operacionais permanecem não avaliados nesta execução.
