package com.example.hardenedkiosk;

public final class SecureEndpointConfig {
    public static final String DEMO_ENDPOINT = "https://10.0.2.2:8443";

    private SecureEndpointConfig() {
    }

    public static String describeTransportPolicy() {
        return "Somente transporte cifrado demonstrativo. Comunicacoes criticas devem validar certificados e considerar pinning quando aplicavel.";
    }
}
