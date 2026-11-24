package com.example.vulnerablekiosk;

public final class LabSecrets {
    public static final String ADMIN_PASSWORD = "admin123";
    public static final String API_KEY = "TEST_API_KEY_123456";
    public static final String SECRET_TOKEN = "fake-secret-token";
    public static final String INSECURE_LOGIN_URL = "http://10.0.2.2:8080/mock/login";
    public static final String INSECURE_API_URL = "http://10.0.2.2:8080/mock/status";

    private LabSecrets() {
    }
}
