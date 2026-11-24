package com.example.hardenedkiosk;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class SecureApiClient {
    public static final String LOGIN_URL = "https://10.0.2.2:8443/mock/login";
    public static final String PAYMENT_URL = "https://10.0.2.2:8443/mock/payment";
    public static final String STATUS_URL = "https://10.0.2.2:8443/mock/status";

    private final SecureStorage storage;

    public SecureApiClient(SecureStorage storage) {
        this.storage = storage;
    }

    public String executeLogin() {
        return request("POST", LOGIN_URL, "{\"user\":\"demo-seguro\"}");
    }

    public String executePayment() {
        return request("POST", PAYMENT_URL, "{\"operation\":\"demo\"}");
    }

    public String executeStatus() {
        return request("GET", STATUS_URL, null);
    }

    private String request(String method, String endpoint, String body) {
        HttpURLConnection connection = null;
        try {
            connection = (HttpURLConnection) new URL(endpoint).openConnection();
            connection.setRequestMethod(method);
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            connection.setRequestProperty("Accept", "application/json");

            if (body != null) {
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
                try (OutputStream output = connection.getOutputStream()) {
                    output.write(body.getBytes(StandardCharsets.UTF_8));
                }
            }

            int statusCode = connection.getResponseCode();
            InputStream stream = statusCode >= 400
                    ? connection.getErrorStream()
                    : connection.getInputStream();
            String response = readBody(stream);

            SafeLogger.info("SecureApiClient", "Chamada HTTPS concluida com status " + statusCode + ".");
            storage.saveNonSensitivePreference("last_network_call_at", now());
            return "HTTPS validado com sucesso"
                    + "\nStatus: " + statusCode
                    + "\nEndpoint: " + endpoint
                    + "\nResposta: " + response;
        } catch (Exception error) {
            SafeLogger.info("SecureApiClient", "Falha generica na chamada HTTPS.");
            return "Falha na chamada HTTPS. Confirme o servidor local na porta 8443."
                    + "\nTipo: " + error.getClass().getSimpleName();
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private String readBody(InputStream stream) throws Exception {
        if (stream == null) {
            return "";
        }
        StringBuilder result = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                result.append(line);
            }
        }
        return result.toString();
    }

    private String now() {
        return new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(new Date());
    }
}
