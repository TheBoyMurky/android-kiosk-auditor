# Instalação completa no Linux Mint

Este procedimento prepara uma máquina Linux Mint ou outra distribuição baseada
em Ubuntu, com processador x86_64, para compilar, testar e demonstrar o projeto.

## Clonar o repositório

Instale o Git caso ele ainda não esteja disponível:

```bash
sudo apt-get update
sudo apt-get install -y git
```

Clone e entre no projeto:

```bash
git clone git@github.com:TheBoyMurky/android-kiosk-auditor.git
cd android-kiosk-auditor
```

O endereço SSH requer uma chave cadastrada no GitHub. Como alternativa:

```bash
git clone https://github.com/TheBoyMurky/android-kiosk-auditor.git
cd android-kiosk-auditor
```

## Executar o instalador

```bash
./scripts/setup_linux_mint.sh
```

O instalador:

1. instala JDK 17, Python, Git, ferramentas básicas e KVM;
2. adiciona o usuário aos grupos `kvm` e `libvirt`;
3. baixa as Android Command-line Tools e verifica seu SHA-256;
4. solicita a aceitação interativa das licenças do Android SDK;
5. instala Platform 35, Build Tools 35.0.0, Platform Tools, Emulator e a imagem
   Google APIs x86_64;
6. grava `ANDROID_HOME` e o `PATH` em `~/.profile`;
7. cria `.venv` e instala as dependências do auditor e do servidor mock;
8. executa testes, compila os APKs e valida os relatórios;
9. cria o AVD `Kiosk_TCC_API_35` quando o KVM já está acessível.

O script não aceita licenças automaticamente. Leia e responda às solicitações
apresentadas por `sdkmanager`.

## Novo login para acesso ao KVM

Na primeira instalação, a associação aos grupos pode exigir que você encerre e
inicie novamente a sessão do Linux Mint. Depois disso:

```bash
cd ~/android-kiosk-auditor
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/Sdk}"
./scripts/create_tcc_avd.sh
```

Valide a aceleração:

```bash
kvm-ok
emulator -accel-check
```

## Preparar a demonstração

```bash
source scripts/activate_venv.sh
./scripts/prepare_tcc_avd_demo.sh --rebuild
TCC_DEVICE=emulator-5556 ./scripts/provision_tcc_device_owner.sh
TCC_DEVICE=emulator-5556 ./scripts/run_framework_audit.sh
```

As etapas detalhadas da apresentação estão em `docs/defense-demo.md`.

## Opções do instalador

```bash
./scripts/setup_linux_mint.sh --help
```

Variáveis úteis:

- `ANDROID_HOME=/outro/caminho`: altera o destino do SDK;
- `TCC_SKIP_APT=1`: não executa `apt-get`;
- `TCC_SKIP_AVD=1`: não cria o AVD;
- `TCC_SKIP_VALIDATION=1`: não executa testes e builds.

O pacote das Command-line Tools e seu checksum correspondem à versão oficial
documentada quando este script foi criado. Se o Google remover esse artefato do
repositório, atualize conjuntamente a versão, a URL e o SHA-256.
