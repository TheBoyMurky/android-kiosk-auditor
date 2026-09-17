package com.example.hardenedkiosk;

import android.app.Activity;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class AdminActivity extends Activity {
    private static final String TAG = "HardenedKioskAdmin";
    private String runtimePinHash;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText("Area Administrativa");
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER_HORIZONTAL);

        TextView explanation = new TextView(this);
        explanation.setText("Demonstração local: cadastre um PIN temporario nesta sessao e valide em seguida. Em producao, autentique por backend confiavel ou MDM.");
        explanation.setPadding(0, 20, 0, 20);

        EditText setupInput = pinInput("PIN temporario da sessao");
        Button setupButton = new Button(this);
        setupButton.setText("Cadastrar PIN Temporario");

        EditText loginInput = pinInput("Validar PIN");
        Button loginButton = new Button(this);
        loginButton.setText("Validar Acesso");

        TextView result = new TextView(this);
        result.setTextSize(16);
        result.setPadding(0, 24, 0, 0);

        setupButton.setOnClickListener(view -> {
            String entered = setupInput.getText().toString();
            if (entered.length() < 4) {
                result.setText("Use pelo menos quatro digitos para esta demonstracao.");
                return;
            }

            runtimePinHash = HashUtils.sha256(entered);
            setupInput.setText("");
            result.setText("PIN temporario cadastrado apenas em memoria.");
            SafeLogger.info(TAG, "Credencial temporaria da sessao criada sem gravacao persistente.");
        });

        loginButton.setOnClickListener(view -> {
            if (runtimePinHash == null) {
                result.setText("Cadastre um PIN temporario antes de validar o acesso.");
                return;
            }

            String enteredHash = HashUtils.sha256(loginInput.getText().toString());
            loginInput.setText("");
            if (runtimePinHash.equals(enteredHash)) {
                result.setText("Acesso administrativo demonstrativo liberado.");
                SafeLogger.info(TAG, "Acesso administrativo demonstrativo validado.");
            } else {
                result.setText("Acesso negado.");
                SafeLogger.info(TAG, "Tentativa administrativa demonstrativa negada.");
            }
        });

        root.addView(title);
        root.addView(explanation);
        root.addView(setupInput, fullWidth());
        root.addView(setupButton);
        root.addView(loginInput, fullWidth());
        root.addView(loginButton);
        root.addView(result);

        setContentView(root);
    }

    private EditText pinInput(String hint) {
        EditText input = new EditText(this);
        input.setHint(hint);
        input.setSingleLine(true);
        input.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_VARIATION_PASSWORD);
        return input;
    }

    private LinearLayout.LayoutParams fullWidth() {
        return new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        );
    }
}
