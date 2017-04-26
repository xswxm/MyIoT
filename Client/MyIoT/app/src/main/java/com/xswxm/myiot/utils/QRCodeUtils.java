package com.xswxm.myiot.utils;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;
import com.xswxm.myiot.R;
import com.xswxm.myiot.global.Constants;

import static com.xswxm.myiot.global.Variables.scanQRType;

/**
 * Created by Air on 4/10/2017.
 */

public class QRCodeUtils {
    private String TAG_QR = "QR";
    public void scanQRCode(Activity activity) {
        IntentIntegrator intentIntegrator = new IntentIntegrator(activity);
        intentIntegrator.setDesiredBarcodeFormats(IntentIntegrator.QR_CODE_TYPES);
        intentIntegrator.setPrompt(activity.getString(R.string.qr_cert_scanning));
        intentIntegrator.setCameraId(0);
        intentIntegrator.setOrientationLocked(true);
        intentIntegrator.setBeepEnabled(false);
        intentIntegrator.initiateScan();
    }

    public void onActivityResult(int requestCode, int resultCode, Intent data, Context context) {
        IntentResult intentResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, data);
        if (intentResult != null) {
            if (intentResult.getContents() != null) {
                switch (scanQRType) {
                    case Constants.SCANDEVICE:
                        Toast.makeText(context, intentResult.getContents(), Toast.LENGTH_SHORT).show();
                        break;
                    case Constants.SCANSERVER:
                        String cert = intentResult.getContents();
                        SpUtils.putString(context, Constants.CERT, cert);
                        Toast.makeText(context, context.getString(R.string.qr_cert_scan_successfully), Toast.LENGTH_SHORT).show();
                        Log.e(TAG_QR, cert);
                        break;
                    default:
                        Toast.makeText(context, intentResult.getContents(), Toast.LENGTH_SHORT).show();
                        break;
                }
            } else {
                Toast.makeText(context, context.getString(R.string.qr_cert_scan_cancelled), Toast.LENGTH_SHORT).show();
            }
        } else {
            onActivityResult(requestCode, resultCode, data, context);
        }
    }
}
