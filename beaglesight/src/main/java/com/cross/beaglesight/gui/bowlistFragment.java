package com.cross.beaglesight.gui;

import android.app.Fragment;
import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.ViewGroup;
import android.widget.TextView;

import com.cross.beaglesight.R;


public class bowlistFragment extends Fragment {
	String bowname = null;
    String bowdescription = null;

	@Override
	public View onCreateView(LayoutInflater inflater, ViewGroup container,
			Bundle savedInstanceState) {
		// Inflate the layout for this fragment
		View vw = inflater.inflate(R.layout.bow_list_fragment, container, false);
		
		if (bowname == null) {
			bowname = savedInstanceState.getString("bowname");
		}

        if (bowdescription == null) {
            bowdescription = savedInstanceState.getString("bowdescription");
        }

		TextView tv = (TextView)vw.findViewById(R.id.bowname);
		tv.setText(bowname);
		tv = (TextView)vw.findViewById(R.id.bowdescription);
		tv.setText(bowdescription);

		vw.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				Intent intent = new Intent(getActivity(), ShowSight.class);
				intent.putExtra("bowname", bowname);
				startActivity(intent);
			}
		});

		return vw;
	}
	
	@Override
    public void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putString("bowname", bowname);
        outState.putString("bowdescription", bowdescription);
    }


	public void setText(String bowname, String bowdescription) {
		this.bowname = bowname;
        this.bowdescription = bowdescription;

	}
}