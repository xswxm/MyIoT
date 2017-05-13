package com.xswxm.myiot.controller;

import android.content.Context;
import android.util.AttributeSet;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.TextView;

import com.xswxm.myiot.R;
import com.xswxm.myiot.animation.RefreshAnimation;

import static android.R.drawable.ic_popup_sync;

/**
 * Created by Air on 3/24/2017.
 */

public class MyButton extends RelativeLayout {
    private TextView deviceName;
    private ImageView imageView;
    private Button removeBtn;
    private Button configBtn;
    public int devicePort;

    public MyButton(Context context) {
        this(context,null);
    }
    public MyButton(Context context, AttributeSet attrs) {
        super(context, attrs);
        initView(context);
    }
    private void initView(Context context) {
        View.inflate(context, R.layout.my_button, this);
        deviceName = (TextView) this.findViewById(R.id.deviceName);
        imageView = (ImageView) this.findViewById(R.id.imageView);
        imageView.setImageResource(ic_popup_sync);
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
        removeBtn.setEnabled(status);
        configBtn.setEnabled(status);
        imageView.setEnabled(status);
    }

    public void setDeviceAnimation(boolean status) {
        if (status) {
            RefreshAnimation.showRefreshAnimation(imageView, MyButton.this.getContext());
        }
        else {
            RefreshAnimation.hideRefreshAnimation(imageView);
        }
    }

    public void setOnTouchLisener(OnTouchListener lisener) {
        imageView.setOnTouchListener(lisener);
    }

    public void setOnRemoveClickListener(OnClickListener listener){
        removeBtn.setOnClickListener(listener);
    }

    public void setOnConfigureClickListener(OnClickListener listener){
        configBtn.setOnClickListener(listener);
    }
}
