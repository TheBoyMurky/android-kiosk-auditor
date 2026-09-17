# Mock Server

Servidor Flask simples para demonstracao academica de comunicacao em apps
Android kiosk.

Ele usa HTTP propositalmente para evidenciar comunicacao insegura no
`VulnerableKioskApp`. Nao use este servidor com dados reais: todos os payloads
esperados sao ficticios e voltados apenas para laboratorio.

## Endpoints

- `GET /health`
- `POST /mock/login`
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

O servidor escuta em:

```text
http://0.0.0.0:8080
```

## Acesso Pelo Emulador Android

Dentro do emulador Android, use o endereco especial:

```text
http://10.0.2.2:8080
```

Exemplo:

```bash
curl http://10.0.2.2:8080/health
```

## Acesso Por Dispositivo Fisico

Use o IP local da maquina que esta executando o servidor, por exemplo:

```text
http://192.168.0.10:8080
```

O dispositivo fisico e a maquina do servidor precisam estar na mesma rede, e o
firewall local deve permitir conexoes na porta `8080`.
