package com.example.vulnerablekiosk;

import android.app.Activity;
import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.IOException;

public class NetworkDemoActivity extends Activity {
    private TextView result;
    private InsecureApiClient apiClient;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        apiClient = new InsecureApiClient(this);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(40, 40, 40, 40);

        TextView title = new TextView(this);
        title.setText("Demo de Rede Insegura");
        title.setTextSize(22);
        title.setGravity(Gravity.CENTER_HORIZONTAL);

        TextView description = new TextView(this);
        description.setText("Chamadas HTTP reais para mock-server local. Dados sao ficticios e propositalmente vulneraveis.");
        description.setPadding(0, 20, 0, 20);

        Button loginButton = button("Enviar Login Mock HTTP");
        loginButton.setOnClickListener(view -> execute("login", () -> apiClient.sendLoginMock()));

        Button paymentButton = button("Enviar Pagamento Mock HTTP");
        paymentButton.setOnClickListener(view -> execute("payment", () -> apiClient.sendPaymentMock()));

        Button statusButton = button("Consultar Status HTTP");
        statusButton.setOnClickListener(view -> execute("status", () -> apiClient.getStatusMock()));

        result = new TextView(this);
        result.setText("Aguardando chamada HTTP para o mock-server.");
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

    private void execute(String label, NetworkCall call) {
        result.setText("Executando chamada HTTP mock: " + label);
        new Thread(() -> {
            try {
                String response = call.run();
                runOnUiThread(() -> result.setText("Resposta mock recebida:\n" + response));
            } catch (IOException exception) {
                runOnUiThread(() -> result.setText("Falha na chamada HTTP mock. Verifique se o mock-server esta rodando."));
            }
        }).start();
    }

    private interface NetworkCall {
        String run() throws IOException;
    }
}
