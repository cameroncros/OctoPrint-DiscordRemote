package com.cross.beaglesight.gui;

import android.app.ActionBar;
import android.app.Activity;
import android.os.Bundle;
import android.text.InputType;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TableLayout;
import android.widget.TableRow;

import com.cross.beaglesight.R;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.mariux.teleport.lib.TeleportClient;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

public class AddActivity extends Activity {
	int methodChoice;
	private TeleportClient mTeleportClient;

	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.add);
		ActionBar actionBar = getActionBar();
		actionBar.setDisplayHomeAsUpEnabled(true);

        mTeleportClient = new TeleportClient(this);

		Spinner spinner = (Spinner) findViewById(R.id.types_spinner);
		// Create an ArrayAdapter using the string array and a default spinner layout
		ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
				R.array.choices_array, android.R.layout.simple_spinner_item);
		// Specify the layout to use when the list of choices appears
		adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
		// Apply the adapter to the spinner
		spinner.setAdapter(adapter);
		spinner.setOnItemSelectedListener(
			new OnItemSelectedListener() {
				@Override
				public void onItemSelected(AdapterView<?> parent, View view, int position,
						long id) {
					methodChoice = position;

				}

				@Override
				public void onNothingSelected(AdapterView<?> parent) {

				}
			});

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
		BowManager bm = BowManager.getInstance(this.getApplicationContext());
		BowConfig bc = bm.getBow(bowname);
		EditText name = (EditText)findViewById(R.id.addName);
		name.setText(bc.getName());
		EditText des = (EditText)findViewById(R.id.addDescription);
		des.setText(bc.getDescription());
		
		Spinner sp = (Spinner)findViewById(R.id.types_spinner);
		sp.setSelection(bc.getMethod());



		TableLayout tl = (TableLayout)findViewById(R.id.addTable);
		tl.removeAllViews();

		Map<String, String> pos = bc.getPositions();
        List<String> keys = new ArrayList(pos.keySet());
        java.util.Collections.sort(keys, new SightSort());
		for (String distance : keys) {
			String position = pos.get(distance);
			addPair(distance, position);
		}



	}

    public class SightSort implements Comparator<String> {
        @Override
        public int compare(String mdi1, String mdi2) {
            if (mdi1.length() < mdi2.length()) {
                return -1;
            } else if (mdi1.length() > mdi2.length()) {
                return 1;
            } else {
                return mdi1.compareTo(mdi2);
            }
        }
    }
    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        // TODO: Implement this method
        MenuInflater inf = getMenuInflater();
        inf.inflate(R.menu.menu_add, menu);
        return super.onCreateOptionsMenu(menu);
    }


	void resetPairs() {
		TableLayout tl = (TableLayout)findViewById(R.id.addTable);
		tl.removeAllViews();
		addPair("20", null);
		addPair("30", null);
		addPair("40", null);
	}

	public boolean addEmptyPair(View bt) {
		addPair(null, null);

        mTeleportClient.syncByteArray("hello","asdfasdf".getBytes());
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
		del.setBackground(this.getResources().getDrawable(R.drawable.ic_action_cancel));
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

	public boolean saveBow() {
		BowManager bm = BowManager.getInstance(this.getApplicationContext());
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

		bc.setMethod(methodChoice);

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
        String protoString = bc.toString();
        //mTeleportClient.syncString(bc.getFileName(), protoString);
		mTeleportClient.syncByteArray("hello", protoString.getBytes());
		finish();
		return false;
	}

	public boolean onOptionsItemSelected(MenuItem item){
		switch (item.getItemId()) {
		case android.R.id.home:
			finish();
			return true;
        case R.id.save:
            saveBow();
            return true;

		}
		return false;
	}

    @Override
    protected void onStart() {
        super.onStart();
        mTeleportClient.connect();
    }

    @Override
    protected void onStop() {
        super.onStop();
        mTeleportClient.disconnect();
    }
}
