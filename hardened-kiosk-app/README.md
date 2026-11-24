# HardenedKioskApp

Aplicativo Android academico e demonstrativo que simula um kiosk de
autoatendimento com hardening basico. Ele foi criado como contraponto ao
`VulnerableKioskApp`, permitindo comparar configuracoes inseguras com uma
versao corrigida e simples de analisar por APK estatico e por ADB.

O app nao implementa bloqueio agressivo do dispositivo, nao coleta dados reais,
nao envia informacoes de usuarios e nao usa credenciais reais.

## Boas Praticas Implementadas

- Manifest com `android:allowBackup="false"` e
  `android:usesCleartextTraffic="false"`.
- `android:debuggable` nao e declarado como `true` no Manifest.
- O build type `debug` tambem define `debuggable false` para manter o APK de
  demonstracao alinhado ao objetivo de hardening.
- `network_security_config.xml` bloqueia trafego cleartext por padrao.
- Somente a permissao normal `INTERNET` e solicitada; nenhuma permissao
  perigosa e usada.
- A `MainActivity` é exportada por ser o launcher. As telas internas não são
  exportadas; o único receiver exportado exige a permissão de assinatura
  `android.permission.BIND_DEVICE_ADMIN`.
- Area administrativa sem senha fixa no codigo-fonte: o PIN e criado em tempo
  de execucao, fica apenas em memoria e e comparado por SHA-256 didatico.
- `SecureStorage` salva somente preferencias nao sensiveis e rejeita chaves ou
  valores com indicadores sensiveis.
- `SafeLogger` registra apenas eventos genericos e condiciona logs de debug a
  `BuildConfig.DEBUG`.
- Nao ha WebView insegura; a tela de atendimento/diagnostico e informativa.
- Demo de rede com chamadas HTTPS reais para o servidor local:
  `https://10.0.2.2:8443/mock/login`,
  `https://10.0.2.2:8443/mock/payment` e
  `https://10.0.2.2:8443/mock/status`.
- `KioskModeManager` demonstra Lock Task Mode somente quando autorizado pelo
  Android/MDM, sem tentar assumir controle agressivo do dispositivo.
- `KioskDeviceAdminReceiver` permite provisionar o APK como Device Owner no AVD
  de laboratório e autorizar explicitamente o pacote para Lock Task Mode.
- Falhas sao tratadas com mensagens genericas, sem exibir stack traces ao
  usuario.

## Demo De Rede Segura Local

Abra o app e toque em `Demo Rede Segura`. A tela oferece:

- `Executar Login Seguro`
- `Executar Pagamento Seguro`
- `Consultar Status Seguro`

A classe `SecureApiClient` realiza a chamada em uma thread de trabalho, não
desabilita validação TLS, não aceita qualquer certificado e não registra
payloads completos. O certificado de `10.0.2.2` é assinado por uma CA exclusiva
do laboratório, confiada apenas para esse domínio na configuração do app.

A chave privada incluída em `mock-server/certs` é pública e serve somente para
esta demonstração local. Ela não deve ser reutilizada em produção nem protege
um segredo real.

O app bloqueia trafego HTTP por `android:usesCleartextTraffic="false"` e por
`network_security_config.xml` com `cleartextTrafficPermitted="false"`.

O analisador deve verificar:

- Ausencia de URLs iniciadas por HTTP nos arquivos compilados do app.
- `android:usesCleartextTraffic="false"`.
- `android:allowBackup="false"`.
- `network_security_config.xml` bloqueando cleartext.
- Componentes internos com `android:exported="false"`.
- Nenhum log com credenciais, payloads completos ou dados pessoais.
- Persistencia apenas de timestamp nao sensivel da ultima simulacao.

## Comparacao Com VulnerableKioskApp

- `debuggable=true` foi removido do Manifest.
- Backup permitido foi substituido por backup desativado.
- Trafego cleartext permitido foi substituido por bloqueio explicito.
- Chamadas HTTP do app vulnerável foram substituídas por HTTPS real com
  validação de certificado no cenário endurecido.
- Permissoes perigosas e sem uso foram removidas.
- Componentes exportados indevidamente foram removidos ou fechados.
- Senhas e chaves fixas foram substituidas por uma simulacao de autenticacao em
  memoria.
