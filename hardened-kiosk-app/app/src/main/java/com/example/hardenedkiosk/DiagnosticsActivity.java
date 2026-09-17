package com.example.hardenedkiosk;

import android.app.Activity;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class DiagnosticsActivity extends Activity {
    private static final String TAG = "HardenedKioskDiag";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        SecureStorage storage = new SecureStorage(this);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText(getIntent().getBooleanExtra("show_service_info", false)
                ? "Atendimento Demonstrativo"
                : "Diagnostico Seguro");
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER_HORIZONTAL);

        TextView details = new TextView(this);
        details.setPadding(0, 24, 0, 24);
        details.setText(buildDetails(storage));

        Button saveButton = new Button(this);
        saveButton.setText("Salvar Preferencia Nao Sensivel");
        saveButton.setOnClickListener(view -> {
            try {
                boolean saved = storage.saveNonSensitivePreference("tema_interface", "claro");
                details.setText(saved
                        ? buildDetails(storage)
                        : "A preferencia foi rejeitada pela politica de armazenamento.");
            } catch (RuntimeException exception) {
                SafeLogger.warn(TAG, "Falha ao salvar preferencia demonstrativa.", exception);
                details.setText("Falha generica. Retorne a tela principal e tente novamente.");
            }
        });

        root.addView(title);
        root.addView(details);
        root.addView(saveButton);

        setContentView(root);
    }

    private String buildDetails(SecureStorage storage) {
        String preference = storage.readPreference("tema_interface", "nao configurado");
        return "Sem WebView insegura nesta versao.\n"
                + "Endpoint demonstrativo HTTPS: " + SecureEndpointConfig.DEMO_ENDPOINT + "\n"
                + SecureEndpointConfig.describeTransportPolicy() + "\n"
                + "Preferencia nao sensivel: " + preference;
    }
}
