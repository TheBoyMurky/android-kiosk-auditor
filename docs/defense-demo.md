# Roteiro de demonstração para a defesa

Este é o roteiro principal para apresentar a prova de conceito. A sequência ao
vivo leva aproximadamente sete minutos e combina a comparação visual dos
aplicativos com a auditoria automatizada do APK e do Android. Ela demonstra o
recorte implementado sem afirmar validação integral dos parâmetros P01-P16.

## Visão geral da apresentação

| Etapa | O que mostrar | Tempo sugerido |
| --- | --- | ---: |
| 1 | Proposta e matriz P01-P16 | 1 min |
| 2 | Aplicativo vulnerável | 1 min |
| 3 | Aplicativo endurecido | 1 min |
| 4 | Execução da auditoria | 2 min |
| 5 | Resultado e limitações | 2 min |

## Preparação no dia anterior

Execute esta seção antes da defesa, com acesso à internet caso alguma
dependência ainda precise ser obtida.

### 1. Entre no projeto e configure o ambiente

```bash
cd ~/Desenvolvimento/android-kiosk-auditor
export ANDROID_HOME=/media/murky/HD/Android/Sdk
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
source scripts/activate_venv.sh
```

O `source` é necessário para manter o ambiente Python ativo no terminal.

### 2. Valide as ferramentas

```bash
java -version
adb version
emulator -accel-check
emulator -list-avds
pytest -q
```

O resultado esperado atualmente é `15 passed`. Se a quantidade crescer no
futuro, o importante é que todos os testes terminem aprovados.

### 3. Crie o AVD, somente se ele ainda não existir

```bash
./scripts/create_tcc_avd.sh
```

O nome padrão é `Kiosk_TCC_API_35`. O script preserva um AVD já existente.

### 4. Compile, instale e salve o snapshot da demonstração

```bash
./scripts/prepare_tcc_avd_demo.sh --rebuild
```

Ao final, confirme os dois pacotes:

```bash
adb -s emulator-5556 shell pm list packages | grep -E 'vulnerablekiosk|hardenedkiosk'
```

### 5. Gere a auditoria completa uma vez

```bash
TCC_DEVICE=emulator-5556 ./scripts/run_framework_audit.sh
less -S reports/framework-audit/framework-audit-summary.md
```

Use as setas laterais no `less` para navegar pela tabela e `q` para sair.
Guarde o relatório já gerado como contingência para a apresentação.

### 6. Autorize o kiosk no AVD de laboratório

Em um AVD limpo e sem contas configuradas:

```bash
TCC_DEVICE=emulator-5556 ./scripts/provision_tcc_device_owner.sh
```

O provisionamento como Device Owner é necessário para o Lock Task Mode completo.
Não use esse procedimento em um aparelho pessoal.

### 7. Prepare a demonstração HTTP opcional

```bash
python -m pip install -r mock-server/requirements.txt
```

Esse servidor só é necessário para demonstrar as requisições fictícias do
aplicativo vulnerável. Nenhum dado real deve ser utilizado.

## Checklist imediatamente antes da banca

- conecte o computador à energia e desative suspensão automática;
- confirme que a virtualização e `/dev/kvm` continuam acessíveis;
- feche outros emuladores para liberar a porta 5556;
- deixe dois terminais abertos na raiz do repositório;
- abra previamente `docs/tcc-traceability.md` e o relatório de contingência;
- teste a resolução do projetor e aumente a fonte do terminal;
- mantenha os comandos desta página disponíveis localmente.

No primeiro terminal, configure o ambiente e inicie o AVD pelo snapshot:

```bash
cd ~/Desenvolvimento/android-kiosk-auditor
export ANDROID_HOME=/media/murky/HD/Android/Sdk
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
source scripts/activate_venv.sh
emulator @Kiosk_TCC_API_35 -snapshot TCC-pronto -accel on -gpu auto -port 5556
```

Depois que o Android abrir, confirme a conexão em outro terminal:

```bash
adb devices
adb -s emulator-5556 shell getprop sys.boot_completed
```

A segunda saída deve ser `1`.

Se for demonstrar a comunicação HTTP, inicie no segundo terminal:

```bash
source .venv/bin/activate
python mock-server/app.py
```

Os endereços `10.0.2.2:8080` e `10.0.2.2:8443` usados pelos aplicativos apontam
do emulador para os serviços HTTP e HTTPS no computador hospedeiro. Não
substitua por `localhost`: dentro do AVD, esse nome aponta para o próprio
Android virtual.

## Sequência ao vivo

### 1. Apresente a contribuição

Abra `docs/tcc-traceability.md` e explique:

> O trabalho organiza 16 parâmetros de segurança em seis camadas. A prova de
> conceito automatiza a coleta de evidências de APKs e de um Android autorizado,
> mantendo explícitos os controles que ainda exigem avaliação humana.

Destaque as coberturas automática, parcial e manual.

### 2. Mostre o cenário vulnerável

```bash
adb -s emulator-5556 shell am start \
  -n com.example.vulnerablekiosk/.MainActivity
```

No aplicativo, mostre brevemente:

