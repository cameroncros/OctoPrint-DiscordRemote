package com.cross.beaglesightwear;

import android.app.Fragment;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesightlibs.PositionCalculator;

/**
 * Created by cameron on 30/12/14.
 */

public class ShowBowFragment extends Fragment implements View.OnClickListener {
    private static final int Fine = 1;
    private static final int Coarse = 5;
    View view = null;
    String bowName = null;
    double distance = 20;

    @Override
    public void setArguments(Bundle args) {
        bowName = (String)args.get("bowName");
        if (view != null) {
            TextView tv = (TextView)view.findViewById(R.id.bowName);
            tv.setText(bowName);
        }
        super.setArguments(args);
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        view = inflater.inflate(R.layout.show_bow_fragment, container, false);
        Button bt = (Button)view.findViewById(R.id.imageButtonMinusCoarse);
        bt.setOnClickListener(this);
        bt = (Button)view.findViewById(R.id.imageButtonPlusCoarse);
        bt.setOnClickListener(this);
        bt = (Button)view.findViewById(R.id.imageButtonMinusFine);
        bt.setOnClickListener(this);
        bt = (Button)view.findViewById(R.id.imageButtonPlusFine);
        bt.setOnClickListener(this);

        TextView tv = (TextView) view.findViewById(R.id.bowName);
        tv.setText(bowName);



        return view;
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
        BowManager bm = BowManager.getInstance(getActivity().getApplicationContext());
        PositionCalculator pc = bm.getPositionCalculator(bowName);
        double position = pc.calcPosition(distance);
        TextView tv = (TextView)view.findViewById(R.id.widgetDistance);
        tv.setText(Double.toString(distance));
        tv = (TextView)view.findViewById(R.id.widgetPosition);
        tv.setText(Double.toString(position));
    }
}