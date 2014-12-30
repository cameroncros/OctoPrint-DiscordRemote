package com.example.beaglesightwear;

import android.app.Activity;
import android.os.Bundle;
import android.support.wearable.view.GridViewPager;
import android.widget.TextView;

public class MainActivity extends Activity {

    private TextView mTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final GridViewPager pager = (GridViewPager) findViewById(R.id.pager);
        pager.setAdapter(new SampleGridPagerAdapter(this, getFragmentManager()));
    }
}
