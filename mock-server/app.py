from pathlib import Path
from threading import Thread

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "message": "Mock server academico em execucao",
        }
    )


@app.route("/mock/login", methods=["GET", "POST"])
def mock_login():
    if request.method == "GET":
        print("[mock-server] Tela de login demonstrativa consultada via HTTP")
        return jsonify(
            {
                "status": "ok",
                "message": "Endpoint de login mock acessado por HTTP",
                "warning": "Ambiente academico: nao envie dados reais",
            }
        )
    payload = request.get_json(silent=True) or {}
    print("[mock-server] Login recebido via HTTP com dados ficticios:", payload)
    return jsonify(
        {
            "status": "ok",
            "message": "Login mock recebido por HTTP",
            "sessionId": "mock-session-001",
        }
    )


@app.post("/mock/payment")
def mock_payment():
    payload = request.get_json(silent=True) or {}
    print("[mock-server] Pagamento recebido via HTTP com dados ficticios:", payload)
    return jsonify(
        {
            "status": "ok",
            "message": "Pagamento mock recebido por HTTP",
            "paymentId": "mock-payment-001",
        }
    )


@app.get("/mock/status")
def mock_status():
    print("[mock-server] Status consultado via HTTP")
    return jsonify(
        {
            "status": "ok",
            "message": "Status mock disponivel por HTTP",
            "deviceState": "laboratorio",
        }
    )


if __name__ == "__main__":
    certificate_dir = Path(__file__).resolve().parent / "certs"
    tls_context = (
        str(certificate_dir / "server-cert.pem"),
        str(certificate_dir / "server-key.pem"),
    )

    http_server = Thread(
        target=lambda: app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False),
        daemon=True,
    )
    http_server.start()
    app.run(
        host="0.0.0.0",
        port=8443,
        debug=False,
        use_reloader=False,
        ssl_context=tls_context,
    )
