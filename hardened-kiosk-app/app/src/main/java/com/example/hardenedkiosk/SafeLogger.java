package com.example.hardenedkiosk;

import android.util.Log;

public final class SafeLogger {
    private SafeLogger() {
    }

    public static void debug(String tag, String message) {
        if (BuildConfig.DEBUG) {
            Log.d(tag, sanitize(message));
        }
    }

    public static void info(String tag, String message) {
        Log.i(tag, sanitize(message));
    }

    public static void warn(String tag, String message, Throwable throwable) {
        String suffix = throwable == null ? "" : " Tipo: " + throwable.getClass().getSimpleName();
        Log.w(tag, sanitize(message) + suffix);
    }

    private static String sanitize(String message) {
        if (message == null || message.trim().isEmpty()) {
            return "Evento do app registrado sem detalhes sensiveis.";
        }
        return message.replace('\n', ' ').replace('\r', ' ');
    }
}
