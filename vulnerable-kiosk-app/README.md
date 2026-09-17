# VulnerableKioskApp

Aplicativo Android de laboratorio intencionalmente vulneravel, criado
exclusivamente como alvo academico para testes de analisadores estaticos de APK
e probes via ADB em cenarios Android/Kiosk.

Este app nao implementa malware, nao coleta dados reais, nao exfiltra
informacoes, nao explora o sistema operacional e nao usa credenciais reais.
Todos os tokens, senhas, URLs e dados persistidos sao ficticios.

## Vulnerabilidades Implementadas

- Manifest inseguro: `android:debuggable="true"`, `android:allowBackup="true"`
  e `android:usesCleartextTraffic="true"`.
- Permissoes excessivas: `INTERNET`, `CAMERA`, `ACCESS_FINE_LOCATION`,
  `RECORD_AUDIO`, `READ_PHONE_STATE`, `READ_EXTERNAL_STORAGE`,
  `WRITE_EXTERNAL_STORAGE` e `RECEIVE_BOOT_COMPLETED`.
- Componentes exportados indevidamente: `ExportedDebugActivity` e
  `DebugReceiver` com `android:exported="true"` e intent filters simples.
- Credenciais hardcoded ficticias: `ADMIN_PASSWORD`, `API_KEY` e
  `SECRET_TOKEN`.
- Armazenamento inseguro em `SharedPreferences` em texto claro.
- Comunicacao insegura simulada com URLs HTTP ficticias.
- Comunicacao insegura real contra mock-server local por HTTP:
  `http://10.0.2.2:8080/mock/login`,
  `http://10.0.2.2:8080/mock/payment` e
  `http://10.0.2.2:8080/mock/status`.
- Logs sensiveis ficticios usando `Log.d` e `Log.i`.
- `WebView` insegura com JavaScript e acesso a arquivos habilitados.
- Criptografia fraca demonstrativa com MD5 e SHA-1.
- Falhas de kiosk simuladas: sem Lock Task Mode real, botao voltar liberado e
  botao "Simular Travamento" que lanca `RuntimeException`.

## Mock Server Local

Antes de usar a tela de rede insegura, inicie o servidor local na raiz do
workspace:

```bash
cd ../mock-server
pip install -r requirements.txt
python app.py
```

No emulador Android, o app acessa a maquina hospedeira por:

```text
http://10.0.2.2:8080
```

Em dispositivo fisico, substitua esse endereco pelo IP local da maquina que
roda o mock-server.

## Demo De Rede Insegura

Abra o app e toque em `Demo Rede HTTP Insegura`. A tela oferece:

- `Enviar Login Mock HTTP`
- `Enviar Pagamento Mock HTTP`
- `Consultar Status HTTP`

As chamadas usam `HttpURLConnection`, enviam JSON ficticio em texto claro,
registram dados ficticios em logs e salvam respostas em `SharedPreferences`
sem criptografia. Isso e proposital para permitir deteccao estatica e via ADB.

O analisador deve conseguir encontrar:

- URLs `http://10.0.2.2:8080/...` no APK.
- `android:usesCleartextTraffic="true"`.
- Permissao `android.permission.INTERNET`.
- Strings ficticias `admin123`, `fake-token-123` e `TEST_API_KEY_123456`.
- Marcacoes `VULNERABLE: cleartext HTTP communication`.
- Marcacoes `VULNERABLE: sensitive data logged`.
- Marcacoes `VULNERABLE: sensitive data stored in plain text`.
- Escrita de `sessionId`, `lastLoginResponse` e `lastPaymentResponse` em
  `SharedPreferences`.

## Como Compilar

Requisitos: Android SDK instalado e Gradle disponivel no ambiente, ou abertura
do projeto pelo Android Studio.

```bash
cd vulnerable-kiosk-app
./gradlew assembleDebug
```

Se voce estiver usando Gradle instalado globalmente em vez do wrapper:

```bash
cd vulnerable-kiosk-app
gradle assembleDebug
```

## Como Instalar Com ADB

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Comandos Uteis Para Auditoria

```bash
adb shell dumpsys package <package_name>
adb shell dumpsys package com.example.vulnerablekiosk
adb shell pm list packages
adb shell am start -n com.example.vulnerablekiosk/.ExportedDebugActivity
adb shell am broadcast -a com.example.vulnerablekiosk.DEBUG_BROADCAST
```

## Relacao Com Camadas Do Framework

- Aplicacao: credenciais hardcoded, logs sensiveis, armazenamento inseguro,
  WebView insegura e uso demonstrativo de hash fraco.
- Sistema Operacional Android: permissoes excessivas, backup permitido,
  debuggable habilitado e componentes exportados.
- Modo Kiosk: ausencia proposital de hardening, Lock Task Mode nao configurado,
  botao voltar liberado e crash sem recuperacao automatica.
- Seguranca Fisica: simulacao de totem sem protecao real contra acesso local ao
  dispositivo, ADB ou inspecao manual.
- Rede e Comunicacao: trafego cleartext permitido e URLs HTTP ficticias
  presentes no codigo; a demo de rede envia JSON ficticio por HTTP ao
  mock-server local.
- Manutencao e Monitoramento: logs contendo dados ficticios sensiveis e painel
  de debug exportado para demonstracao de riscos.

## Relacao Com OWASP

- OWASP Mobile M5 Insecure Communication: o app permite cleartext e executa
  chamadas HTTP sem TLS para o mock-server local.
- OWASP IoT I7 Insecure Data Transfer and Storage: dados ficticios de login,
  sessao e pagamento trafegam sem criptografia e respostas sao salvas em texto
  claro para demonstracao academica.

## Escopo

Use este APK apenas em laboratorio controlado. Ele foi escrito para ser ruim de
proposito, com indicadores faceis de detectar por ferramentas de auditoria.
