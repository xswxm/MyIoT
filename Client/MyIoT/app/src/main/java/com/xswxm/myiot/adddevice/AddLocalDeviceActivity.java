package com.xswxm.myiot.adddevice;

import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListAdapter;
import android.widget.SimpleAdapter;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.xswxm.myiot.R;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import static com.xswxm.myiot.global.Constants.RESULT_ADD;
import static com.xswxm.myiot.global.Variables.classNameList;

public class AddLocalDeviceActivity extends AppCompatActivity {
    private EditText titleEdt;
    private EditText portEdt;
    private Spinner classNameSinnper;
    private List<String> classNames = new ArrayList<>();
    private List<String> classPorts = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_local_device);
        titleEdt = (EditText) findViewById(R.id.edt_title);
        portEdt = (EditText) findViewById(R.id.edt_port);
        classNameSinnper = (Spinner) findViewById(R.id.spinner_classname);
        classNameSinnper.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                if (classPorts.get(position).equals("True")) {
                    portEdt.setEnabled(true);
                } else {
                    portEdt.setEnabled(false);
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                portEdt.setEnabled(false);
            }
        });
        Button addBtn = (Button) findViewById(R.id.btn_add);
        addBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (titleEdt.getText().toString().isEmpty()) {
                    Toast.makeText(AddLocalDeviceActivity.this, getString(R.string.notify_empty_device_title), Toast.LENGTH_SHORT).show();
                    return;
                } else if (portEdt.getText().toString().isEmpty() && portEdt.isEnabled()) {
                    Toast.makeText(AddLocalDeviceActivity.this, getString(R.string.notify_empty_device_port), Toast.LENGTH_SHORT).show();
                    return;
                }
                //do something
                Intent intent = new Intent();
                intent.putExtra("classname", classNameSinnper.getSelectedItem().toString());
                intent.putExtra("title", titleEdt.getText().toString());
                if (portEdt.isEnabled()) {
                    intent.putExtra("port", Integer.parseInt(portEdt.getText().toString()));
                }
                setResult(RESULT_ADD, intent);
                finish();

            }
        });

/*
        ArrayAdapter adapter = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_item, classNameList);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        ssidSpinner.setAdapter(adapter);
*/

/*
        ListAdapter adapter = new SimpleAdapter(this, classNameList,
                R.layout.list_item, new String[]{"name", "email",
                "mobile"}, new int[]{R.id.name,
                R.id.email, R.id.mobile});
*/
        for(int i = 0; i < classNameList.size(); i++) {
            classNames.add(classNameList.get(i).get("classname"));
            classPorts.add(classNameList.get(i).get("port"));
        }
        ArrayAdapter adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, classNames);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        classNameSinnper.setAdapter(adapter);
    }
}
