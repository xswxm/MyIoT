package com.xswxm.myiot;

import android.content.Intent;
import android.content.res.Configuration;
import android.os.Bundle;
import android.support.v4.widget.SwipeRefreshLayout;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.CompoundButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import com.xswxm.myiot.adddevice.AddLocalDeviceActivity;
import com.xswxm.myiot.configuredevice.ConfigureLocalDeviceActivity;
import com.xswxm.myiot.controller.MyButton;
import com.xswxm.myiot.controller.MySeekBar;
import com.xswxm.myiot.controller.MySwitch;
import com.xswxm.myiot.controller.MyValue;
import com.xswxm.myiot.global.Constants;
import com.xswxm.myiot.utils.AssetUtils;
import com.xswxm.myiot.utils.QRCodeUtils;
import com.xswxm.myiot.utils.SpUtils;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URISyntaxException;
import java.security.KeyManagementException;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.util.ArrayList;
import java.util.HashMap;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManagerFactory;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;


import static android.R.color.holo_blue_light;
import static com.xswxm.myiot.global.Constants.RESULT_ADD;
import static com.xswxm.myiot.global.Constants.RESULT_CONFIG;
import static com.xswxm.myiot.global.Variables.address;
import static com.xswxm.myiot.global.Variables.addressopt;
import static com.xswxm.myiot.global.Variables.askforconfig;
import static com.xswxm.myiot.global.Variables.classNameList;
import static com.xswxm.myiot.global.Variables.password;
import static com.xswxm.myiot.global.Variables.postText;
import static com.xswxm.myiot.global.Variables.scanQRType;
import static com.xswxm.myiot.global.Variables.syncinterval;
import static com.xswxm.myiot.global.Variables.token;
import static com.xswxm.myiot.global.Variables.username;
import static com.xswxm.myiot.global.Variables.autologin;
import com.xswxm.myiot.https.*;


public class DrawerActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {

