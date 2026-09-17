package com.example.hardenedkiosk;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.admin.DevicePolicyManager;
import android.content.Context;
import android.os.Build;

public final class KioskModeManager {
    public enum Result {
        STARTED,
        STOPPED,
        NOT_AUTHORIZED,
        NOT_SUPPORTED,
        ERROR
    }

    private final Activity activity;
    private final DevicePolicyManager devicePolicyManager;
    private final ActivityManager activityManager;

    public KioskModeManager(Activity activity) {
        this.activity = activity;
        this.devicePolicyManager = (DevicePolicyManager) activity.getSystemService(Context.DEVICE_POLICY_SERVICE);
        this.activityManager = (ActivityManager) activity.getSystemService(Context.ACTIVITY_SERVICE);
    }

    public Result startControlledLockTask() {
        // Demonstracao controlada. Em producao, o app deve ser Device Owner ou
        // gerenciado por MDM para uso correto de kiosk.
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
            return Result.NOT_SUPPORTED;
        }

        try {
            String packageName = activity.getPackageName();
            boolean permitted = devicePolicyManager != null
                    && devicePolicyManager.isLockTaskPermitted(packageName);
            if (!permitted) {
                return Result.NOT_AUTHORIZED;
            }

            activity.startLockTask();
            return Result.STARTED;
        } catch (RuntimeException exception) {
            SafeLogger.warn("KioskModeManager", "Falha generica ao iniciar modo kiosk demonstrativo.", exception);
            return Result.ERROR;
        }
    }

    public Result stopControlledLockTask() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) {
            return Result.NOT_SUPPORTED;
        }

        try {
            if (isInLockTaskMode()) {
                activity.stopLockTask();
                return Result.STOPPED;
            }
            return Result.NOT_AUTHORIZED;
        } catch (RuntimeException exception) {
            SafeLogger.warn("KioskModeManager", "Falha generica ao encerrar modo kiosk demonstrativo.", exception);
            return Result.ERROR;
        }
    }

    public boolean isInLockTaskMode() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M || activityManager == null) {
            return false;
        }
        return activityManager.getLockTaskModeState() != ActivityManager.LOCK_TASK_MODE_NONE;
    }
}
