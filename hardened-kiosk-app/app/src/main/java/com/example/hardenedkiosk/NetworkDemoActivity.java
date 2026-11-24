package com.example.hardenedkiosk;

import android.app.Activity;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class NetworkDemoActivity extends Activity {
    private TextView result;
    private SecureApiClient apiClient;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        SecureStorage storage = new SecureStorage(this);
        apiClient = new SecureApiClient(storage);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText("Demo de Rede Segura");
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER_HORIZONTAL);

        TextView description = new TextView(this);
        description.setText("Chamadas HTTPS reais para o servidor local, com certificado validado e cleartext bloqueado.");
        description.setPadding(0, 20, 0, 20);

        Button loginButton = button("Executar Login Seguro");
        loginButton.setOnClickListener(view -> execute(apiClient::executeLogin));

        Button paymentButton = button("Executar Pagamento Seguro");
        paymentButton.setOnClickListener(view -> execute(apiClient::executePayment));

        Button statusButton = button("Consultar Status Seguro");
        statusButton.setOnClickListener(view -> execute(apiClient::executeStatus));

        result = new TextView(this);
        result.setText("Aguardando chamada HTTPS.");
        result.setPadding(0, 24, 0, 0);

        root.addView(title);
        root.addView(description);
        root.addView(loginButton);
        root.addView(paymentButton);
        root.addView(statusButton);
        root.addView(result);

        setContentView(root);
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

    private void show(String message) {
        result.setText(message);
    }

    private void execute(NetworkCall call) {
        show("Executando chamada HTTPS...");
        executor.execute(() -> {
            String message = call.run();
            runOnUiThread(() -> show(message));
        });
    }

    @Override
    protected void onDestroy() {
        executor.shutdownNow();
        super.onDestroy();
    }

    private interface NetworkCall {
        String run();
    }
}
