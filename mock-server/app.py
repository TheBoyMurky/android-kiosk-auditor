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


@app.post("/mock/login")
def mock_login():
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
    app.run(host="0.0.0.0", port=8080, debug=False)
