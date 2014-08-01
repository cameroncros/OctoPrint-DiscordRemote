package com.cross.beaglesight.gui;

import android.app.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import android.widget.TableLayout.LayoutParams;
import android.support.v4.app.ActionBarDrawerToggle;
import android.support.v4.widget.DrawerLayout;
import android.text.*;

import com.cross.beaglesight.BowManager;
import com.cross.beaglesight.PositionCalculator;
import com.cross.beaglesight.R;
import java.text.*;

public class MainActivity extends Activity
{
//    private String[] mPlanetTitles;
//    private DrawerLayout mDrawerLayout;
    private TableLayout mDrawerList;
    private DrawerLayout mDrawerLayout;
    private ActionBarDrawerToggle mDrawerToggle;
	
	BowManager bm = null;
	DecimalFormat df = null, hn = null;
	PositionCalculator pc = null;
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
	{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        mDrawerList = (TableLayout) findViewById(R.id.left_drawer);
        
        mDrawerLayout = (DrawerLayout) findViewById(R.id.drawer_layout);
        mDrawerToggle = new ActionBarDrawerToggle(this, mDrawerLayout,
                R.drawable.ic_drawer, R.string.drawer_open, R.string.drawer_close) {

            /** Called when a drawer has settled in a completely closed state. */
            public void onDrawerClosed(View view) {
                super.onDrawerClosed(view);
                invalidateOptionsMenu(); // creates call to onPrepareOptionsMenu()
            }

            /** Called when a drawer has settled in a completely open state. */
            public void onDrawerOpened(View drawerView) {
                super.onDrawerOpened(drawerView);
                invalidateOptionsMenu(); // creates call to onPrepareOptionsMenu()
            }
        };

        // Set the drawer toggle as the DrawerListener
        mDrawerLayout.setDrawerListener(mDrawerToggle);
        
        
        
        bm = BowManager.getInstance();
    	bm.loadBows(this);
    	
    	fillSideBar();
//    	bm.saveBows(this);
    	df = new DecimalFormat("#.##");
    	hn = new DecimalFormat("#");
    	pc = bm.getPositionCalculator(bm.getCurrentBow());
    	
    	if (pc == null) {
    		//TODO: show popup telling user to add a bow config and select it
    		return;
    	}

        
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

	private void fillSideBar() {
		bm = BowManager.getInstance();
		TableLayout lv = (TableLayout)findViewById(R.id.left_drawer);
		if(lv.getChildCount() > 0) {
		    lv.removeAllViews(); 
		}
		for (String bowname : bm.getBowList()) {
			TableRow tr = new TableRow(this);
			tr.setLayoutParams(new TableRow.LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT, 1));
			
			TextView tv = new TextView(this);
			tv.setTextAppearance(this, android.R.style.TextAppearance_DeviceDefault_Medium);
			tv.setText(bowname);
			
			Button edit = new Button(this);
			edit.setText(R.string.edit);
			
			Button del = new Button(this);
			del.setText(R.string.delete);
			
			tr.addView(tv);
			tr.addView(edit);
			tr.addView(del);
			lv.addView(tr);
			lv.invalidate();
			
		}
		// TODO Auto-generated method stub
		
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
