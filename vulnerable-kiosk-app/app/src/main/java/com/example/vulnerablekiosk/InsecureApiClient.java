package com.example.vulnerablekiosk;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class InsecureApiClient {
    private static final String TAG = "VulnerableKioskNetwork";
    private static final String PREFS_NAME = "insecure_network_responses";

    public static final String LOGIN_URL = "http://10.0.2.2:8080/mock/login";
    public static final String PAYMENT_URL = "http://10.0.2.2:8080/mock/payment";
    public static final String STATUS_URL = "http://10.0.2.2:8080/mock/status";

    private final SharedPreferences preferences;

    public InsecureApiClient(Context context) {
        this.preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public String sendLoginMock() throws IOException {
        JSONObject payload = new JSONObject();
        try {
            payload.put("user", "cliente_teste");
            payload.put("password", "admin123");
            payload.put("sessionToken", "fake-token-123");
            payload.put("apiKey", "TEST_API_KEY_123456");
        } catch (Exception exception) {
            throw new IOException("Falha ao montar JSON ficticio de login.", exception);
        }

        // VULNERABLE: sensitive data logged
        Log.i(TAG, "Enviando login ficticio user=cliente_teste password=admin123 token=fake-token-123");
        Log.d(TAG, "API key ficticia enviada em texto claro: TEST_API_KEY_123456");

        String response = postJson(LOGIN_URL, payload.toString());
        savePlainText("lastLoginResponse", response);
        saveSessionIdIfPresent(response);
        return response;
    }

    public String sendPaymentMock() throws IOException {
        JSONObject payload = new JSONObject();
        try {
            payload.put("orderId", "pedido-teste-001");
            payload.put("amount", 10.50);
            payload.put("cardLastDigits", "0000");
        } catch (Exception exception) {
            throw new IOException("Falha ao montar JSON ficticio de pagamento.", exception);
        }

        // VULNERABLE: sensitive data logged
        Log.i(TAG, "Enviando pagamento ficticio orderId=pedido-teste-001 amount=10.50 cardLastDigits=0000");

        String response = postJson(PAYMENT_URL, payload.toString());
        savePlainText("lastPaymentResponse", response);
        return response;
    }

    public String getStatusMock() throws IOException {
        // VULNERABLE: cleartext HTTP communication
        Log.i(TAG, "Consultando status via HTTP claro: " + STATUS_URL);
        return request("GET", STATUS_URL, null);
    }

    private String postJson(String endpoint, String payload) throws IOException {
        // VULNERABLE: cleartext HTTP communication
        Log.d(TAG, "Payload JSON ficticio enviado via HTTP claro: " + payload);
        return request("POST", endpoint, payload);
    }

    private String request(String method, String endpoint, String payload) throws IOException {
        HttpURLConnection connection = null;
        try {
            URL url = new URL(endpoint);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod(method);
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            connection.setRequestProperty("Accept", "application/json");

            if (payload != null) {
                connection.setDoOutput(true);
                try (OutputStream outputStream = connection.getOutputStream();
                     BufferedWriter writer = new BufferedWriter(
                             new OutputStreamWriter(outputStream, StandardCharsets.UTF_8))) {
                    writer.write(payload);
                }
            }

            int statusCode = connection.getResponseCode();
            InputStream inputStream = statusCode >= 400
                    ? connection.getErrorStream()
                    : connection.getInputStream();
            String response = readFully(inputStream);
            Log.i(TAG, "Resposta HTTP ficticia recebida status=" + statusCode + " body=" + response);
            return response;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private String readFully(InputStream inputStream) throws IOException {
        if (inputStream == null) {
            return "";
        }

        StringBuilder builder = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(inputStream, StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
        }
        return builder.toString();
    }

    private void saveSessionIdIfPresent(String response) {
        try {
            JSONObject json = new JSONObject(response);
            String sessionId = json.optString("sessionId", "mock-session-desconhecida");
            savePlainText("sessionId", sessionId);
        } catch (Exception exception) {
            savePlainText("sessionId", "mock-session-desconhecida");
        }
    }

    private void savePlainText(String key, String value) {
        // VULNERABLE: sensitive data stored in plain text
        preferences.edit().putString(key, value).apply();
        Log.d(TAG, "Dado ficticio salvo em SharedPreferences texto claro: " + key + "=" + value);
    }
}
