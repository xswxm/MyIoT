package com.xswxm.myiot.utils;

import android.content.Context;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.BitmapShader;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Shader;
import android.os.StrictMode;

import com.xswxm.myiot.DrawerActivity;
import com.xswxm.myiot.global.Constants;

import java.io.BufferedInputStream;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;

/**
 * Created by Air on 4/5/2017.
 */

public class AssetUtils {
    //Decode stream into bitmap
    private Bitmap getBitmap(AssetManager assetManager, String fileName) {
        try {
            InputStream inputStream = assetManager.open(fileName);
            return BitmapFactory.decodeStream(inputStream);
        } catch (IOException e) {
            return null;
        }
    }
    //Read a pic from asset folder
    public Bitmap getRoundedBitmap(AssetManager assetManager, String fileName) {
        Bitmap bitmap = getBitmap(assetManager, fileName);
        return getRoundedBitmap(bitmap);
    }
    //Convert a bitmap into round bitmap (picture)
    private Bitmap getRoundedBitmap(Bitmap bitmap) {
        assert bitmap != null;
        Bitmap bitmapRounded = Bitmap.createBitmap(bitmap.getWidth(), bitmap.getHeight(), bitmap.getConfig());
        Canvas canvas = new Canvas(bitmapRounded);
        Paint paint = new Paint();
        paint.setAntiAlias(true);
        paint.setShader(new BitmapShader(bitmap, Shader.TileMode.CLAMP, Shader.TileMode.CLAMP));
        canvas.drawRoundRect((new RectF(0, 0, bitmap.getWidth(), bitmap.getHeight())), bitmap.getWidth() / 2, bitmap.getWidth() / 2, paint);
        return bitmapRounded;
    }
    //Convert a inputstream into round bitmap
    public Bitmap getRoundedBitmap(InputStream inputStream) {
        BufferedInputStream bufferedInputStream = new BufferedInputStream(inputStream);

        //Prevent from image reading failure
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);
        Bitmap bitmap = BitmapFactory.decodeStream(bufferedInputStream);

        return getRoundedBitmap(bitmap);
    }

    public Certificate getCertificate(Context context) {
        try {
            CertificateFactory certificateFactory = CertificateFactory.getInstance("X.509");

            //InputStream inputStream = assetManager.open("cert.pem");
            String cert = SpUtils.getString(context, Constants.CERT);
            InputStream inputStream = new ByteArrayInputStream(cert.getBytes(StandardCharsets.UTF_8));

            InputStream caInput = new BufferedInputStream(inputStream);
            return certificateFactory.generateCertificate(caInput);
        } catch (CertificateException e) {
            return null;
        }
    }
}
