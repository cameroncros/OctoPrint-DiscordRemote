package com.cross.beaglesight;

import android.app.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import android.widget.TableLayout.LayoutParams;
import android.text.*;

import com.cross.beaglesight.PositionCalculator;
import java.text.*;

public class MainActivity extends Activity
{
	BowManager bm = null;
	DecimalFormat df = null, hn = null;
	PositionCalculator pc = null;
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
	{
    	bm = BowManager.getInstance();
    	df = new DecimalFormat("#.##");
    	hn = new DecimalFormat("#");
    	pc = bm.getPositionCalculator(bm.getCurrentPostion());
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        calculateIncrements(pc);
        		
		EditText et = (EditText)findViewById(R.id.calcDistance);
		et.addTextChangedListener(new TextWatcher() {
			public void afterTextChanged(Editable s) {
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

	@Override
	public boolean onCreateOptionsMenu(Menu menu)
	{
		// TODO: Implement this method
		MenuInflater inf = getMenuInflater();
		inf.inflate(R.menu.menu, menu);
		return super.onCreateOptionsMenu(menu);
	}
	
	private void calculateIncrements(PositionCalculator pc) {
		Double pos;
		TableLayout tl = (TableLayout)findViewById(R.id.mainTable);
			
		
		Double[] sampleDistances = {10.0, 15.0, 18.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0};
		if(tl.getChildCount() > 0) {
		    tl.removeAllViews(); 
		}

		
		for (Double val : sampleDistances) {
			pos = pc.calcPosition(val);
			TableRow tr = new TableRow(this);
			tr.setLayoutParams(new TableLayout.LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT, 1));
			
			EditText et = new EditText(this);
			et.setEnabled(false);
			et.setGravity(Gravity.RIGHT);
			et.setText(df.format(pos));
			
			TextView tv = new TextView(this);
			tv.setLabelFor(et.getId());
			tv.setTextAppearance(this, android.R.style.TextAppearance_DeviceDefault_Medium);
			tv.setText(hn.format(val)+":");
			
			tr.addView(tv);
			tr.addView(et);
			tl.addView(tr);
			tl.invalidate();
		}
	}
	
//	public void addNewBow() {
//		Intent intent = new Intent(this, AddNewBowActivity.class);
//		startActivity(intent);
//	}
}
