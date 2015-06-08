package com.cross.beaglesightwear;

import android.os.Bundle;
import android.support.wearable.activity.WearableActivity;
import android.support.wearable.view.GridViewPager;
import android.widget.TextView;

public class MainActivity extends WearableActivity {
    private TextView mTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final GridViewPager pager = (GridViewPager) findViewById(R.id.pager);
        pager.setAdapter(new SampleGridPagerAdapter(this, getFragmentManager()));
        setAmbientEnabled();
    }

    @Override
    public void onEnterAmbient(Bundle ambientDetails) {
        super.onEnterAmbient(ambientDetails);

//        mStateTextView.setTextColor(Color.WHITE);
//        mStateTextView.getPaint().setAntiAlias(false);
    }

    @Override
    public void onExitAmbient() {
        super.onExitAmbient();

//        mStateTextView.setTextColor(Color.GREEN);
//        mStateTextView.getPaint().setAntiAlias(true);
    }
}
