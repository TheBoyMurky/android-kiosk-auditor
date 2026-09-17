package com.example.hardenedkiosk;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String TAG = "HardenedKioskMain";
    private KioskModeManager kioskModeManager;
    private TextView kioskStatus;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        kioskModeManager = new KioskModeManager(this);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(48, 48, 48, 48);
        root.setBackgroundColor(Color.rgb(246, 248, 249));

        TextView title = new TextView(this);
        title.setText("HardenedKioskApp");
        title.setTextSize(28);
        title.setTextColor(Color.rgb(20, 35, 40));
        title.setGravity(Gravity.CENTER);

        TextView subtitle = new TextView(this);
        subtitle.setText("Versao segura demonstrativa para comparacao academica");
        subtitle.setTextSize(16);
        subtitle.setTextColor(Color.rgb(75, 85, 99));
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 16, 0, 28);

        kioskStatus = new TextView(this);
        kioskStatus.setText("Modo kiosk demonstrativo inativo.");
        kioskStatus.setTextSize(15);
        kioskStatus.setGravity(Gravity.CENTER);
        kioskStatus.setPadding(0, 0, 0, 20);

        Button startServiceButton = button("Iniciar Atendimento");
        startServiceButton.setOnClickListener(view -> showServiceInfo());

        Button adminButton = button("Area Administrativa");
        adminButton.setOnClickListener(view -> startActivity(new Intent(this, AdminActivity.class)));

        Button diagnosticsButton = button("Diagnostico Seguro");
        diagnosticsButton.setOnClickListener(view -> startActivity(new Intent(this, DiagnosticsActivity.class)));

        Button networkButton = button("Demo Rede Segura");
        networkButton.setOnClickListener(view -> startActivity(new Intent(this, NetworkDemoActivity.class)));

        Button kioskButton = button("Ativar Kiosk Demonstrativo");
        kioskButton.setOnClickListener(view -> updateKioskStatus(kioskModeManager.startControlledLockTask()));

        Button leaveKioskButton = button("Encerrar Kiosk Demonstrativo");
        leaveKioskButton.setOnClickListener(view -> updateKioskStatus(kioskModeManager.stopControlledLockTask()));

        root.addView(title);
        root.addView(subtitle);
        root.addView(kioskStatus);
        root.addView(startServiceButton);
        root.addView(adminButton);
        root.addView(diagnosticsButton);
        root.addView(networkButton);
        root.addView(kioskButton);
        root.addView(leaveKioskButton);

        setContentView(root);
        SafeLogger.info(TAG, "Tela principal iniciada.");
    }

    private void showServiceInfo() {
        SafeLogger.debug(TAG, "Atendimento demonstrativo iniciado.");
        Intent intent = new Intent(this, DiagnosticsActivity.class);
        intent.putExtra("show_service_info", true);
        startActivity(intent);
    }

    private void updateKioskStatus(KioskModeManager.Result result) {
        switch (result) {
            case STARTED:
                kioskStatus.setText("Modo kiosk demonstrativo ativo com autorizacao do sistema.");
                break;
            case STOPPED:
                kioskStatus.setText("Modo kiosk demonstrativo encerrado.");
                break;
            case NOT_AUTHORIZED:
                kioskStatus.setText("Kiosk nao autorizado. Configure Device Owner ou MDM em ambiente gerenciado.");
                break;
            case NOT_SUPPORTED:
                kioskStatus.setText("Recurso nao suportado nesta versao do Android.");
                break;
            default:
                kioskStatus.setText("Falha generica. Retorne a tela principal e tente novamente.");
                break;
        }
    }

    private Button button(String text) {
        Button button = new Button(this);
        button.setText(text);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(0, 10, 0, 10);
        button.setLayoutParams(params);
        return button;
    }
}
