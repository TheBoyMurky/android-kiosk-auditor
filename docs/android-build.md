# Ambiente e compilação dos aplicativos Android

Os dois aplicativos de referência usam a mesma base de compilação:

- JDK 17 ou mais recente;
- Gradle Wrapper 8.10.2;
- Android Gradle Plugin 8.7.3;
- Android SDK Platform 35;
- Android SDK Build Tools 35.0.0.

O `VulnerableKioskApp` usa `minSdk 23`, `targetSdk 28` e `compileSdk 35`.
O `HardenedKioskApp` usa `minSdk 23`, `targetSdk 35` e `compileSdk 35`.

## Configuração do SDK

Defina uma das variáveis reconhecidas pelo Android Gradle Plugin:

```bash
export ANDROID_HOME=/caminho/para/Android/Sdk
```

ou:

```bash
export ANDROID_SDK_ROOT=/caminho/para/Android/Sdk
```

Confirme que a plataforma existe:

```bash
test -f "$ANDROID_HOME/platforms/android-35/android.jar"
```

Se utilizar as ferramentas oficiais de linha de comando, instale os pacotes
após ler e aceitar pessoalmente os termos do Android SDK:

```bash
sdkmanager "platforms;android-35" "build-tools;35.0.0" "platform-tools"
```

Não versione `local.properties`: esse arquivo contém um caminho específico da
máquina e já está incluído no `.gitignore`.

## Compilação reproduzível

Na raiz do repositório, execute:

```bash
./scripts/build_reference_apks.sh
```

O script valida Java e a plataforma Android 35 antes de executar
`assembleDebug` nos dois projetos. Os artefatos esperados são:

```text
vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk
hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk
```

Depois da compilação, regenere as evidências:

```bash
python -m apk_analyzer.cli \
  --vulnerable vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk \
  --hardened hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk
```

## Limites da compilação

Um build bem-sucedido confirma que o código e os recursos são compiláveis no
ambiente documentado. Ele não comprova confinamento kiosk, comportamento em
execução, segurança TLS, proteção física ou conformidade integral com P01-P16.
