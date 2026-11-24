# Auditoria automatizada do framework P01-P16

O orquestrador combina análise estática dos dois APKs e coleta somente leitura
de um dispositivo Android autorizado por ADB. A saída registra todos os
parâmetros P01-P16, inclusive aqueles que continuam pendentes de avaliação
manual.

## Execução

Com o emulador aberto:

```bash
source scripts/activate_venv.sh
export TCC_DEVICE=emulator-5556
./scripts/run_framework_audit.sh
```

O serial padrão é `emulator-5556`. Para outro dispositivo:

```bash
TCC_DEVICE=emulator-5554 ./scripts/run_framework_audit.sh
```

## Arquivos gerados

```text
reports/framework-audit/
├── framework-audit-report.json
├── framework-audit-summary.md
├── adb-device-snapshot.json
├── vulnerable-apk-report.json
├── hardened-apk-report.json
├── apk-comparison-report.json
└── apk-comparison-summary.md
```

O JSON principal contém horário, duração, hashes dos APKs, identificação do
dispositivo, evidências por parâmetro, cobertura e próxima verificação
necessária. O Markdown apresenta a tabela P01-P16 para a defesa.

Para visualizar a tabela larga mantendo as colunas alinhadas no terminal:

```bash
less -S reports/framework-audit/framework-audit-summary.md
```

Use as setas laterais para navegar e `q` para sair.

## Interpretação

- `automatic`: a regra implementada produz evidência direta no recorte definido;
- `partial`: a automação coleta indicadores, mas exige interpretação adicional;
- `manual`: o parâmetro depende de inspeção ou procedimento fora da ferramenta.

Os estados são `conforme`, `nao_conforme`, `nao_avaliado` e `nao_aplicavel`.
Quando os dois aplicativos têm resultados diferentes, o registro agregado
permanece `nao_avaliado` e conserva os estados individuais de cada artefato.
O resumo Markdown mostra colunas separadas para o APK vulnerável, o APK
endurecido e o dispositivo. A indicação `evidência coletada` confirma que a
automação executou, mesmo quando a conclusão depende de interpretação ou teste
manual. O JSON também inclui `scenario_results`, `scenario_status_counts` e a
quantidade de parâmetros que receberam evidências.

O relatório não converte ausência de achados em segurança integral. P06, P07,
P12, P14, P15 e P16 permanecem manuais; P08-P11 são apenas parcialmente
avaliados pelo ADB Probe.

P03 e P04 são conclusivos no perfil estático de referência: respectivamente,
permissões perigosas e componentes internos exportados. P05 conclui somente
sobre os padrões explícitos de literais de credencial no DEX; segredos
ofuscados, dinâmicos ou remotos continuam fora desse resultado.

Em P04, a Activity launcher esperada e o `KioskDeviceAdminReceiver` protegido
pela permissão de assinatura `BIND_DEVICE_ADMIN` não são tratados como exposição
indevida. Em P11, o ADB Probe registra a política Device Owner do AVD, mas a
avaliação de governança permanece contextual.

## Uso durante a defesa

Execute a auditoria depois de mostrar os dois aplicativos no AVD. Comece pelo
contraste de P01 e, em seguida, explique que `evidência coletada` confirma a
execução, enquanto `nao_avaliado` preserva a necessidade de interpretação.
O roteiro completo está em `docs/defense-demo.md`.
