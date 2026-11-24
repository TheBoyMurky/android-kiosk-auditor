# AVD oficial com aceleração KVM

O ambiente visual da defesa usa o Android Emulator oficial e uma imagem de
sistema compatível com a arquitetura do computador. No Linux, a aceleração é
fornecida pelo KVM.

## Pré-requisitos

- virtualização Intel VT-x ou AMD-V habilitada na BIOS/UEFI;
- KVM instalado e `/dev/kvm` acessível ao usuário;
- Android Command-line Tools em `cmdline-tools/latest`;
- `ANDROID_HOME` ou `ANDROID_SDK_ROOT` configurado;
- contrato do Android SDK aceito pelo próprio usuário.

Em Ubuntu, a instalação do KVM pode ser feita com:

```bash
sudo apt-get install qemu-kvm libvirt-daemon-system libvirt-clients \
  bridge-utils cpu-checker
sudo usermod -aG kvm "$USER"
```

Encerre e entre novamente na sessão após alterar os grupos. Depois valide:

```bash
kvm-ok
ls -l /dev/kvm
```

O Android Emulator usa KVM diretamente. O `virt-manager` não participa da
criação ou execução deste AVD.

Exemplo:

```bash
export ANDROID_HOME=/caminho/para/Android/Sdk
```

O script exige aceleração real e encerra com erro se o KVM não estiver
disponível. Ele não usa emulação lenta por software como fallback silencioso.

## Criar o AVD

```bash
./scripts/create_tcc_avd.sh
```

Configuração padrão:

- AVD: `Kiosk_TCC_API_35`;
- API: 35;
- imagem: Google APIs;
- arquitetura: `x86_64` em computadores Intel/AMD;
- perfil: Pixel 6.

É possível alterar os padrões antes da execução:

```bash
TCC_AVD_NAME=Kiosk_Defesa \
TCC_DEVICE_PROFILE=pixel_6 \
./scripts/create_tcc_avd.sh
```

O script preserva um AVD existente com o mesmo nome. Ele não apaga imagens nem
usa `--force`.

Algumas combinações recentes de Command-line Tools e imagens do sistema podem
exibir uma mensagem sobre `devices.xml` mesmo após criar o AVD. O script valida
o resultado com `avdmanager list avd` e `emulator -list-avds`; a criação só é
considerada concluída quando ambos reconhecem o nome configurado.

## Preparar a demonstração

```bash
./scripts/prepare_tcc_avd_demo.sh --rebuild
```

Esse comando:

1. compila os dois aplicativos quando solicitado;
2. inicia o AVD com aceleração obrigatória;
3. aguarda o Android concluir o boot;
4. instala os dois APKs;
5. regenera os relatórios estáticos;
6. retorna à tela inicial;
7. salva o snapshot `TCC-pronto`.

O script usa, nesta ordem, `PYTHON_COMMAND`, `.venv/bin/python`, `python3` ou
`python`. Se a execução for interrompida depois da instalação dos APKs, ela pode
ser retomada sem `--rebuild`.

Se ainda não existir um ambiente Python do projeto, prepare-o uma vez:

```bash
source scripts/activate_venv.sh
```

O emulador padrão usa a porta 5556 e aparece no ADB como `emulator-5556`.

Depois da preparação, gere também o registro P01-P16 usado na defesa:

```bash
TCC_DEVICE=emulator-5556 ./scripts/run_framework_audit.sh
```

## Autorizar o Lock Task Mode

Em um AVD limpo, provisione o aplicativo endurecido como Device Owner:

```bash
TCC_DEVICE=emulator-5556 ./scripts/provision_tcc_device_owner.sh
```

Depois, o botão `Ativar Kiosk Demonstrativo` poderá autorizar o próprio pacote
e iniciar Lock Task Mode. O botão `Encerrar Kiosk Demonstrativo` permanece
acessível pela rolagem da tela.

Device Owner só pode ser configurado quando o Android considera o dispositivo
elegível. Caso o comando seja recusado por contas, usuário já provisionado ou
outro proprietário, feche o emulador, aplique `Wipe Data` ao AVD e repita a
preparação. Não execute esse provisionamento em um aparelho pessoal.

## Servidor mock

Em outro terminal:

```bash
source .venv/bin/activate
pip install -r mock-server/requirements.txt
python mock-server/app.py
```

No Android Emulator, `10.0.2.2` aponta para o computador hospedeiro. O cenário
vulnerável usa HTTP na porta 8080; o endurecido usa HTTPS na porta 8443 com a CA
de laboratório restrita a esse domínio.

## Abrir os aplicativos

```bash
adb -s emulator-5556 shell am start \
  -n com.example.vulnerablekiosk/.MainActivity

adb -s emulator-5556 shell am start \
  -n com.example.hardenedkiosk/.MainActivity
```

## Restaurar o snapshot

Com o emulador fechado:

```bash
emulator @Kiosk_TCC_API_35 -snapshot TCC-pronto -accel on -gpu auto -port 5556
```

Se `emulator` não estiver no `PATH`, configure o SDK usado nesta máquina:

```bash
export ANDROID_HOME=/media/murky/HD/Android/Sdk
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$PATH"
```

Snapshots dependem da versão do emulador, da imagem do sistema e da configuração
do AVD. Atualizações podem invalidá-los. Faça uma validação completa no mesmo
computador antes da defesa.

Para encerrar o emulador:

```bash
adb -s emulator-5556 emu kill
```

O roteiro integrado para a banca está em `docs/defense-demo.md`.

## Limite da demonstração

O AVD é um ambiente controlado. Ele permite demonstrar os aplicativos, ADB,
rede e coleta de evidências, mas não representa controles físicos, firmware de
um fabricante ou um terminal comercial em produção.
