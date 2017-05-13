package com.xswxm.myiot;

import android.content.Intent;
import android.content.res.Configuration;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;

import com.xswxm.myiot.global.Constants;
import com.xswxm.myiot.utils.SpUtils;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);


/*        if (!SpUtils.getBoolean(this,Constants.FIRSTBOOT)) {
            //Put default variables
            SpUtils.putBoolean(this, Constants.AUTOLOGIN, false);
            SpUtils.putString(this, Constants.USERNAME, "username");
            SpUtils.putString(this, Constants.PASSWORD, "password");
            SpUtils.putString(this, Constants.ADDRESS, "https://192.168.1.200:8888/");
            SpUtils.putInt(this, Constants.SYNCINTERVAL, 600);
            SpUtils.putBoolean(this, Constants.FIRSTBOOT, true);
        }*/

        Intent intent = new Intent(MainActivity.this,
                DrawerActivity.class);
        startActivity(intent);
        finish();
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
    }

    @Override
    protected void onResume() {
        super.onResume();
    }

}
