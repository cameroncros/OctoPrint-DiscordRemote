package com.cross.beaglesight;

import android.app.*;
import android.content.Intent;
import android.os.*;
import android.view.*;
import android.widget.*;
import android.text.*;
import com.cross.beaglesight.PositionCalculator;
import java.text.*;

public class MainActivity extends Activity
{
	BowManager bm = BowManager.getInstance();
	DecimalFormat df = new DecimalFormat("#.##");
	PositionCalculator pc = bm.getPositionCalculator(bm.getCurrentPostion());
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
	{
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
		TextView tv;
		tv=(TextView)findViewById(R.id.meter10);
		pos = pc.calcPosition(10);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter20);
		pos = pc.calcPosition(20);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter30);
		pos = pc.calcPosition(30);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter40);
		pos = pc.calcPosition(40);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter50);
		pos = pc.calcPosition(50);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter60);
		pos = pc.calcPosition(60);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter70);
		pos = pc.calcPosition(70);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter80);
		pos = pc.calcPosition(80);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter90);
		pos = pc.calcPosition(90);
		tv.setText(df.format(pos));
		
		tv=(TextView)findViewById(R.id.meter100);
		pos = pc.calcPosition(100);
		tv.setText(df.format(pos));
	}
	
	public void addNewBow() {
		Intent intent = new Intent(this, AddNewBowActivity.class);
		startActivity(intent);
	}
}
