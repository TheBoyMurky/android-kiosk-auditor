package com.example.hardenedkiosk;

public final class SecureEndpointConfig {
    public static final String DEMO_ENDPOINT = "https://example.com/secure-api";

    private SecureEndpointConfig() {
    }

    public static String describeTransportPolicy() {
        return "Somente transporte cifrado demonstrativo. Comunicacoes criticas devem validar certificados e considerar pinning quando aplicavel.";
    }
}