1. `Area Administrativa`, que representa tratamento inseguro de credenciais;
2. `Diagnostico`, que representa armazenamento e logs inseguros;
3. `Demo Rede HTTP Insegura` e uma requisição mock, se o servidor estiver ativo;
4. a presença proposital de recursos inadequados para comparação acadêmica.

Não use dados reais. Evite `Simular Travamento` durante a defesa, pois ele não
acrescenta evidência essencial e pode atrasar a sequência.

### 3. Mostre o cenário endurecido

```bash
adb -s emulator-5556 shell am start \
  -n com.example.hardenedkiosk/.MainActivity
```

Compare visualmente:

1. `Area Administrativa`, com PIN temporário em vez de segredo fixo;
2. `Diagnostico Seguro`, sem persistência de dados sensíveis fictícios;
3. `Demo Rede Segura`, que realiza chamadas HTTPS locais com certificado de
   laboratório validado pelo aplicativo;
4. `Ativar Kiosk Demonstrativo`, mostrando o Lock Task autorizado pelo Device
   Owner do AVD e explicando que esse laboratório não equivale a uma política
   MDM de produção.

Se ativar o kiosk demonstrativo, encerre-o pelo botão correspondente antes de
prosseguir.

### 4. Execute a auditoria combinada

No terminal com o ambiente Python ativo:

```bash
TCC_DEVICE=emulator-5556 ./scripts/run_framework_audit.sh
```

Esse comando analisa os dois APKs, coleta propriedades do Android por ADB em
modo somente leitura e registra os parâmetros P01-P16.

### 5. Apresente o resultado

```bash
less -S reports/framework-audit/framework-audit-summary.md
```

Explique as colunas separadamente:

- `APK vulnerável` mostra os resultados e indicadores do cenário inseguro;
- `APK endurecido` mostra o contraste produzido pelo hardening;
- `Dispositivo` confirma as evidências coletadas no emulador;
- `Conclusão global` permanece `nao_avaliado` quando os cenários divergem ou a
  decisão exige contexto adicional;
- `evidência coletada` significa que o teste foi executado, não que o parâmetro
  tenha sido automaticamente aprovado.

Em P01, P03 e P04, destaque o contraste esperado: o APK vulnerável é
`nao_conforme` e o endurecido é `conforme`. P05 apresenta o mesmo contraste,
mas sua conclusão é limitada aos padrões explícitos de literais estáticos. Em
controles indicativos, como backup e texto claro, explique por que a ferramenta
preserva `nao_avaliado` até existir interpretação ou teste complementar.

### 6. Encerre com os limites

> A prova de conceito produz evidências reproduzíveis e melhora a rastreabilidade
> da auditoria. Ela não certifica um terminal nem substitui testes físicos, TLS,
> MDM, processos de atualização, manutenção ou validação em hardware comercial.

## Perguntas previsíveis da banca

### Por que zero achados não significa segurança?

Porque o resultado cobre somente as regras executadas. Controles dinâmicos,
físicos, administrativos e específicos do dispositivo continuam necessários.

### Por que vários itens aparecem como `nao_avaliado`?

Porque a automação pode coletar um indicador sem conhecer a finalidade do
recurso ou os controles compensatórios. O relatório diferencia ausência de
execução de evidência coletada que ainda depende de análise.

### Por que permissões e componentes exportados não recebem conclusão automática?

Eles podem ser funcionalmente necessários e estar protegidos corretamente. A
conclusão depende da justificativa, dos controles de acesso e de testes de
invocação.

### O emulador comprova a segurança de um kiosk físico?

Não. Ele permite uma demonstração reproduzível de aplicativos, ADB, rede e
lock task. Gabinete, USB, boot, recovery, firmware e MDM dependem do terminal
real e do ambiente de produção.

### Qual é a contribuição principal?

O catálogo contextualizado P01-P16, sua organização em seis camadas e o
processo de coleta, interpretação, tratamento e reavaliação. O auditor é o
instrumento que materializa parte desse processo.

### Como o experimento pode ser reproduzido?

O repositório documenta JDK, Gradle, plugin Android, SDK, AVD, compilação dos
APKs, hashes dos artefatos e um comando único para regenerar a auditoria.

### A severidade representa risco universal?

Não. Ela é uma prioridade inicial de triagem. O risco depende da exposição, do
impacto, da função do terminal e das condições de exploração.

## Plano de contingência

Se o emulador não iniciar:

1. mostre `reports/framework-audit/framework-audit-summary.md` já gerado;
2. apresente `reports/apk-comparison-summary.md` como evidência estática;
3. execute `pytest -q`, que não depende do emulador;
4. explique que a coleta ADB foi validada previamente no ambiente documentado.

Se o servidor mock falhar, pule as requisições HTTP e HTTPS visuais. A análise
estática dos APKs e a auditoria não dependem dele.

Se a auditoria ao vivo falhar, não altere o ambiente durante a apresentação.
Use o relatório de contingência e mostre os hashes e horários registrados.

## Encerramento do ambiente

Depois da defesa, encerre o emulador de forma controlada:

```bash
adb -s emulator-5556 emu kill
```

Encerre o servidor mock com `Ctrl+C` no terminal em que ele estiver rodando.
