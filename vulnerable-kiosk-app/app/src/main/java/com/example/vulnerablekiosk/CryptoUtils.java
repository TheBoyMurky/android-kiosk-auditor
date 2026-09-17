package com.example.vulnerablekiosk;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public final class CryptoUtils {
    private CryptoUtils() {
    }

    public static String md5(String value) {
        // Uso propositalmente inseguro para fins academicos.
        return digest("MD5", value);
    }

    public static String sha1(String value) {
        // Uso propositalmente inseguro para fins academicos.
        return digest("SHA-1", value);
    }

    private static String digest(String algorithm, String value) {
        try {
            MessageDigest digest = MessageDigest.getInstance(algorithm);
            byte[] bytes = digest.digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder builder = new StringBuilder();
            for (byte b : bytes) {
                builder.append(String.format("%02x", b));
            }
            return builder.toString();
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("Algoritmo de hash indisponivel: " + algorithm, exception);
        }
    }
}