    private Socket socket;
    private LinearLayout deviceList;
    private NavigationView navigationView;
    private SwipeRefreshLayout swipeRefreshLayout;
    private String TAG_Socket = "Socket";
    private String TAG_HTTPS = "HTTPS";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_drawer);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();


        navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        // Disable 'refresh' button and 'add device' button cause users have not signed in.
        deviceList = (LinearLayout) findViewById(R.id.deviceList);
        setNavItem(R.id.nav_refresh, getString(R.string.nav_refresh), false);
        setNavItem(R.id.nav_add_device, getString(R.string.nav_add_device), false);

        swipeRefreshLayout = (SwipeRefreshLayout) findViewById(R.id.swipeRefreshLayout);
        swipeRefreshLayout.setColorScheme(holo_blue_light);
        swipeRefreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                Menu menu = navigationView.getMenu();
                MenuItem menuItem = menu.findItem(R.id.nav_refresh);
                if (menuItem.isEnabled()) {
                    getAllDevices();
                } else {
                    //Toast.makeText(DrawerActivity.this, getString(R.string.notify_login), Toast.LENGTH_SHORT).show();
                    //swipeRefreshLayout.setRefreshing(false);
                    login();
                }
            }
        });

        //Check AUTOLOGIN value in sharedpreferences and sign in automatically if the value ids ture.
        Log.e("autologin: ", SpUtils.getBoolean(DrawerActivity.this, Constants.AUTOLOGIN).toString());
        if (SpUtils.getBoolean(DrawerActivity.this, Constants.AUTOLOGIN)) {
            login();
        }
    }

    private void setNavItem(int itemID, String title, boolean value) {
        Menu menu = this.navigationView.getMenu();
        MenuItem menuItem = menu.findItem(itemID);
        menuItem.setTitle(title);
        menuItem.setEnabled(value);
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.drawer, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        switch (id) {
            case R.id.action_settings:
                Intent intent = new Intent(this, SettingsActivity.class);
                startActivity(intent);
                return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();
        Intent intent;
        switch (id) {
            case R.id.nav_login:
                if (item.getTitle().equals(getString(R.string.nav_login))) {
                    login();
                } else {
                    socket.disconnect();
                }
                break;
            case R.id.nav_refresh:
                getAllDevices();
                break;
            case R.id.nav_add_device:
                intent = new Intent(this, AddLocalDeviceActivity.class);
                startActivityForResult(intent, RESULT_ADD);
                break;
/*                intent = new Intent(this, com.xswxm.adddevice.GuideActivity.class);
                startActivity(intent);*/
                //finish();
            case R.id.nav_update_cert:
                scanQRType = Constants.SCANSERVER;
                new QRCodeUtils().scanQRCode(this);
                break;
            case R.id.nav_settings:
                intent = new Intent(this, SettingsActivity.class);
                startActivity(intent);
                return true;
            case R.id.nav_about:
                Toast.makeText(this, "Developing...it is used for testing purpose currently.", Toast.LENGTH_SHORT).show();
/*                intent = new Intent(this, com.xswxm.adddevice.GuideActivity.class);
                startActivity(intent);*/
                //finish();
                return true;
                //break;
        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
    }

    /*
     * Reload configurations in sharedpreferencs and compare with current values in memory
     * post changes to the server.
     */
    @Override
    protected void onResume() {
        super.onResume();

        detectIllegalSyncInterval();

        if (!askforconfig) {
            loadPreferences();
            return;
        }

        askforconfig = false;
        autologin = SpUtils.getBoolean(DrawerActivity.this, Constants.AUTOLOGIN);
        postText = "";
        String text = SpUtils.getString(DrawerActivity.this, Constants.USERNAME);
        if (!text.equals(username)) {
            username = text;
            postText += "username=" + username;
        }
        text = SpUtils.getString(DrawerActivity.this, Constants.PASSWORD);
        if (!text.equals(password)) {
            password = text;
            if (!postText.isEmpty()) {
                postText += "&";
            }
            postText += "password=" + password;
        }
        text = SpUtils.getString(DrawerActivity.this, Constants.ADDRESS);
        if (!text.equals(address)) {
            address = text;
            if (!postText.isEmpty()) {
                postText += "&";
            }
            postText += "address=" + address;
        }
        int interval = SpUtils.getInt(DrawerActivity.this, Constants.SYNCINTERVAL);
        if (interval != syncinterval) {
            syncinterval = interval;
            if (!postText.isEmpty()) {
                postText += "&";
            }
            postText += "syncinterval=" + Integer.toString(syncinterval);
        }
        if (!postText.isEmpty()) {
            postText += "&token=" + token;
            addressopt = "configuration";
            //AssetManager assManager = DrawerActivity.this.getAssets();
            new ModifyConfiguration().execute(DrawerActivity.this);
            Log.e(TAG_HTTPS, "Configuration update request sent.");
        }

    }

    /*
     * It is a post request, which used to send new configurations to the server.
     */
    private class ModifyConfiguration extends PostTask {
        @Override
        protected InputStream doInBackground(Object... params) {
            return super.doInBackground(params);
        }

        @Override
        protected void onPostExecute(InputStream is) {
            super.onPostExecute(is);
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(is));
            try {
                String responseText = bufferedReader.readLine();
                switch (responseText) {
                    case "401":
                        responseText = getString(R.string.notify_config_authorization_failed);
                        break;
                    case "200":
                    default:
                        responseText = getString(R.string.notify_config_successfully);
                        break;
                }
                Toast.makeText(DrawerActivity.this, responseText, Toast.LENGTH_SHORT).show();
            } catch (IOException e) {
                e.printStackTrace();
                Toast.makeText(DrawerActivity.this,  getString(R.string.notify_connection_failed), Toast.LENGTH_SHORT).show();
            }
        }
    }

    /*
     * This is a temp solution since in the 'preference' page, all values (EditPreference) are stores as strings.
     * While the sync interval should be an integer.
     */
    private void detectIllegalSyncInterval() {
        try {
            int value = 0;
            String text = SpUtils.getString(this, Constants.SYNCINTERVAL);
            if (!text.isEmpty()) {
                try {
                    value = Integer.parseInt(text);
                } catch (Exception ignore) {
                    value = Integer.MAX_VALUE;
                }
            }
            SpUtils.removeKey(this, Constants.SYNCINTERVAL);
            SpUtils.putInt(this, Constants.SYNCINTERVAL, value);
        }catch (Exception ignore) {
        }
    }

    /*
     * Load necessary values from the sharedpreferences.
     */
    private void loadPreferences() {
        detectIllegalSyncInterval();
        username = SpUtils.getString(DrawerActivity.this, Constants.USERNAME);
        password = SpUtils.getString(DrawerActivity.this, Constants.PASSWORD);
        address = SpUtils.getString(DrawerActivity.this, Constants.ADDRESS);
        syncinterval = SpUtils.getInt(DrawerActivity.this, Constants.SYNCINTERVAL);
        autologin = SpUtils.getBoolean(DrawerActivity.this, Constants.AUTOLOGIN);
    }

    /*
     * Establish socketio connection and connect to the server.
     */
    private void connectServer(String token) {
        try {
            //Import self signed certification
            Certificate ca = new AssetUtils().getCertificate(this);

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
            SSLContext mySSLContext = SSLContext.getInstance("SSL");
            mySSLContext.init(null, tmf.getTrustManagers(), null);

            //Skip SSL HostName Verification Java HttpsURLConnection
            HostnameVerifier myHostnameVerifier = new HostnameVerifier() {
                @Override
                public boolean verify(String hostname, SSLSession session) {
                    return true;
                }
            };

            // Default settings for all sockets
            IO.setDefaultSSLContext(mySSLContext);
            IO.setDefaultHostnameVerifier(myHostnameVerifier);
            // Set as an option
            IO.Options opts = new IO.Options();
            opts.sslContext = mySSLContext;
            opts.hostnameVerifier = myHostnameVerifier;
            //opts.path = "/devices";
            opts.query = "token=" + token;
            //opts.port = 8888;

            Log.e(TAG_Socket, "IP Address -  " + address);
            socket = IO.socket(address + "devices", opts);

            socket.on(Socket.EVENT_CONNECT, onConnect);
            socket.on(Socket.EVENT_DISCONNECT, onDisconnect);
            socket.on("set", onSetDevice);
            socket.on("add", onAddDevice);
            socket.on("adddone", onAddDeviceDone);
            socket.on("remove", onRemoveDevice);
            socket.on("configure", onConfigureDevice);
            socket.on("setClassNameList", onSetClassNameList);
            socket.on("notify", onNotify);
            socket.connect();
            Log.e(TAG_Socket, "Signin Info Emitted - ");
            setNavItem(R.id.nav_login, getString(R.string.nav_logout), true);

        } catch (URISyntaxException | IOException | CertificateException | KeyStoreException | NoSuchAlgorithmException | KeyManagementException e) {
            e.printStackTrace();
        }
    }

    /*
     * Get all the devices connected to the server.
     * 1, set swipeRefreshLayout's refreshing to true
     * 2. disable nav_refresh
     */
    private void getAllDevices() {
        deviceList.removeAllViews();
        swipeRefreshLayout.setRefreshing(true);
        setNavItem(R.id.nav_refresh, getString(R.string.nav_refresh), false);
        socket.emit("getAll");
        Log.e(TAG_Socket, "getAllDevices Emitted!");
    }

    /*
     * Get a particular device connected to the server.
     */
    private void getDevice(int deviceID) {
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", deviceID);
            socket.emit("get", jsonObject);
            Log.e(TAG_Socket, "getDevice Emitted - " + jsonObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "getDevice Failed!");
        }
    }

    /*
     * Set a particular device connected to the server.
     */
    private void setDevice(int deviceID, String deviceCategory, Object deviceValue) {
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", deviceID);
            //jsonObject.put("category", deviceCategory);
            switch (deviceCategory) {
                case "Switch":
                    jsonObject.put("value", (boolean)deviceValue);
                    break;
                case "Value":
                    jsonObject.put("value", (int)deviceValue);
                    break;
                case "SeekBar":
                    jsonObject.put("value", (int)deviceValue);
                    break;
                case "Button":
                    jsonObject.put("value", (boolean)deviceValue);
                    break;
            }
            socket.emit("set", jsonObject);
            Log.e(TAG_Socket, "setDevice Emitted - " + jsonObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "setDevice Failed!");
        }
    }
    /*
     * Add a particular local device to the server.
     */
    private void addDevice(String deviceClassName, String deviceTitle, int devicePort) {
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("classname", deviceClassName);
            jsonObject.put("title", deviceTitle);
            jsonObject.put("port", devicePort);
            socket.emit("add", jsonObject);
            Log.e(TAG_Socket, "addDevice Emitted - " + jsonObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "addDevice Failed!");
        }
    }
    private void addDevice(String deviceClassName, String deviceTitle) {
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("classname", deviceClassName);
            jsonObject.put("title", deviceTitle);
            socket.emit("add", jsonObject);
            Log.e(TAG_Socket, "addDevice Emitted - " + jsonObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "addDevice Failed!");
        }
    }
    /*
     * Configure a particular local device to the server.
     */
    private void configureDevice(int deviceID, String deviceTitle, int devicePort) {
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", deviceID);
            jsonObject.put("title", deviceTitle);
            jsonObject.put("port", devicePort);
            socket.emit("configure", jsonObject);
            Log.e(TAG_Socket, "configureDevice Emitted - " + jsonObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "configureDevice Failed!");
        }
    }
    private void configureDevice(int deviceID, String deviceTitle) {
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", deviceID);
            jsonObject.put("title", deviceTitle);
            socket.emit("configure", jsonObject);
            Log.e(TAG_Socket, "configureDevice Emitted - " + jsonObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "configureDevice Failed!");
        }
    }
    /*
     * Add a particular local device to the server.
     */
    private void removeDevice(int deviceID) {
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", deviceID);
            socket.emit("remove", jsonObject);
            Log.e(TAG_Socket, "removeDevice Emitted - " + jsonObject.toString());
        } catch (JSONException e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "removeDevice Failed!");
        }
    }
    /*
     * Add a particular local device to the server.
     */
    private void getClassNameList() {
        try {
            socket.emit("getclassnamelist");
            Log.e(TAG_Socket, "getClassNameList Emitted!");
        } catch (Exception e) {
            e.printStackTrace();
            Log.e(TAG_Socket, "getClassNameList Failed!");
        }
    }
    /*
     * Once we have connected to the server, we need to get our avatar and nick name (username here).
     * Furthermore, it also enables some buttons/functions, including refresh devices and add device.
     */
    private Emitter.Listener onConnect = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            //islogin = true;
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    //Set UserName and get Avatar
                    TextView textView = (TextView) navigationView.getHeaderView(0).findViewById(R.id.avatar_name);
                    textView.setText(username);

                    postText = "token=" + token;
                    addressopt = "avatar";
                    new GetAvatar().execute(DrawerActivity.this);
                    Log.e(TAG_HTTPS, "Avatar request sent.");

                    //Get devices from the server
                    getAllDevices();
                    getClassNameList();
                }
            });
        }
    };
    /*
     * Once we are disconnected, disable some buttons/functions.
     */
    private Emitter.Listener onDisconnect = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            //islogin = false;
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    deviceList.removeAllViews();
                    setNavItem(R.id.nav_login, getString(R.string.nav_login), true);
                    setNavItem(R.id.nav_refresh, getString(R.string.nav_refresh), false);
                    setNavItem(R.id.nav_add_device, getString(R.string.nav_add_device), false);
                    swipeRefreshLayout.setRefreshing(false);

                    //Remove UserName and get Avatar
                    TextView textView = (TextView) navigationView.getHeaderView(0).findViewById(R.id.avatar_name);
                    textView.setText("");
                    ImageView imageAvatar = (ImageView) navigationView.getHeaderView(0).findViewById(R.id.imageAvatar);
                    imageAvatar.setImageBitmap(null);

                    socket.close();
                    Toast.makeText(DrawerActivity.this, getString(R.string.notify_logout_successfully), Toast.LENGTH_SHORT).show();
                }
            });
        }
    };

    /*
     * Need further development.... dis/enable device
     * Receive changes of devices connected to the server
     * and response to these changes.
     */
    private Emitter.Listener onSetDevice = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        Log.e(TAG_Socket, "onSetDevice received - " + args[0].toString());
                        JSONObject jsonObject = (JSONObject) args[0];
                        int deviceID = jsonObject.getInt("id");
                        String deviceCategory = jsonObject.getString("category");
                        boolean deviceFeasible = jsonObject.getBoolean("feasible");
                        Object deviceValue = jsonObject.get("value");
                        Object device = deviceList.findViewById(deviceID);
                        switch (deviceCategory) {
                            case "Switch":
                                MySwitch mySwitch = (MySwitch)device;
                                mySwitch.setChecked((boolean)deviceValue);
                                mySwitch.setDeviceEnabled(deviceFeasible);
                                break;
                            case "Value":
                                MyValue myValue = (MyValue)device;
                                myValue.setDeviceValue((String)deviceValue);
                                myValue.setDeviceEnabled(deviceFeasible);
                                break;
                            case "SeekBar":
                                MySeekBar mySeekBar = (MySeekBar)device;
                                mySeekBar.setDeviceSeekBar((String)deviceValue);
                                mySeekBar.setDeviceValue((String)deviceValue);
                                mySeekBar.setDeviceEnabled(deviceFeasible);
                                break;
                            case "Button":
                                MyButton myButton = (MyButton)device;
                                myButton.setDeviceEnabled(deviceFeasible);
                                myButton.setDeviceAnimation((boolean)deviceValue);
                                break;
                            default:
                                break;
                        }
                        Log.e(TAG_Socket, "setDevice succeed!");
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.e(TAG_Socket, "setDevice failed!");
                    }
                }
            });

        }
    };
    /*
     * Receive new devices connected to the server,
     * add them to our list and assign events to them.
     */
    private Emitter.Listener onAddDevice = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            Runnable runnable = new Runnable() {
                @Override
                public void run() {
                    {
                        try {
                            Log.e(TAG_Socket, "onAddDevice received - " + args[0].toString());
                            JSONObject jsonObject = (JSONObject) args[0];
                            int deviceID = jsonObject.getInt("id");
                            String deviceTitle = jsonObject.getString("title");
                            int devicePort = -1;
                            if (jsonObject.has("port")) {
                                devicePort = jsonObject.getInt("port");
                            }
                            String deviceCategory = jsonObject.getString("category");
                            final Object deviceValue = jsonObject.get("value");
                            switch (deviceCategory) {
                                case "Switch":
                                    final MySwitch mySwitch = new MySwitch(DrawerActivity.this);
                                    mySwitch.setTitle(deviceTitle);
                                    mySwitch.setId(deviceID);
                                    mySwitch.devicePort = devicePort;
                                    mySwitch.setPadding(0,16,0,16);
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            mySwitch.setChecked((boolean)deviceValue);
                                            deviceList.addView(mySwitch);
                                        }
                                    });
                                    mySwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                                        @Override
                                        public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                                            mySwitch.setDeviceEnabled(false);
                                            setDevice(mySwitch.getId(), "Switch", (Object)isChecked);
                                        }
                                    });
                                    mySwitch.setOnConfigureClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            Intent intent = new Intent(DrawerActivity.this, ConfigureLocalDeviceActivity.class);
                                            intent.putExtra("com.xswxm.myiot.deviceID", mySwitch.getId());
                                            intent.putExtra("com.xswxm.myiot.deviceTitle", mySwitch.getTitle());
                                            intent.putExtra("com.xswxm.myiot.devicePort", mySwitch.devicePort);
                                            startActivityForResult(intent, RESULT_CONFIG);
                                        }
                                    });
                                    mySwitch.setOnRemoveClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            mySwitch.setDeviceEnabled(false);
                                            removeDevice(mySwitch.getId());
                                        }
                                    });
                                    break;
                                case "Value":
                                    final MyValue myValue = new MyValue(DrawerActivity.this);
                                    myValue.setTitle(deviceTitle);
                                    myValue.setId(deviceID);
                                    myValue.devicePort = devicePort;
                                    myValue.setPadding(0,16,0,16);
                                    myValue.setDeviceValue((String)deviceValue);
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            deviceList.addView(myValue);
                                        }
                                    });
                                    myValue.setOnValueClickLisener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            myValue.setDeviceEnabled(false);
                                            getDevice(myValue.getId());
                                        }
                                    });
                                    myValue.setOnConfigureClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            Intent intent = new Intent(DrawerActivity.this, ConfigureLocalDeviceActivity.class);
                                            intent.putExtra("com.xswxm.myiot.deviceID", myValue.getId());
                                            intent.putExtra("com.xswxm.myiot.deviceTitle", myValue.getTitle());
                                            intent.putExtra("com.xswxm.myiot.devicePort", myValue.devicePort);
                                            startActivityForResult(intent, RESULT_CONFIG);
                                        }
                                    });
                                    myValue.setOnRemoveClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            myValue.setDeviceEnabled(false);
                                            removeDevice(myValue.getId());
                                        }
                                    });
                                    break;
                                case "SeekBar":
                                    final MySeekBar mySeekBar = new MySeekBar(DrawerActivity.this);
                                    mySeekBar.setTitle(deviceTitle);
                                    mySeekBar.setId(deviceID);
                                    mySeekBar.devicePort = devicePort;
                                    mySeekBar.setPadding(0,16,0,16);
                                    mySeekBar.setDeviceValue((String)deviceValue);
                                    mySeekBar.setDeviceSeekBar((String)deviceValue);
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            deviceList.addView(mySeekBar);
                                        }
                                    });
                                    mySeekBar.setOnValueClickLisener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            mySeekBar.setDeviceEnabled(false);
                                            getDevice(mySeekBar.getId());
                                        }
                                    });
                                    mySeekBar.setOnConfigureClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            Intent intent = new Intent(DrawerActivity.this, ConfigureLocalDeviceActivity.class);
                                            intent.putExtra("com.xswxm.myiot.deviceID", mySeekBar.getId());
                                            intent.putExtra("com.xswxm.myiot.deviceTitle", mySeekBar.getTitle());
                                            intent.putExtra("com.xswxm.myiot.devicePort", mySeekBar.devicePort);
                                            startActivityForResult(intent, RESULT_CONFIG);
                                        }
                                    });
                                    mySeekBar.setOnRemoveClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            mySeekBar.setDeviceEnabled(false);
                                            removeDevice(mySeekBar.getId());
                                        }
                                    });
                                    mySeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
                                        @Override
                                        public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                                            if (seekBar.isEnabled()) {
                                                mySeekBar.setDeviceValue(Integer.toString(progress) + " %");
                                            }
                                        }

                                        @Override
                                        public void onStartTrackingTouch(SeekBar seekBar) {
                                        }

                                        @Override
                                        public void onStopTrackingTouch(SeekBar seekBar) {
                                            mySeekBar.setDeviceEnabled(false);
                                            setDevice(mySeekBar.getId(), "SeekBar", (Object)seekBar.getProgress());
                                        }
                                    });
                                    break;
                                case "Button":
                                    final MyButton myButton = new MyButton(DrawerActivity.this);
                                    myButton.setTitle(deviceTitle);
                                    myButton.setId(deviceID);
                                    myButton.devicePort = devicePort;
                                    myButton.setPadding(0,16,0,16);
                                    myButton.setDeviceAnimation((boolean)deviceValue);
                                    runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            deviceList.addView(myButton);
                                        }
                                    });
                                    myButton.setOnConfigureClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            Intent intent = new Intent(DrawerActivity.this, ConfigureLocalDeviceActivity.class);
                                            intent.putExtra("com.xswxm.myiot.deviceID", myButton.getId());
                                            intent.putExtra("com.xswxm.myiot.deviceTitle", myButton.getTitle());
                                            intent.putExtra("com.xswxm.myiot.devicePort", myButton.devicePort);
                                            startActivityForResult(intent, RESULT_CONFIG);
                                        }
                                    });
                                    myButton.setOnRemoveClickListener(new View.OnClickListener() {
                                        @Override
                                        public void onClick(View v) {
                                            myButton.setDeviceEnabled(false);
                                            removeDevice(myButton.getId());
                                        }
                                    });
                                    myButton.setOnTouchLisener(new View.OnTouchListener() {
                                        @Override
                                        public boolean onTouch(View v, MotionEvent event) {
                                            switch (event.getAction()) {
                                                case MotionEvent.ACTION_DOWN:
                                                    myButton.setDeviceAnimation(true);
                                                    setDevice(myButton.getId(), "Button", (Object)true);
                                                    break;
                                                case MotionEvent.ACTION_UP:
                                                    myButton.setDeviceAnimation(false);
                                                    setDevice(myButton.getId(), "Button", (Object)false);
                                                    break;
                                            }
                                            return true;
                                        }
                                    });
                                    break;
                                default:
                                    break;
                            }
                            Log.e(TAG_Socket, "onAddDevice succeed!");
                        } catch (Exception e) {
                            e.printStackTrace();
                            Log.e(TAG_Socket, "onAddDevice failed!");
                        }
                    }
                }
            };
            runnable.run();
        }
    };
    /*
     * Add device finished:
     *  1. set swipeRefreshLayout's refreshing to false
     *  2. enable nav_refresh
     */
    private Emitter.Listener onAddDeviceDone = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        Log.e(TAG_Socket, "onAddDeviceDone received");
                        setNavItem(R.id.nav_refresh, getString(R.string.nav_refresh), true);
                        swipeRefreshLayout.setRefreshing(false);
                        Log.e(TAG_Socket, "onAddDeviceDone succeed!");
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.e(TAG_Socket, "onAddDeviceDone failed!");
                    }
                }
            });

        }
    };
    /*
     * Receive removed devices connected to the server
     * and remove them from our list.
     */
    private Emitter.Listener onRemoveDevice = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        Log.e(TAG_Socket, "onRemoveDevice received - " + args[0].toString());
                        JSONObject jsonObject = (JSONObject) args[0];
                        int deviceID = jsonObject.getInt("id");
                        View device = deviceList.findViewById(deviceID);
                        deviceList.removeView(device);
                        Log.e(TAG_Socket, "onRemoveDevice succeed!");
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.e(TAG_Socket, "onRemoveDevice failed!");
                    }
                }
            });

        }
    };
    /*
     * Receive changes of a device from the server
     * and configure the device
     */
    private Emitter.Listener onConfigureDevice = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        Log.e(TAG_Socket, "onConfigureDevice received - " + args[0].toString());
                        JSONObject jsonObject = (JSONObject) args[0];
                        int deviceID = jsonObject.getInt("id");
                        String deviceTitle = jsonObject.getString("title");
                        View device = deviceList.findViewById(deviceID);
                        String deviceCategory = jsonObject.getString("category");
                        switch (deviceCategory) {
                            case "Switch":
                                MySwitch mySwitch = (MySwitch)device;
                                mySwitch.setTitle(deviceTitle);
                                break;
                            case "Value":
                                MyValue myValue = (MyValue)device;
                                myValue.setTitle(deviceTitle);
                                break;
                            case "SeekBar":
                                MySeekBar mySeekBar = (MySeekBar)device;
                                mySeekBar.setTitle(deviceTitle);
                                break;
                            case "Button":
                                MyButton myButton = (MyButton)device;
                                myButton.setTitle(deviceTitle);
                                break;
                        }
                        Log.e(TAG_Socket, "onConfigureDevice succeed!");
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.e(TAG_Socket, "onConfigureDevice failed!");
                    }
                }
            });

        }
    };
    /*
     * Receive class name list for adding different local devices
     */
    private Emitter.Listener onSetClassNameList = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        Log.e(TAG_Socket, "onGetClassNameList received - " + args[0].toString());
                        JSONObject jsonObject = (JSONObject) args[0];
                        JSONArray jsonArray = jsonObject.getJSONArray("classnamelist");
                        classNameList = new ArrayList<>();
                        for (int i = 0; i < jsonArray.length(); i++) {
                            JSONObject jsonObj = jsonArray.getJSONObject(i);
                            HashMap<String, String> className = new HashMap<String, String>();
                            className.put("classname", jsonObj.getString("classname"));
                            className.put("port", jsonObj.getString("port"));
                            classNameList.add(className);
                        }
                        setNavItem(R.id.nav_add_device, getString(R.string.nav_add_device), true);
                        Log.e(TAG_Socket, "onGetClassNameList succeed!");
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.e(TAG_Socket, "onGetClassNameList failed!");
                    }
                }
            });

        }
    };

    //Handle notification/response sent from the server, e.g.: signin and signout, configurations for the server
    private Emitter.Listener onNotify = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    try {
                        Log.e(TAG_Socket, "onNotify received - " + args[0].toString());
                        JSONObject jsonObject = (JSONObject) args[0];
                        String jsonKey = jsonObject.keys().next();
                        String jsonText = jsonObject.getString(jsonKey);
                        switch (jsonKey) {
                            case "signin":
                                setNavItem(R.id.nav_login, getString(R.string.nav_logout), true);
                                break;
                            case "signout":
                                break;
                            case "invalid":
                                break;
                            case "config":
                                break;
                        }
                        Toast.makeText(DrawerActivity.this, jsonText, Toast.LENGTH_SHORT).show();
                        Log.e(TAG_Socket, "notify succeed!");
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.e(TAG_Socket, "notify failed!");
                    }
                }
            });

        }
    };

    /*
     * Login request (Https post)
     * 1. in order to get an token to establish socket.io connection
     */
    private void login() {
        swipeRefreshLayout.setRefreshing(true);
        loadPreferences();
        setNavItem(R.id.nav_login, getString(R.string.nav_login_ing), false);
        postText = "username=" + username +
                "&password=" + password;
        addressopt = "login";
        //AssetManager assManager = DrawerActivity.this.getAssets();
        new Login().execute(DrawerActivity.this);
        Log.e(TAG_HTTPS, "Login request sent.");
    }

    /*
     * Get a token from the server if users successfully signed in.
     */
    private class Login extends PostTask {
        @Override
        protected InputStream doInBackground(Object... params) {
            return super.doInBackground(params);
        }

        @Override
        protected void onPostExecute(InputStream is) {
            super.onPostExecute(is);
            try {
                if (is == null) {
                    signinProcess("404");
                } else {
                    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(is));
                    signinProcess(bufferedReader.readLine());
                }
                Log.e(TAG_HTTPS, "Login successfully.");
            } catch (IOException e) {
                e.printStackTrace();
                Log.e(TAG_HTTPS, "Login failed.");
            }
        }
    }
    /*
     * Handel the login response from the server
     * 1. if sign in failed, set swipeRefreshLayout's refreshing to false
     * 2. if succeed, use the received token to establish socket.io connection
     */
    private void signinProcess(String responseOutput){
        String toastText;
        switch (responseOutput) {
            case "401":
                toastText = getString(R.string.notify_authorization_failed);
                setNavItem(R.id.nav_login, getString(R.string.nav_login), true);
                break;
            case "404":
                toastText = getString(R.string.notify_connection_failed);
                setNavItem(R.id.nav_login, getString(R.string.nav_login), true);
                swipeRefreshLayout.setRefreshing(false);
                break;
            default:
                toastText = getString(R.string.notify_login_successfully);
                token = responseOutput;
                connectServer(responseOutput);
                break;
        }
        Toast.makeText(DrawerActivity.this, toastText, Toast.LENGTH_SHORT).show();
    }
    /*
     * Get the avatar stored on the server (HTTPS post)
     */
    private class GetAvatar extends PostTask {
        @Override
        protected InputStream doInBackground(Object... params) {
            return super.doInBackground(params);
        }

        @Override
        protected void onPostExecute(InputStream inputStream) {
            super.onPostExecute(inputStream);
            ImageView imageAvatar = (ImageView) navigationView.getHeaderView(0).findViewById(R.id.imageAvatar);
            imageAvatar.setImageBitmap(new AssetUtils().getRoundedBitmap(inputStream));
            Log.e(TAG_HTTPS, "Avatar received.");
        }
    }

    /*
     * Update device's title (Display Name) if it is available
     */
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        Log.e("onActivityResult", Integer.toString(resultCode));
        Bundle bundle;
        switch (resultCode) {
            case RESULT_ADD:
                super.onActivityResult(requestCode, resultCode, data);
                bundle = data.getExtras();
                if (bundle.containsKey("port")) {
                    addDevice(bundle.getString("classname"), bundle.getString("title"), bundle.getInt("port"));
                } else {
                    addDevice(bundle.getString("classname"), bundle.getString("title"));
                }
                break;
            case RESULT_CONFIG:
                super.onActivityResult(requestCode, resultCode, data);
                bundle = data.getExtras();
                if (bundle.containsKey("port")) {
                    configureDevice(bundle.getInt("id"), bundle.getString("title"), bundle.getInt("port"));
                } else {
                    configureDevice(bundle.getInt("id"), bundle.getString("title"));
                }
                break;
            case -1:
                try {
                    new QRCodeUtils().onActivityResult(requestCode, resultCode, data, this);
                } catch (Exception e) {
                    Log.e("QRCodeUtils", e.toString());
                }
            default:
                break;
        }
    }

    /**
     * Disable all the sub-controllers under the viewGroup
     */
