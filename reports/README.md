# Evidências da demonstração

Este diretório contém as evidências estáticas canônicas usadas na demonstração
dos aplicativos de referência:

- `vulnerable-apk-report.json`;
- `hardened-apk-report.json`;
- `apk-comparison-report.json`;
- `apk-comparison-summary.md`.

Os relatórios devem ser regenerados pelo comando `android-kiosk-compare`
documentado no README da raiz. A geração registra o SHA-256 de cada APK e usa
somente caminhos relativos quando o artefato está dentro do repositório.

Os arquivos registram apenas o alcance das regras estáticas implementadas. Eles
não representam certificação, conformidade integral com P01-P16 ou avaliação de
controles dinâmicos, físicos, operacionais e de dispositivo.
