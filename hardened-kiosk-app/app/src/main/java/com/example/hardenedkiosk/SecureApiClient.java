package com.example.hardenedkiosk;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class SecureApiClient {
    public static final String LOGIN_URL = "https://example.com/secure-api/login";
    public static final String PAYMENT_URL = "https://example.com/secure-api/payment";
    public static final String STATUS_URL = "https://example.com/secure-api/status";

    private final SecureStorage storage;

    public SecureApiClient(SecureStorage storage) {
        this.storage = storage;
    }

    public String executeLoginSimulation() {
        return simulateSecureCall("login", LOGIN_URL);
    }

    public String executePaymentSimulation() {
        return simulateSecureCall("payment", PAYMENT_URL);
    }

    public String executeStatusSimulation() {
        return simulateSecureCall("status", STATUS_URL);
    }

    private String simulateSecureCall(String operation, String endpoint) {
        // Em producao, chamadas criticas devem usar HTTPS com validacao adequada
        // de certificado e, quando aplicavel, SSL Pinning. Esta demo nao
        // desabilita validacao de certificado nem aceita certificados invalidos.
        SafeLogger.info("SecureApiClient", "Chamada segura simulada concluida.");
        storage.saveNonSensitivePreference("last_network_simulation_at", now());
        return "Operacao segura simulada: " + operation
                + "\nEndpoint HTTPS demonstrativo: " + endpoint
                + "\nNenhum payload sensivel foi registrado ou persistido.";
    }

    private String now() {
        return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(new Date());
    }
}
