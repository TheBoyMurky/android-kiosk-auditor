package com.example.vulnerablekiosk;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.TextView;

public class ExportedDebugActivity extends Activity {
    private static final String TAG = "VulnerableExportedDebug";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Activity exportada indevidamente para demonstracao academica.
        Log.i(TAG, "Painel debug exportado acessado. Token ficticio: " + LabSecrets.SECRET_TOKEN);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.CENTER);
        root.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText("Painel Debug Exportado");
        title.setTextSize(24);
        title.setGravity(Gravity.CENTER);

        TextView warning = new TextView(this);
        warning.setText("Componente vulneravel propositalmente exportado para laboratorio.");
        warning.setTextSize(16);
        warning.setGravity(Gravity.CENTER);
        warning.setPadding(0, 20, 0, 0);

        root.addView(title);
        root.addView(warning);
        setContentView(root);
    }
}
