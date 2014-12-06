package com.cross.beaglesight.gui;

import java.util.Set;

import android.app.FragmentManager;
import android.app.FragmentTransaction;
import android.content.Intent;
import android.os.*;
import android.view.*;
import android.widget.LinearLayout;
import android.support.v4.app.FragmentActivity;
import com.cross.beaglesight.BowManager;
import com.cross.beaglesight.R;

public class MainActivity extends FragmentActivity
{
	BowManager bm = null;
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
	{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        bm = BowManager.getInstance();
        bm.setContext(this);
        
        fillBowList();   
    }
    
    @Override
	protected void onStart() {
    	super.onStart();
    	fillBowList();  
    };
    
    @Override
	public boolean onCreateOptionsMenu(Menu menu)
	{
		// TODO: Implement this method
		MenuInflater inf = getMenuInflater();
		inf.inflate(R.menu.menu, menu);
		return super.onCreateOptionsMenu(menu);
	}
    
    
    
    
    
    void fillBowList() {
    	BowManager bm = BowManager.getInstance();
    	bm.loadBows();
    	
    	LinearLayout lv = (LinearLayout) findViewById(R.id.bowList);
    	lv.removeAllViews(); 
    	FragmentManager fragmentManager = getFragmentManager();
    	
    	

		Set<String> bows = bm.getBowList();

		for (String bowname : bows) {
			 
			FragmentTransaction fragmentTransaction = fragmentManager.beginTransaction();
            bowlistFragment hello = new bowlistFragment();
           
            fragmentTransaction.add(R.id.bowList, hello, bowname);
            fragmentTransaction.commit();
            hello.setText(bowname);
		
		}

		lv.invalidate();
	
	}
    

	
	


	
	public boolean addNewBow(MenuItem item) {
		Intent intent = new Intent(this, AddActivity.class);
		startActivity(intent);
		return false;
	}
}
