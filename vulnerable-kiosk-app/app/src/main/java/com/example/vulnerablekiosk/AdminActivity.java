package com.example.vulnerablekiosk;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;

public class AdminActivity extends Activity {
    private static final String TAG = "VulnerableKioskAdmin";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText("Area Administrativa - Laboratorio");
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER_HORIZONTAL);

        EditText passwordInput = new EditText(this);
        passwordInput.setHint("Senha administrativa ficticia");
        passwordInput.setSingleLine(true);

        Button loginButton = new Button(this);
        loginButton.setText("Entrar");

        TextView result = new TextView(this);
        result.setTextSize(16);
        result.setPadding(0, 24, 0, 0);

        loginButton.setOnClickListener(view -> {
            String password = passwordInput.getText().toString();

            // Vulneravel propositalmente: senha hardcoded e log de segredo ficticio.
            Log.d(TAG, "Tentativa admin com senha ficticia: " + password);
            Log.i(TAG, "Senha esperada hardcoded: " + LabSecrets.ADMIN_PASSWORD);

            if (LabSecrets.ADMIN_PASSWORD.equals(password)) {
                String weakHash = CryptoUtils.md5(password);
                result.setText("Acesso liberado em laboratorio. Hash MD5: " + weakHash);
            } else {
                result.setText("Senha incorreta. Dica de laboratorio: admin123");
            }
        });

        root.addView(title);
        root.addView(passwordInput, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
        ));
        root.addView(loginButton);
        root.addView(result);

        setContentView(root);
    }
}
