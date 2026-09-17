package com.example.hardenedkiosk;

import android.content.Context;
import android.content.SharedPreferences;

import java.util.Locale;

public final class SecureStorage {
    private static final String PREFS_NAME = "hardened_kiosk_preferences";
    private static final String[] BLOCKED_KEY_PARTS = {
            "senha",
            "pin",
            "cpf",
            "documento",
            "sessao",
            "credencial",
            "autenticacao"
    };

    private final SharedPreferences preferences;

    public SecureStorage(Context context) {
        this.preferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public boolean saveNonSensitivePreference(String key, String value) {
        if (!isAllowed(key) || !isAllowed(value)) {
            SafeLogger.info("SecureStorage", "Preferencia rejeitada por conter indicador sensivel.");
            return false;
        }

        preferences.edit().putString(key, value).apply();
        SafeLogger.debug("SecureStorage", "Preferencia nao sensivel salva.");
        return true;
    }

    public String readPreference(String key, String fallback) {
        if (!isAllowed(key)) {
            SafeLogger.info("SecureStorage", "Leitura rejeitada por chave sensivel.");
            return fallback;
        }
        return preferences.getString(key, fallback);
    }

    private boolean isAllowed(String value) {
        if (value == null) {
            return true;
        }

        String normalized = value.toLowerCase(Locale.ROOT);
        for (String blocked : BLOCKED_KEY_PARTS) {
            if (normalized.contains(blocked)) {
                return false;
            }
        }
        return true;
    }
}
