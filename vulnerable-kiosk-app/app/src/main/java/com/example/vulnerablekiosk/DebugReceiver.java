package com.example.vulnerablekiosk;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.util.Log;

public class DebugReceiver extends BroadcastReceiver {
    private static final String TAG = "VulnerableDebugReceiver";

    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent == null ? "sem_action" : intent.getAction();

        // Receiver exportado propositalmente e logando segredo ficticio para fins academicos.
        Log.i(TAG, "Broadcast recebido: " + action);
        Log.d(TAG, "API_KEY ficticia no receiver: " + LabSecrets.API_KEY);
        Log.d(TAG, "SECRET_TOKEN ficticio no receiver: " + LabSecrets.SECRET_TOKEN);
    }
}
