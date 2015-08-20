package com.cross.beaglesight;

import android.app.Activity;
import android.os.Bundle;
import android.support.wearable.view.WatchViewStub;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesightlibs.PositionCalculator;

import java.text.DecimalFormat;

public class ShowBow extends Activity implements View.OnClickListener {
    private static final int Fine = 1;
    private static final int Coarse = 5;
    private ShowBow sb;
    String bowName = null;
    double distance = 20;
    static DecimalFormat df = new DecimalFormat("#.##");
    static DecimalFormat single = new DecimalFormat("#");
    PositionCalculator pc = null;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        sb = this;
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_show_bow);
        Bundle bundle = getIntent().getExtras();
        bowName = bundle.getString("bowname");
        BowManager bm = BowManager.getInstance(this);
        PositionCalculator pc = bm.getPositionCalculator(bowName);
        if (pc == null) {
            finish();
        }
        final WatchViewStub stub = (WatchViewStub) findViewById(R.id.watch_view_stub);
        stub.setOnLayoutInflatedListener(new WatchViewStub.OnLayoutInflatedListener() {
            @Override
            public void onLayoutInflated(WatchViewStub stub) {
                Button bt = (Button) findViewById(R.id.imageButtonMinusCoarse);
                bt.setOnClickListener(sb);
                bt = (Button) findViewById(R.id.imageButtonPlusCoarse);
                bt.setOnClickListener(sb);
                bt = (Button) findViewById(R.id.imageButtonMinusFine);
                bt.setOnClickListener(sb);
                bt = (Button) findViewById(R.id.imageButtonPlusFine);
                bt.setOnClickListener(sb);

                TextView tv = (TextView) findViewById(R.id.bowName);
                tv.setText(bowName);

                updateValues();
            }
        });
    }


    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.imageButtonMinusCoarse:
                distance -= Coarse;
                break;
            case R.id.imageButtonMinusFine:
                distance -= Fine;
                break;
            case R.id.imageButtonPlusCoarse:
                distance += Coarse;
                break;
            case R.id.imageButtonPlusFine:
                distance += Fine;
                break;
        }
        updateValues();
    }

    private void updateValues() {
        double position = pc.calcPosition(distance);
        TextView tv = (TextView)findViewById(R.id.widgetDistance);
        tv.setText(single.format(distance));
        tv = (TextView)findViewById(R.id.widgetPosition);
        tv.setText(df.format(position));
    }
}
