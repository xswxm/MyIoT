package com.xswxm.myiot.controller;

import android.content.Context;
import android.util.AttributeSet;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.SeekBar;
import android.widget.TextView;

import com.xswxm.myiot.R;
import com.xswxm.myiot.animation.RefreshAnimation;

import static android.R.drawable.ic_popup_sync;

/**
 * Created by Air on 3/24/2017.
 */

public class MySeekBar extends RelativeLayout {
    private TextView deviceName;
    private TextView deviceValue;
    private ImageView imageView;
    private SeekBar deviceSeekBar;
    private Button removeBtn;
    private Button configBtn;
    public int devicePort;

    public MySeekBar(Context context) {
        this(context,null);
    }
    public MySeekBar(Context context, AttributeSet attrs) {
        super(context, attrs);
        initView(context);
    }
    private void initView(Context context) {
        View.inflate(context, R.layout.my_seekbar, this);
        deviceName = (TextView) this.findViewById(R.id.deviceName);
        deviceValue = (TextView) this.findViewById(R.id.deviceValue);
        imageView = (ImageView) this.findViewById(R.id.imageView);
        deviceSeekBar = (SeekBar) this.findViewById(R.id.deviceSeekBar);
        removeBtn = (Button) this.findViewById(R.id.btn_remove);
        configBtn = (Button) this.findViewById(R.id.btn_config);
    }

    public void setTitle(String title) {
        deviceName.setText(title);
    }
    public String getTitle() {
        return deviceName.getText().toString();
    }

    public void setDeviceEnabled(boolean status) {
        deviceValue.setEnabled(status);
        deviceSeekBar.setEnabled(status);
        removeBtn.setEnabled(status);
        configBtn.setEnabled(status);
        if(status) {
            RefreshAnimation.hideRefreshAnimation(imageView);
            imageView.setImageResource(0);
        }
        else {
            setDeviceValue("");
            imageView.setImageResource(ic_popup_sync);
            RefreshAnimation.showRefreshAnimation(imageView, MySeekBar.this.getContext());
        }
    }

    public void setOnValueClickLisener(OnClickListener l) {
        deviceValue.setOnClickListener(l);
    }

    public void setOnRemoveClickListener(OnClickListener listener){
        removeBtn.setOnClickListener(listener);
    }

    public void setOnConfigureClickListener(OnClickListener listener){
        configBtn.setOnClickListener(listener);
    }

    public void setDeviceValue(String val) {
        deviceValue.setText(val);
    }

    public void setDeviceSeekBar(String val) {
        val = val.replace(" ", "").replace("%", "");
        int progress = Integer.parseInt(val);
        deviceSeekBar.setProgress(progress );
    }

    public void setOnSeekBarChangeListener(SeekBar.OnSeekBarChangeListener onSeekBarChangeListener){
        deviceSeekBar.setOnSeekBarChangeListener(onSeekBarChangeListener);
    }
}