/*
    public static void disableSubControllers(ViewGroup viewGroup) {
        for (int i = 0; i < viewGroup.getChildCount(); i++) {
            View v = viewGroup.getChildAt(i);
            if (v instanceof ViewGroup) {
                if (v instanceof Spinner) {
                    Spinner spinner = (Spinner) v;
                    spinner.setClickable(false);
                    spinner.setEnabled(false);
                } else if (v instanceof ListView) {
                    ((ListView) v).setClickable(false);
                    ((ListView) v).setEnabled(false);
                } else {
                    disableSubControllers((ViewGroup) v);
                }
            } else if (v instanceof TextView) {
                ((TextView) v).setEnabled(false);
                ((TextView) v).setClickable(false);
            } else if (v instanceof SeekBar) {
                ((SeekBar) v).setEnabled(false);
            }
        }
    }
*/

    /**
     * Refresh animation when refreshing controllers
     */
/*
    protected MenuItem refreshItem;
    private void showRefreshAnimation(MenuItem item) {
        hideRefreshAnimation();
        refreshItem = item;

        ImageView refreshActionView = (ImageView) getLayoutInflater().inflate(R.layout.action_refresh, null);
        refreshActionView.setImageResource(ic_popup_sync);
        refreshItem.setActionView(refreshActionView);

        Animation animation = AnimationUtils.loadAnimation(this, R.anim.refresh);
        animation.setRepeatMode(Animation.RESTART);
        animation.setRepeatCount(Animation.INFINITE);
        refreshActionView.startAnimation(animation);
    }

    private void hideRefreshAnimation() {
        if (refreshItem != null) {
            View view = refreshItem.getActionView();
            if (view != null) {
                view.clearAnimation();
                refreshItem.setActionView(null);
            }
        }
    }
*/
}
