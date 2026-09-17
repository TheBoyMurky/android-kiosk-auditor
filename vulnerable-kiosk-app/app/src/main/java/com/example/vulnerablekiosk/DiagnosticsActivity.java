package com.example.vulnerablekiosk;

import android.app.Activity;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class DiagnosticsActivity extends Activity {
    private static final String TAG = "VulnerableKioskDiag";
    private static final String PREFS_NAME = "diagnostico_kiosk_inseguro";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText("Diagnostico de Laboratorio");
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER_HORIZONTAL);

        TextView status = new TextView(this);
        status.setPadding(0, 24, 0, 24);
        status.setText("Nenhum diagnostico gravado nesta sessao.");

        Button saveButton = new Button(this);
        saveButton.setText("Salvar Diagnostico Ficticio");
        saveButton.setOnClickListener(view -> {
            saveInsecureDiagnostics();
            status.setText("Dados ficticios gravados em SharedPreferences em texto claro.");
        });

        root.addView(title);
        root.addView(status);
        root.addView(saveButton);

        setContentView(root);
    }

    private void saveInsecureDiagnostics() {
        SharedPreferences preferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        // Vulneravel propositalmente: dados ficticios em texto claro.
        preferences.edit()
                .putString("cpf_teste", "123.456.789-00")
                .putString("session_token_teste", LabSecrets.SECRET_TOKEN)
                .putString("admin_password_teste", LabSecrets.ADMIN_PASSWORD)
                .putString("api_key_teste", LabSecrets.API_KEY)
                .putString("endpoint_http_teste", LabSecrets.INSECURE_LOGIN_URL)
                .apply();

        // Inseguro propositalmente: logs com dados ficticios sensiveis.
        Log.d(TAG, "cpf_teste=123.456.789-00");
        Log.i(TAG, "session_token_teste=" + LabSecrets.SECRET_TOKEN);
        Log.i(TAG, "admin_password_teste=" + LabSecrets.ADMIN_PASSWORD);
        Log.d(TAG, "api_key_teste=" + LabSecrets.API_KEY);
    }
}
