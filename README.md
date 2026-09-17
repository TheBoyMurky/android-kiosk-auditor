# android-kiosk-auditor

Base extensível para auditorias de aplicações Android em modo kiosk. A versão
atual fornece o modelo canônico de achados, regras YAML, relatórios JSON e uma
análise básica do `AndroidManifest.xml` contido em APKs.

## Estrutura

- `apk_analyzer`: extrai o manifesto e verifica `debuggable`, backup, permissões
  perigosas e componentes exportados.
- `adb_probe`: coleta propriedades e estado do dispositivo por comandos ADB
  somente leitura, executados sem shell.
- `core`: modelos, regras e relatórios compartilhados.
- `vulnerable-kiosk-app`: app Android propositalmente vulnerável para testes
  acadêmicos da análise estática de APK e da coleta via ADB.
- `hardened-kiosk-app`: app Android demonstrativo com hardening básico para
  comparação acadêmica com o alvo vulnerável.
- `mock-server`: servidor Flask local em HTTP para demonstrar comunicação
  insegura controlada no `VulnerableKioskApp`.

## Uso rápido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python -m examples.generate_report
```

O exemplo grava `kiosk-audit-report.json` no diretório atual.

## Análise de APK

```python
from apk_analyzer import ApkAnalyzer

findings = ApkAnalyzer("rules/kiosk_rules.yaml").analyze("app.apk")
```

Manifests binários, usados normalmente em APKs, são decodificados pelo
Androguard. Cada condição detectada é ligada a uma regra YAML e produz um
`Finding` independente com evidências específicas.

## Coleta por ADB

```python
from adb_probe import AdbProbe

snapshot = AdbProbe(serial="emulator-5554").collect()
print(snapshot.to_dict())
```

O snapshot contém versão e SDK do Android, `ro.debuggable`, `ro.secure`,
`ro.adb.secure`, estado de `adb_enabled`, pacotes instalados e a saída de
`dumpsys device_policy`. O executor usa listas de argumentos, timeout e
`shell=False` em todas as chamadas.
