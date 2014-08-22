package com.cross.beaglesight.gui;

import java.util.Map;

import com.cross.beaglesight.BowConfig;
import com.cross.beaglesight.BowManager;
import com.cross.beaglesight.R;

import android.app.ActionBar;
import android.app.Activity;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TableLayout;
import android.widget.TableRow;

public class AddActivity extends Activity {
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.add);
		ActionBar actionBar = getActionBar();
		actionBar.setDisplayHomeAsUpEnabled(true);
		try {
			Bundle bundle = getIntent().getExtras();
			String bowname = bundle.getString("bowname");

			loadBow(bowname);
		}
		catch (NullPointerException e) {
			resetPairs();
		}
	}

	private void loadBow(String bowname) {
		BowManager bm = BowManager.getInstance();
		BowConfig bc = bm.getBow(bowname);
		EditText name = (EditText)findViewById(R.id.addName);
		name.setText(bc.getName());
		EditText des = (EditText)findViewById(R.id.addDescription);
		des.setText(bc.getDescription());



		TableLayout tl = (TableLayout)findViewById(R.id.addTable);
		tl.removeAllViews();

		Map<String, String> pos = bc.getPositions();

		for (String distance : pos.keySet()) {
			String position = pos.get(distance);
			addPair(distance, position);
		}



	}

	public void onStart() {
		super.onStart();
	}


	void resetPairs() {
		TableLayout tl = (TableLayout)findViewById(R.id.addTable);
		tl.removeAllViews();
		addPair(null, null);
		addPair(null, null);
		addPair(null, null);
	}

	public boolean addEmptyPair(View bt) {
		addPair(null, null);
		return false;
	}

	void addPair(String distance, String position) {
		TableLayout tl = (TableLayout)findViewById(R.id.addTable);
		TableRow tr = new TableRow(this);
		EditText dist = new EditText(this);
		dist.setHint(R.string.distance);
		dist.setTag("dist");
		dist.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_CLASS_PHONE);
		if (distance != null) {
			dist.setText(distance);
		}

		EditText pos = new EditText(this);
		pos.setHint(R.string.position);
		pos.setTag("pos");
		pos.setInputType(InputType.TYPE_CLASS_NUMBER | InputType.TYPE_CLASS_PHONE);
		if (position != null) {
			pos.setText(position);
		}

		Button del = new Button(this);
		del.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				deletePair(v);
			}
		});

		dist.setNextFocusForwardId(pos.getId());

		tr.addView(dist);
		tr.addView(pos);
		tr.addView(del);
		tl.addView(tr);
		tl.invalidate();
	}

	public boolean deletePair(View bt) {
		TableRow tr = (TableRow)bt.getParent();
		TableLayout tl = (TableLayout)tr.getParent();
		tl.removeView(tr);
		return false;
	}

	public boolean saveBow(View v) {
		BowManager bm = BowManager.getInstance();
		BowConfig bc = new BowConfig();
		EditText name = (EditText)findViewById(R.id.addName);
		bc.setName(name.getText().toString());
		String namestring = bc.getName();
		if (namestring == null || namestring == "") {
			Log.e("Invalid Name", "Not a valid name");
			return false;
		}
		EditText des = (EditText)findViewById(R.id.addDescription);
		bc.setDescription(des.getText().toString());

		TableLayout tl = (TableLayout)findViewById(R.id.addTable);

		//TODO:
		for (int i = 0; i < tl.getChildCount(); i++) {
			TableRow tr = (TableRow)tl.getChildAt(i);
			String distance = null;
			String position = null;
			for (int j = 0; j < tr.getChildCount(); j++) {
				View te = tr.getChildAt(j);
				if (te.getTag() != null) {
					if (te.getTag() == "dist") {
						distance = ((EditText) te).getText().toString();
					} else if (te.getTag() == "pos") {
						position = ((EditText) te).getText().toString();
					}
				}
			}
			try {
				if (Double.valueOf(distance) != Double.NaN && Double.valueOf(distance) != Double.NaN) {
					bc.addPosition(distance, position);
				} else {
					Log.e("BeagleSight", "Failed to get valid coordinates");
				}
			}
			catch (Exception e) {

			}

		}

		bm.saveNewBowConfig(bc);

		finish();
		return false;
	}
	
	public boolean onOptionsItemSelected(MenuItem item){
		switch (item.getItemId()) {
		case android.R.id.home:
			finish();
			return true;
		}
		return false;
	}
}