- Dados sensiveis em texto claro foram substituidos por preferencias nao
  sensiveis controladas por `SecureStorage`.
- Logs com dados privados foram substituidos por logs genericos.
- WebView insegura foi substituida por tela informativa.
- MD5/SHA-1 foram substituidos por SHA-256 apenas para demonstracao didatica.
- Botao de crash e comportamento sem recuperacao foram removidos.

## Camadas Do Framework

- Aplicacao: autenticacao demonstrativa sem senha fixa, armazenamento restrito,
  logs genericos, tratamento basico de falhas e ausencia de WebView insegura.
- Sistema Operacional Android: backup desativado, cleartext bloqueado,
  componentes internos nao exportados e permissoes reduzidas.
- Modo Kiosk: Lock Task Mode usado apenas quando autorizado; em producao, o app
  deve ser Device Owner ou gerenciado por MDM.
- Seguranca Fisica: o app nao tenta bloquear o usuario de forma abusiva; a
  protecao fisica deve ser combinada com gabinete, politicas de ADB e MDM.
- Rede e Comunicação: chamadas HTTPS reais no laboratório, CA restrita ao
  domínio `10.0.2.2` e cleartext bloqueado; produção deve usar certificados e
  infraestrutura próprios e pode considerar pinning quando aplicável.
- Manutencao e Monitoramento: logs seguros, mensagens genericas de falha e
  configuracao visivel para inspecao por ADB.

## Relacao Com OWASP Mobile

- M1 Improper Credential Usage: sem credenciais fixas no codigo-fonte.
- M3 Insecure Authentication/Authorization: autenticacao administrativa
  demonstrativa sem senha padrao persistida.
- M5 Insecure Communication: cleartext bloqueado e endpoints HTTPS locais com
  validação de certificado na demonstração segura.
- M7 Insufficient Binary Protections: `debuggable=true` nao e declarado no
  Manifest.
- M8 Security Misconfiguration: backup desativado, componentes internos fechados
  e permissoes minimas.
- M9 Insecure Data Storage: apenas preferencias nao sensiveis sao persistidas.
- M10 Insufficient Cryptography: sem MD5/SHA-1; SHA-256 aparece somente como
  exemplo didatico, com comentario sobre uso robusto em producao.

## Relacao Com OWASP IoT

- I4 Lack of Secure Update Mechanism: versao e pacote claros no Gradle para
  apoiar inventario e atualizacao controlada por MDM/loja corporativa.
- I7 Insecure Data Transfer and Storage: cleartext bloqueado, chamada HTTPS
  validada e armazenamento de dados sensíveis evitado.
- I8 Lack of Device Management: `KioskModeManager` documenta uso correto com
  Device Owner ou MDM.
- I9 Insecure Default Settings: configuracoes padrao inseguras foram removidas.
- I10 Lack of Physical Hardening: o README explicita que hardening fisico deve
  ser tratado fora do app.

## Como Compilar

Requisitos: Android SDK instalado e Gradle disponivel no ambiente, ou abertura
do projeto pelo Android Studio.

```bash
cd hardened-kiosk-app
./gradlew assembleDebug
```

## Como Instalar Via ADB

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

Para habilitar o kiosk no AVD limpo usado na defesa:

```bash
export ANDROID_HOME=/media/murky/HD/Android/Sdk
TCC_DEVICE=emulator-5556 ./scripts/provision_tcc_device_owner.sh
```

O Android só permite definir Device Owner em um dispositivo elegível, sem outro
proprietário e normalmente sem contas configuradas. Se o AVD já tiver sido
provisionado de forma incompatível, recrie-o ou faça `Wipe Data` antes de
executar o script. Essa operação é exclusiva do emulador acadêmico.

## Comandos Para Inspecao

```bash
adb shell dumpsys package com.example.hardenedkiosk
adb shell pm list packages | grep hardenedkiosk
adb shell dumpsys activity activities
```

## Observacoes

Este projeto e propositalmente simples para facilitar a leitura em TCC,
apresentacoes e testes automatizados. Ele demonstra boas praticas basicas, mas
nao substitui revisao de seguranca, modelagem de ameacas, MDM, Android Keystore,
EncryptedSharedPreferences ou controles de infraestrutura em um ambiente real.
