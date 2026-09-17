package com.example.vulnerablekiosk;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String TAG = "VulnerableKioskMain";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Log.i(TAG, "Laboratorio iniciado com token ficticio: " + LabSecrets.SECRET_TOKEN);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(48, 48, 48, 48);
        root.setBackgroundColor(Color.rgb(245, 247, 250));

        TextView title = new TextView(this);
        title.setText("VulnerableKioskApp");
        title.setTextSize(28);
        title.setTextColor(Color.rgb(24, 32, 40));
        title.setGravity(Gravity.CENTER);

        TextView subtitle = new TextView(this);
        subtitle.setText("Ambiente de teste/laboratorio - propositalmente vulneravel");
        subtitle.setTextSize(16);
        subtitle.setTextColor(Color.rgb(75, 85, 99));
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 16, 0, 32);

        Button startButton = button("Iniciar Atendimento");
        startButton.setOnClickListener(view -> startActivity(new Intent(this, WebViewActivity.class)));

        Button adminButton = button("Area Administrativa");
        adminButton.setOnClickListener(view -> startActivity(new Intent(this, AdminActivity.class)));

        Button diagnosticsButton = button("Diagnostico");
        diagnosticsButton.setOnClickListener(view -> startActivity(new Intent(this, DiagnosticsActivity.class)));

        Button networkButton = button("Demo Rede HTTP Insegura");
        networkButton.setOnClickListener(view -> startActivity(new Intent(this, NetworkDemoActivity.class)));

        Button crashButton = button("Simular Travamento");
        crashButton.setOnClickListener(view -> {
            // Falha proposital: kiosk simulado nao recupera automaticamente apos crash.
            throw new RuntimeException("Crash academico simulado no kiosk vulneravel");
        });

        root.addView(title);
        root.addView(subtitle);
        root.addView(startButton);
        root.addView(adminButton);
        root.addView(diagnosticsButton);
        root.addView(networkButton);
        root.addView(crashButton);

        setContentView(root);
    }

    private Button button(String text) {
        Button button = new Button(this);
        button.setText(text);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(0, 12, 0, 12);
        button.setLayoutParams(params);
        return button;
    }

    @Override
    public void onBackPressed() {
        // Kiosk propositalmente fraco: o botao voltar permite sair da tela principal.
        super.onBackPressed();
    }
}
