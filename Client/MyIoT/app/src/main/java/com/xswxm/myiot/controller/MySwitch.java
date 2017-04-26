package com.xswxm.myiot.controller;

import android.app.Activity;
import android.content.Context;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.RelativeLayout;
import android.widget.Switch;
import android.widget.TextView;

import com.xswxm.myiot.DrawerActivity;
import com.xswxm.myiot.R;

/**
 * Created by Air on 3/24/2017.
 */

public class MySwitch extends RelativeLayout {
    private TextView deviceName;
    private Switch deviceSwitch;
    private Button removeBtn;
    private Button configBtn;
    public int devicePort;

    public MySwitch(Context context) {
        this(context,null);
    }
    public MySwitch(Context context, AttributeSet attrs) {
        super(context, attrs);
        initView(context);
    }
    private void initView(Context context) {
        View.inflate(context, R.layout.my_switch, this);
        deviceName = (TextView) this.findViewById(R.id.deviceName);
        deviceSwitch = (Switch) this.findViewById(R.id.deviceSwitch);
        removeBtn = (Button) this.findViewById(R.id.btn_remove);
        configBtn = (Button) this.findViewById(R.id.btn_config);
    }

    public void setTitle(String title) {
        deviceName.setText(title);
    }
    public String getTitle() {
        return deviceName.getText().toString();
    }

    public void setOnCheckedChangeListener(CompoundButton.OnCheckedChangeListener listener){
        deviceSwitch.setOnCheckedChangeListener(listener);
    }

    public void setOnRemoveClickListener(OnClickListener listener){
        removeBtn.setOnClickListener(listener);
    }

    public void setOnConfigureClickListener(OnClickListener listener){
        configBtn.setOnClickListener(listener);
    }

    public void setChecked(boolean checked) {
        deviceSwitch.setChecked(checked);
    }

    public void setDeviceEnabled(boolean status) {
        deviceSwitch.setEnabled(status);
        removeBtn.setEnabled(status);
        configBtn.setEnabled(status);
    }

}
