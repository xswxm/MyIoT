package com.xswxm.myiot.configuredevice;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Toast;

import com.xswxm.myiot.R;

import static com.xswxm.myiot.global.Constants.RESULT_ADD;
import static com.xswxm.myiot.global.Constants.RESULT_CONFIG;

public class ConfigureLocalDeviceActivity extends AppCompatActivity {
    private EditText titleEdt;
    private EditText portEdt;
    private int deviceID;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_configure_local_device);

        Intent intent = getIntent();
        deviceID = intent.getIntExtra("com.xswxm.myiot.deviceID", -1);
        String deviceTitle = intent.getStringExtra("com.xswxm.myiot.deviceTitle");
        int devicePort = intent.getIntExtra("com.xswxm.myiot.devicePort", -1);
        Log.e("Intent", Integer.toString(deviceID) + ", " + Integer.toString(devicePort));
        titleEdt = (EditText) findViewById(R.id.edt_title);
        portEdt = (EditText) findViewById(R.id.edt_port);
        titleEdt.setText(deviceTitle);
        if (devicePort == -1) {
            portEdt.setEnabled(false);
        } else {
            portEdt.setText(Integer.toString(devicePort));
        }

        Button configBtn = (Button) findViewById(R.id.btn_config);
        configBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (titleEdt.getText().toString().isEmpty()) {
                    Toast.makeText(ConfigureLocalDeviceActivity.this, getString(R.string.notify_empty_device_title), Toast.LENGTH_SHORT).show();
                    return;
                } else if (portEdt.getText().toString().isEmpty() && portEdt.isEnabled()) {
                    Toast.makeText(ConfigureLocalDeviceActivity.this, getString(R.string.notify_empty_device_port), Toast.LENGTH_SHORT).show();
                    return;
                }
                //do something
                Intent intent = new Intent();
                intent.putExtra("id", deviceID);
                intent.putExtra("title", titleEdt.getText().toString());
                if (portEdt.isEnabled()) {
                    intent.putExtra("port", Integer.parseInt(portEdt.getText().toString()));
                }
                setResult(RESULT_CONFIG, intent);
                finish();
            }
        });
    }
}
