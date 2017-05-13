package com.xswxm.myiot.https;

import android.content.Context;
import android.content.res.AssetManager;
import android.os.AsyncTask;
import android.util.Log;

import com.xswxm.myiot.utils.AssetUtils;

import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.security.KeyManagementException;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManagerFactory;

import static com.xswxm.myiot.global.Variables.address;
import static com.xswxm.myiot.global.Variables.addressopt;
import static com.xswxm.myiot.global.Variables.postText;

/**
 * Created by Air on 4/5/2017.
 */

public abstract class PostTask extends AsyncTask<Object, Object, InputStream> {
    @Override
    protected InputStream doInBackground(Object... params) {
        try {
            //Import self signed certification;
            Certificate ca = new AssetUtils().getCertificate((Context) params[0]);

            // Create a KeyStore containing our trusted CAs
            String keyStoreType = KeyStore.getDefaultType();
            KeyStore keyStore = KeyStore.getInstance(keyStoreType);
            keyStore.load(null, null);
            keyStore.setCertificateEntry("ca", ca);

            // Create a TrustManager that trusts the CAs in our KeyStore
            String tmfAlgorithm = TrustManagerFactory.getDefaultAlgorithm();
            TrustManagerFactory tmf = TrustManagerFactory.getInstance(tmfAlgorithm);
            tmf.init(keyStore);

            // Create an SSLContext that uses our TrustManager
            SSLContext context = SSLContext.getInstance("SSL");
            context.init(null, tmf.getTrustManagers(), null);

            //Skip SSL HostName Verification Java HttpsURLConnection
            HostnameVerifier hostnameVerifier = new HostnameVerifier() {
                @Override
                public boolean verify(String hostname, SSLSession session) {
                    return true;
                }
            };


            URL url = new URL(address + addressopt);

            HttpsURLConnection.setFollowRedirects(false);
            HttpsURLConnection httpsURLConnection = null;
            try {
                httpsURLConnection = (HttpsURLConnection)url.openConnection();
            } catch (Exception e) {
                return null;
            }
            httpsURLConnection.setRequestMethod("HEAD");
            httpsURLConnection.setConnectTimeout(5000); //set timeout to 5 seconds

            //Tell the URLConnection to use a SocketFactory from our SSLContext
            httpsURLConnection.setSSLSocketFactory(context.getSocketFactory());
            //Skip SSL HostName Verification Java HttpsURLConnection
            httpsURLConnection.setHostnameVerifier(hostnameVerifier);

            String urlParameters = postText;
            httpsURLConnection.setRequestMethod("POST");
            httpsURLConnection.setRequestProperty("USER-AGENT", "Mozilla/5.0");
            httpsURLConnection.setRequestProperty("ACCEPT-LANGUAGE", "en-US, en; 0.5");

            httpsURLConnection.setDoOutput(true);
            DataOutputStream dataOutputStream = new DataOutputStream(httpsURLConnection.getOutputStream());

            dataOutputStream.writeBytes(urlParameters);
            dataOutputStream.flush();
            dataOutputStream.close();

            //int responseCode = httpsURLConnection.getResponseCode();
            //String output = "Request URL: " + url;
            //output += System.getProperty("line.separator") + "Request Parameters: " + urlParameters;
            //output += System.getProperty("line.separator") + "Request Code: " + responseCode;

/*            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(httpsURLConnection.getInputStream()));
            return bufferedReader.readLine();*/
            return httpsURLConnection.getInputStream();

        } catch (IOException | CertificateException | NoSuchAlgorithmException | KeyManagementException | KeyStoreException e) {
            e.printStackTrace();
        }
        return null;
    }
}