package com.cross.beaglesight.gui;

import java.text.DecimalFormat;

import android.app.ActionBar;
import android.content.Intent;
import android.os.*;
import android.view.*;
import android.widget.EditText;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.TableLayout.LayoutParams;
import android.support.v4.app.FragmentActivity;
import android.text.Editable;
import android.text.TextWatcher;

import com.cross.beaglesight.BowManager;
import com.cross.beaglesight.PositionCalculator;
import com.cross.beaglesight.R;

public class ShowSight extends FragmentActivity
{
	DecimalFormat df = null, hn = null;
	BowManager bm = null;
	PositionCalculator pc = null;

	String bowname = null;
	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.showsight);

	}
	
	@Override
	protected void onStart() {
		super.onStart();
		Bundle bundle = getIntent().getExtras();
		bowname = bundle.getString("bowname");
		setTitle(bowname);
		ActionBar actionBar = getActionBar();
		actionBar.setDisplayHomeAsUpEnabled(true);
		bm = BowManager.getInstance();
		hn = new DecimalFormat("#");
		df = new DecimalFormat("#.##");
		pc = bm.getPositionCalculator(bowname);
		textListenerSetup();
		calculateIncrements();
	};

	@Override
	public boolean onCreateOptionsMenu(Menu menu)
	{
		// TODO: Implement this method
		MenuInflater inf = getMenuInflater();
		inf.inflate(R.menu.show_sight_menu, menu);
		return super.onCreateOptionsMenu(menu);
	}

	private void calculateIncrements() {
		Double pos = 0.0;
		TableLayout tl = (TableLayout)findViewById(R.id.mainTable);


		Double[] sampleDistances = {10.0, 15.0, 18.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0};
		if(tl.getChildCount() > 0) {
			tl.removeAllViews(); 
		}


		for (Double val : sampleDistances) {
			//TODO highlight known values
			if (pc != null) {
				pos = pc.calcPosition(val);
			}
			TableRow tr = new TableRow(this);
			tr.setLayoutParams(new TableLayout.LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT, 1));

			EditText et = new EditText(this);
			et.setEnabled(false);
			et.setGravity(Gravity.RIGHT);
			et.setText(df.format(pos));

			TextView tv = new TextView(this);
			tv.setLabelFor(et.getId());
			tv.setTextSize(18);
			tv.setText(hn.format(val)+":");

			tr.addView(tv);
			tr.addView(et);
			tl.addView(tr);
		}

		tl.invalidate();
	}

	private void textListenerSetup() {
		EditText et = (EditText)findViewById(R.id.calcDistance);
		et.addTextChangedListener(new TextWatcher() {
			public void afterTextChanged(Editable s) {
				BowManager bm = BowManager.getInstance();
				pc = bm.getPositionCalculator(bowname);
				Double pos;
				EditText et = (EditText)findViewById(R.id.calcDistance);
				TextView tv = (TextView)findViewById(R.id.calcPosition);
				try {
					Double dist = Double.valueOf(et.getText().toString());
					pos = pc.calcPosition(dist);
					tv.setText(df.format(pos));
				}
				catch (NumberFormatException e) {
					tv.setText("");
				}

			}

			public void beforeTextChanged(CharSequence s, int a, int b, int c) {}
			public void onTextChanged(CharSequence s, int a, int b, int c) {}

		});
	}

	public boolean onOptionsItemSelected(MenuItem item){
		Intent intent;
		switch (item.getItemId()) {
		case android.R.id.home:
			finish();
			return true;
		case R.id.menu_edit:
			intent = new Intent(getApplicationContext(), AddActivity.class);
			intent.putExtra("bowname", bowname);
			startActivity(intent);
			return true;
		//case R.id.menu_share:
		case R.id.menu_delete:
			bm.deleteBow(bowname);
			intent = new Intent(getApplicationContext(), MainActivity.class);
			startActivityForResult(intent, 0);
			return true;
		default:
			return false;

		}
	}
}
