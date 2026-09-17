package com.example.vulnerablekiosk;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class WebViewActivity extends Activity {
    private static final String TAG = "VulnerableKioskWebView";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        WebView webView = new WebView(this);
        WebSettings settings = webView.getSettings();

        // WebView insegura propositalmente para fins academicos.
        settings.setJavaScriptEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setDomStorageEnabled(true);

        webView.setWebViewClient(new WebViewClient());

        // URL HTTP ficticia mantida para deteccao estatica. Nao envie dados reais.
        Log.i(TAG, "Carregando URL insegura ficticia: " + LabSecrets.INSECURE_LOGIN_URL);
        webView.loadUrl(LabSecrets.INSECURE_LOGIN_URL);

        setContentView(webView);
    }
}
