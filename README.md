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
- `mock-server`: servidor Flask local em HTTP para o cenário vulnerável e HTTPS
  com certificado de laboratório para o cenário endurecido.

A matriz [`docs/tcc-traceability.md`](docs/tcc-traceability.md) relaciona os
parâmetros P01-P16, os IDs da planilha, as regras implementadas e as evidências
manuais ainda necessárias.

Os requisitos de JDK/Android SDK e o procedimento de compilação estão em
[`docs/android-build.md`](docs/android-build.md).

O roteiro completo da defesa, incluindo preparação, sequência ao vivo,
interpretação dos resultados e contingência, está em
[`docs/defense-demo.md`](docs/defense-demo.md).

A criação do AVD oficial acelerado por KVM e a preparação do snapshot estão em
[`docs/avd-demo.md`](docs/avd-demo.md).

## Uso rápido

Para criar, completar e ativar o ambiente Python no terminal atual:

```bash
source scripts/activate_venv.sh
```

O script cria `.venv` quando necessário e instala as dependências de
desenvolvimento somente quando elas ainda não estão disponíveis.

O procedimento equivalente, executado manualmente, é:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python -m examples.generate_report
```

O exemplo grava `kiosk-audit-report.json` no diretório atual.

Para compilar os dois aplicativos de referência após configurar o Android SDK:

```bash
./scripts/build_reference_apks.sh
```

Para executar testes, builds, geração de evidências e validação dos JSONs em uma
única sequência:

```bash
./scripts/validate_project.sh
```

## Auditoria combinada do framework

Com um emulador ou dispositivo autorizado conectado por ADB, execute:

```bash
export TCC_DEVICE=emulator-5556
./scripts/run_framework_audit.sh
```

O comando combina os relatórios dos APKs, a coleta somente leitura do Android e
um registro P01-P16 em `reports/framework-audit/`. Parâmetros que exigem contexto,
teste dinâmico, inspeção física ou processo operacional permanecem
`nao_avaliado` e recebem uma indicação da próxima evidência necessária.

O formato completo das saídas está documentado em
[`docs/framework-audit.md`](docs/framework-audit.md).

## Demonstração da defesa

Para preparar o ambiente visual completo pela primeira vez:

```bash
export ANDROID_HOME=/media/murky/HD/Android/Sdk
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
source scripts/activate_venv.sh
./scripts/create_tcc_avd.sh
./scripts/prepare_tcc_avd_demo.sh --rebuild
TCC_DEVICE=emulator-5556 ./scripts/provision_tcc_device_owner.sh
TCC_DEVICE=emulator-5556 ./scripts/run_framework_audit.sh
```

O provisionamento como Device Owner deve ser realizado somente no AVD acadêmico
limpo. Depois dele, salve o snapshot `TCC-pronto`. Na defesa, restaure esse
snapshot, apresente os dois aplicativos e execute novamente apenas a auditoria
combinada. Siga a ordem em [`docs/defense-demo.md`](docs/defense-demo.md).

## Análise de APK

```python
from apk_analyzer import ApkAnalyzer

findings = ApkAnalyzer("rules/kiosk_rules.yaml").analyze("app.apk")
```

Manifests binários, usados normalmente em APKs, são decodificados pelo
Androguard. Cada condição detectada é ligada a uma regra YAML e produz um
`Finding` independente com evidências específicas.

## Comparação reproduzível dos APKs de referência

Depois de compilar os dois aplicativos, gere novamente todas as evidências
estáticas com um único comando:

```bash
android-kiosk-compare \
  --vulnerable vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk \
  --hardened hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk
```

Como alternativa, sem depender do script instalado no ambiente:

```bash
python -m apk_analyzer.cli \
  --vulnerable vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk \
  --hardened hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk
```

O comando sobrescreve os relatórios canônicos em `reports/`, registra o
SHA-256 e o tamanho de cada APK, executa as regras implementadas pelo
`ApkAnalyzer`, coleta indicadores de strings dos arquivos DEX e atualiza o
resumo comparativo. Ele não precisa de `aapt` ou `dexdump`.

A contagem de achados representa somente as regras implementadas na versão
atual. Ausência de achados não comprova segurança completa e não cobre o
dispositivo, o confinamento kiosk, TLS, testes dinâmicos, controles físicos ou
procedimentos operacionais.

Cada controle executado também recebe um estado de avaliação:

- `conforme`: uma regra conclusiva produziu evidência suficiente de atendimento;
- `nao_conforme`: uma regra conclusiva produziu evidência suficiente de falha;
- `nao_avaliado`: faltam evidências contextuais ou procedimentos complementares;
- `nao_aplicavel`: somente pode ser atribuído manualmente, com justificativa.

Regras classificadas como indicadores permanecem `nao_avaliado`, com ou sem
ocorrência detectada. P03 e P04 são conclusivos dentro do perfil estático de
referência. P05 é conclusivo somente para os padrões de literais definidos e
não exclui segredos ofuscados ou dinâmicos. A severidade é apenas uma prioridade
inicial de triagem e não constitui uma pontuação universal validada de risco.

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
