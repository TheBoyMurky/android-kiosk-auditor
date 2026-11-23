# Relatório de comparação estática dos APKs

Gerado em: 2026-11-23T00:03:33.117014+00:00

## Artefatos

- VulnerableKioskApp: `vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk` (`sha256: 88dccd991a6b0e12f1f27ee975f339265068e673be1bcbb085354c47d7a3d812`)
- HardenedKioskApp: `hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk` (`sha256: f09a7c36a8ba4aa49bbc84676ac779b45903db8878bb72fc80dbcd633b2c77dc`)

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

- VulnerableKioskApp: `{"conforme": 0, "nao_conforme": 1, "nao_avaliado": 3, "nao_aplicavel": 0}`
- HardenedKioskApp: `{"conforme": 1, "nao_conforme": 0, "nao_avaliado": 3, "nao_aplicavel": 0}`

Somente regras conclusivas podem atribuir `conforme` automaticamente. Regras
indicativas permanecem `nao_avaliado` até a revisão das evidências contextuais.
`nao_aplicavel` sempre exige justificativa humana documentada.

## Escopo

Esta comparação cobre somente verificações estáticas implementadas e indicadores de strings DEX. Controles de dispositivo, kiosk, TLS, físicos, dinâmicos e operacionais permanecem não avaliados nesta execução.
