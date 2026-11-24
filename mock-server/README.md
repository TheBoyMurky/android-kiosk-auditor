# Mock Server

Servidor Flask simples para demonstracao academica de comunicacao em apps
Android kiosk.

Ele oferece HTTP para evidenciar comunicação insegura no `VulnerableKioskApp`
e HTTPS com certificado de laboratório para o `HardenedKioskApp`. Não use este
servidor com dados reais: todos os payloads são fictícios.

## Endpoints

- `GET /health`
- `GET /mock/login` para a WebView demonstrativa
- `POST /mock/login` para os clientes de API
- `POST /mock/payment`
- `GET /mock/status`

## Instalar Dependencias

```bash
cd mock-server
pip install -r requirements.txt
```

## Executar

```bash
python app.py
```

O mesmo processo inicia os dois endereços:

```text
http://0.0.0.0:8080
https://0.0.0.0:8443
```

## Acesso Pelo Emulador Android

Dentro do emulador Android, use o endereco especial:

```text
http://10.0.2.2:8080
https://10.0.2.2:8443
```

Testes no computador hospedeiro:

```bash
curl http://127.0.0.1:8080/health
curl --cacert certs/ca-cert.pem https://127.0.0.1:8443/health
```

O APK endurecido contém a CA pública do laboratório e valida o hostname/IP do
certificado normalmente. A chave privada versionada é exclusiva da prova de
conceito e nunca deve ser usada fora deste ambiente.

## Acesso Por Dispositivo Fisico

Use o IP local da maquina que esta executando o servidor, por exemplo:

```text
http://192.168.0.10:8080
```

O dispositivo fisico e a maquina do servidor precisam estar na mesma rede, e o
firewall local deve permitir conexoes na porta `8080`.

O certificado HTTPS fornecido cobre somente `10.0.2.2`, `127.0.0.1` e
`localhost`, portanto a demonstração HTTPS pronta é específica do emulador. Um
dispositivo físico exigiria certificado emitido para o IP ou nome realmente
utilizado e uma configuração de confiança correspondente no aplicativo.
